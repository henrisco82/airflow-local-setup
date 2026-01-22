"""
Example DAG for Airflow 3.x
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    'example_dag',
    default_args=default_args,
    description='A simple example DAG',
    schedule=timedelta(days=1),  # Changed from schedule_interval
    catchup=False,
    tags=['example'],
)

# Define tasks
task1 = BashOperator(
    task_id='print_hello',
    bash_command='echo "Hello from Airflow 3.x!"',
    dag=dag,
)

task2 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag,
)

# Set task dependencies
task1 >> task2
