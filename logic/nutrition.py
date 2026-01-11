import pandas as pd


def _to_number(val):
    if val is None:
        return float("nan")
    try:
        return float(str(val).strip())
    except Exception:
        return float("nan")


def _to_bool(val):
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "y")
    return False


def normalisasi_gram(gram):
    try:
        gram = float(gram)
    except Exception:
        raise ValueError("Gram harus angka")

    if gram <= 0:
        raise ValueError("Gram harus > 0")

    return gram


def perhitungan_nutrisi(food_id, gram, clean_df, category_df):
    """
    Menghitung nutrisi makanan berdasarkan gram.
    """
    gram = normalisasi_gram(gram)

    row = clean_df[clean_df["id"] == food_id]
    if row.empty:
        raise ValueError(f"Food ID tidak ditemukan: {food_id}")

    cat = category_df[category_df["id"] == food_id]
    is_animal = _to_bool(cat.iloc[0]["is_animal"]) if not cat.empty else False

    factor = gram / 100.0

    protein = _to_number(row.iloc[0]["protein_(g)"]) * factor
    fat = _to_number(row.iloc[0]["lemak_(g)"]) * factor
    carb = _to_number(row.iloc[0]["karbohidrat_(g)"]) * factor
    fiber = _to_number(row.iloc[0]["serat_(g)"]) * factor

    energy = carb * 4 + protein * 4 + fat * 9 + fiber * 2

    return {
        "energy": energy,
        "protein": protein,
        "fat": fat,
        "carbohydrate": carb,
        "fiber": fiber,
        "animal_protein": protein if is_animal else 0.0
    }


def aggregate(items):
    totals = {
        "energy": 0.0,
        "protein": 0.0,
        "fat": 0.0,
        "carbohydrate": 0.0,
        "fiber": 0.0,
        "animal_protein": 0.0
    }

    for item in items or []:
        for k in totals:
            totals[k] += float(item.get(k, 0.0))

    return totals


def evaluasi_mbg(total, std):
    return {
        "energy_status": (
            "LOW" if total["energy"] < std["min_energy_kcal"]
            else "HIGH" if total["energy"] > std["max_energy_kcal"]
            else "OK"
        ),
        "protein_ok": total["protein"] >= std["min_protein_g"],
        "animal_protein_ok": total["animal_protein"] >= std["min_animal_protein_g"],
        "fiber_ok": total["fiber"] >= std["min_fiber_g"],
        "carbohydrate_ok": total["carbohydrate"] >= std["min_carbohydrate_g"]
    }


def get_standard(group_id, std_df):
    row = std_df[std_df["group_id"] == group_id]
    if row.empty:
        raise ValueError("Standar MBG tidak ditemukan")
    return row.iloc[0]


if __name__ == "__main__":

    clean_df = pd.read_csv("data/clean_data.csv", delimiter=";", encoding="utf-8-sig")
    category_df = pd.read_csv("data/food_category.csv", delimiter=";", encoding="utf-8-sig")
    std_df = pd.read_csv("data/standar_mbg.csv", delimiter=";", encoding="utf-8-sig")

    clean_df.columns = [c.strip().strip('"').replace(" ", "_").lower() for c in clean_df.columns]
    category_df.columns = [c.strip().strip('"').replace(" ", "_").lower() for c in category_df.columns]

    foods = [
        perhitungan_nutrisi(food_id="1", gram=100, clean_df=clean_df, category_df=category_df),
        perhitungan_nutrisi(food_id="2", gram=75, clean_df=clean_df, category_df=category_df)
    ]

    total = aggregate(foods)
    std = std_df.iloc[0]  # contoh ambil baris pertama sebagai standar
    result = evaluasi_mbg(total, std)

    print("TOTAL NUTRISI:", total)
    print("EVALUASI MBG:", result)
