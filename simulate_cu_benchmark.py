#!/usr/bin/env python3
"""
Generate synthetic CU (Compute Unit) benchmark data for Prop AMM operations.

This script creates realistic CU distributions for all 14 operations, simulating
production behavior without needing live transactions.

Perfect for:
- Testing the CU Percentile Heatmap before mainnet deployment
- Comparing different optimization strategies
- Understanding CU patterns by operation type

Usage:
  python simulate_cu_benchmark.py --samples 500 --output outputs/cu_benchmark_logs.csv
"""

import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class OperationProfile:
    """Defines CU cost profile for an operation"""
    name: str
    base_cu: float
    variance: float  # Coefficient of variation (0.1 = 10% variance)
    spike_probability: float  # Probability of p99 spike
    spike_multiplier: float  # How much higher spike is
    
    def generate_samples(self, count: int = 100) -> np.ndarray:
        """Generate realistic CU samples matching this profile"""
        # Base distribution: Normal + occasional spikes
        normal_samples = np.random.normal(
            loc=self.base_cu,
            scale=self.base_cu * self.variance,
            size=count
        )
        
        # Add spikes (extreme outliers that still happen in prod)
        spike_indices = np.random.random(count) < self.spike_probability
        normal_samples[spike_indices] *= self.spike_multiplier
        
        # Ensure non-negative
        normal_samples = np.maximum(normal_samples, self.base_cu * 0.5)
        
        return normal_samples


class CUBenchmarkSimulator:
    """Generate realistic CU benchmarks for Prop AMM operations"""
    
    # Realistic CU profiles based on typical AMM implementations
    # (Numbers based on Solana program analysis + Feb 2026 validator specs)
    OPERATION_PROFILES: Dict[str, OperationProfile] = {
        # Update operations (cheap!)
        'BlindUpdate / blindupdate': OperationProfile(
            name='BlindUpdate / blindupdate',
            base_cu=45.0,
            variance=0.15,
            spike_probability=0.02,
            spike_multiplier=2.5
        ),
        'FastUpdate / all': OperationProfile(
            name='FastUpdate / all',
            base_cu=120.0,
            variance=0.20,
            spike_probability=0.03,
            spike_multiplier=2.0
        ),
        'FullUpdate / oracle-only': OperationProfile(
            name='FullUpdate / oracle-only',
            base_cu=420.0,
            variance=0.25,
            spike_probability=0.04,
            spike_multiplier=1.8
        ),
        'FullUpdate / bid-all': OperationProfile(
            name='FullUpdate / bid-all',
            base_cu=1850.0,
            variance=0.30,
            spike_probability=0.05,
            spike_multiplier=1.7
        ),
        'FullUpdate / ask-all': OperationProfile(
            name='FullUpdate / ask-all',
            base_cu=1920.0,
            variance=0.28,
            spike_probability=0.05,
            spike_multiplier=1.7
        ),
        'FullUpdate / both-all': OperationProfile(
            name='FullUpdate / both-all',
            base_cu=3350.0,
            variance=0.32,
            spike_probability=0.06,
            spike_multiplier=1.6
        ),
        
        # Swap operations (more expensive)
        'Swap Sell / Curve A': OperationProfile(
            name='Swap Sell / Curve A',
            base_cu=12400.0,
            variance=0.22,
            spike_probability=0.04,
            spike_multiplier=1.9
        ),
        'Swap Sell / Curve B': OperationProfile(
            name='Swap Sell / Curve B',
            base_cu=16800.0,
            variance=0.25,
            spike_probability=0.05,
            spike_multiplier=1.85
        ),
        'Swap Sell / Curve C': OperationProfile(
            name='Swap Sell / Curve C',
            base_cu=28500.0,
            variance=0.28,
            spike_probability=0.06,
            spike_multiplier=1.8
        ),
        'Swap Sell / mixed': OperationProfile(
            name='Swap Sell / mixed',
            base_cu=32600.0,
            variance=0.32,
            spike_probability=0.08,
            spike_multiplier=2.0
        ),
        'Swap Buy / Curve A': OperationProfile(
            name='Swap Buy / Curve A',
            base_cu=13200.0,
            variance=0.21,
            spike_probability=0.04,
            spike_multiplier=1.9
        ),
        'Swap Buy / Curve B': OperationProfile(
            name='Swap Buy / Curve B',
            base_cu=17600.0,
            variance=0.26,
            spike_probability=0.05,
            spike_multiplier=1.85
        ),
        'Swap Buy / Curve C': OperationProfile(
            name='Swap Buy / Curve C',
            base_cu=29800.0,
            variance=0.29,
            spike_probability=0.07,
            spike_multiplier=1.8
        ),
        'Swap Buy / mixed': OperationProfile(
            name='Swap Buy / mixed',
            base_cu=34200.0,
            variance=0.33,
            spike_probability=0.08,
            spike_multiplier=2.1
        ),
    }
    
    def __init__(self, seed: int = 42):
        """Initialize simulator with optional seed for reproducibility"""
        np.random.seed(seed)
    
    def generate_benchmark_data(
        self,
        samples_per_operation: int = 500,
        include_volatility_scenarios: bool = True
    ) -> List[Dict]:
        """
        Generate complete benchmark dataset.
        
        Args:
            samples_per_operation: Number of CU samples per operation
            include_volatility_scenarios: Add "high volatility" variant runs
        
        Returns:
            List of benchmark records
        """
        records = []
        
        # Base generation for each operation
        for operation_name, profile in self.OPERATION_PROFILES.items():
            cu_samples = profile.generate_samples(count=samples_per_operation)
            
            # Create records
            for i, cu in enumerate(cu_samples):
                # Simulate realistic timestamp spread
                slot = np.random.randint(100_000_000, 300_000_000)
                timestamp = (
                    datetime.now() - timedelta(days=np.random.randint(0, 30))
                ).isoformat()
                tx_hash = f"sim_{operation_name.replace(' ', '_').replace('/', '_')}_{i:06d}"
                
                record = {
                    'operation': operation_name,
                    'cu': int(np.round(cu)),
                    'timestamp': timestamp,
                    'slot': slot,
                    'tx_hash': tx_hash,
                    'base_cu': int(profile.base_cu),
                    'remaining_cu': None  # Would be filled from real tx
                }
                records.append(record)
        
        # Optional: Add volatility scenario (higher CU during network congestion)
        if include_volatility_scenarios:
            print("📈 Adding volatility scenario data...")
            volatility_records = []
            
            for operation_name, profile in self.OPERATION_PROFILES.items():
                # During volatility: higher variance + spike probability
                high_variance_profile = OperationProfile(
                    name=profile.name,
                    base_cu=profile.base_cu * 1.15,  # 15% higher baseline
                    variance=profile.variance * 1.5,  # 1.5x higher variance
                    spike_probability=profile.spike_probability * 2,  # 2x spike rate
                    spike_multiplier=profile.spike_multiplier * 1.1  # 10% higher spikes
                )
                
                cu_samples = high_variance_profile.generate_samples(count=100)
                
                for i, cu in enumerate(cu_samples):
                    slot = np.random.randint(100_000_000, 300_000_000)
                    timestamp = (
                        datetime.now() - timedelta(days=np.random.randint(0, 10))
                    ).isoformat()
                    tx_hash = f"sim_volatile_{operation_name.replace(' ', '_').replace('/', '_')}_{i:06d}"
                    
                    record = {
                        'operation': operation_name,
                        'cu': int(np.round(cu)),
                        'timestamp': timestamp,
                        'slot': slot,
                        'tx_hash': tx_hash,
                        'base_cu': int(profile.base_cu),
                        'remaining_cu': None
                    }
                    volatility_records.append(record)
            
            records.extend(volatility_records)
        
        return records
    
    def compute_percentiles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute percentile summary for each operation"""
        percentiles = [0, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0]
        
        summary = df.groupby('operation')['cu'].quantile(percentiles).unstack()
        summary.columns = ['min', 'p25', 'p50', 'p75', 'p90', 'p95', 'p99', 'max']
        
        return summary
    
    def generate_and_save(
        self,
        output_path: str = 'outputs/cu_benchmark_logs.csv',
        samples_per_operation: int = 500,
        verbose: bool = True
    ) -> Tuple[str, pd.DataFrame]:
        """
        Generate benchmark data and save to CSV.
        
        Returns:
            (output_path, dataframe)
        """
        if verbose:
            print("🔄 Generating synthetic CU benchmark data...")
            print(f"   Operations: {len(self.OPERATION_PROFILES)}")
            print(f"   Samples per operation: {samples_per_operation}")
        
        # Generate records
        records = self.generate_benchmark_data(
            samples_per_operation=samples_per_operation,
            include_volatility_scenarios=True
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        
        if verbose:
            print(f"✅ Saved {len(df)} records to {output_path}")
        
        # Print statistics
        if verbose:
            print("\n📊 Percentile Summary (from generated data):")
            summary = self.compute_percentiles(df)
            print(summary.round(0).to_string())
            
            print("\n⚠️  Operations with p99 > 30k CU (danger zone):")
            dangerous = summary[summary['p99'] > 30000]
            if len(dangerous) > 0:
                print(dangerous[['p99', 'max']].round(0).to_string())
            else:
                print("   None (good!)")
            
            print("\n✓ Operations in safe zone (p99 < 20k CU):")
            safe = summary[summary['p99'] < 20000]
            print(f"   {len(safe)}/{len(summary)} operations safe")
        
        return output_path, df


def main():
    parser = argparse.ArgumentParser(
        description='Generate synthetic CU benchmark data for Prop AMM'
    )
    parser.add_argument(
        '--samples',
        type=int,
        default=500,
        help='Samples per operation (default: 500)'
    )
    parser.add_argument(
        '--output',
        default='outputs/cu_benchmark_logs.csv',
        help='Output CSV path'
    )
    parser.add_argument(
        '--no-volatility',
        action='store_true',
        help='Skip volatility scenario generation'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility'
    )
    
    args = parser.parse_args()
    
    # Run simulation
    simulator = CUBenchmarkSimulator(seed=args.seed)
    output_path, df = simulator.generate_and_save(
        output_path=args.output,
        samples_per_operation=args.samples,
        verbose=True
    )
    
    print(f"\n🚀 Ready! Next steps:")
    print(f"   1. Open CU_PERCENTILE_HEATMAP.ipynb")
    print(f"   2. Point to: {output_path}")
    print(f"   3. Run all cells to generate heatmap")
    print(f"\n💡 Tip: Replace this simulated data with real mainnet CU data for your submission!")


if __name__ == '__main__':
    main()
