# =========================
# IMPORT & SETUP
# =========================
import streamlit as st
import pandas as pd
import time
import uuid

st.set_page_config(
    page_title="AI Validasi Menu MBG",
    layout="wide"
)

# =========================
# STATE INIT
# =========================
if "menu_items" not in st.session_state:
    st.session_state.menu_items = []

if "validated" not in st.session_state:
    st.session_state.validated = False

if "result" not in st.session_state:
    st.session_state.result = None

if "logbook" not in st.session_state:
    st.session_state.logbook = []

# =========================
# DATA MENU
# =========================
MENU_CATEGORIES = {
    "Makanan Pokok": [
        "Nasi Putih", "Nasi Merah", "Nasi Jagung", "Kentang Rebus", "Ubi Rebus", "Mie"
    ],
    "Lauk Pauk": [
        "Ayam Goreng", "Ayam Bakar", "Ikan Goreng", "Ikan Bakar",
        "Tempe Goreng", "Tahu Goreng", "Telur Rebus", "Telur Dadar"
    ],
    "Sayuran": [
        "Sayur Asem", "Sayur Sop", "Tumis Kangkung", "Capcay", "Sayur Lodeh"
    ],
    "Buah": [
        "Pisang", "Apel", "Jeruk", "Pepaya", "Semangka"
    ]
}

st.title("🍽️ AI Validasi Menu MBG")
st.caption("Validasi otomatis menu gizi sesuai SOP")

# menu choice
st.subheader("🍴 Pilihan Menu Makanan")

for category, options in MENU_CATEGORIES.items():
    with st.expander(category, expanded=False):
        selected = st.multiselect(
            f"Pilih {category}",
            options,
            key=f"select_{category}"
        )

        for item in selected:
            exists = any(m["name"] == item for m in st.session_state.menu_items)
            if not exists:
                st.session_state.menu_items.append({
                    "id": str(uuid.uuid4()),
                    "category": category,
                    "name": item,
                    "portion": 100,
                    "custom": False
                })

# portion control
st.subheader("⚖️ Kontrol Porsi")

if not st.session_state.menu_items:
    st.info("Pilih menu terlebih dahulu")
else:
    for item in st.session_state.menu_items:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{item['name']}**")
        with col2:
            item["custom"] = st.checkbox(
                "Porsi Bebas",
                value=item["custom"],
                key=f"custom_{item['id']}"
            )
        with col3:
            item["portion"] = st.number_input(
                "gram",
                min_value=0,
                step=10,
                disabled=not item["custom"],
                value=item["portion"],
                key=f"portion_{item['id']}"
            )

# ai validation
st.subheader("✨ AI Validasi Menu")

can_validate = len(st.session_state.menu_items) > 0

if st.button(
    "Validasi Menu",
    disabled=not can_validate
):
    with st.spinner("Memproses menu dengan AI..."):
        time.sleep(1)
        st.info("Menganalisis komposisi nutrisi...")
        time.sleep(1)
        st.info("Memeriksa kepatuhan SOP...")
        time.sleep(1)
        st.info("Menyusun laporan...")
        time.sleep(1)

    total_energy = sum(i["portion"] * 1.2 for i in st.session_state.menu_items)
    total_protein = sum(i["portion"] * 0.08 for i in st.session_state.menu_items)
    total_carb = sum(i["portion"] * 0.2 for i in st.session_state.menu_items)
    total_fiber = sum(i["portion"] * 0.03 for i in st.session_state.menu_items)

    status = "sesuai" if total_energy >= 400 else "tidak sesuai"

    st.session_state.result = {
        "energi": int(total_energy),
        "protein": int(total_protein),
        "karbohidrat": int(total_carb),
        "serat": int(total_fiber),
        "status": status,
        "message": "Menu memenuhi standar MBG" if status == "sesuai" else "Energi belum mencukupi"
    }

    if status == "sesuai":
        st.session_state.logbook.append({
            "id": str(uuid.uuid4()),
            "namaMenu": ", ".join(i["name"] for i in st.session_state.menu_items),
            "bahanUtama": st.session_state.menu_items[0]["name"],
            "kelas": "SD",
            "energi": int(total_energy),
            "statusSOP": "Sesuai SOP"
        })

    st.session_state.validated = True

# output result
if st.session_state.validated and st.session_state.result:
    st.subheader("📊 Output Laporan Gizi")

    r = st.session_state.result

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Energi", f"{r['energi']} kkal")
    c2.metric("Protein", f"{r['protein']} g")
    c3.metric("Karbohidrat", f"{r['karbohidrat']} g")
    c4.metric("Serat", f"{r['serat']} g")

    if r["status"] == "sesuai":
        st.success(f"✅ {r['message']}")
    else:
        st.error(f"❌ {r['message']}")

