import pandas as pd

df = pd.read_csv('players_processed_v7.csv')
print('Shape:', df.shape)
print('\nFirst 5 columns:', df.columns[:5].tolist())
print('\nHas quality_score:', 'quality_score' in df.columns)
print('Has quality_final:', 'quality_final' in df.columns)
print('Has fit_gegenpress:', 'fit_gegenpress' in df.columns)
print('Has final_value:', 'final_value' in df.columns)
print('Has position:', 'position' in df.columns)
print('Has sub_position:', 'sub_position' in df.columns)
print('\nSample row:')
print(df[['Player', 'Squad', 'position', 'sub_position', 'quality_score', 'final_value']].iloc[0])
