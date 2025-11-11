#  Flask + Celery + Redis + Supabase

Aplicación Flask conectada a Redis y Supabase, utilizando Celery para procesamiento asíncrono de tareas.

##  Descripción
Este proyecto implementa una arquitectura de procesamiento asíncrono:

- **Flask**: Servidor web que recibe solicitudes HTTP.  
- **Celery**: Worker que procesa tareas en segundo plano de forma asíncrona.  
- **Redis**: Broker de mensajes y almacenamiento temporal de URLs.  
- **Supabase (PostgreSQL)**: Base de datos para persistir URLs procesadas.  

**Flujo de la aplicación:**

1. Flask recibe URLs desde un formulario web.  
2. Las inserta en Redis como cola de tareas.  
3. Celery consume los elementos de la cola y los inserta en Supabase.
##  Requisitos
- Tener instalado [Docker](https://www.docker.com/)
- Clonar este repositorio:
  ```bash
  git clone https://github.com/falin23333/Arquitecturas_Big_data.git
  cd tu_proyecto
  docker-compose up --build
## 🗂 Estructura del Proyecto

```text
my_celery_app/
    app/
        config.py
        tasks.py
        requirements.txt
    Dockerfile

my_flask_app/
    app/
        __pycache__/
        static/
        templates/
            contenido.html
            index.html
            welcome.html
        app.py
        config.py
        tasks.py
        requirements.txt
    Dockerfile

docker-compose.yml



  

