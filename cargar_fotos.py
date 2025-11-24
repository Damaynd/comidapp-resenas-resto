import os
import django
from django.utils.text import slugify

# Configurar Django para usarlo en este script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miespacio.settings') # <--- OJO: Cambia 'miespacio' por el nombre real de tu carpeta de proyecto si es distinto
django.setup()

from aplicacion.models import Restaurant, Photo
from django.conf import settings

def arreglar_fotos():
    # Ruta base donde están las fotos según tu árbol: data/fixtures/photos/restaurant/
    # Como MEDIA_ROOT es 'data', buscamos dentro de eso.
    base_photos_path = os.path.join(settings.MEDIA_ROOT, 'photos', 'restaurant')

    print(f"Buscando fotos en: {base_photos_path}...")

    if not os.path.exists(base_photos_path):
        print("❌ Error: No encuentro la carpeta de fotos. Revisa la ruta.")
        return

    # Recorremos todos los restaurantes de la base de datos
    restaurantes = Restaurant.objects.all()
    
    count = 0
    for restaurante in restaurantes:
        # Intentamos adivinar el nombre de la carpeta (slug del nombre o nombre exacto)
        # Ejemplo: "Ambrosia Bistro" -> "ambrosia_bistro"
        folder_name = slugify(restaurante.name).replace('-', '_')
        
        # Ruta completa a la carpeta del restaurante
        restaurant_path = os.path.join(base_photos_path, folder_name)
        
        # A veces la estructura tiene subcarpetas como 'places' o 'dishes'
        # Buscamos recursivamente o en carpetas específicas
        rutas_a_explorar = [
            restaurant_path,
            os.path.join(restaurant_path, 'places'),
            os.path.join(restaurant_path, 'dishes')
        ]

        found_photos = []

        for ruta in rutas_a_explorar:
            if os.path.exists(ruta):
                for file in os.listdir(ruta):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        # Encontramos una imagen.
                        # La ruta que guardamos en BD debe ser relativa a MEDIA_ROOT (carpeta 'data')
                        # Ejemplo: fixtures/photos/restaurant/ambrosia_bistro/places/foto.jpg
                        full_path = os.path.join(ruta, file)
                        relative_path = os.path.relpath(full_path, settings.MEDIA_ROOT)
                        found_photos.append(relative_path)

        # Si encontramos fotos, creamos (o actualizamos) los objetos Photo
        if found_photos:
            print(f"✅ {restaurante.name}: Se encontraron {len(found_photos)} fotos.")
            
            # Opcional: Borrar las fotos "rotas" anteriores que tengan "image"
            Photo.objects.filter(restaurant=restaurante, image='image').delete()

            for path_img in found_photos:
                # Evitar duplicados: Solo crear si no existe
                if not Photo.objects.filter(restaurant=restaurante, image=path_img).exists():
                    Photo.objects.create(
                        restaurant=restaurante,
                        category=Photo.Category.OTHER, # O la categoría que prefieras
                        category_label="Foto cargada automáticamente",
                        image=path_img
                    )
                    count += 1
        else:
            print(f"⚠️ {restaurante.name}: No se encontraron fotos en {restaurant_path}")

    print(f"\n🎉 Proceso terminado. Se cargaron {count} fotos nuevas.")

if __name__ == '__main__':
    arreglar_fotos()