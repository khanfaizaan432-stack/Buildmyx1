import pandas as pd
import subprocess
import sys

# Check CSV file
df = pd.read_csv('players_processed_v7.csv')
print('CSV File Check:')
print('Shape:', df.shape)
print('Has quality_score:', 'quality_score' in df.columns)
print('Has quality_final:', 'quality_final' in df.columns)
print()

# Check streamlit
print('Streamlit Check:')
try:
    result = subprocess.run(['streamlit', '--version'], capture_output=True, text=True)
    print(result.stdout + result.stderr)
except Exception as e:
    print(f'Error: {e}')
