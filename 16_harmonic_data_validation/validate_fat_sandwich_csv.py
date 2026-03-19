import pandas as pd
import os

# Path to the CSV file (update this as needed)
CSV_PATH = os.path.join(os.path.dirname(__file__), 'only_all_fat_sandwich.csv')

# Validation checks
REQUIRED_COLUMNS = [
    'tx_id', 'block', 'pool', 'attacker', 'victim', 'profit', 'timestamp'
]

def load_csv(path):
    try:
        df = pd.read_csv(path)
        print(f"Loaded {len(df)} rows from {path}")
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def validate_columns(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        print(f"Missing columns: {missing}")
    else:
        print("All required columns present.")
    return missing

def check_duplicates(df):
    dupes = df.duplicated(subset=['tx_id'])
    n_dupes = dupes.sum()
    if n_dupes:
        print(f"Found {n_dupes} duplicate tx_id entries.")
    else:
        print("No duplicate tx_id entries.")
    return n_dupes

def check_nulls(df):
    nulls = df.isnull().sum()
    print("Null values per column:")
    print(nulls)
    return nulls

def main():
    df = load_csv(CSV_PATH)
    if df is None:
        return
    results = {}
    missing = validate_columns(df)
    results['missing_columns'] = missing
    n_dupes = check_duplicates(df)
    results['duplicate_tx_id_count'] = n_dupes
    nulls = check_nulls(df)
    results['nulls_per_column'] = nulls.to_dict()
    # Add more checks as needed

    # Save results to CSV
    results_rows = []
    for key, value in results.items():
        if isinstance(value, dict):
            for subkey, subval in value.items():
                results_rows.append({'check': f'{key}:{subkey}', 'result': subval})
        elif isinstance(value, list):
            results_rows.append({'check': key, 'result': ', '.join(value)})
        else:
            results_rows.append({'check': key, 'result': value})
    results_df = pd.DataFrame(results_rows)
    results_path = os.path.join(os.path.dirname(__file__), 'fat_sandwich_validation_results.csv')
    results_df.to_csv(results_path, index=False)
    print(f"Validation results saved to {results_path}")

if __name__ == '__main__':
    main()
