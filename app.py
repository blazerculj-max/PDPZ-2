import streamlit as st
import plotly.graph_objects as go

# Nastavitve strani
st.set_page_config(
    page_title="PDPZ Odkup: Analiza dajatev",
    page_icon="💸",
    layout="centered"
)

st.title("💸 Analiza enkratnega odkupa PDPZ")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Vhodni podatki")
    st_tip = st.radio(
        "Tip pokojninskega varčevanja:",
        ("Stari načrt / Individualno", "Novi kolektivni načrt (po 2013)")
    )
    
    st_znesek = st.number_input("Bruto privarčevana sredstva (EUR)", value=15000, step=1000)
    
    st_placa = st.number_input(
        "Vaša letna neto pokojnina/plača (EUR)", 
        value=12000,
        help="Nujno za izračun progresije dohodnine."
    )
    
    st_stroski_odstotek = st.slider("Izstopni stroški upravljavca (%)", 0.5, 3.0, 1.0)

# --- LOGIKA PREVERJANJA ZAKONODAJE ---
meja_novi_nacrt = 12000.0
dovoljen_odkup = True
opozorilo_besedilo = ""

if st_tip == "Novi kolektivni načrt (po 2013)" and st_znesek > meja_novi_nacrt:
    dovoljen_odkup = False
    opozorilo_besedilo = f"Skladno z zakonodajo enkratni odkup pri novih načrtih nad {meja_novi_nacrt:,.0f} EUR ni dovoljen. Izbrati morate rento."

# --- IZRAČUN (Če je odkup dovoljen) ---
if dovoljen_odkup:
    # 1. Izstopni stroški
    izstopni_stroski = st_znesek * (st_stroski_odstotek / 100)
    osnova_za_davek = st_znesek - izstopni_stroski
    
    # 2. Akontacija (25%)
    akontacija = osnova_za_davek * 0.25
    
    # 3. Poračun dohodnine (Lestvica 2026)
    def izracun_dohodnine(bruto_osnova):
        if bruto_osnova <= 9500: return bruto_osnova * 0.16
        elif bruto_osnova <= 20000: return 1520 + (bruto_osnova - 9500) * 0.26
        elif bruto_osnova <= 55000: return 4250 + (bruto_osnova - 20000) * 0.33
        elif bruto_osnova <= 80000: return 15800 + (bruto_osnova - 55000) * 0.39
        else: return 25550 + (bruto_osnova - 80000) * 0.50

    # Ocenjen bruto iz neto dohodkov
    letni_bruto_obstojeci = st_placa / 0.88
    davek_brez_odkupa = izracun_dohodnine(letni_bruto_obstojeci)
    davek_z_odkupom = izracun_dohodnine(letni_bruto_obstojeci + osnova_za_davek)
    
    dejanski_davek_odkup = davek_z_odkupom - davek_brez_odkupa
    poracun_naslednje_leto = dejanski_davek_odkup - akontacija
    neto_izplen = st_znesek - izstopni_stroski - dejanski_davek_odkup

    # --- PRIKAZ ---
    st.subheader("Rezultat enkratnega odkupa")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Bruto znesek", f"{st_znesek:,.2f} €")
        st.metric("Dejanski NETO izplen", f"{neto_izplen:,.2f} €")
    
    with c2:
        skupni_stroski_davek = st_znesek - neto_izplen
        st.metric("Izguba (Davki + Stroški)", f"{skupni_stroski_davek:,.2f} €", delta_color="inverse")
        st.write(f"Dejanska obdavčitev: **{((skupni_stroski_davek)/st_znesek)*100:.1f}%**")

    # Graf
    fig = go.Figure(data=[go.Pie(
        labels=['Neto izplačilo', 'Dohodnina (takoj)', 'Dohodnina (poračun)', 'Stroški'],
        values=[neto_izplen, akontacija, max(0, poracun_naslednje_leto), izstopni_stroski],
        hole=.4,
        marker_colors=['#27ae60', '#e67e22', '#c0392b', '#34495e']
    )])
    st.plotly_chart(fig, use_container_width=True)

    # Tabela razčlenitve
    st.markdown("### Podrobna razčlenitev")
    st.table({
        "Opis": ["Bruto varčevanje", "Izstopni stroški", "Akontacija dohodnine (ob izplačilu)", "Doplačilo dohodnine (ob poračunu)", "Končni neto znesek"],
        "Znesek (EUR)": [f"{st_znesek:,.2f}", f"-{izstopni_stroski:,.2f}", f"-{akontacija:,.2f}", f"-{max(0, poracun_naslednje_leto):,.2f}", f"**{neto_izplen:,.2f}**"]
    })

else:
    st.error(f"❌ **Odkup ni mogoč!**")
    st.info(opozorilo_besedilo)
    st.write("Pri novih kolektivnih načrtih zakonodaja varuje vašo namensko rabo sredstev. Nad mejo 12.000 EUR je edina zakonita pot črpanje preko pokojninske rente.")

# --- KRITIČNI ARGUMENT ---
st.markdown("---")
st.caption("Vir podatkov: ZPIZ-2, ZDoh-2 in informativne lestvice FURS 2026. Izračun je informativne narave.")
