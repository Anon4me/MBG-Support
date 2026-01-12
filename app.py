import streamlit as st
import pandas as pd
import uuid

from logic.nutrition import perhitungan_nutrisi, aggregate
from logic.mbg import group_age, group_up, get_standard, evaluasi_mbg

st.set_page_config(page_title="MBG Menu Evaluator", layout="wide")

st.markdown("""
<style>
.card {background:white;border-radius:16px;padding:24px;border:1px solid #e5e7eb;box-shadow:0 6px 14px rgba(0,0,0,0.06);}
.title {font-size:1.25rem;font-weight:600;margin-bottom:1rem;}
.label {font-size:0.85rem;font-weight:500;}
</style>
""", unsafe_allow_html=True)

def load_csv(path):
    df = pd.read_csv(path, encoding="utf-8-sig", engine="python")
    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]
    return df

tkpi = load_csv("data/clean_data.csv")
food_cat = load_csv("data/food_category.csv")
age_df = load_csv("data/age_group.csv")
edu_df = load_csv("data/education_level.csv")
std_df = load_csv("data/standar_mbg.csv")

menu_categories = {
    "makanan-pokok": "Makanan Pokok",
    "lauk-pauk": "Lauk Pauk",
    "sayuran": "Sayuran",
    "buah-buahan": "Buah-buahan"
}

if "menu_items" not in st.session_state:
    st.session_state.menu_items = []

if "student" not in st.session_state:
    st.session_state.student = {"kelas": "", "gender": ""}

def kelas_to_age(k):
    return {
        "SD Kelas I":7,"SD Kelas II":8,"SD Kelas III":9,
        "SD Kelas IV":10,"SD Kelas V":11,"SD Kelas VI":12,
        "SMP Kelas VII":13,"SMP Kelas VIII":14,"SMP Kelas IX":15,
        "SMA Kelas X":16,"SMA Kelas XI":17,"SMA Kelas XII":18
    }.get(k, 7)

left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">👤 Informasi Siswa</div>', unsafe_allow_html=True)

    jenjang = st.selectbox("", ["", "SD", "SMP", "SMA"])
    kelas = st.selectbox("", [""] + {
        "SD": ["SD Kelas I","SD Kelas II","SD Kelas III","SD Kelas IV","SD Kelas V","SD Kelas VI"],
        "SMP": ["SMP Kelas VII","SMP Kelas VIII","SMP Kelas IX"],
        "SMA": ["SMA Kelas X","SMA Kelas XI","SMA Kelas XII"]
    }.get(jenjang, []))

    gender = st.selectbox("", ["Semua","Perempuan","Laki-laki"])

    st.session_state.student.update({"kelas": kelas, "gender": gender})
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">🍽️ Pilihan Menu</div>', unsafe_allow_html=True)

    for cid, cname in menu_categories.items():
        items = [i for i in st.session_state.menu_items if i["category"] == cid]
        checked = st.checkbox(cname, value=len(items) > 0, key=f"chk_{cid}")

        if checked and not items:
            st.session_state.menu_items.append({
                "id": str(uuid.uuid4()),
                "category": cid,
                "name": "",
                "portion": 100,
                "custom": False
            })

        if not checked:
            st.session_state.menu_items = [i for i in st.session_state.menu_items if i["category"] != cid]

        for item in items:
            foods = sorted(tkpi["nama"].tolist())
            cols = st.columns([4,1])
            item["name"] = cols[0].selectbox("", [""]+foods, key=item["id"], index=foods.index(item["name"])+1 if item["name"] in foods else 0)
            if cols[1].button("🗑️", key=f"del_{item['id']}"):
                st.session_state.menu_items.remove(item)
                st.rerun()

        if items:
            if st.button(f"➕ Tambah {cname}", key=f"add_{cid}"):
                st.session_state.menu_items.append({
                    "id": str(uuid.uuid4()),
                    "category": cid,
                    "name": "",
                    "portion": 100,
                    "custom": False
                })

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">⚖️ Kontrol Porsi</div>', unsafe_allow_html=True)

    if not st.session_state.menu_items:
        st.info("Pilih menu terlebih dahulu")
    else:
        for item in st.session_state.menu_items:
            st.write(item["name"] or "Menu belum dipilih")
            item["custom"] = st.checkbox("Porsi Bebas", value=item["custom"], key=f"c_{item['id']}")
            item["portion"] = st.number_input(
                "Gram",
                value=int(item["portion"]),
                min_value=0,
                step=10,
                disabled=not item["custom"],
                key=f"p_{item['id']}"
            )

        st.divider()
        st.write("Total Item:", len(st.session_state.menu_items))
        st.write("Total Gram:", sum(i["portion"] for i in st.session_state.menu_items))

    st.markdown('</div>', unsafe_allow_html=True)

if st.button("✨ Validasi Menu", disabled=not (st.session_state.menu_items and st.session_state.student["kelas"])):
    foods = []

    for item in st.session_state.menu_items:
        if not item["name"]:
            st.error("Ada menu belum dipilih")
            st.stop()

        row = tkpi[tkpi["nama"] == item["name"]]
        food_id = str(row.iloc[0]["id"])

        foods.append(
            perhitungan_nutrisi(
                food_id=food_id,
                gram=item["portion"],
                clean_df=tkpi,
                category_df=food_cat
            )
        )

    total = aggregate(foods)

    age = kelas_to_age(st.session_state.student["kelas"])
    gender = st.session_state.student["gender"].lower()
    gender = "male" if gender == "laki-laki" else "female" if gender == "perempuan" else "all"

    level, grade, default_gender = group_age(age, age_df)
    group_id = group_up(level, grade, edu_df, gender if gender != "all" else default_gender)
    std = get_standard(group_id, std_df)

    result = evaluasi_mbg(total, std)

    st.subheader("📊 Hasil Evaluasi")
    st.json({
        "group_id": group_id,
        "total": total,
        "evaluation": result
    })
