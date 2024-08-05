from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import pandas as pd

def clean_data():
    try:
        df = pd.read_csv('/home/safidy/airflow/data/air_pollution_data.csv', error_bad_lines=False)
        # Vérifier les colonnes disponibles
        print("Colonnes dans air_pollution_data.csv :", df.columns)

        # Nettoyer les données
        df = df.dropna()
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.to_csv('/home/safidy/airflow/data/cleaned_data.csv', index=False)
        print("Données nettoyées et stockées dans cleaned_data.csv")
    except Exception as e:
        print(f"Erreur lors du nettoyage des données : {e}")


def merge_data(**kwargs):
    try:
        air_pollution_df = pd.read_csv('/home/safidy/airflow/data/cleaned_data.csv')
        demographic_df = pd.read_csv('/home/safidy/airflow/data/Demographic_Data.csv')
        geographic_df = pd.read_csv('/home/safidy/airflow/data/Geographic_Data.csv')

        # Vérifiez les colonnes disponibles dans chaque DataFrame
        print("Colonnes dans air_pollution_df:", air_pollution_df.columns)
        print("Colonnes dans demographic_df:", demographic_df.columns)
        print("Colonnes dans geographic_df:", geographic_df.columns)

        # Fusionner les données
        merged_df = pd.merge(air_pollution_df, demographic_df, left_on='city', right_on='Location', how='left')
        merged_df = pd.merge(merged_df, geographic_df, left_on='city', right_on='Location', how='left')

        merged_df.to_csv('/home/safidy/airflow/data/merged_data.csv', index=False)
        print("Données fusionnées et stockées avec succès dans merged_data.csv")
    except Exception as e:
        print(f"Erreur lors de la fusion des données : {e}")

def aggregate_data(**kwargs):
    df = pd.read_csv('/home/safidy/airflow/data/merged_data.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    daily_aggregated_df = df.groupby(df['timestamp'].dt.date).agg({
        'PM2.5': 'mean',
        'PM10': 'mean',
        'O3': 'mean',
        'NO2': 'mean',
        'SO2': 'mean',
        'CO': 'mean',
        'Population': 'mean',
        'Density (people/km²)': 'mean',
        'Urbanization (%)': 'mean',
        'Average Income (USD)': 'mean',
        'Education Level (% with Bachelor\'s or higher)': 'mean',
        'Altitude (m)': 'mean',
        'Proximity to Industry (km)': 'mean'
    }).reset_index()
    daily_aggregated_df.to_csv('/home/safidy/airflow/data/daily_aggregated_data.csv', index=False)
    print("Données agrégées et stockées dans daily_aggregated_data.csv")

# Définir le DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

dag = DAG(
    'process_air_pollution_data_dag',
    default_args=default_args,
    description='Un DAG pour nettoyer, fusionner et agréger les données de pollution de l\'air',
    schedule_interval='@daily',
)

# Définir les tâches
clean_task = PythonOperator(
    task_id='clean_data',
    python_callable=clean_data,
    dag=dag,
)

merge_task = PythonOperator(
    task_id='merge_data',
    python_callable=merge_data,
    dag=dag,
)

aggregate_task = PythonOperator(
    task_id='aggregate_data',
    python_callable=aggregate_data,
    dag=dag,
)

# Définir les dépendances entre les tâches
clean_task >> merge_task >> aggregate_task
