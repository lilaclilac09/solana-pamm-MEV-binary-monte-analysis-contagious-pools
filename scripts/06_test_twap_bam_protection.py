import numpy as np
import pandas as pd

def simulate_with_twap_bam(n_sims=10000, base_cascade=0.801, twap_reduction=0.85, bam_reduction=0.65):
    results = []
    for _ in range(n_sims):
        effective = base_cascade * (1 - twap_reduction) * (1 - bam_reduction)
        cascades = np.random.binomial(5, effective)  # max 5 jumps per slot
        results.append(cascades)
    
    df = pd.DataFrame({'cascades': results})
    print(df.describe())
    print(f"Expected cascades with TWAP+BAM: {df['cascades'].mean():.3f} (was {base_cascade*5:.1f} without)")
    df.to_csv('outputs/twap_bam_simulation.csv', index=False)

simulate_with_twap_bam()
