import streamlit as st
import plotly.graph_objects as go

# Nastavitve strani
st.set_page_config(
    page_title="PDPZ Analitik: Enkratni Odkup",
    page_icon="💰",
    layout="centered"
)

# Naslov aplikacije
st.title("💰 Kalkulator dajatev pri enkratnem odkupu PDPZ")
st.markdown("""
Ta aplikacija analizira finančni učinek enkratnega dviga sredstev. 
Upošteva **izstopne stroške**, **takojšnjo 25% akontacijo** in **končni letni poračun dohodnine**.
""")

# --- STRANSKA VRSTICA (Vnos podatkov) ---
with st.sidebar:
    st.header("📋 Vnos podatkov")
    
    st_tip_nacrta = st.radio(
        "Tip varčevanja:",
        ("Stari načrt / Individualno", "Novi kolektivni načrt (po 2013)")
    )
    
    st_bruto_pdpz = st.number_input("Privarčevana sredstva (Bruto v EUR)", value=15000, step=1000)
    
    st_neto_pokojnina = st.number_input(
        "Vaša mesečna neto pokojnina (EUR)", 
        value=800,
        help="Nujno za določitev davčnega razreda pri letnem poračunu dohodnine."
    )
    
    st_stroski_p = st.slider("Izstopni stroški upravljavca (%)", 0.5, 3.0, 1.0)
    
    st.markdown("---")
    st.info("💡 **Zakonodaja 2026:** Pri novih načrtih je odkup omejen na 12.000 €.")

# --- LOGIKA PREVERJANJA (Omejitev 12.000 €) ---
MEJA_NOVI = 12000.0
is_legal = True
if st_tip_nacrta == "Novi kolektivni načrt (po 2013)" and st_bruto_pdpz > MEJA_NOVI:
    is_legal = False

# --- IZRAČUN (Če je zakonito) ---
if is_legal:
    # 1. Izstopni stroški
    izstopni_stroski = st_bruto_pdpz * (st_stroski_p / 100)
    davčna_osnova_odkup = st_bruto_pdpz - izstopni_stroski
    
    # 2. Takojšnja akontacija (VEDNO 25% po zakonu)
    akontacija_takoj = davčna_osnova_odkup * 0.25
    izplačilo_na_trr_danes = davčna_osnova_odkup - akontacija_takoj
    
    # 3. Poračun dohodnine (Informativna lestvica 2026)
    def izracun_dohodnine(bruto_osnova):
        # Splošna olajšava (približek 5.500 €)
        osnova = max(0, bruto_osnova - 5500)
        if osnova <= 9500: return osnova * 0.16
        elif osnova <= 20000: return 1520 + (osnova - 9500) * 0.26
        elif osnova <= 55000: return 4250 + (osnova - 20000) * 0.33
        else: return 15800 + (osnova - 55000) * 0.39

    # Izračun progresije
    letni_bruto_pokojnina = (st_neto_pokojnina * 12) / 0.95
    davek_brez_odkupa = izracun_dohodnine(letni_bruto_obstojeci := letni_bruto_pokojnina)
    davek_z_odkupom = izracun_dohodnine(letni_bruto_obstojeci + davčna_osnova_odkup)
    
    dejanski_skupni_davek_odkup = davek_z_odkupom - davek_brez_odkupa
    poracun_furs = dejanski_skupni_davek_odkup - akontacija_takoj
    končni_neto_izplen = st_bruto_pdpz - izstopni_stroski - dejanski_skupni_davek_odkup

    # --- VIZUALIZACIJA ---
    st.subheader("📊 Finančna razčlenitev")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Takojšnje izplačilo (na TRR)", f"{izplačilo_na_trr_danes:,.2f} €")
        st.caption("Znesek po odštetju stroškov in 25% akontacije.")
    with col2:
        st.metric("Končni neto (po poračunu)", f"{končni_neto_izplen:,.2f} €")
        st.caption("Dejanski znesek, ki vam ostane po enem letu.")

    # Grafika (Pita)
    labels = ['Čisti neto izplen', 'Akontacija dohodnine (25%)', 'Poračun dohodnine (FURS)', 'Izstopni stroški']
    values = [končni_neto_izplen, akontacija_takoj, max(0, poracun_furs), izstopni_stroski]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=.4,
        marker_colors=['#27ae60', '#f39c12', '#c0392b', '#2c3e50'],
        textinfo='percent'
    )])
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(fig, use_container_width=True)

    # Opozorilo o poračunu
    if poracun_furs > 0:
        st.error(f"⚠️ **Pozor:** Zaradi progresivne lestvice boste ob letnem poračunu verjetno morali DOPLAČATI cca. **{poracun_furs:,.2f} €**.")
    else:
        st.success(f"✅ **Informacija:** Zaradi nižjih skupnih prihodkov bi vam FURS ob poračunu lahko vrnil cca. **{abs(poracun_furs):,.2f} €**.")

    # Tabela
    st.table({
        "Postavka": ["Bruto stanje", "Izstopni stroški", "Takojšnja dohodnina (25%)", "Poračun dohodnine", "**Končni NETO**"],
        "Znesek (EUR)": [f"{st_bruto_pdpz:,.2f}", f"-{izstopni_stroski:,.2f}", f"-{akontacija_takoj:,.2f}", f"{'-' if poracun_furs > 0 else '+'}{abs(poracun_furs):,.2f}", f"**{končni_neto_izplen:,.2f}**"]
    })

else:
    # Prikaz blokade za nove načrte
    st.error(f"❌ **Odkup ni dovoljen!**")
    st.markdown(f"""
    Skladno z **ZPIZ-2** enkratni odkup pri novih načrtih (vplačila po 2013) nad **{MEJA_NOVI:,.0f} €** ni mogoč.
    
    **Možnosti:**
    - Dvignite znesek do {MEJA_NOVI} €, preostanek pa prenesite v rento.
    - Celoten znesek koristite kot dosmrtno pokojninsko rento (davčno ugodneje).
    """)

# Noga aplikacije
st.markdown("---")
st.caption("Viri: ZPIZ, GOV.si in PISRS (Zakon o dohodnini ter ZPIZ-2). Izračun je informativen.")
