import streamlit as st
import plotly.graph_objects as go

# --- KONFIGURACIJA IN STIL ---
st.set_page_config(
    page_title="PDPZ Analitik 2026",
    page_icon="⚖️",
    layout="wide" # Razširjen pogled za boljšo preglednost
)

# Custom CSS za modern izgled
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .footer { position: fixed; bottom: 0; width: 100%; text-align: center; color: gray; font-size: 12px; }
    div[data-testid="stExpander"] { border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- STRANSKA VRSTICA ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2489/2489756.png", width=100)
    st.title("Parametri izračuna")
    
    st_tip_nacrta = st.selectbox(
        "Tip varčevanja:",
        ("Stari načrt / Individualno", "Novi kolektivni načrt (po 2013)")
    )
    
    st_bruto_pdpz = st.number_input("Privarčevana sredstva (Bruto €)", value=15000, step=1000)
    st_neto_pokojnina = st.number_input("Mesečna neto pokojnina (€)", value=800)
    st_stroski_p = st.slider("Izstopni stroški upravljavca (%)", 0.0, 5.0, 1.0, 0.1)
    
    st.info("💡 **Zakonodaja 2026:** Pri novih načrtih je odkup omejen na 12.000 €.")

# --- LOGIKA ---
MEJA_NOVI = 12000.0
is_legal = not (st_tip_nacrta == "Novi kolektivni načrt (po 2013)" and st_bruto_pdpz > MEJA_NOVI)

# Funkcija za dohodnino
def izracun_dohodnine(bruto_osnova):
    osnova = max(0, bruto_osnova - 5500)
    if osnova <= 9500: return osnova * 0.16
    elif osnova <= 20000: return 1520 + (osnova - 9500) * 0.26
    elif osnova <= 55000: return 4250 + (osnova - 20000) * 0.33
    else: return 15800 + (osnova - 55000) * 0.39

# --- GLAVNI DEL ---
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

    # Ključni indikatorji (KPI)
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Bruto znesek", f"{st_bruto_pdpz:,.2f} €")
    col_b.metric("Takoj na TRR", f"{izplačilo_na_trr_danes:,.2f} €", delta_color="normal")
    col_c.metric("Končni neto izplen", f"{končni_neto_izplen:,.2f} €", help="Znesek po vseh stroških in končnem poračunu dohodnine.")

    st.markdown("---")

    # Razdelitev na graf in tabelo
    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        st.subheader("📊 Struktura stroškov in izplačila")
        labels = ['Čisti neto izplen', 'Akontacija (25%)', 'Poračun FURS', 'Stroški']
        values = [končni_neto_izplen, akontacija_takoj, max(0, poracun_furs), izstopni_stroski]
        colors = ['#2ECC71', '#F1C40F', '#E74C3C', '#34495E']

        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=.5,
            marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2))
        )])
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("📝 Podrobna kalkulacija")
        st.write(f"**Tip načrta:** {st_tip_nacrta}")
        
        # Dinamično opozorilo
        if poracun_furs > 0:
            st.warning(f"⚠️ Ob poračunu boste doplačali: **{poracun_furs:,.2f} €**")
        else:
            st.success(f"✅ Ob poračunu prejmete vrnjeno: **{abs(poracun_furs):,.2f} €**")

        # Tabela v Markdown za lepši izgled
        st.markdown(f"""
        | Postavka | Znesek |
        | :--- | :--- |
        | **Bruto privarčevano** | {st_bruto_pdpz:,.2f} € |
        | Izstopni stroški ({st_stroski_p}%) | -{izstopni_stroski:,.2f} € |
        | Takojšnja akontacija (25%) | -{akontacija_takoj:,.2f} € |
        | Poračun dohodnine (ocena) | {"-" if poracun_furs > 0 else "+"}{abs(poracun_furs):,.2f} € |
        | --- | --- |
        | **DEJANSKI NETO IZPLEN** | **{končni_neto_izplen:,.2f} €** |
        """)

else:
    st.error("### 🛑 Odkup ni mogoč!")
    st.info(f"Skladno z zakonodajo ZPIZ-2 pri novih načrtih (vplačila po letu 2013) enkratni odkup nad **{MEJA_NOVI:,.0f} €** ni dovoljen.")
    st.markdown("""
    **Priporočeni naslednji koraki:**
    1. Znižajte znesek odkupa na 12.000 €.
    2. Razmislite o prenosu v **pokojninsko rento**, ki je davčno bistveno bolj ugodna (obdavčena le 50% rente).
    """)

st.markdown('<div class="footer">Informativni izračun • PDPZ Analitik 2026 • Viri: ZPIZ, FURS</div>', unsafe_allow_html=True)
