import os, csv, unicodedata, re
from pathlib import Path

# Para correrlo como como script
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miespacio.settings")
import django
django.setup()

from django.conf import settings
from aplicacion.models import Restaurant, Dish

# estructura del path: data/photos/restaurant/<rest>/{dishes|places}/...
PHOTOS_ROOT = Path(settings.BASE_DIR) / "data" / "photos" / "restaurant"
OUT_CSV = Path(settings.BASE_DIR) / "data" / "fixtures" / "photos.csv"
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

def _norm(s: str) -> str:
    s = s.replace("_", " ").replace("-", " ").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))  # quita tildes
    s = re.sub(r"\s+", " ", s)
    return s

# Indexamos en memoria para búsquedas robustas y evitamos problemas de tildes/mayus
ALL_RESTS = list(Restaurant.objects.all())
REST_INDEX = {_norm(r.name): r for r in ALL_RESTS}

def match_restaurant(dirname: str):
    #  si calza directo
    r = Restaurant.objects.filter(name__iexact=dirname).first()
    if r: return r
    # normalizamos y buscamos en el índice en memoria
    return REST_INDEX.get(_norm(dirname)) \
        or REST_INDEX.get(_norm(dirname.replace("_", " "))) \
        or None

def match_dish(restaurant, fname_stem: str):
    cand = _norm(fname_stem)
    # Buscamos por ORM primero (rápido si calza)
    d = Dish.objects.filter(restaurant = restaurant, name__iexact = fname_stem.replace("_"," ")).first()
    if d: return d
    # Si no, normalizamos todos los platos del rest en memoria y matcheamos
    for dish in Dish.objects.filter(restaurant = restaurant).only("id","name"):
        if _norm(dish.name) == cand:
            return dish
    # contiene
    return Dish.objects.filter(restaurant = restaurant, name__icontains = fname_stem.replace("_"," ")).first()

def main():
    if not PHOTOS_ROOT.exists():
        print("No existe carpeta:", PHOTOS_ROOT)
        return

    rows, next_id = [], 1
    for rest_dir in PHOTOS_ROOT.iterdir():
        if not rest_dir.is_dir():
            continue
        rest = match_restaurant(rest_dir.name)
        if not rest:
            print("Alertiña: no se encontró Restaurant para carpeta:", rest_dir.name)
            continue

        for kind in ("dishes", "places"):
            kdir = rest_dir / kind
            if not kdir.exists():
                continue

            for root, _, files in os.walk(kdir):
                for fname in files:
                    ext = Path(fname).suffix.lower()
                    if ext not in EXTS:
                        continue

                    # path relativo que guardaremos (coherente con el árbol real)
                    rel = Path("data") / "photos" / "restaurant" / rest_dir.name / kind / fname

                    category = "dish" if kind == "dishes" else "other"
                    dish_id = ""
                    category_label = ""

                    if kind == "dishes":
                        stem = Path(fname).stem
                        dish = match_dish(rest, stem)
                        if dish:
                            dish_id = str(dish.id)
                        else:
                            print(f"Alertiña: no se encontró Dish en '{rest.name}' para archivo '{stem}'")
                    else:
                        category_label = Path(fname).stem

                    rows.append({
                        "id": str(next_id),
                        "uploaded_by_id": "",
                        "restaurant_id": str(rest.id),
                        "dish_id": dish_id,
                        "category": category,
                        "category_label": category_label,
                        "path": rel.as_posix(),
                        "taken_at": "",
                        "is_approved": "False",
                    })
                    next_id += 1

    OUT_CSV.parent.mkdir(parents = True, exist_ok = True)
    with open(OUT_CSV, "w", encoding = "utf-8", newline = "") as f:
        w = csv.DictWriter(f, fieldnames = [
            "id","uploaded_by_id","restaurant_id","dish_id",
            "category","category_label","path","taken_at","is_approved"
        ])
        w.writeheader()
        w.writerows(rows)

    print(f"Todo rekio: escrito {len(rows)} registros en {OUT_CSV}")

if __name__ == "__main__":
    main()
