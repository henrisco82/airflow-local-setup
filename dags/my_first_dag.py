
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.standard.operators.python import PythonOperator

from datetime import datetime

DB_SCHEMA = "ws_mkt_dst"
GP_CONN_ID = "GP_CONN_ID"

def my_task():
    print("Hello from Airflow 3!")


def exec_sql(sql):
    pg_hook = PostgresHook(postgres_conn_id=f"{GP_CONN_ID}")
    pg_conn = pg_hook.get_conn()
    pg_cursor = pg_conn.cursor()

    start_time = datetime.now()

    pg_cursor.execute(sql)
    pg_conn.commit()

    time_elapsed = datetime.now() - start_time
    print("exec time: (hh:mm:ss.ms) {}".format(time_elapsed))

    # Closing connection to Greenplum
    pg_cursor.close()
    pg_conn.close()


def _copy_singlestore_to_gp():
    # copy singlestore to gp
    print("Copying forms data from Singlestore to Greenplum")
    sql = f"SELECT {DB_SCHEMA}.sp_b2b_generic_collect_configurator_data();"
    exec_sql(sql)



with DAG(
    dag_id="my_first_dag",
    start_date=datetime(2025, 12, 4),
    schedule="@daily",  # ✅ Use 'schedule' instead of 'schedule_interval'
    catchup=False
) as dag:

    task1 = PythonOperator(
        task_id="print_hello",
        python_callable=my_task
    )

    task2 = PythonOperator(
        task_id = "test",
        python_callable= _copy_singlestore_to_gp
    )


(
    task1
    >> task2
)
