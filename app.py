import streamlit as st
import plotly.graph_objects as go

# Nastavitve strani
st.set_page_config(page_title="PDPZ Upokojenski Kalkulator", layout="centered")

st.title("💸 PDPZ Odkup z upoštevanjem olajšav")
st.markdown("---")

# --- STRANSKA VRSTICA ---
with st.sidebar:
    st.header("⚙️ Vhodni podatki")
    st_tip = st.radio("Tip varčevanja:", ("Stari načrt / Individualno", "Novi kolektivni (po 2013)"))
    st_znesek = st.number_input("Bruto znesek na PDPZ računu (EUR)", value=15000, step=1000)
    st_neto_pokojnina = st.number_input("Vaša mesečna neto pokojnina (EUR)", value=800, step=50)
    st_stroski_odstotek = st.slider("Izstopni stroški (%)", 0.5, 3.0, 1.0)

# --- KONSTANTE 2026 (Predvideno) ---
SPLOSNA_OLASAVA = 5500.0  # Informativni znesek za 2026
UPOKOJENSKA_OLASAVA_STOPNJA = 0.135 # 13,5% od pokojnine

# --- LOGIKA ---
meja_novi_nacrt = 12000.0
dovoljen_odkup = not (st_tip == "Novi kolektivni (po 2013)" and st_znesek > meja_novi_nacrt)

if dovoljen_odkup:
    # 1. Osnove
    letna_neto_pokojnina = st_neto_pokojnina * 12
    # Približek bruto pokojnine (pokojnine so manj obremenjene s prispevki kot plače)
    letni_bruto_pokojnina = letna_neto_pokojnina / 0.95 
    
    izstopni_stroski = st_znesek * (st_stroski_odstotek / 100)
    bruto_odkup_osnova = st_znesek - izstopni_stroski
    
    # 2. Funkcija za dohodnino z upoštevanjem olajšav
    def izracunaj_koncno_dohodnino(bruto_prihodek, je_pokojnina=True):
        # Davčna osnova = Bruto - Splošna olajšava
        davčna_osnova = max(0, bruto_prihodek - SPLOSNA_OLASAVA)
        
        # Izračun po lestvici
        if davčna_osnova <= 9500: d = davčna_osnova * 0.16
        elif davčna_osnova <= 20000: d = 1520 + (davčna_osnova - 9500) * 0.26
        elif davčna_osnova <= 55000: d = 4250 + (davčna_osnova - 20000) * 0.33
        else: d = 15800 + (davčna_osnova - 55000) * 0.39
        
        # Odšteti upokojensko olajšavo (13,5% od pokojnine, ne od odkupa!)
        if je_pokojnina:
            dejanska_upok_olajšava = letni_bruto_pokojnina * UPOKOJENSKA_OLASAVA_STOPNJA
            d = max(0, d - dejanska_upok_olajšava)
        return d

    # Izračun razlike
    davek_brez_odkupa = izracunaj_koncno_dohodnino(letni_bruto_pokojnina)
    davek_z_odkupom = izracunaj_koncno_dohodnino(letni_bruto_pokojnina + bruto_odkup_osnova)
    
    skupni_davek_odkup = davek_z_odkupom - davek_brez_odkupa
    akontacija = bruto_odkup_osnova * 0.25
    poracun = skupni_davek_odkup - akontacija
    neto_izplen = st_znesek - izstopni_stroski - skupni_davek_odkup

    # --- VIZUALIZACIJA ---
    st.subheader("Analiza neto izplena")
    
    col1, col2 = st.columns(2)
    col1.metric("Bruto na računu", f"{st_znesek:,.0f} €")
    col2.metric("Dejanski neto izplen", f"{neto_izplen:,.2f} €")

    # Graf
    fig = go.Figure(data=[go.Pie(
        labels=['Neto (vam ostane)', 'Dohodnina (takoj)', 'Dohodnina (poračun)', 'Stroški'],
        values=[neto_izplen, akontacija, max(0, poracun), izstopni_stroski],
        hole=.4,
        marker_colors=['#27ae60', '#f39c12', '#c0392b', '#2c3e50']
    )])
    st.plotly_chart(fig)

    st.write(f"### ⚠️ Vaša efektivna obdavčitev: **{( (st_znesek - neto_izplen) / st_znesek * 100):.1f}%**")
    st.info(f"V izračunu je upoštevana splošna olajšava ({SPLOSNA_OLASAVA} €) in upokojenska olajšava (13,5%).")

else:
    st.error("❌ Odkup nad 12.000 € pri novih načrtih ni dovoljen.")
    st.write("Skladno z ZPIZ-2 morate za ta znesek izbrati rento.")
