import streamlit as st
import plotly.graph_objects as go

# Nastavitve strani
st.set_page_config(
    page_title="PDPZ Analiza Odkupa",
    page_icon="⚠️",
    layout="centered"
)

# Naslov in uvod
st.title("⚠️ Analiza enkratnega odkupa PDPZ")
st.markdown("""
Ta kalkulator izračuna realni neto izplen enkratnega dviga sredstev, vključno z 
**izstopnimi stroški**, **takojšnjo akontacijo** in **končnim poračunom dohodnine**.
""")

# --- STRANSKA VRSTICA ---
with st.sidebar:
    st.header("Vhodni podatki")
    st_tip = st.selectbox("Tip pokojninskega načrta", ["Stari (pred 2013)", "Novi (po 2013)"])
    st_znesek = st.number_input("Bruto privarčevana sredstva (EUR)", value=20000, step=1000)
    st_placa = st.number_input("Vaša letna neto pokojnina/plača (EUR)", value=12000, 
                               help="Podatek je nujen za določitev vašega dohodninskega razreda.")
    st_stroski_odstotek = st.slider("Izstopni stroški upravljavca (%)", 0.0, 5.0, 1.0)

# --- LOGIKA IZRAČUNA (Dohodninska lestvica 2026) ---
def izracun_dohodnine_2026(bruto_osnova):
    # Informativna lestvica (meje in stopnje)
    if bruto_osnova <= 9500:
        return bruto_osnova * 0.16
    elif bruto_osnova <= 20000:
        return 1520 + (bruto_osnova - 9500) * 0.26
    elif bruto_osnova <= 55000:
        return 4250 + (bruto_osnova - 20000) * 0.33
    elif bruto_osnova <= 80000:
        return 15800 + (bruto_osnova - 55000) * 0.39
    else:
        return 25550 + (bruto_osnova - 80000) * 0.50

# 1. Izstopni stroški
izstopni_stroski = st_znesek * (st_stroski_odstotek / 100)
osnova_za_davek = st_znesek - izstopni_stroski

# 2. Takojšnja akontacija (25%)
akontacija = osnova_za_davek * 0.25

# 3. Poračun dohodnine
# Predpostavimo približen bruto iz redne pokojnine (neto / 0.88)
letni_bruto_redno = st_placa / 0.88
davek_brez_odkupa = izracun_dohodnine_2026(letni_bruto_redno)
davek_z_odkupom = izracun_dohodnine_2026(letni_bruto_redno + osnova_za_davek)

skupni_davek_na_odkup = davek_z_odkupom - davek_brez_odkupa
poracun_naslednje_leto = skupni_davek_na_odkup - akontacija
neto_izplen = st_znesek - izstopni_stroski - skupni_davek_na_odkup

# --- PRIKAZ REZULTATOV ---
st.subheader("Končni finančni rezultat")

col1, col2, col3 = st.columns(3)
col1.metric("Bruto znesek", f"{st_znesek:,.0f} €")
col2.metric("Vsi davki in stroški", f"{st_znesek - neto_izplen:,.2f} €", delta_color="inverse")
col3.metric("Dejanski NETO", f"{neto_izplen:,.2f} €")

st.markdown("---")

# Grafični prikaz razporeditve denarja
labels = ['Neto izplačilo', 'Dohodnina (Akontacija)', 'Dohodnina (Poračun)', 'Izstopni stroški']
values = [neto_izplen, akontacija, max(0, poracun_naslednje_leto), izstopni_stroski]

fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, 
                             marker_colors=['#00CC96', '#EF553B', '#AB63FA', '#636EFA'])])
fig.update_layout(title_text="Kam gre vaš denar?")
st.plotly_chart(fig)

# Podrobna tabela
st.subheader("Razčlenitev stroškov")
data = {
    "Postavka": ["Bruto privarčevano", "Izstopni stroški", "Akontacija dohodnine (takoj)", "Predviden poračun (čez 1 leto)", "**Dejanski neto izplen**"],
    "Znesek (EUR)": [f"{st_znesek:,.2f}", f"-{izstopni_stroski:,.2f}", f"-{akontacija:,.2f}", f"-{max(0, poracun_naslednje_leto):,.2f}", f"**{neto_izplen:,.2f}**"]
}
st.table(data)

# Zakonodajni okvir (PISRS/ZPIZ)
st.info(f"💡 **Pravno obvestilo (Vir: ZPIZ-2):** Pri {st_tip.lower()} načrtih velja, da enkratni odkup pomeni prekinitev zavarovanja. Celoten znesek (brez stroškov) se prišteje k vašim letnim prihodkom, kar vas lahko potisne v višji davčni razred.")

if st_tip == "Novi (po 2013)":
    st.warning("⚠️ **Pozor:** Po ZPIZ-2 enkratno izplačilo pri novih načrtih po zakonu sploh ni dovoljeno, razen če skupni znesek ne presega cca. 5.000 € (meja se spreminja) ali v primeru invalidnosti/smrti.")
