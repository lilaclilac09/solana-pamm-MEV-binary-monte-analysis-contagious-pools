//! Rust port of `08_monte_carlo_risk/mev_contagion_monte_carlo.py`.
//!
//! Reproduces the three Monte Carlo scenarios (jito_baseline, bam_privacy,
//! harmony_multibuilder) and writes one CSV per scenario plus a summary CSV
//! whose schema and column order match the Python output.
//!
//! Each scenario is independent so we run them in parallel via Rayon. The
//! per-scenario RNG is seeded deterministically (base_seed + scenario index)
//! so a given (--seed, --n-sims) pair produces identical output across
//! invocations.

use std::fs::File;
use std::path::PathBuf;
use std::sync::Mutex;
use std::time::Instant;

use clap::Parser;
use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};
use rand_distr::{Binomial, Distribution, Normal, Uniform};
use rayon::prelude::*;
use serde::Serialize;

#[derive(Parser, Debug)]
#[command(version, about = "Rust port of the MEV contagion Monte Carlo")]
struct Cli {
    /// Number of simulations per scenario (Python default: 100_000)
    #[arg(long, default_value_t = 100_000)]
    n_sims: u32,

    /// Base RNG seed; per-scenario seed = base + scenario index
    #[arg(long, default_value_t = 42)]
    seed: u64,

    /// Override default oracle lag in milliseconds
    #[arg(long, default_value_t = 180.0)]
    oracle_lag_ms: f64,

    /// Output directory for the per-scenario CSVs and summary CSV
    #[arg(long, default_value = "08_monte_carlo_risk/outputs/rust")]
    out_dir: PathBuf,

    /// Optional scenario filter ("all" or one of the scenario keys)
    #[arg(long, default_value = "all")]
    scenario: String,

    /// Optional tag suffix for output filenames (default: "rust")
    #[arg(long, default_value = "rust")]
    tag: String,
}

#[derive(Clone, Copy)]
struct Scenario {
    key: &'static str,
    name: &'static str,
    base_trigger_prob: f64,
    cascade_rate: f64,
    visibility_reduction: f64,
    competition_factor: Option<f64>,
}

const SCENARIOS: &[Scenario] = &[
    Scenario {
        key: "jito_baseline",
        name: "Jito Baseline (Current)",
        base_trigger_prob: 0.15,
        cascade_rate: 0.801,
        visibility_reduction: 0.0,
        competition_factor: None,
    },
    Scenario {
        key: "bam_privacy",
        name: "BAM Privacy (65% visibility reduction)",
        base_trigger_prob: 0.15,
        cascade_rate: 0.801,
        visibility_reduction: 0.65,
        competition_factor: None,
    },
    Scenario {
        key: "harmony_multibuilder",
        name: "Harmony Multi-Builder (40% reduction + competition)",
        base_trigger_prob: 0.15,
        cascade_rate: 0.801,
        visibility_reduction: 0.40,
        competition_factor: Some(0.8),
    },
];

const SLOT_TIME_MS: f64 = 400.0;
const RUNS_PER_SLOT: u64 = 5;
const SKIPPED_SLOT_THRESHOLD: u32 = 3;

#[derive(Serialize)]
struct SimRow {
    sim: u32,
    trigger: u8,
    cascades: u32,
    slots_jumped: u32,
    total_loss: f64,
    scenario: &'static str,
    scenario_name: &'static str,
    infra_gap: f64,
    high_risk: u8,
    oracle_lag_ms: f64,
}

#[derive(Serialize)]
struct SummaryRow {
    scenario: &'static str,
    n_sims: u32,
    attack_rate: f64,
    attack_rate_pct: f64,
    mean_cascades: f64,
    median_cascades: f64,
    p90_cascades: f64,
    p99_cascades: f64,
    mean_slots_jumped: f64,
    p90_slots_jumped: f64,
    p99_slots_jumped: f64,
    mean_loss: f64,
    p90_loss: f64,
    high_risk_rate: f64,
    high_risk_pct: f64,
    mean_infra_gap: f64,
    elapsed_ms: u64,
}

fn quantile(sorted: &[f64], q: f64) -> f64 {
    // Linear-interpolation quantile, matching pandas' default ("linear")
    if sorted.is_empty() {
        return 0.0;
    }
    if sorted.len() == 1 {
        return sorted[0];
    }
    let pos = q * (sorted.len() as f64 - 1.0);
    let lo = pos.floor() as usize;
    let hi = pos.ceil() as usize;
    if lo == hi {
        sorted[lo]
    } else {
        let frac = pos - lo as f64;
        sorted[lo] * (1.0 - frac) + sorted[hi] * frac
    }
}

fn median(sorted: &[f64]) -> f64 {
    quantile(sorted, 0.5)
}

fn run_scenario(
    scenario: &Scenario,
    n_sims: u32,
    oracle_lag: f64,
    base_seed: u64,
    scenario_index: u64,
    out_path: &PathBuf,
) -> SummaryRow {
    let started = Instant::now();

    // Per-scenario seed keeps each scenario reproducible while still
    // letting them run in parallel safely.
    let mut rng = StdRng::seed_from_u64(base_seed.wrapping_add(scenario_index));

    let visibility_red = scenario.visibility_reduction;
    let mut effective_cascade_rate = scenario.cascade_rate * (1.0 - visibility_red);
    if let Some(cf) = scenario.competition_factor {
        effective_cascade_rate *= cf;
    }
    // Clamp to [0, 1] for safety when constructing Binomial.
    let p_cascade = effective_cascade_rate.clamp(0.0, 1.0);

    let cascade_time_dist = Uniform::new(100.0_f64, 700.0_f64);
    let normal_noise = Normal::new(0.0_f64, 20.0_f64).expect("valid normal");
    let loss_per_cascade = 50.0 + oracle_lag * 0.3;
    let baseline_loss_jito = 5.0 * loss_per_cascade;

    let mut writer = csv::Writer::from_path(out_path).expect("open output CSV");

    let mut triggered_cascades: Vec<f64> = Vec::with_capacity(n_sims as usize / 5);
    let mut triggered_slots: Vec<f64> = Vec::with_capacity(n_sims as usize / 5);
    let mut triggered_loss: Vec<f64> = Vec::with_capacity(n_sims as usize / 5);
    let mut trigger_count: u32 = 0;
    let mut high_risk_count: u32 = 0;
    let mut infra_gap_sum: f64 = 0.0;

    for sim in 0..n_sims {
        let trigger: bool = rng.gen::<f64>() < scenario.base_trigger_prob;
        if !trigger {
            writer
                .serialize(SimRow {
                    sim,
                    trigger: 0,
                    cascades: 0,
                    slots_jumped: 0,
                    total_loss: 0.0,
                    scenario: scenario.key,
                    scenario_name: scenario.name,
                    infra_gap: 0.0,
                    high_risk: 0,
                    oracle_lag_ms: oracle_lag,
                })
                .expect("write row");
            continue;
        }

        trigger_count += 1;

        // Binomial(n=runs_per_slot, p=effective_cascade_rate)
        let bin = Binomial::new(RUNS_PER_SLOT, p_cascade).expect("valid binomial");
        let cascades = bin.sample(&mut rng) as u32;

        let slots_jumped = if cascades > 0 {
            let total: f64 = (0..cascades)
                .map(|_| cascade_time_dist.sample(&mut rng))
                .sum();
            (total / SLOT_TIME_MS).ceil() as u32
        } else {
            0
        };

        let noise = normal_noise.sample(&mut rng);
        let mut total_loss = (cascades as f64) * loss_per_cascade + noise;
        if total_loss < 0.0 {
            total_loss = 0.0;
        }

        let infra_gap = if scenario.key == "jito_baseline" {
            0.0
        } else if baseline_loss_jito > 0.0 {
            ((baseline_loss_jito - total_loss) / baseline_loss_jito).max(0.0)
        } else {
            0.0
        };

        let high_risk = (slots_jumped > SKIPPED_SLOT_THRESHOLD) as u8;
        if high_risk == 1 {
            high_risk_count += 1;
        }
        infra_gap_sum += infra_gap;

        triggered_cascades.push(cascades as f64);
        triggered_slots.push(slots_jumped as f64);
        triggered_loss.push(total_loss);

        writer
            .serialize(SimRow {
                sim,
                trigger: 1,
                cascades,
                slots_jumped,
                total_loss,
                scenario: scenario.key,
                scenario_name: scenario.name,
                infra_gap,
                high_risk,
                oracle_lag_ms: oracle_lag,
            })
            .expect("write row");
    }

    writer.flush().expect("flush csv");

    triggered_cascades.sort_by(|a, b| a.partial_cmp(b).unwrap());
    triggered_slots.sort_by(|a, b| a.partial_cmp(b).unwrap());
    triggered_loss.sort_by(|a, b| a.partial_cmp(b).unwrap());

    let n = n_sims as f64;
    let attack_rate = trigger_count as f64 / n;
    let mean = |v: &[f64]| -> f64 {
        if v.is_empty() {
            0.0
        } else {
            v.iter().sum::<f64>() / v.len() as f64
        }
    };

    SummaryRow {
        scenario: scenario.key,
        n_sims,
        attack_rate,
        attack_rate_pct: attack_rate * 100.0,
        mean_cascades: mean(&triggered_cascades),
        median_cascades: median(&triggered_cascades),
        p90_cascades: quantile(&triggered_cascades, 0.90),
        p99_cascades: quantile(&triggered_cascades, 0.99),
        mean_slots_jumped: mean(&triggered_slots),
        p90_slots_jumped: quantile(&triggered_slots, 0.90),
        p99_slots_jumped: quantile(&triggered_slots, 0.99),
        mean_loss: mean(&triggered_loss),
        p90_loss: quantile(&triggered_loss, 0.90),
        high_risk_rate: high_risk_count as f64 / n,
        high_risk_pct: (high_risk_count as f64 / n) * 100.0,
        mean_infra_gap: infra_gap_sum / n,
        elapsed_ms: started.elapsed().as_millis() as u64,
    }
}

fn main() {
    let cli = Cli::parse();
    std::fs::create_dir_all(&cli.out_dir).expect("create output dir");

    let selected: Vec<(usize, &Scenario)> = SCENARIOS
        .iter()
        .enumerate()
        .filter(|(_, s)| cli.scenario == "all" || cli.scenario == s.key)
        .collect();

    if selected.is_empty() {
        eprintln!(
            "Unknown scenario '{}'. Choose: all | {}",
            cli.scenario,
            SCENARIOS
                .iter()
                .map(|s| s.key)
                .collect::<Vec<_>>()
                .join(" | ")
        );
        std::process::exit(2);
    }

    println!("=== Rust Monte Carlo: MEV contagion ===");
    println!(
        "n_sims={}  seed={}  oracle_lag_ms={}  scenarios={:?}  out_dir={}",
        cli.n_sims,
        cli.seed,
        cli.oracle_lag_ms,
        selected.iter().map(|(_, s)| s.key).collect::<Vec<_>>(),
        cli.out_dir.display()
    );
    let global_start = Instant::now();

    let summary_rows = Mutex::new(Vec::<SummaryRow>::new());

    selected.par_iter().for_each(|(idx, scenario)| {
        let path = cli.out_dir.join(format!(
            "monte_carlo_{}_{}.csv",
            scenario.key, cli.tag
        ));
        let summary = run_scenario(
            scenario,
            cli.n_sims,
            cli.oracle_lag_ms,
            cli.seed,
            *idx as u64,
            &path,
        );
        println!(
            "  [{:>22}] n_sims={} trigger_rate={:.3}% mean_loss={:.2} elapsed={}ms",
            scenario.key,
            cli.n_sims,
            summary.attack_rate_pct,
            summary.mean_loss,
            summary.elapsed_ms
        );
        summary_rows.lock().unwrap().push(summary);
    });

    let mut summary_rows = summary_rows.into_inner().unwrap();
    summary_rows.sort_by_key(|r| {
        SCENARIOS
            .iter()
            .position(|s| s.key == r.scenario)
            .unwrap_or(usize::MAX)
    });

    let summary_path = cli.out_dir.join(format!("monte_carlo_summary_{}.csv", cli.tag));
    let mut summary_writer = csv::Writer::from_writer(File::create(&summary_path).expect("create summary"));
    for row in &summary_rows {
        summary_writer.serialize(row).expect("write summary row");
    }
    summary_writer.flush().expect("flush summary");

    println!(
        "Total Rust wall-clock: {} ms (parallel across {} scenarios)",
        global_start.elapsed().as_millis(),
        selected.len()
    );
    println!("Summary CSV: {}", summary_path.display());
}
