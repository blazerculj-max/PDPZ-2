import streamlit as st
import plotly.graph_objects as go

# Nastavitve strani za moderen in pregleden videz
st.set_page_config(
    page_title="Analiza odkupa PDPZ 2026",
    page_icon="💸",
    layout="centered"
)

# Stilsko oblikovanje za boljšo vizualno izkušnjo
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("💸 Analiza enkratnega odkupa PDPZ")
st.markdown("Ta aplikacija natančno izračuna dajatve in neto izplen pri enkratnem dvigu sredstev po zakonodaji ZPIZ-2 in ZDoh-2.")
st.markdown("---")

# --- STRANSKA VRSTICA (Vhodni podatki) ---
with st.sidebar:
    st.header("⚙️ Nastavitve")
    
    st_tip = st.radio(
        "Tip varčevanja:",
        ("Stari načrt / Individualno", "Novi kolektivni načrt (po 2013)")
    )
    
    st_znesek = st.number_input("Bruto privarčevana sredstva (EUR)", value=15000, step=1000)
    
    st_placa = st.number_input(
        "Vaša letna neto pokojnina/plača (EUR)", 
        value=12000,
        help="To je ključno za izračun končnega poračuna dohodnine."
    )
    
    st_stroski_odstotek = st.slider("Izstopni stroški upravljavca (%)", 0.5, 3.0, 1.0)
    
    st.markdown("---")
    st.caption("Izračunano na podlagi dohodninske lestvice za leto 2026.")

# --- LOGIKA PREVERJANJA ZAKONODAJE (Meja 12.000 EUR) ---
meja_novi_nacrt = 12000.0
dovoljen_odkup = True

if st_tip == "Novi kolektivni načrt (po 2013)" and st_znesek > meja_novi_nacrt:
    dovoljen_odkup = False

# --- IZRAČUN ---
if dovoljen_odkup:
    # 1. Izstopni stroški (Trgajo se prvi)
    izstopni_stroski = st_znesek * (st_stroski_odstotek / 100)
    
    # 2. Davčna osnova za akontacijo
    osnova_za_davek = st_znesek - izstopni_stroski
    
    # 3. Akontacija dohodnine (25% od osnove po stroških)
    akontacija = osnova_za_davek * 0.25
    
    # 4. Poračun dohodnine (Progresivna lestvica 2026)
    def izracun_dohodnine(bruto_osnova):
        if bruto_osnova <= 9500: return bruto_osnova * 0.16
        elif bruto_osnova <= 20000: return 1520 + (bruto_osnova - 9500) * 0.26
        elif bruto_osnova <= 55000: return 4250 + (bruto_osnova - 20000) * 0.33
        elif bruto_osnova <= 80000: return 15800 + (bruto_osnova - 55000) * 0.39
        else: return 25550 + (bruto_osnova - 80000) * 0.50

    # Bruto ocena obstoječih prihodkov (neto / 0.88)
    letni_bruto_obstojeci = st_placa / 0.88
    
    davek_brez_odkupa = izracun_dohodnine(letni_bruto_obstojeci)
    davek_z_odkupom = izracun_dohodnine(letni_bruto_obstojeci + osnova_za_davek)
    
    dejanski_skupni_davek = davek_z_odkupom - davek_brez_odkupa
    poracun_naslednje_leto = dejanski_skupni_davek - akontacija
    
    neto_izplen = st_znesek - izstopni_stroski - dejanski_skupni_davek
    izguba_skupaj = st_znesek - neto_izplen

    # --- PRIKAZ REZULTATOV ---
    st.subheader("Končni finančni izplen")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Dejanski NETO na račun", f"{neto_izplen:,.2f} €")
    with c2:
        st.metric("Skupna izguba (Dajatve)", f"{izguba_skupaj:,.2f} €", delta_color="inverse")

    # Vizualizacija s Pito
    labels = [
        'Neto izplačilo (vam ostane)', 
        'Akontacija (25% od osnove)', 
        'Doplačilo dohodnine (poračun)', 
        'Izstopni stroški'
    ]
    values = [neto_izplen, akontacija, max(0, poracun_naslednje_leto), izstopni_stroski]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=.4,
        marker_colors=['#27ae60', '#f39c12', '#c0392b', '#2c3e50'],
        textinfo='percent'
    )])
    
    fig.update_layout(
        title="Kam dejansko izpuhti vaš privarčevani denar?",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Razčlenitev v tabeli
    st.markdown("### Podrobna razčlenitev dajatev")
    st.table({
        "Postavka": [
            "Bruto stanje na računu", 
            "Izstopni stroški upravljavca", 
            "Takojšnja akontacija dohodnine", 
            "Doplačilo ob letnem poračunu (ocena)", 
            "**KONČNI ČISTI IZPLEN**"
        ],
        "Znesek (EUR)": [
            f"{st_znesek:,.2f}", 
            f"-{izstopni_stroski:,.2f}", 
            f"-{akontacija:,.2f}", 
            f"-{max(0, poracun_naslednje_leto):,.2f}", 
            f"**{neto_izplen:,.2f}**"
        ]
    })
    
    # Kritičen argument
    st.warning(f"⚠️ **Kritični faktor:** Zaradi progresivne dohodnine ste državi oddali **{(izguba_skupaj/st_znesek)*100:.1f}%** svojega prihranka.")

else:
    # Blokada za nove načrte nad 12k
    st.error("❌ Odkup po zakonu ni mogoč!")
    st.markdown(f"""
    Pri **novih kolektivnih načrtih (vplačila po 2013)** zakonodaja ZPIZ-2 ne dovoljuje enkratnega odkupa, 
    če znesek presega **{meja_novi_nacrt:,.0f} EUR**. 
    
    V tem primeru ste primorani izbrati **dosmrtno pokojninsko rento**, ki pa je davčno bistveno bolj ugodna 
    (obdavčena je le polovica zneska).
    """)

st.markdown("---")
st.caption("Vir: Analiza temelji na PISRS (ZPIZ-2), ZDoh-2 in spletnih informacijah ZPIZ/GOV.si za leto 2026.")
