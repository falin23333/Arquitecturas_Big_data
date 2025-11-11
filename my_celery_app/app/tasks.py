
from config import dbname, password, port, user, host, REDIS_HOST,REDIS_PORT
import redis
import psycopg2
from typing import List
from  celery import Celery
import json
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

app_Celery = Celery("tasks", broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def connect_to_database():
    try:
        # Conectarse a la base de datos PostgreSQL
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        print(e)



def insert_urls_to_database(data_list: List[tuple]):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO tracked_urls (id_user,url) VALUES (%s, %s)",data_list)
        conn.commit()
        print(f"✅ {len(data_list)} registros insertados correctamente.")
    except Exception as e:
        print(f"Error al insertar valor: {e}")
    finally:
        conn.close()

def get_tracked_urls_from_redis(count:int):
        pipe = redis_conn.pipeline()
        pipe.lrange("url_queue", 0, count - 1)
        pipe.ltrim("url_queue", count, -1)
        result = pipe.execute()

        # result[0] contiene la lista de elementos obtenidos
        url_items = result[0] or []

        tracked_data = []
        for item in url_items:
            try:
                data = json.loads(item)  # convierte el JSON en dict
                tracked_data.append((data["id"], data["url"]))  # guarda como tupla (id, url)
            except Exception as e:
                print(f"Error al procesar item: {item} -> {e}")

        return tracked_data


@app_Celery.task
def move_from_redis_to_postgres():
    urls = get_tracked_urls_from_redis(5)
    
    if len(urls)>0:
        insert_urls_to_database(urls)
        # Guardamos los últimos URLs en un JSON
       
app_Celery.conf.beat_schedule = {
    "cada-diez-segundos":{
        "task": "tasks.move_from_redis_to_postgres",
        "schedule":60.0,

    },
}

