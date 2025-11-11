# data/load_fixture.py
import csv
from pathlib import Path
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from aplicacion.models import (
    # catálogos
    Cuisine, Tag, DishType, DishTypeAlias,
    # core
    Restaurant, Dish,
    # relaciones
    RestaurantTag, DishTag,
    # opcionales
    Photo, Review,
)

# === dónde están tus CSV ===
BASE = Path(settings.BASE_DIR) / "data" / "fixtures"

# ---------- helpers ----------
def to_float(v, default=None):
    try: return float(v)
    except (ValueError, TypeError): return default

def to_int(v, default=None):
    try: return int(v)
    except (ValueError, TypeError): return default

def to_bool(v, default=None):
    if v is None: return default
    s = str(v).strip().lower()
    if s in ("true","1","t","yes","y","si","sí"): return True
    if s in ("false","0","f","no","n"): return False
    return default

def norm(v): return "" if v is None else str(v).strip()

def parse_date(s):
    s = norm(s)
    if not s: return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try: return datetime.strptime(s, fmt).date()
        except ValueError: pass
    return None

def csv_rows(path: Path):
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            yield {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}

def nf(name): print("Not found:", (BASE / name).resolve())

# ---------- loaders ----------
@transaction.atomic
def load_cuisines():
    name = "cuisines.csv"; path = BASE / name
    if not path.exists(): nf(name); return
    c, u = 0, 0
    for r in csv_rows(path):
        _, created = Cuisine.objects.update_or_create(
            id=to_int(r["id"]),
            defaults={"name": norm(r["name"])},
        )
        c += created; u += (0 if created else 1)
    print(f"Cuisines: created={c}, updated={u}, total={Cuisine.objects.count()}")

@transaction.atomic
def load_tags():
    name = "tags.csv"; path = BASE / name
    if not path.exists(): nf(name); return
    c, u = 0, 0
    for r in csv_rows(path):
        _, created = Tag.objects.update_or_create(
            id=to_int(r["id"]),
            defaults=dict(
                code=norm(r["code"]),
                name=norm(r["name"]),
                scope=norm(r.get("scope") or "both"),
                group=norm(r.get("group") or ""),
            ),
        )
        c += created; u += (0 if created else 1)
    print(f"Tags: created={c}, updated={u}, total={Tag.objects.count()}")

@transaction.atomic
def load_restaurants():
    name = "restaurants.csv"; path = BASE / name
    if not path.exists(): nf(name); return
    c, u = 0, 0
    for r in csv_rows(path):
        _, created = Restaurant.objects.update_or_create(
            id=to_int(r["id"]),
            defaults=dict(
                name=norm(r["name"]),
                address=norm(r["address"]),
                lat=to_float(r["lat"]),
                lon=to_float(r["lon"]),
                price=to_int(r["price"]),
                url=(norm(r["url"]) or None),
                avg_rating=(to_float(r.get("avg_rating"), 0.0) or 0.0),
                review_count=(to_int(r.get("review_count"), 0) or 0),
            ),
        )
        c += created; u += (0 if created else 1)
    print(f"Restaurants: created={c}, updated={u}, total={Restaurant.objects.count()}")

@transaction.atomic
def load_restaurant_cuisine():
    name = "restaurant_cuisines.csv"; path = BASE / name
    if not path.exists(): nf(name); return
    linked, miss = 0, 0
    for r in csv_rows(path):
        try:
            rest = Restaurant.objects.get(id=to_int(r["restaurant_id"]))
            cuis = Cuisine.objects.get(id=to_int(r["cuisine_id"]))
        except ObjectDoesNotExist:
            miss += 1; continue
        rest.cuisines.add(cuis)
        linked += 1
    print(f"Restaurant–Cuisine: linked={linked}, skipped_missing={miss}")

@transaction.atomic
def load_restaurant_tags():
    name = "restaurant_tags.csv"; path = BASE / name
    if not path.exists(): nf(name); return
    linked, miss = 0, 0
    for r in csv_rows(path):
        try:
            rest = Restaurant.objects.get(id=to_int(r["restaurant_id"]))
            tag = Tag.objects.get(id=to_int(r["tag_id"]))
        except ObjectDoesNotExist:
            miss += 1; continue
        RestaurantTag.objects.get_or_create(restaurant=rest, tag=tag)
        linked += 1
    print(f"Restaurant–Tag: linked={linked}, skipped_missing={miss}")

@transaction.atomic
def load_dish_types():
    name = "dish_types.csv"; path = BASE / name
    if not path.exists(): nf(name); return
    c, u = 0, 0
    for r in csv_rows(path):
        _, created = DishType.objects.update_or_create(
            id=to_int(r["id"]),
            defaults=dict(
                code=norm(r["code"]),
                name=norm(r["name"]),
                category=norm(r.get("category") or ""),
            ),
        )
        c += created; u += (0 if created else 1)
    print(f"DishTypes: created={c}, updated={u}, total={DishType.objects.count()}")

@transaction.atomic
def load_dish_type_alias():
    name = "dish_type_alias.csv"; path = BASE / name
    if not path.exists():
        print("DishTypeAlias: (optional) not found"); return
    c, miss = 0, 0
    for r in csv_rows(path):
        try:
            dt = DishType.objects.get(id=to_int(r["dish_type_id"]))
        except ObjectDoesNotExist:
            miss += 1; continue
        DishTypeAlias.objects.get_or_create(
            dish_type=dt,
            code=norm(r["code"]),
            defaults={"name": norm(r["name"])},
        )
        c += 1
    print(f"DishTypeAlias: created={c}, skipped_missing_fk={miss}")

@transaction.atomic
def load_dishes():
    name = "dishes.csv"; path = BASE / name
    if not path.exists(): nf(name); return
    c, u, miss = 0, 0, 0
    for r in csv_rows(path):
        try:
            rest = Restaurant.objects.get(id=to_int(r["restaurant_id"]))
        except ObjectDoesNotExist:
            miss += 1; continue

        dish_type = None
        dtid = to_int(r.get("dish_type_id"))
        if dtid:
            try: dish_type = DishType.objects.get(id=dtid)
            except ObjectDoesNotExist: pass

        _, created = Dish.objects.update_or_create(
            id=to_int(r["id"]),
            defaults=dict(
                restaurant=rest,
                dish_type=dish_type,
                name=norm(r["name"]),
                description=norm(r.get("description") or ""),
                price_ref=to_int(r.get("price_ref"), 0) or 0,
            ),
        )
        c += created; u += (0 if created else 1)
    print(f"Dishes: created={c}, updated={u}, skipped_missing_restaurant={miss}")

@transaction.atomic
def load_dish_tags():
    name = "dish_tags.csv"; path = BASE / name
    if not path.exists(): nf(name); return
    linked, miss = 0, 0
    for r in csv_rows(path):
        try:
            dish = Dish.objects.get(id=to_int(r["dish_id"]))
            tag = Tag.objects.get(id=to_int(r["tag_id"]))
        except ObjectDoesNotExist:
            miss += 1; continue
        DishTag.objects.update_or_create(
            dish=dish, tag=tag,
            defaults={"cross_contamination": bool(to_bool(r.get("cross_contamination"), True))}
        )
        linked += 1
    print(f"Dish–Tag: linked/updated={linked}, skipped_missing_fk={miss}")

# (opcionales) --------------------------------------------------
@transaction.atomic
def load_photos():
    name = "photos.csv"; path = BASE / name
    if not path.exists(): print("Photos: (optional) not found"); return
    from django.contrib.auth import get_user_model
    User = get_user_model()
    c, miss = 0, 0
    for r in csv_rows(path):
        try:
            rest = Restaurant.objects.get(id=to_int(r["restaurant_id"]))
        except ObjectDoesNotExist:
            miss += 1; continue
        dish = None
        did = to_int(r.get("dish_id"))
        if did:
            try: dish = Dish.objects.get(id=did)
            except ObjectDoesNotExist: pass
        user = None
        uid = to_int(r.get("uploaded_by_id"))
        if uid:
            try: user = User.objects.get(id=uid)
            except ObjectDoesNotExist: pass
        # created_at es auto_now_add: no se setea desde CSV
        Photo.objects.update_or_create(
            id=to_int(r["id"]),
            defaults=dict(
                uploaded_by=user,
                restaurant=rest,
                dish=dish,
                category=norm(r.get("category")),
                category_label=norm(r.get("category_label") or ""),
                path=norm(r.get("path")),
                taken_at=parse_date(r.get("taken_at")),
                is_approved=bool(to_bool(r.get("is_approved"), False)),
            ),
        )
        c += 1
    print(f"Photos: upserted={c}, skipped_missing_fk={miss}")

@transaction.atomic
def load_reviews():
    name = "reviews.csv"; path = BASE / name
    if not path.exists(): print("Reviews: (optional) not found"); return
    from django.contrib.auth import get_user_model
    User = get_user_model()
    c, miss = 0, 0
    for r in csv_rows(path):
        try:
            dish = Dish.objects.get(id=to_int(r["dish_id"]))
            user = User.objects.get(id=to_int(r["user_id"]))
        except ObjectDoesNotExist:
            miss += 1; continue
        Review.objects.update_or_create(
            id=to_int(r["id"]),
            defaults=dict(
                dish=dish,
                user=user,
                rating=to_float(r.get("rating"), 0.0) or 0.0,
                comment=norm(r.get("comment") or ""),
                price_paid=to_int(r.get("price_paid"), 0) or 0,
            ),
        )
        c += 1
    print(f"Reviews: upserted={c}, skipped_missing_fk={miss}")

# ---------- orquestador ----------
def main():
    print("Using fixtures from:", BASE.resolve())
    print("Found CSVs:", sorted(p.name for p in BASE.glob("*.csv")))

    # catálogos
    load_cuisines()
    load_tags()

    # core
    load_restaurants()
    load_restaurant_cuisine()
    load_restaurant_tags()

    # platos
    load_dish_types()
    load_dish_type_alias()  # opcional
    load_dishes()
    load_dish_tags()

    # opcionales
    load_photos()
    load_reviews()

    # resumen
    print("Summary:",
          "Cuisines", Cuisine.objects.count(),
          "| Tags", Tag.objects.count(),
          "| Restaurants", Restaurant.objects.count(),
          "| DishTypes", DishType.objects.count(),
          "| Dishes", Dish.objects.count(),
          "| R-Tags", RestaurantTag.objects.count(),
          "| D-Tags", DishTag.objects.count(),
          )

if __name__ == "__main__":
    main()
