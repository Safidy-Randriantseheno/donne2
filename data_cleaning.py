import pandas as pd

air_pollution_df = pd.read_csv('/path/to/your/air_pollution_data.csv')

# Nettoyage des données
air_pollution_df = air_pollution_df.dropna()
air_pollution_df['timestamp'] = pd.to_datetime(air_pollution_df['timestamp'], unit='s')

# Vérifier les types de données
print(air_pollution_df.dtypes)

# Supprimer les valeurs aberrantes si nécessaire (exemple : vérifier les valeurs extrêmes)
print(air_pollution_df.describe())
