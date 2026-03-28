import streamlit as st
import plotly.graph_objects as go
import requests
from streamlit_lottie import st_lottie

# --- 1. KONFIGURACIJA STRANI ---
st.set_page_config(
    page_title="PDPZ Analitik 2026",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. FUNKCIJE ZA VIZUALNE DODATKE ---
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Nalaganje animacij (Lottie)
lottie_money = load_lottieurl("https://lottie.host/79059550-9851-4089-8086-53844f6f897d/7S7m6bZ2Qh.json") # Denar
lottie_warning = load_lottieurl("https://lottie.host/9f50f968-0723-4566-b31c-32269a83853d/D8O5Z48nU6.json") # Opozorilo

# --- 3. NAPREDEN CSS (Glassmorphism & Animacije) ---
st.markdown("""
    <style>
    /* Glavno ozadje */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Stil za kartice (Glassmorphism) */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
    }

    /* Prilagoditev naslovov */
    h1 {
        color: #1a2a6c;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Gumbi in vnosna polja */
    .stNumberInput, .stSlider, .stSelectbox {
        background: white;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. STRANSKA VRSTICA (Vnos) ---
with st.sidebar:
    if lottie_money:
        st_lottie(lottie_money, height=150, key="money_sidebar")
    
    st.title("📋 Nastavitve")
    st.markdown("Prilagodite parametre za natančen izračun.")
    
    st_tip_nacrta = st.selectbox(
        "Tip varčevanja:",
        ("Stari načrt / Individualno", "Novi kolektivni načrt (po 2013)")
    )
    
    st_bruto_pdpz = st.number_input("Privarčevana sredstva (Bruto €)", value=15000, step=1000)
    st_neto_pokojnina = st.number_input("Vaša mesečna neto pokojnina (€)", value=800)
    st_stroski_p = st.slider("Izstopni stroški upravljavca (%)", 0.0, 5.0, 1.0, 0.1)
    
    st.divider()
    st.caption("Verzija: 2.0.1 (Zakonodaja 2026)")

# --- 5. LOGIKA IZRAČUNA ---
MEJA_NOVI = 12000.0
is_legal = not (st_tip_nacrta == "Novi kolektivni načrt (po 2013)" and st_bruto_pdpz > MEJA_NOVI)

def izracun_dohodnine(bruto_osnova):
    osnova = max(0, bruto_osnova - 5500)
    if osnova <= 9500: return osnova * 0.16
    elif osnova <= 20000: return 1520 + (osnova - 9500) * 0.26
    elif osnova <= 55000: return 4250 + (osnova - 20000) * 0.33
    else: return 15800 + (osnova - 55000) * 0.39

# --- 6. PRIKAZ REZULTATOV ---
st.title("💰 PDPZ Analitik: Enkratni Odkup")

if is_legal:
    # Izračun vrednosti
    izstopni_stroski = st_bruto_pdpz * (st_stroski_p / 100)
    davčna_osnova_odkup = st_bruto_pdpz - izstopni_stroski
    akontacija_takoj = davčna_osnova_odkup * 0.25
    izplačilo_na_trr_danes = davčna_osnova_odkup - akontacija_takoj
    
    letni_bruto_pokojnina = (st_neto_pokojnina * 12) / 0.95
    davek_brez_odkupa = izracun_dohodnine(letni_bruto_pokojnina)
    davek_z_odkupom = izracun_dohodnine(letni_bruto_pokojnina + davčna_osnova_odkup)
    
    dejanski_skupni_davek_odkup = davek_z_odkupom - davek_brez_odkupa
    poracun_furs = dejanski_skupni_davek_odkup - akontacija_takoj
    končni_neto_izplen = st_bruto_pdpz - izstopni_stroski - dejanski_skupni_davek_odkup

    # KPI Kartice
    c1, c2, c3 = st.columns(3)
    c1.metric("BRUTO STANJE", f"{st_bruto_pdpz:,.0f} €")
    c2.metric("TAKOJŠNJE IZPLAČILO", f"{izplačilo_na_trr_danes:,.2f} €", delta="-25% akontacija", delta_color="inverse")
    c3.metric("KONČNI NETO", f"{končni_neto_izplen:,.2f} €", delta=f"{končni_neto_izplen/st_bruto_pdpz*100:.1f}% od bruto")

    st.write("") # Razmik

    # Graf in Tabela
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.subheader("📊 Porazdelitev sredstev")
        labels = ['Neto izplen', 'Akontacija (25%)', 'Doplačilo FURS', 'Stroški']
        values = [končni_neto_izplen, akontacija_takoj, max(0, poracun_furs), izstopni_stroski]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=.5,
            marker=dict(colors=['#2ECC71', '#F1C40F', '#E74C3C', '#34495E'])
        )])
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("📑 Povzetek izračuna")
        if poracun_furs > 0:
            st.error(f"⚠️ **Doplačilo ob poračunu:** {poracun_furs:,.2f} €")
        else:
            st.success(f"✅ **Vračilo ob poračunu:** {abs(poracun_furs):,.2f} €")
            
        st.markdown(f"""
        | Opis | Vrednost |
        | :--- | :--- |
        | **Bruto privarčevano** | {st_bruto_pdpz:,.2f} € |
        | Izstopni stroški | -{izstopni_stroski:,.2f} € |
        | Takojšnja akontacija | -{akontacija_takoj:,.2f} € |
        | Poračun dohodnine | {'-' if poracun_furs > 0 else '+'}{abs(poracun_furs):,.2f} € |
        | --- | --- |
        | **KONČNI IZPLEN (ČISTO)** | **{končni_neto_izplen:,.2f} €** |
        """)

else:
    # Vizualni prikaz blokade
    st.error("## ⛔ Odkup po zakonodaji ni dovoljen!")
    c1, c2 = st.columns([1, 2])
    with c1:
        if lottie_warning:
            st_lottie(lottie_warning, height=200)
    with c2:
        st.write(f"Znesek {st_bruto_pdpz:,.0f} € presega zakonsko mejo **{MEJA_NOVI:,.0f} €** za nove kolektivne načrte.")
        st.info("Svetujemo prenos v pokojninsko rento ali znižanje zneska dviga.")

# --- 7. NOGA ---
st.divider()
st.caption("Izračun je informativne narave in temelji na predvideni davčni lestvici za leto 2026.")
