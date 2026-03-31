import streamlit as st
import plotly.graph_objects as go
import requests
from streamlit_lottie import st_lottie

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="PDPZ Analitik 2026", page_icon="💰", layout="wide")

# --- 2. FUNKCIJE ZA IZRAČUN ---

def izracun_splosne_olajsave(skupni_dohodek):
    """Izračun po priloženi tabeli (Screenshot 08.30.07)"""
    if skupni_dohodek <= 17766.18:
        # Formula: 5.551,93 + (20.832,39 - 1,17259 * skupni dohodek)
        return 5551.93 + (20832.39 - 1.17259 * skupni_dohodek)
    else:
        return 5551.90

def izracun_dohodnine_lestvica(davčna_osnova):
    """Izračun po letni lestvici (Screenshot 08.30.31)"""
    if davčna_osnova <= 9721.40:
        return davčna_osnova * 0.16
    elif davčna_osnova <= 28592.44:
        return 1555.40 + (davčna_osnova - 9721.40) * 0.26
    elif davčna_osnova <= 57184.88:
        return 6461.89 + (davčna_osnova - 28592.44) * 0.33
    elif davčna_osnova <= 82346.20:
        return 15897.40 + (davčna_osnova - 57184.88) * 0.39
    else:
        return 25710.30 + (davčna_osnova - 82346.20) * 0.50

def celovit_izracun(bruto_pdpz, neto_mesecna_pokojnina, stroski_odstotek):
    # 1. Bruto prihodki iz pokojnine (ocena bruto iz neto)
    # Pokojnina je obdavčena, a ima 13.5% olajšavo. Za oceno letnega bruta:
    letni_neto_pokojnina = neto_mesecna_pokojnina * 12
    # Približek bruta (pokojnine so manj obremenjene, 1.1 je konzervativna ocena)
    letni_bruto_pokojnina = letni_neto_pokojnina / 0.92 
    
    izstopni_stroski = bruto_pdpz * (stroski_odstotek / 100)
    osnova_odkup = bruto_pdpz - izstopni_stroski
    
    # --- STANJE A: Brez odkupa ---
    skupni_prihodek_A = letni_bruto_pokojnina
    olajsava_A = izracun_splosne_olajsave(skupni_prihodek_A)
    davčna_osnova_A = max(0, skupni_prihodek_A - olajsava_A)
    davek_A = izracun_dohodnine_lestvica(davčna_osnova_A)
    # Upokojenska olajšava (13.5% od bruta pokojnine)
    upok_olajsava_A = letni_bruto_pokojnina * 0.135
    koncni_davek_A = max(0, davek_A - upok_olajsava_A)

    # --- STANJE B: Z odkupom ---
    skupni_prihodek_B = letni_bruto_pokojnina + osnova_odkup
    olajsava_B = izracun_splosne_olajsave(skupni_prihodek_B)
    davčna_osnova_B = max(0, skupni_prihodek_B - olajsava_B)
    davek_B = izracun_dohodnine_lestvica(davčna_osnova_B)
    upok_olajsava_B = letni_bruto_pokojnina * 0.135
    koncni_davek_B = max(0, davek_B - upok_olajsava_B)

    # Razlika v davku je tisto, kar "stane" odkup
    dejanski_davek_na_odkup = koncni_davek_B - koncni_davek_A
    akontacija = osnova_odkup * 0.25
    poracun = dejanski_davek_na_odkup - akontacija
    neto_izplen = osnova_odkup - dejanski_davek_na_odkup

    return neto_izplen, akontacija, poracun, izstopni_stroski, dejanski_davek_na_odkup

# --- 3. UI (SIDEBAR) ---
with st.sidebar:
    st.title("📋 Nastavitve")
    st_tip_nacrta = st.selectbox("Tip varčevanja:", ("Stari načrt / Individualno", "Novi kolektivni načrt (po 2013)"))
    st_bruto_pdpz = st.number_input("Privarčevana sredstva (Bruto €)", value=15000, step=1000)
    st_neto_pokojnina = st.number_input("Vaša mesečna neto pokojnina (€)", value=800)
    st_stroski_p = st.slider("Izstopni stroški upravljavca (%)", 0.0, 5.0, 1.0, 0.1)

# --- 4. LOGIKA IN PRIKAZ ---
MEJA_NOVI = 12000.0
is_legal = not (st_tip_nacrta == "Novi kolektivni načrt (po 2013)" and st_bruto_pdpz > MEJA_NOVI)

st.title("💰 PDPZ Analitik: Enkratni Odkup 2026")

if is_legal:
    neto, akon, poracun, stroski, skupni_davek = celovit_izracun(st_bruto_pdpz, st_neto_pokojnina, st_stroski_p)

    c1, c2, c3 = st.columns(3)
    c1.metric("BRUTO STANJE", f"{st_bruto_pdpz:,.0f} €")
    c2.metric("AKONTACIJA (25%)", f"{akon:,.2f} €", delta=None)
    c3.metric("KONČNI NETO", f"{neto:,.2f} €", delta=f"{-skupni_davek:,.2f} € davka", delta_color="inverse")

    col_left, col_right = st.columns([1.4, 1])
    with col_left:
        fig = go.Figure(data=[go.Pie(
            labels=['Neto izplen', 'Dojen davek (Akontacija + Poračun)', 'Stroški'],
            values=[neto, skupni_davek, stroski],
            hole=.4,
            marker=dict(colors=['#27ae60', '#e74c3c', '#2c3e50'])
        )])
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("📝 Povzetek")
        if poracun > 0:
            st.warning(f"⚠️ Pričakujte doplačilo dohodnine: {poracun:,.2f} €")
        else:
            st.success(f"✅ Možno vračilo dohodnine: {abs(poracun):,.2f} €")
        
        st.markdown(f"""
        | Postavka | Znesek |
        | :--- | :--- |
        | **Bruto znesek** | {st_bruto_pdpz:,.2f} € |
        | Izstopni stroški | -{stroski:,.2f} € |
        | Akontacija (plačana takoj) | -{akon:,.2f} € |
        | Poračun ob dohodnini | {'-' if poracun > 0 else '+'}{abs(poracun):,.2f} € |
        | **Dejanski neto izplen** | **{neto:,.2f} €** |
        """)
else:
    st.error(f"## ⛔ Odkup nad {MEJA_NOVI} € pri novih kolektivnih načrtih zakonsko ni mogoč.")
