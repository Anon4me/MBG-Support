import pandas as pd
from loguru import logger


def load_csv(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        if df.empty:
            raise ValueError("CSV kosong")

        df.columns = df.columns.str.strip()
        logger.info(f"Loaded {path} ({len(df)} rows)")
        return df
    except Exception as e:
        logger.exception(f"Gagal load CSV: {path}")
        raise RuntimeError(e)


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


def normalize_gram(gram):
    try:
        gram = float(gram)
    except Exception:
        raise ValueError("Gram harus angka")

    if gram <= 0:
        raise ValueError("Gram harus > 0")

    return gram


def calculate_nutrition(food_id, gram, clean_df, category_df):
    """
    Default: gram = 100
    Custom gram allowed
    """
    gram = normalize_gram(gram)

    row = clean_df[clean_df["Id"] == food_id]
    if row.empty:
        raise ValueError(f"Food ID tidak ditemukan: {food_id}")

    cat = category_df[category_df["Id"] == food_id]
    is_animal = _to_bool(cat.iloc[0]["is_animal"]) if not cat.empty else False

    factor = gram / 100.0

    protein = _to_number(row.iloc[0]["Protein (g)"]) * factor
    fat = _to_number(row.iloc[0]["Lemak (g)"]) * factor
    carb = _to_number(row.iloc[0]["Karbohidrat (g)"]) * factor
    fiber = _to_number(row.iloc[0]["Serat (g)"]) * factor

    energy = (
        carb * 4 +
        protein * 4 +
        fat * 9 +
        fiber * 2
    )

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


def evaluate_mbg(total, std):
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
    clean_df = load_csv("clean_data.csv")
    category_df = load_csv("food_category.csv")
    std_df = load_csv("standar_mbg.csv")

    foods = [
        calculate_nutrition(food_id=1, gram=100, clean_df=clean_df, category_df=category_df),
        calculate_nutrition(food_id=2, gram=75, clean_df=clean_df, category_df=category_df),
        calculate_nutrition(food_id=3, gram=120, clean_df=clean_df, category_df=category_df),
    ]

    total = aggregate(foods)

    std = get_standard("SD_7_9_M", std_df)
    result = evaluate_mbg(total, std)

    print("TOTAL NUTRISI:", total)
    print("EVALUASI MBG:", result)
