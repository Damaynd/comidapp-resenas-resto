# ComidApp

## Descripción
Esta es una aplicación web desarrollada en Django que permite a los usuarios
descubrir y valorar restaurantes según sus necesidades específicas y preferencias.
Los restaurantes pueden ser filtrados mediante **tags** y otras propiedades como:
- Restricción alimenticia
- Accesibilidad ante movilidad reducia
- Distancia
- Valoraciones, etc.

Los usuarios pueden subir valoraciones, fotos y comentarios de los restaurantes que
han visitado mediante un formulario que les permitirá realizar la recomendación.

## Características
- Registro y autenticación de usuarios.
- Gestión de tags específicos para restaurantes.
- Valoración y comentarios de usuarios.
- Subida de fotos.
- Filtrado de restaurantes según necesidades y preferencias.

## Estructura del proyecto

Este corresponde solo a la estructura actual, más no la final.
```bash
DCC-CC4401/2025-2-CC4401-grupo-6/
|
├── manage.py
├── mi_espacio/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
|
├── restaurants/                    
│   ├── migrations/
│   │   └── __init__.py
|   ├── static/styles
│   ├── templates
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
|
├── db.sqlite3
├── requirements.txt                 
├── .gitignore
└── README.md
```

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/DCC-CC4401/2025-2-CC4401-grupo-6.git
cd DCC-CC4401/2025-2-CC4401-grupo-6/
```
2. Crear y activar un entorno virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```
3. Instalar dependencias
```bash
pip install -r requirements.txt
```
4. Ejecutar migraciones
```bash
python manage.py migrate
```
5. Crear superusuario(opcional)
```bash
python manage.py createsuperuser
```
6. Iniciar servidor
```bash
python manage.py runserver
```
## Uso
- Acceder al panel de administración en `http://localhost:8000/admin` para añadir 
restaurantes y tags.
- Los usuarios pueden registrarse, filtrar restaurantes por tags, dejar valoraciones
y subir fotos.

## Tecnologías
- Python 3.x
- Django 4.x
- SQLite (por defecto)
- HTML, CSS, JS
  
