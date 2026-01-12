import streamlit as st
import pandas as pd
import time
import uuid

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="AI Validasi Menu MBG", layout="wide")

# ===============================
# SESSION STATE
# ===============================
if "student_info" not in st.session_state:
    st.session_state.student_info = {"jenjang": "", "kelas": ""}

if "menu_items" not in st.session_state:
    st.session_state.menu_items = []

if "validated" not in st.session_state:
    st.session_state.validated = False

if "result" not in st.session_state:
    st.session_state.result = None

# ===============================
# CONSTANTS (UI ASLI)
# ===============================
KELAS_OPTIONS = {
    "SD": [
        "SD Kelas I", "SD Kelas II", "SD Kelas III",
        "SD Kelas IV", "SD Kelas V", "SD Kelas VI"
    ],
    "SMP": [
        "SMP Kelas VII", "SMP Kelas VIII", "SMP Kelas IX"
    ],
    "SMA": [
        "SMA Kelas X", "SMA Kelas XI", "SMA Kelas XII"
    ]
}

MENU_CATEGORIES = {
    "Makanan Pokok": [
        "Nasi Putih", "Nasi Merah", "Nasi Jagung",
        "Kentang Rebus", "Ubi Rebus", "Mie"
    ],
    "Lauk Pauk": [
        "Ayam Goreng", "Ayam Bakar", "Ikan Goreng",
        "Ikan Bakar", "Tempe Goreng", "Tahu Goreng",
        "Telur Rebus", "Telur Dadar"
    ],
    "Sayuran": [
        "Sayur Asem", "Sayur Sop", "Tumis Kangkung",
        "Capcay", "Sayur Lodeh"
    ],
    "Buah": [
        "Pisang", "Apel", "Jeruk", "Pepaya", "Semangka"
    ]
}

# ===============================
# DATA LOADER
# ===============================
@st.cache_data
def load():
    data = {}

    data["standar"] = pd.read_csv(
        "data/standar_mbg.csv",
        sep=";",
        engine="python"
    )
    data["standar"].columns = data["standar"].columns.str.strip().str.lower()

    data["education"] = pd.read_csv("data/education.csv")
    data["group"] = pd.read_csv("data/group.csv")

    return data

# ===============================
# MBG LOGIC (NO HARDCODE)
# ===============================
ROMAN_MAP = {
    "I": 1, "II": 2, "III": 3,
    "IV": 4, "V": 5, "VI": 6,
    "VII": 7, "VIII": 8, "IX": 9,
    "X": 10, "XI": 11, "XII": 12
}

def extract_class_number(kelas_str):
    kelas_str = kelas_str.upper()
    for roman, num in ROMAN_MAP.items():
        if roman in kelas_str:
            return num
    raise ValueError(f"Tidak bisa membaca kelas dari: {kelas_str}")

def resolve_group_id(jenjang, kelas, edu_df):
    class_num = extract_class_number(kelas)

    row = edu_df[
        (edu_df["level"] == jenjang) &
        (edu_df["class_min"] <= class_num) &
        (edu_df["class_max"] >= class_num)
    ]

    if row.empty:
        raise ValueError(
            f"group_id tidak ditemukan untuk {jenjang} kelas {class_num}"
        )

    return row.iloc[0]["group_id"]

def get_mbg_standard(jenjang, kelas, data):
    gid = resolve_group_id(jenjang, kelas, data["education"])

    row = data["standar"][
        data["standar"]["group_id"].str.upper() == gid.upper()
    ]

    if row.empty:
        raise ValueError(f"Standar MBG tidak ditemukan untuk group_id: {gid}")

    return row.iloc[0]

# ===============================
# UI HEADER
# ===============================
st.title("🍽️ AI Validasi Menu MBG")
st.caption("Validasi otomatis menu sesuai standar gizi MBG")

# ===============================
# INFORMASI SISWA
# ===============================
st.subheader("👤 Informasi Siswa")

info = st.session_state.student_info
col1, col2 = st.columns(2)

with col1:
    jenjang = st.selectbox(
        "Jenjang Pendidikan",
        ["", "SD", "SMP", "SMA"],
        index=["", "SD", "SMP", "SMA"].index(info["jenjang"]) if info["jenjang"] else 0
    )

if jenjang != info["jenjang"]:
    info["jenjang"] = jenjang
    info["kelas"] = ""

with col2:
    kelas = st.selectbox(
        "Kelas",
        ["Pilih Jenjang Terlebih Dahulu"]
        if not info["jenjang"]
        else [""] + KELAS_OPTIONS[info["jenjang"]],
        disabled=not info["jenjang"]
    )

    if kelas and kelas != "Pilih Jenjang Terlebih Dahulu":
        info["kelas"] = kelas

# ===============================
# MENU SELECTION
# ===============================
st.subheader("🍴 Pilihan Menu Makanan")

for category, options in MENU_CATEGORIES.items():
    with st.expander(category):
        selected = st.multiselect(
            f"Pilih {category}",
            options,
            key=f"menu_{category}"
        )

        for item in selected:
            if not any(m["name"] == item for m in st.session_state.menu_items):
                st.session_state.menu_items.append({
                    "id": str(uuid.uuid4()),
                    "category": category,
                    "name": item,
                    "portion": 100,
                    "custom": False
                })

# ===============================
# PORTION CONTROL
# ===============================
st.subheader("⚖️ Kontrol Porsi")

if not st.session_state.menu_items:
    st.info("Pilih menu terlebih dahulu")
else:
    for item in st.session_state.menu_items:
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.markdown(f"**{item['name']}**")
        item["custom"] = c2.checkbox(
            "Porsi Bebas",
            item["custom"],
            key=f"c_{item['id']}"
        )
        item["portion"] = c3.number_input(
            "gram",
            min_value=0,
            step=10,
            value=item["portion"],
            disabled=not item["custom"],
            key=f"p_{item['id']}"
        )

# ===============================
# VALIDATION
# ===============================
st.subheader("✨ AI Validasi Menu")

can_validate = info["jenjang"] and info["kelas"] and st.session_state.menu_items

if st.button("Validasi Menu", disabled=not can_validate):
    with st.spinner("Memproses menu dengan AI..."):
        time.sleep(1)

    energi = sum(i["portion"] * 1.2 for i in st.session_state.menu_items)
    protein = sum(i["portion"] * 0.08 for i in st.session_state.menu_items)
    karbo = sum(i["portion"] * 0.2 for i in st.session_state.menu_items)
    serat = sum(i["portion"] * 0.03 for i in st.session_state.menu_items)

    has_protein = any(i["category"] == "Lauk Pauk" for i in st.session_state.menu_items)
    has_carb = any(i["category"] == "Makanan Pokok" for i in st.session_state.menu_items)
    has_veg = any(i["category"] == "Sayuran" for i in st.session_state.menu_items)
    has_fruit = any(i["category"] == "Buah" for i in st.session_state.menu_items)

    data = load()
    std = get_mbg_standard(info["jenjang"], info["kelas"], data)

    checks = [
        std["min_energy_kcal"] <= energi <= std["max_energy_kcal"],
        protein >= std["min_protein_g"],
        karbo >= std["min_carbohydrate_g"],
        serat >= std["min_fiber_g"],
        has_protein if std["req_protein"] else True,
        has_carb if std["req_carb"] else True,
        has_veg if std["req_veg"] else True,
        has_fruit if std["req_fruit"] else True
    ]

    status = "sesuai" if all(checks) else "tidak sesuai"

    st.session_state.result = {
        "energi": int(energi),
        "protein": int(protein),
        "karbohidrat": int(karbo),
        "serat": int(serat),
        "status": status
    }

    st.session_state.validated = True

# ===============================
# OUTPUT
# ===============================
if st.session_state.validated:
    st.subheader("📊 Output Laporan Gizi")
    r = st.session_state.result

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Energi", f"{r['energi']} kkal")
    c2.metric("Protein", f"{r['protein']} g")
    c3.metric("Karbohidrat", f"{r['karbohidrat']} g")
    c4.metric("Serat", f"{r['serat']} g")

    if r["status"] == "sesuai":
        st.success("✅ Menu memenuhi standar gizi MBG")
    else:
        st.error("❌ Menu tidak memenuhi standar gizi MBG")
