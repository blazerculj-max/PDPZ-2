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
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

lottie_money = load_lottieurl("https://lottie.host/79059550-9851-4089-8086-53844f6f897d/7S7m6bZ2Qh.json")
lottie_warning = load_lottieurl("https://lottie.host/9f50f968-0723-4566-b31c-32269a83853d/D8O5Z48nU6.json")

# --- 3. POSODOBLJEN CSS (Bela vsebina, Gradient ozadje) ---
st.markdown("""
    <style>
    /* Ozadje celotne aplikacije */
    .stApp {
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
    }
    
    /* Glavni vsebnik za graf in tabelo naredimo bel */
    [data-testid="stVerticalBlock"] > div:has(div[data-testid="stHorizontalBlock"]) {
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* Kartice z metrikami (ostanejo Glass, a bolj čiste) */
    div[data-testid="stMetric"] {
        background: white !important;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #edf2f7;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Naslovi */
    h1, h2, h3 {
        color: #2d3748;
        font-family: 'Inter', sans-serif;
    }

    /* Stranska vrstica */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. STRANSKA VRSTICA ---
with st.sidebar:
    if lottie_money:
        st_lottie(lottie_money, height=150, key="money_sidebar")
    
    st.title("📋 Nastavitve")
    st_tip_nacrta = st.selectbox(
        "Tip varčevanja:",
        ("Stari načrt / Individualno", "Novi kolektivni načrt (po 2013)")
    )
    st_bruto_pdpz = st.number_input("Privarčevana sredstva (Bruto €)", value=15000, step=1000)
    st_neto_pokojnina = st.number_input("Vaša mesečna neto pokojnina (€)", value=800)
    st_stroski_p = st.slider("Izstopni stroški upravljavca (%)", 0.0, 5.0, 1.0, 0.1)
    st.divider()
    st.caption("Verzija: 2.1.0 • Leto 2026")

# --- 5. LOGIKA ---
MEJA_NOVI = 12000.0
is_legal = not (st_tip_nacrta == "Novi kolektivni načrt (po 2013)" and st_bruto_pdpz > MEJA_NOVI)

def izracun_dohodnine(bruto_osnova):
    osnova = max(0, bruto_osnova - 5500)
    if osnova <= 9500: return osnova * 0.16
    elif osnova <= 20000: return 1520 + (osnova - 9500) * 0.26
    elif osnova <= 55000: return 4250 + (osnova - 20000) * 0.33
    else: return 15800 + (osnova - 55000) * 0.39

# --- 6. GLAVNI PRIKAZ ---
st.title("💰 PDPZ Analitik: Enkratni Odkup")

if is_legal:
    # Izračuni
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

    # 1. Vrstica: Metrike
    c1, c2, c3 = st.columns(3)
    c1.metric("BRUTO STANJE", f"{st_bruto_pdpz:,.0f} €")
    c2.metric("TAKOJ NA TRR", f"{izplačilo_na_trr_danes:,.2f} €")
    c3.metric("KONČNI NETO", f"{končni_neto_izplen:,.2f} €")

    st.write("") 

    # 2. Vrstica: Beli blok z grafom in tabelo
    # (CSS zgoraj poskrbi, da je ta del v belem okvirju)
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.subheader("📊 Struktura odkupa")
        labels = ['Neto izplen', 'Akontacija (25%)', 'Doplačilo FURS', 'Stroški']
        values = [končni_neto_izplen, akontacija_takoj, max(0, poracun_furs), izstopni_stroski]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=.4,
            marker=dict(colors=['#27ae60', '#f1c40f', '#e74c3c', '#2c3e50'])
        )])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=0, r=0),
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("📝 Povzetek")
        if poracun_furs > 0:
            st.warning(f"Doplačilo FURS: {poracun_furs:,.2f} €")
        else:
            st.success(f"Vračilo FURS: {abs(poracun_furs):,.2f} €")
            
        st.markdown(f"""
        | Postavka | Znesek |
        | :--- | :--- |
        | **Bruto** | {st_bruto_pdpz:,.2f} € |
        | Stroški | -{izstopni_stroski:,.2f} € |
        | Akontacija | -{akontacija_takoj:,.2f} € |
        | Poračun | {'-' if poracun_furs > 0 else '+'}{abs(poracun_furs):,.2f} € |
        | **NETO** | **{končni_neto_izplen:,.2f} €** |
        """)

else:
    st.error("## ⛔ Odkup ni dovoljen")
    c1, c2 = st.columns([1, 2])
    with c1:
        if lottie_warning:
            st_lottie(lottie_warning, height=200)
    with c2:
        st.write(f"Znesek presega mejo **{MEJA_NOVI:,.0f} €** za nove načrte.")

st.divider()
st.caption("Informativni izračun PDPZ 2026")
