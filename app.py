import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide", page_title="Age of the Universe - Live Monitor")

# --- TITEL & EINLEITUNG ---
st.title("🔭 age-of-the-universe.com")
st.markdown("""
### Live-Analyse der Hubble-Konstante & des Weltalters
Basiert auf den neuesten Daten des **Vera C. Rubin Observatory (LSST)** via Lasair.
""")

# --- 1. DATEN LADEN ---
@st.cache_data
def load_data():
    # Hier laden wir vorerst deine CSV. 
    # Später ersetzen wir das durch den direkten Lasair-API-Link!
    df = pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv')
    return df.dropna(subset=['z', 'h0_estimate', 'nDiaSources', 'lastDiaSourceMjdTai'])

df_raw = load_data()

# --- 2. SIDEBAR (FILTER) ---
st.sidebar.header("Filter-Einstellungen")
z_min = st.sidebar.slider("Minimale Rotverschiebung (z)", 0.0, 0.1, 0.02, 0.01)
h0_lim = st.sidebar.slider("H0 Bereich", 20, 150, (40, 120))
qualitaet_prozent = st.sidebar.slider("Elite-Schwelle (Top % der Datenqualität)", 0, 100, 50)

# Filter anwenden
df_filtered = df_raw[(df_raw['z'] > z_min) & 
                     (df_raw['h0_estimate'].between(h0_lim[0], h0_lim[1]))].copy()

# Elite-Berechnung basierend auf Schieberegler
schwelle = np.percentile(df_filtered['nDiaSources'], qualitaet_prozent)
df_elite = df_filtered[df_filtered['nDiaSources'] >= schwelle].copy()

h0_elite = df_elite['h0_estimate'].median()
h0_alle = df_filtered['h0_estimate'].median()

# --- 3. DIE TABELLE (Oben) ---
st.subheader("Vergleich der kosmologischen Modelle")
alter_planck = (977.8 / 67.4) * 0.95
alter_shoes = (977.8 / 73.0) * 0.96
alter_alle = (977.8 / h0_alle) * 0.96
alter_elite = (977.8 / h0_elite) # Deine lineare Hypothese

vergleich_data = {
    "Planck (CMB)": ["67.4", f"{alter_planck:.2f}"],
    "SH0ES (SN Ia)": ["73.0", f"{alter_shoes:.2f}"],
    "Alle Rubin-Daten": [f"{h0_alle:.1f}", f"{alter_alle:.2f}"],
    "Elite-Daten (Deine Wahl)": [f"{h0_elite:.1f}", f"{alter_elite:.2f}"]
}
st.table(pd.DataFrame(vergleich_data, index=["Hubble-Konstante (H0)", "Weltalter (Mrd. Jahre)"]))

# --- 4. GRAFIKEN ---
col1, col2 = st.columns(2)

with col1:
    st.write("### Elite-Verteilung")
    fig1, ax1 = plt.subplots()
    sns.histplot(df_elite['h0_estimate'], bins=10, kde=True, ax=ax1, color='skyblue')
    ax1.axvline(h0_elite, color='gold', linewidth=3, label=f"Median: {h0_elite:.1f}")
    ax1.legend()
    st.pyplot(fig1)

with col2:
    st.write("### H0 vs. Rotverschiebung (Elite-Trend)")
    fig2, ax2 = plt.subplots()
    ax2.scatter(df_filtered['z'], df_filtered['h0_estimate'], c=df_filtered['nDiaSources'], alpha=0.5)
    m, b = np.polyfit(df_elite['z'], df_elite['h0_estimate'], 1)
    ax2.plot(df_filtered['z'], m*df_filtered['z'] + b, color='orange', label="Elite-Trend")
    ax2.legend()
    st.pyplot(fig2)

st.write("### Chronologische Stabilisierung (Alle gefilterten Daten)")

# Berechnung der Konvergenz mit Standardfehler
df_konv = df_filtered.sort_values('lastDiaSourceMjdTai').copy()
df_konv['running_median'] = df_konv['h0_estimate'].expanding().median()
df_konv['running_std'] = df_konv['h0_estimate'].expanding().std()
df_konv['running_n'] = np.arange(1, len(df_konv) + 1)
df_konv['stderr'] = df_konv['running_std'] / np.sqrt(df_konv['running_n'])

fig3, ax3 = plt.subplots(figsize=(12, 5))
ax3.plot(df_konv['lastDiaSourceMjdTai'], df_konv['running_median'], color='purple', linewidth=3, label="Laufender Median")

# Das lila Schattenband (Sigma-Bereich)
ax3.fill_between(df_konv['lastDiaSourceMjdTai'], 
                 df_konv['running_median'] - df_konv['stderr'], 
                 df_konv['running_median'] + df_konv['stderr'], 
                 color='purple', alpha=0.2, label="Statistischer Fehlerbereich")

ax3.axhline(67.4, color='red', linestyle='--', alpha=0.5, label="Planck (67.4)")
ax3.axhline(73.0, color='green', linestyle='--', alpha=0.5, label="SH0ES (73.0)")

ax3.set_xlabel("Zeit (Modified Julian Date)")
ax3.set_ylabel("Hubble-Konstante H0")
ax3.legend(loc='upper left', ncol=2)
st.pyplot(fig3)

# --- NEU: ERKLÄRUNGS-TEXT ---
st.divider()
st.markdown("""
### Über dieses Projekt
Dieses Dashboard analysiert die Expansion des Universums in Echtzeit. 
Während das Standardmodell der Kosmologie einen Korrekturfaktor für die Dunkle Energie nutzt, 
basiert die Spalte **'Elite-Daten'** auf einer rein linearen Expansionshypothese ($t = 1/H_0$).

**Warum ein höheres Weltalter?**
Sollten die Daten weiterhin einen niedrigeren $H_0$-Wert (um 63-64) bestätigen, deutet dies auf ein 
Universum hin, das ca. 15,4 Milliarden Jahre alt ist – was die Existenz extrem alter Sterne 
im frühen Universum weitaus besser erklären würde als das aktuelle Standardmodell.
""")

# --- IMPRESSUM & KONTAKT ---
st.divider() # Erzeugt eine feine Trennlinie

# Wir nutzen Spalten, damit das Impressum dezent wirkt
m_col1, m_col2 = st.columns([2, 1])

with m_col1:
    st.markdown("""
    #### Impressum & Kontakt
    **Herausgeber:** Rolf Bense  
    Achtern Wehrt Hoff 1  
    21635 Jork  
    
    **Kontakt:** 📧 rolf.bense@web.de
                """)

with m_col2:
    st.markdown("""
    #### Über die Daten
    Die Analysen basieren auf SN Ia Daten des **Vera C. Rubin Observatory**, 
    bereitgestellt durch den **Lasair Broker** (University of Edinburgh/Belfast).
    """)

st.caption("© 2026 age-of-the-universe.com | Wissenschaftliche Analyse der kosmischen Expansion.")