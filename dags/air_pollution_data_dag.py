from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import requests
import pandas as pd
import os

# Informations d'API
API_KEY = '4a35b382b8d0e669fc1f1de462ea1006'

# Liste des villes avec leurs coordonnées géographiques
cities = {
    'Los_Angeles': {'lat': 34.0522, 'lon': -118.2437},
    'Paris': {'lat': 48.8566, 'lon': 2.3522},
    'Tokyo': {'lat': 35.6895, 'lon': 139.6917},
    'Antananarivo': {'lat': -18.8792, 'lon': 47.5079},
    'Nairobi': {'lat': -1.286389, 'lon': 36.817223},
    'Lima': {'lat': -12.0464, 'lon': -77.0428}
}

# Nom du fichier CSV pour stocker les données
csv_file = '/home/safidy/airflow/data/air_pollution_data.csv'

def fetch_air_pollution_data(city, lat, lon, **kwargs):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        print(f"Données récupérées avec succès pour {city}")
    else:
        print(f"Erreur lors de la récupération des données pour {city}")
        return

    components = data['list'][0]['components']
    components['city'] = city
    components['timestamp'] = data['list'][0]['dt']
    df = pd.DataFrame([components])

    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_file, index=False)

    print(f"Données stockées dans {csv_file}")


# Définir le DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

dag = DAG(
    'air_pollution_data_dag',
    default_args=default_args,
    description='Un DAG pour collecter les données de pollution de l\'air',
    schedule_interval='@hourly',
)

# Définir les tâches
tasks = []
for city, coords in cities.items():
    task = PythonOperator(
        task_id=f'fetch_air_pollution_data_{city}',
        python_callable=fetch_air_pollution_data,
        op_kwargs={'city': city, 'lat': coords['lat'], 'lon': coords['lon']},
        dag=dag,
    )
    tasks.append(task)

# Définir l'ordre des tâches
for i in range(len(tasks) - 1):
    tasks[i] >> tasks[i + 1]

