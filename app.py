import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Nastavitve strani za moderen videz
st.set_page_config(
    page_title="PDPZ Analitik 2026",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stilsko oblikovanje s CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 Kalkulator PDPZ: Renta ali Enkratni odkup?")
st.markdown("---")

# --- STRANSKA VRSTICA ZA VHODNE PODATKE ---
with st.sidebar:
    st.header("⚙️ Nastavitve izračuna")
    
    st_tip_nacrta = st.radio(
        "Tip pokojninskega načrta:",
        ("Novi (vplačila po 1.1.2013)", "Stari (vplačila pred 2013)")
    )
    
    st_privarcevano = st.number_input("Skupna privarčevana sredstva (EUR)", value=25000, step=1000)
    
    st_redna_pokojnina = st.number_input(
        "Vaša redna neto pokojnina (EUR/mesec)", 
        value=1000, 
        help="Potrebno za izračun dohodninskega razreda ob poračunu."
    )
    
    st_leta_rente = st.slider("Doba prejemanja rente (leta)", 5, 30, 20)
    
    st.markdown("---")
    st.info("ℹ️ **Predpostavke:**\n- Izstopni stroški: 1%\n- Akontacija dohodnine: 25%\n- Davčna osnova za rento: 50%")

# --- LOGIKA IZRAČUNA ---

# 1. Izračun za Enkratni Odkup
stroski_odkup = st_privarcevano * 0.01
osnova_za_davek = st_privarcevano - stroski_odkup
akontacija_odkup = osnova_za_davek * 0.25

# Funkcija za informativni izračun dohodnine (Lestvica 2025/2026)
def informativna_dohodnina(letni_prejemki):
    # Poenostavljena slovenska dohodninska lestvica
    if letni_prejemki <= 9500: return letni_prejemki * 0.16
    elif letni_prejemki <= 20000: return 1520 + (letni_prejemki - 9500) * 0.26
    elif letni_prejemki <= 55000: return 4250 + (letni_prejemki - 20000) * 0.33
    elif letni_prejemki <= 80000: return 15800 + (letni_prejemki - 55000) * 0.39
    else: return 25550 + (letni_prejemki - 80000) * 0.50

letna_redna_neto = st_redna_pokojnina * 12
# Bruto ocena za redno pokojnino (približek)
letna_redna_bruto = letna_redna_neto / 0.88 

# Dohodnina brez odkupa vs z odkupom
davek_brez_odkupa = informativna_dohodnina(letna_redna_bruto)
davek_z_odkupom = informativna_dohodnina(letna_redna_bruto + osnova_za_davek)
dejanski_davek_odkup = davek_z_odkupom - davek_brez_odkupa

neto_odkup_koncni = st_privarcevano - stroski_odkup - dejanski_davek_odkup

# 2. Izračun za Rento
# Pri renti se v davčno osnovo šteje le 50% zneska
letna_renta_bruto = st_privarcevano / st_leta_rente
obdavčljiv_del_rente = letna_renta_bruto * 0.5
akontacija_rente = obdavčljiv_del_rente * 0.25
letna_renta_neto = letna_renta_bruto - akontacija_rente
skupaj_rente_neto = letna_renta_neto * st_leta_rente

# --- VIZUALNI PRIKAZ ---

c1, c2 = st.columns(2)

with c1:
    st.subheader("🔴 Enkratni odkup")
    st.metric("Neto na račun (po poračunu)", f"{neto_odkup_koncni:,.2f} EUR")
    
    labels = ['Neto izplačilo', 'Skupna dohodnina', 'Izstopni stroški']
    values = [max(0, neto_odkup_koncni), dejanski_davek_odkup, stroski_odkup]
    
    fig1 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=['#2ecc71', '#e74c3c', '#34495e'])])
    fig1.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig1, use_container_width=True)
    
    st.error(f"Država vam bo pri enkratnem dvigu vzela cca. **{dejanski_davek_odkup:,.2f} EUR** dohodnine.")

with c2:
    st.subheader("🟢 Mesečna renta")
    st.metric("Neto mesečni dodatek", f"{letna_renta_neto/12:,.2f} EUR/mesec")
    
    # Primerjava skupnih zneskov skozi čas
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name='Enkratni odkup', x=['Skupno izplačilo'], y=[neto_odkup_koncni], marker_color='#e74c3c'))
    fig2.add_trace(go.Bar(name='Vsota vseh rent', x=['Skupno izplačilo'], y=[skupaj_rente_neto], marker_color='#2ecc71'))
    
    fig2.update_layout(barmode='group', margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig2, use_container_width=True)
    
    razlika = skupaj_rente_neto - neto_odkup_koncni
    st.success(f"Z rento boste skupaj prejeli **{razlika:,.2f} EUR več** kot pri odkupu.")

# --- DODATNA ANALIZA IZ VIROV (ZPIZ & GOV.SI) ---
st.markdown("---")
st.subheader("⚠️ Kritični opomniki glede na zakonodajo")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"**Pravila za {st_tip_nacrta}:**")
    if "Novi" in st_tip_nacrta:
        st.write("• Enkraten dvig po ZPIZ-2 praviloma **ni mogoč**, razen če je znesek izjemno nizek ali gre za specifične pogoje.")
        st.write("• Sredstva so namenjena izključno dodatni pokojnini.")
    else:
        st.write("• Pri starih načrtih lahko dvignete sredstva, vendar so davčno izjemno neugodna.")
        st.write("• Obračuna se polna dohodnina po progresivni lestvici.")

with col_b:
    st.markdown("**Zakaj je renta davčno boljša?**")
    st.write("1. **50% olajšava:** Dohodnina se plača le od polovice zneska rente.")
    st.write("2. **Ni progresivnega skoka:** Ker se prejemki razporedijo na 20 let, ne skočite v višji davčni razred, kot bi pri enkratnem dvigu.")

st.info("💡 **Nasvet:** Pred končno odločitvijo preverite informativni izračun pri svojem upravljavcu (Modra zavarovalnica, Sava, Triglav itd.), saj imajo lahko različne stroške vodenja rente.")
