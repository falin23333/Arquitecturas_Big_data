from flask import Flask, render_template, request, session, redirect, url_for
import re
import datetime
from config import dbname, password, port, user, host, REDIS_HOST,REDIS_PORT
import redis
import psycopg2
from zoneinfo import ZoneInfo
import json
import os
from tasks import get_tracked_urls_from_redis
"docker run -d --name redis-stack-5 -p 6379:6379 -p 8001:8001 redis/redis-stack:latest"
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))



redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)



app = Flask(__name__) # ejecuto una app, quiero que detectes en que ubicacion se encuentra
app.secret_key = "1234"
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
 
def insert_url_to_database(url: str, idd: list):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tracked_urls (url, id_user) VALUES (%s, %s)",(url, idd))
        conn.commit()
        
    except Exception as e:
        print(f"Error al insertar valor: {e}")
    finally:
        conn.close()


################# REDIS ################
def insert_url_to_redis(url: str,idd: int):
    try:
        data = {"id": idd, "url": url}
        print(data)
        redis_conn.rpush("url_queue", json.dumps(data))  #url_queue puede ser el que queramos
    except Exception as e:
        print("Error al insertar en REDIS:",e)
def get_name_from_redis(user):
    
    # Obtener todos los elementos de la lista
    data = [json.loads(x) for x in redis_conn.lrange("url_queue", 0, -1)]

    # Filtrar por valor de "element"
    result = [d for d in data if d["element"] == user]

    print(result)


def get_tracke_url_from_redis():
    pipe = redis_conn.pipeline()
    pipe.lrange("url_queue", 0, -1)  # solo agregamos al pipeline
    urls_tracked_from_redis = pipe.execute()
    url_items = urls_tracked_from_redis[0] or []

    tracked_data = []
    for item in url_items:
        try:
            data = json.loads(item)  # ✅ ya es string, no decode()
            tracked_data.append((data["id"], data["url"]))
        except Exception as e:
            print(f"Error al procesar item: {item} -> {e}")
    return tracked_data
#################################



def insert_name_to_database(name: str):
    try:
        ahora = datetime.datetime.now(ZoneInfo("Europe/Madrid"))
        ahora = ahora.strftime("%Y-%m-%d %H:%M:%S")
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (usuario, fecha_Reg) VALUES (%s, %s)",(name, ahora))
        conn.commit()
        
    except Exception as e:
        print(f"Error al insertar valor: {e}")
    finally:
        conn.close()

def find_name_to_database(name: str):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE usuario = %s", (name,))
        result = cursor.fetchone()
        return result
        
    except Exception as e:
        print(f"NO EXISTE EL USUARIO {e}")
    finally:
        conn.close()
def find_urls_from_user_to_database(id_user: int):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tracked_urls WHERE id_user = %s", (id_user,))
        result = cursor.fetchall()
        return result
        
    except Exception as e:
        print(f"NO EXISTE EL USUARIO {e}")
    finally:
        conn.close()
def top_users_post():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""SELECT u.usuario, COUNT(t.id_user) AS total_urls
                        FROM users u
                        LEFT JOIN tracked_urls t ON u.id = t.id_user
                        GROUP BY u.usuario
                        ORDER BY total_urls DESC""")
        result = cursor.fetchall()
        return result
        
    except Exception as e:
        print(f"NO EXISTE EL USUARIO {e}")
    finally:
        conn.close()
def top_urls():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""SELECT url, COUNT(*) AS total_veces FROM 
                        tracked_urls GROUP BY url ORDER BY total_veces DESC;""")
        result = cursor.fetchall()
        return result
        
    except Exception as e:
        print(f"NO EXISTE EL USUARIO {e}")
    finally:
        conn.close()
def is_valid_url(url: str) -> bool:
    pattern = r"^(https?:\/\/)?(www\.)?[a-zA-Z0-9]+\.[a-zA-Z]+$"
    return bool(re.fullmatch(pattern, url))  # Comprueba si la URL cumple el patrón

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nombre = request.form.get('url_input')
        idd = find_name_to_database(nombre)
        
        if not idd:
            print("home", top_users,tracked_urls_user, top_urlss)
            insert_name_to_database(nombre)
            
            idd = find_name_to_database(nombre)
            
            tracked_urls_user = find_urls_from_user_to_database(idd[0])
            session["idd"] = idd
            top_users = top_users_post()
            
            top_urlss = top_urls()
            return render_template('contenido.html',nombre=nombre, idd=idd,tracked_urls_user=tracked_urls_user,top_users=top_users,top_urlss=top_urlss)
        else:
            
            tracked_urls_user = find_urls_from_user_to_database(idd[0])
            
            session["idd"] = idd
            top_users = top_users_post()
            
            top_urlss = top_urls()
            print("home_else", top_users,tracked_urls_user, top_urlss)
            return render_template('contenido.html',nombre=nombre,idd=idd,tracked_urls_user=tracked_urls_user,top_users=top_users,top_urlss=top_urlss)
        
    else:
        return render_template('index.html')

@app.route("/display_url/<path:url>", methods=['GET', 'POST'])
def display_url(url=None):
    if url:
        if request.method == 'POST':
            url2 = request.form.get('urlinput')
            if is_valid_url(url2):
                # Process the form data here (if needed)
                return redirect(url_for('display_url', url=url2))
            else:
                return "Error: Url Incorrecta"
        else:
            return render_template('index.html', url=url)
    else:
        return redirect(url_for('home'))


@app.route("/contenido",methods=["GET","POST"])
def contenido():
    idd = session.get("idd") #recupero la variable nombre idd[0]=id, idd[1]=nombre
    tracked_urls_user = []
    if idd:
        if request.method=="POST":
            url = request.form.get("urlinput")
            
            if url and is_valid_url(url):
                insert_url_to_redis(url,idd[0])
            else:
                return "Urls no valida"
        top_users,tracked_urls_user, top_urlss = [],[],[]
        tracked_data=get_tracke_url_from_redis()
        #top_users = top_users_post()
        #tracked_urls_user = find_urls_from_user_to_database(idd[0])   
        #top_urlss = top_urls()
        
    return render_template("contenido.html",tracked_data = tracked_data,tracked_urls_user=tracked_urls_user, idd= idd,top_users=top_users,top_urlss=top_urlss)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)