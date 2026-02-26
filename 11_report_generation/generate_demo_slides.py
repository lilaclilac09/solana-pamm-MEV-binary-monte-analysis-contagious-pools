#!/usr/bin/env python3
"""Generate a 12-slide PDF demo deck for the Solana PAMM MEV analysis."""
from pathlib import Path
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch

OUTPUT_DIR = Path("11_report_generation/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PDF = OUTPUT_DIR / "Solana_PAMM_MEV_Demo_Slides.pdf"

PLOTS = {
    "mev_distribution": OUTPUT_DIR / "mev_distribution_comprehensive.png",
    "top_attackers": OUTPUT_DIR / "top_attackers.png",
    "agg_vs_mev": OUTPUT_DIR / "aggregator_vs_mev_detailed_comparison.png",
    "filtered_vs_unfiltered": OUTPUT_DIR / "filtered_vs_unfiltered_impact.png",
    "contagion_dashboard": OUTPUT_DIR / "contagion_analysis_dashboard.png",
    "pool_network": OUTPUT_DIR / "pool_coordination_network.png",
    "oracle_update_rates": OUTPUT_DIR / "oracle_update_rates_by_pool.png",
    "oracle_burst_density": OUTPUT_DIR / "oracle_burst_density_by_pool.png",
}

SLIDE_W, SLIDE_H = landscape(letter)
MARGIN = 0.6 * inch
TITLE_Y = SLIDE_H - 0.7 * inch


def draw_title(c, title, subtitle=None):
    c.setFont("Helvetica-Bold", 28)
    c.drawString(MARGIN, TITLE_Y, title)
    if subtitle:
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.grey)
        c.drawString(MARGIN, TITLE_Y - 0.35 * inch, subtitle)
        c.setFillColor(colors.black)


def draw_bullets(c, bullets, x, y, font_size=16, leading=22):
    c.setFont("Helvetica", font_size)
    text = c.beginText(x, y)
    text.setLeading(leading)
    for item in bullets:
        text.textLine(f"- {item}")
    c.drawText(text)


def draw_image(c, image_path, x, y, w, h):
    if image_path.exists():
        c.drawImage(str(image_path), x, y, width=w, height=h, preserveAspectRatio=True, mask='auto')
    else:
        c.setFont("Helvetica-Oblique", 12)
        c.setFillColor(colors.red)
        c.drawString(x, y + h - 12, f"Missing image: {image_path.name}")
        c.setFillColor(colors.black)


def slide_title(c):
    draw_title(c, "Solana PAMM MEV Demo", "Validated MEV + contagion analysis (Feb 26, 2026)")
    draw_bullets(
        c,
        [
            "617 validated fat sandwich attacks",
            "112.428 SOL total MEV profit",
            "Contagion analysis across 7 pools",
        ],
        MARGIN,
        TITLE_Y - 1.0 * inch,
        font_size=18,
        leading=26,
    )


def slide_agenda(c):
    draw_title(c, "Agenda")
    draw_bullets(
        c,
        [
            "Dataset and validation",
            "MEV patterns and detection",
            "Top attackers and protocol exposure",
            "Aggregator vs MEV separation",
            "Contagion findings",
            "Key takeaways",
        ],
        MARGIN,
        TITLE_Y - 0.7 * inch,
        font_size=18,
        leading=26,
    )


def slide_dataset(c):
    draw_title(c, "Dataset and Validation")
    draw_bullets(
        c,
        [
            "Source: Solana pAMM events across 8 protocols",
            "Initial detections: 1,501 MEV candidates",
            "Filtered to 617 validated fat sandwich attacks",
            "False positives removed: 58.9% (failed + multi-hop)",
            "Validation signal: net_profit_sol > 0 and sandwich_complete > 0",
            "Columns normalized: attacker_signer → signer, amm_trade → pool",
        ],
        MARGIN,
        TITLE_Y - 0.7 * inch,
        font_size=17,
        leading=24,
    )


def slide_key_stats(c):
    draw_title(c, "Key Stats")
    draw_bullets(
        c,
        [
            "Total MEV profit: 112.428 SOL",
            "Average profit per attack: 0.1822 SOL",
            "Unique attackers: 179",
            "Top pool (HumidiFi): 66.8% of total MEV",
            "Median profit: 0.0360 SOL (right-skewed distribution)",
            "Top 20 attackers capture ~49% of total profit",
        ],
        MARGIN,
        TITLE_Y - 0.7 * inch,
        font_size=18,
        leading=26,
    )


def slide_oracle_update_rates(c):
    draw_title(c, "Oracle Update Density")
    draw_image(c, PLOTS["oracle_update_rates"], MARGIN, 0.6 * inch, SLIDE_W - 2 * MARGIN, 4.8 * inch)
    draw_bullets(
        c,
        [
            "HumidiFi leads: ~55.9 updates/sec; 22.9 updates/slot",
            "Lower-rate pools show larger staleness windows",
            "MEV bots synchronize execution with oracle cadence",
        ],
        MARGIN,
        0.5 * inch,
        font_size=12,
        leading=16,
    )


def slide_oracle_burst_density(c):
    draw_title(c, "Oracle Burst Density")
    draw_image(c, PLOTS["oracle_burst_density"], MARGIN, 0.6 * inch, SLIDE_W - 2 * MARGIN, 4.8 * inch)
    draw_bullets(
        c,
        [
            "Burst windows capture rapid oracle update clusters",
            "High burst counts correlate with higher MEV exposure",
            "Burst spikes amplify timing gaps for sandwiches",
        ],
        MARGIN,
        0.5 * inch,
        font_size=12,
        leading=16,
    )


def slide_mev_distribution(c):
    draw_title(c, "MEV Distribution by Protocol")
    draw_image(c, PLOTS["mev_distribution"], MARGIN, 0.7 * inch, SLIDE_W - 2 * MARGIN, 4.5 * inch)
    draw_bullets(
        c,
        [
            "HumidiFi captures 66.8% of total MEV profit (75.1 SOL)",
            "BisonFi and SolFiV2 show moderate exposure (10.0% and 6.7%)",
            "Risk is protocol-specific: profit is not proportional to volume",
        ],
        MARGIN,
        0.55 * inch,
        font_size=12,
        leading=16,
    )


def slide_top_attackers(c):
    draw_title(c, "Top Attackers by Profit")
    draw_image(c, PLOTS["top_attackers"], MARGIN, 0.7 * inch, SLIDE_W - 2 * MARGIN, 4.5 * inch)
    draw_bullets(
        c,
        [
            "Top attacker profit corrected to 16.731 SOL",
            "Top 20 attackers capture ~49% of total MEV profit",
            "High concentration implies latency and routing advantages",
        ],
        MARGIN,
        0.55 * inch,
        font_size=12,
        leading=16,
    )


def slide_agg_vs_mev(c):
    draw_title(c, "Aggregator vs MEV Separation")
    draw_image(c, PLOTS["agg_vs_mev"], MARGIN, 0.6 * inch, SLIDE_W - 2 * MARGIN, 4.8 * inch)
    draw_bullets(
        c,
        [
            "Aggregators show high pool diversity and low MEV scores",
            "MEV bots cluster at low diversity and high MEV scores",
            "Separation validates filtering of aggregators and multi-hop",
            "Decision boundary isolates 97.9% of cases; 2.1% ambiguous",
            "Pool diversity and MEV score show inverse correlation (r≈-0.64)",
        ],
        MARGIN,
        0.5 * inch,
        font_size=12,
        leading=16,
    )


def slide_filtering(c):
    draw_title(c, "Data Correction and Filtering")
    draw_image(c, PLOTS["filtered_vs_unfiltered"], MARGIN, 0.7 * inch, SLIDE_W - 2 * MARGIN, 4.5 * inch)
    draw_bullets(
        c,
        [
            "1,501 detections reduced to 617 validated attacks",
            "Removed 865 failed sandwiches and 19 multi-hop cases",
            "Corrected rankings shift profit concentration upward",
            "Classification logic uses sandwich_complete, fat_sandwich, front/back flags",
            "All plots rebuilt from all_fat_sandwich_only.csv ground truth",
        ],
        MARGIN,
        0.55 * inch,
        font_size=12,
        leading=16,
    )


def slide_contagion_dashboard(c):
    draw_title(c, "Contagion Analysis Dashboard")
    draw_image(c, PLOTS["contagion_dashboard"], MARGIN, 0.6 * inch, SLIDE_W - 2 * MARGIN, 4.8 * inch)
    draw_bullets(
        c,
        [
            "Trigger pool: HumidiFi with highest MEV concentration",
            "Immediate cascade rate is 0% within 5,000 ms",
            "Delayed contagion: 20-22% attacker overlap across pools",
            "Downstream attack probabilities: BisonFi 22.4%, SolFiV2 21.8%, GoonFi 21.6%",
            "Risk classification: 100% MODERATE across 7 pools",
        ],
        MARGIN,
        0.5 * inch,
        font_size=12,
        leading=16,
    )


def slide_pool_network(c):
    draw_title(c, "Pool Coordination Network (Zoomed)")
    draw_image(c, PLOTS["pool_network"], MARGIN, 0.6 * inch, SLIDE_W - 2 * MARGIN, 4.8 * inch)
    draw_bullets(
        c,
        [
            "Heatmap shows shared attackers between pool pairs",
            "HumidiFi has the widest attacker overlap",
            "Cross-pool risk is driven by attacker migration, not same-slot cascades",
            "Shared attacker counts typically 20-50 across major pools",
            "ObricV2 and SolFi show minimal overlap (3-13 shared attackers)",
        ],
        MARGIN,
        0.5 * inch,
        font_size=12,
        leading=16,
    )


def slide_detection(c):
    draw_title(c, "MEV Pattern and Detection")
    draw_bullets(
        c,
        [
            "Fat sandwich definition: sandwich_complete > 0 AND fat_sandwich > 0",
            "Failed sandwich: net_profit_sol == 0 or null",
            "Multi-hop arbitrage: front_running/back_running without sandwich_complete",
            "Validated dataset includes only true fat sandwich attacks",
        ],
        MARGIN,
        TITLE_Y - 0.7 * inch,
        font_size=16,
        leading=24,
    )
    draw_bullets(
        c,
        [
            "Filtering removes benign routing and failed attempts",
            "Classification logic aligns with profit-positive sandwich patterns",
            "Validation rule prioritizes realized profit over pattern hints",
            "Columns standardized before aggregation to avoid drift",
        ],
        MARGIN,
        TITLE_Y - 3.0 * inch,
        font_size=14,
        leading=20,
    )


def slide_takeaways(c):
    draw_title(c, "Demo Takeaways")
    draw_bullets(
        c,
        [
            "MEV is highly concentrated: HumidiFi dominates profit and volume",
            "No immediate cascade, but 22% delayed contagion via attacker overlap",
            "Clear behavioral separation between aggregators and MEV bots",
            "Validated data materially changes rankings and conclusions",
        ],
        MARGIN,
        TITLE_Y - 0.7 * inch,
        font_size=18,
        leading=26,
    )


def main():
    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=landscape(letter))

    slides = [
        slide_title,
        slide_agenda,
        slide_dataset,
        slide_key_stats,
        slide_oracle_update_rates,
        slide_oracle_burst_density,
        slide_mev_distribution,
        slide_top_attackers,
        slide_agg_vs_mev,
        slide_filtering,
        slide_contagion_dashboard,
        slide_pool_network,
        slide_detection,
        slide_takeaways,
    ]

    for slide in slides:
        slide(c)
        c.showPage()

    c.save()
    print(f"Generated: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
