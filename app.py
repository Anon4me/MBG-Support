import streamlit as st
import pandas as pd
import uuid
from loguru import logger


def load_csv(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", engine="python")

        if df.empty:
            raise ValueError("CSV kosong")

        df.columns = [
            c.strip()
            .replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
            .lower()
            for c in df.columns
        ]

        logger.info(f"Loaded {path} ({len(df)} rows)")
        return df

    except Exception as e:
        logger.exception(f"Gagal load CSV: {path}")
        raise


def _to_number(val):
    try:
        return float(str(val).strip())
    except Exception:
        return 0.0


def _to_bool(val):
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "y")
    return False


def group_age(age: int, age_df: pd.DataFrame):
    row = age_df[
        (age_df["age_min"] <= age) &
        (age_df["age_max"] >= age)
    ]

    if row.empty:
        raise ValueError("Usia tidak valid")

    return (
        row.iloc[0]["education_level"],
        int(row.iloc[0]["grade"]),
        row.iloc[0]["default_gender"]
    )


def group_up(level: str, grade: int, edu_df: pd.DataFrame, gender: str = "all"):
    df = edu_df[
        (edu_df["level"] == level) &
        (edu_df["class_min"] <= grade) &
        (edu_df["class_max"] >= grade)
    ]

    if gender != "all":
        suffix = "_m" if gender == "male" else "_f"
        df = df[df["group_id"].str.lower().str.endswith(suffix)]

    if df.empty:
        raise ValueError("Group MBG tidak ditemukan")

    return df.iloc[0]["group_id"]


def get_standard(group_id: str, std_df: pd.DataFrame):
    row = std_df[std_df["group_id"] == group_id]

    if row.empty:
        raise ValueError("Standar MBG tidak ditemukan")

    return row.iloc[0]


def perhitungan_nutrisi(food_id, gram, tkpi_df, category_df):
    if gram <= 0:
        raise ValueError("Gram harus > 0")

    row = tkpi_df[tkpi_df["id"].astype(str) == str(food_id)]
    if row.empty:
        raise ValueError(f"Food ID tidak ditemukan: {food_id}")

    cat = category_df[category_df["id"].astype(str) == str(food_id)]
    is_animal = _to_bool(cat.iloc[0]["is_animal"]) if not cat.empty else False

    factor = gram / 100.0

    protein = _to_number(row.iloc[0]["protein_g"]) * factor
    fat = _to_number(row.iloc[0]["lemak_g"]) * factor
    carb = _to_number(row.iloc[0]["karbohidrat_g"]) * factor
    fiber = _to_number(row.iloc[0]["serat_g"]) * factor

    energy = (
        protein * 4 +
        carb * 4 +
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
    total = {
        "energy": 0.0,
        "protein": 0.0,
        "fat": 0.0,
        "carbohydrate": 0.0,
        "fiber": 0.0,
        "animal_protein": 0.0
    }

    for item in items:
        for k in total:
            total[k] += float(item.get(k, 0))

    return total


def evaluasi_mbg(total, std):
    return {
        "energy_status": (
            "LOW"
            if total["energy"] < std["min_energy_kcal"]
            else "HIGH"
            if total["energy"] > std["max_energy_kcal"]
            else "OK"
        ),
        "protein_ok": total["protein"] >= std["min_protein_g"],
        "animal_protein_ok": total["animal_protein"] >= std["min_animal_protein_g"],
        "fiber_ok": total["fiber"] >= std["min_fiber_g"],
        "carbohydrate_ok": total["carbohydrate"] >= std["min_carbohydrate_g"]
    }


st.set_page_config("MBG Menu Evaluator", layout="wide")

st.markdown("""
<style>
.card {background:white;border-radius:16px;padding:24px;border:1px solid #e5e7eb;
box-shadow:0 6px 14px rgba(0,0,0,0.06);}
.title {font-size:1.2rem;font-weight:600;margin-bottom:1rem;}
</style>
""", unsafe_allow_html=True)


tkpi = load_csv("data/clean_data.csv")
food_cat = load_csv("data/food_category.csv")
age_df = load_csv("data/age_group.csv")
edu_df = load_csv("data/education_level.csv")
std_df = load_csv("data/standar_mbg.csv")


if "menu_items" not in st.session_state:
    st.session_state.menu_items = []

if "student" not in st.session_state:
    st.session_state.student = {"kelas": "", "gender": ""}



left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">👤 Informasi Siswa</div>', unsafe_allow_html=True)

    kelas = st.selectbox(
        "Kelas",
        [
            "SD Kelas I","SD Kelas II","SD Kelas III",
            "SD Kelas IV","SD Kelas V","SD Kelas VI",
            "SMP Kelas VII","SMP Kelas VIII","SMP Kelas IX",
            "SMA Kelas X","SMA Kelas XI","SMA Kelas XII"
        ]
    )

    gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])

    st.session_state.student.update({"kelas": kelas, "gender": gender})
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">🍽️ Menu</div>', unsafe_allow_html=True)

    foods = sorted(tkpi["nama_bahan_makanan"].tolist())

    if st.button("➕ Tambah Menu"):
        st.session_state.menu_items.append({
            "id": str(uuid.uuid4()),
            "name": "",
            "gram": 100
        })

    for item in st.session_state.menu_items:
        cols = st.columns([4, 1, 1])
        item["name"] = cols[0].selectbox(
            "Makanan",
            [""] + foods,
            key=item["id"]
        )
        item["gram"] = cols[1].number_input(
            "Gram",
            min_value=1,
            value=item["gram"],
            step=10,
            key=f"g_{item['id']}"
        )
        if cols[2].button("🗑️", key=f"d_{item['id']}"):
            st.session_state.menu_items.remove(item)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# validasi
with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">📊 Evaluasi</div>', unsafe_allow_html=True)

    if st.button("✨ Validasi Menu") and st.session_state.menu_items:
        items = []

        for m in st.session_state.menu_items:
            row = tkpi[tkpi["nama_bahan_makanan"] == m["name"]]
            food_id = row.iloc[0]["id"]

            items.append(
                perhitungan_nutrisi(
                    food_id,
                    m["gram"],
                    tkpi,
                    food_cat
                )
            )

        total = aggregate(items)

        kelas_map = {
            "SD Kelas I":7,"SD Kelas II":8,"SD Kelas III":9,
            "SD Kelas IV":10,"SD Kelas V":11,"SD Kelas VI":12,
            "SMP Kelas VII":13,"SMP Kelas VIII":14,"SMP Kelas IX":15,
            "SMA Kelas X":16,"SMA Kelas XI":17,"SMA Kelas XII":18
        }

        age = kelas_map[st.session_state.student["kelas"]]
        gender = "male" if st.session_state.student["gender"] == "Laki-laki" else "female"

        level, grade, default_gender = group_age(age, age_df)
        group_id = group_up(level, grade, edu_df, gender)
        std = get_standard(group_id, std_df)

        result = evaluasi_mbg(total, std)

        st.json({
            "group_id": group_id,
            "total_nutrisi": total,
            "evaluasi": result
        })

    st.markdown('</div>', unsafe_allow_html=True)
