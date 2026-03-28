import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Nastavitve strani
st.set_page_config(page_title="PDPZ Kalkulator: Renta vs. Odkup", layout="wide")

st.title("📊 Analiza PDPZ: Enkratni odkup vs. Dosmrtna renta")
st.markdown("""
Ta aplikacija izračuna finančni učinek dveh poti ob upokojitvi na podlagi zakonodaje ZPIZ-2 in ZDoh-2.
""")

with st.sidebar:
    st.header("Vhodni podatki")
    st_privarcevano = st.number_input("Privarčevana sredstva (EUR)", value=30000, step=1000)
    st_mesecna_pokojnina = st.number_input("Vaša neto redna pokojnina (EUR/mesec)", value=12000/12, step=50)
    st_leta_prejemanja = st.slider("Pričakovana doba prejemanja rente (v letih)", 5, 30, 20)
    
    st.info("💡 Izstopni stroški so predvideni v višini 1%.")

# --- IZRAČUN 1: ENKRATNI ODKUP ---
izstopni_stroski = st_privarcevano * 0.01
osnova_za_davek = st_privarcevano - izstopni_stroski
akontacija_dohodnine = osnova_za_davek * 0.25

# Simulacija poračuna dohodnine (poenostavljena lestvica 2026)
# Skupni letni prihodki = redna pokojnina + odkup PDPZ
letna_redna = st_mesecna_pokojnina * 12
skupni_letni_prihodek = letna_redna + osnova_za_davek

# Izračun dohodnine (približek za prikaz progresije)
def izracunaj_dohodnino(znesek):
    if znesek < 9000: return znesek * 0.16
    elif znesek < 19000: return 1440 + (znesek - 9000) * 0.26
    elif znesek < 51000: return 4040 + (znesek - 19000) * 0.33
    elif znesek < 75000: return 14600 + (znesek - 51000) * 0.39
    else: return 23960 + (znesek - 75000) * 0.50

davek_skupaj = izracunaj_dohodnino(skupni_letni_prihodek) - izracunaj_dohodnino(letna_redna)
neto_odkup = osnova_za_davek - davek_skupaj

# --- IZRAČUN 2: RENTA ---
# Predpostavimo 3% letno donosnost v fazi izplačevanja in upoštevamo 50% davčno olajšavo
letna_renta_bruto = st_privarcevano / st_leta_prejemanja 
davčna_osnova_renta = letna_renta_bruto * 0.5
akontacija_rente = davčna_osnova_renta * 0.25 # Poenostavljeno
letna_renta_neto = letna_renta_bruto - akontacija_rente
skupaj_renta_neto = letna_renta_neto * st_leta_prejemanja

# --- VIZUALIZACIJA ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Enkratni odkup")
    st.metric("Neto izplačilo na račun", f"{neto_odkup:,.2f} EUR")
    st.write(f"Dejanska obdavčitev: {((st_privarcevano-neto_odkup)/st_privarcevano)*100:.1f}%")

    fig_pie = go.Figure(data=[go.Pie(labels=['Neto izplačilo', 'Dohodnina (država)', 'Izstopni stroški'], 
                             values=[neto_odkup, davek_skupaj, izstopni_stroski], hole=.3)])
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Dodatna renta")
    st.metric("Skupaj izplačano v 20 letih", f"{skupaj_renta_neto:,.2f} EUR")
    st.write(f"Mesečni dodatek k pokojnini: {letna_renta_neto/12:,.2f} EUR")

    fig_bar = go.Figure(data=[
        go.Bar(name='Odkup (Takoj)', x=['Primerjava'], y=[neto_odkup]),
        go.Bar(name='Renta (Skozi čas)', x=['Primerjava'], y=[skupaj_renta_neto])
    ])
    st.plotly_chart(fig_bar, use_container_width=True)

st.warning("⚠️ **Pozor:** Izračun poračuna dohodnine je informativen. Višina poračuna je odvisna od vseh vaših letnih prihodkov in olajšav.")
