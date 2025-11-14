Estructura del path:

data/build_photos_csv.py
data/photos/restaurant/<name-restaurant>/<dishes|places>/<photo.ext>

Tienes que asegurarte que el directorio del repositorio obedezca eso, o modificar el archivo
.py para rutear correctamente.

Una vez que eso esté asegurado, correr los comandos:

python manage.py shell -c "import data.build_photos_csv as s; s.main()"
python manage.py shell -c "from data.load_fixture import load_photos; load_photos()"