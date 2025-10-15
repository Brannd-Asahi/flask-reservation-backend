# Hostal Tucán — Backend (Flask) — Demo

Repositorio de práctica para un backend sencillo de gestión de usuarios y reservas. Proyecto pensado para estudiantes: funcional, fácil de levantar y entendible.

> Estado: proyecto educativo — no para producción. Incluye ejemplos y un `demo.html` para probar la API desde el navegador.

-------------------------------------------------------------------------------------------------------------------------------------------------

## Archivos clave y qué hacen 
- `main.py` — API (endpoints: `/login`, `/usuarios`, `/reservas`, etc.).  
- `config.py` — lee `.env` y configura conexión MySQL y JWT.  
- `crear_usuario.py` — script interactivo para crear un usuario administrador.  
- `esquema.sql` — crea BD, tablas y perfiles iniciales.  
- `demo.html` — UI mínima para probar login, crear usuarios (admin), crear/listar/editar reservas (según rol).  
- `.env.example` — plantilla de variables de entorno (usa esto para crear `.env`).  
- `requirements.txt` — dependencias Python.

-------------------------------------------------------------------------------------------------------------------------------------------------

## Requisitos (local)
- Python 3.8+
- MySQL (o MariaDB) corriendo localmente
- Opcional: VSCode + Thunder Client (muy útil para probar endpoints)

-------------------------------------------------------------------------------------------------------------------------------------------------

## 1) Preparacion del entorno  

### 1.1 Clonar repo
``bash
git clone <tu-repo-url>
cd <tu-repo-folder>/backend


## 2) Crear entorno virtual e instalar dependencias 

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt


## 3) Crear archivo .env desde .env.example  

copy .env.example .env
notepad .env

## 4) Crear la base de datos y tablas 

mysql -u root -p < esquema.sql

## 5) Crear usuario administrador 

python crear_usuario.py

## 6) Ejecutar la API  

python main.py

## 7) Probar con ThunderClient/demo.html









