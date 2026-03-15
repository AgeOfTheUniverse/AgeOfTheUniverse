import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests  
import lasair 
from datetime import datetime

# --- 1. CONFIG (MUSS ZUERST STEHEN) ---
st.set_page_config(
    page_title="The Age of the Universe",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. DATEN-LADE-FUNKTION ---
@st.cache_data(ttl=3600)
def load_data():
    try:
        token = st.secrets["LASAIR_TOKEN"]
        L = lasair.lasair_client(token, endpoint='https://lasair-lsst.lsst.ac.uk/api')
        
        selected   = 'objectId, z, h0_estimate, nDiaSources, lastDiaSourceMjdTai'
        tables     = 'objects'
        conditions = 'h0_estimate IS NOT NULL AND z > 0'
        
        results = L.query(selected, tables, conditions, limit=1000)
        
        if results:
            if isinstance(results, list) and len(results) > 0:
                if isinstance(results[0], dict) and 'doc' in results[0]:
                    df = pd.DataFrame([r['doc'] for r in results])
                else:
                    df = pd.DataFrame(results)
                
                df.columns = [c.lower() for c in df.columns]
                valid_cols = [c for c in ['z', 'h0_estimate', 'ndiasources', 'lastdiasourcemjdtai'] if c in df.columns]
                
                if not df.empty:
                    # Wir geben im Erfolgsfall den API-DF zurück
                    return df.dropna(subset=valid_cols)
        
    except Exception as e:
        st.sidebar.warning(f"Lasair-Client Fehler: {e}")

    # Fallback auf die lokale CSV
    return pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv')

# --- 3. DATEN JETZT LADEN (Damit df_raw für die Metrics bereit ist) ---
df_raw = load_data()

# --- 4. TITEL & METRICS ---
st.title("🔭 age-of-the-universe.com")
st.markdown("### Live-Analyse der Hubble-Konstante & des Weltalters")

# Berechnung der Header-Metriken
avg_h_header = df_raw['h0_estimate'].mean()
age_header = 977.8 / avg_h_header if avg_h_header > 0 else 0

m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.metric("Objekte (Live)", len(df_raw))
with m_col2:
    st.metric("Durchschnitt H₀", f"{avg_h_header:.2f} km/s/Mpc")
with m_col3:
    st.metric("Geschätztes Weltalter", f"{age_header:.1f} Mrd. Jahre")

st.info("""
**Physikalischer Hintergrund:** Das Weltalter wird hier über die Formel $t = 1/H_0$ (Hubble-Zeit) geschätzt. 
Der Faktor **977.8** dient zur Umrechnung der Einheiten von $(km/s)/Mpc$ in Milliarden Jahre.
""")
st.divider()

# --- 5. SIDEBAR (STATUS & FILTER) ---
with st.sidebar:
    # Status-Check
    is_api = "lastdiasourcemjdtai" in df_raw.columns
    if is_api:
        st.success(f"✅ VERBUNDEN: Lasair-API")
        st.caption(f"Abgleich: {datetime.now().strftime('%H:%M:%S')}")
    else:
        st.warning("⚠️ QUELLE: Backup-CSV")
    
    st.divider()
    st.header("Filter-Einstellungen")
    z_min = st.sidebar.slider("Minimale Rotverschiebung (z)", 0.0, 0.1, 0.02, 0.01)
    h0_lim = st.sidebar.slider("H0 Bereich", 20, 150, (40, 120))
    qualitaet_prozent = st.sidebar.slider("Elite-Schwelle (Top % Qualität)", 0, 100, 50)

# Filter anwenden
df_filtered = df_raw[(df_raw['z'] > z_min) & 
                     (df_raw['h0_estimate'].between(h0_lim[0], h0_lim[1]))].copy()

if not df_filtered.empty:
    # Elite-Berechnung
    schwelle = np.percentile(df_filtered['ndiasources'], qualitaet_prozent)
    df_elite = df_filtered[df_filtered['ndiasources'] >= schwelle].copy()
    h0_elite = df_elite['h0_estimate'].median()
    h0_alle = df_filtered['h0_estimate'].median()
else:
    st.error("Keine Daten im gewählten Filterbereich!")
    st.stop()

# --- 6. VERGLEICHS-TABELLE ---
st.subheader("Vergleich der kosmologischen Modelle")
alter_planck = (977.8 / 67.4) * 0.95
alter_shoes = (977.8 / 73.0) * 0.96
alter_alle = (977.8 / h0_alle) * 0.96
alter_elite = (977.8 / h0_elite) # Lineare Hypothese

vergleich_data = {
    "Planck (CMB)": ["67.4", f"{alter_planck:.2f}"],
    "SH0ES (SN Ia)": ["73.0", f"{alter_shoes:.2f}"],
    "Alle Rubin-Daten": [f"{h0_alle:.1f}", f"{alter_alle:.2f}"],
    "Elite-Daten (Deine Wahl)": [f"{h0_elite:.1f}", f"{alter_elite:.2f}"]
}
st.table(pd.DataFrame(vergleich_data, index=["Hubble-Konstante (H0)", "Weltalter (Mrd. Jahre)"]))

# --- 7. GRAFIKEN ---
g_col1, g_col2 = st.columns(2)

with g_col1:
    st.write("### Elite-Verteilung (H0)")
    fig1, ax1 = plt.subplots()
    sns.histplot(df_elite['h0_estimate'], bins=10, kde=True, ax=ax1, color='skyblue')
    ax1.axvline(h0_elite, color='gold', linewidth=3, label=f"Median: {h0_elite:.1f}")
    ax1.legend()
    st.pyplot(fig1)

with g_col2:
    st.write("### H0 vs. Rotverschiebung (Elite-Trend)")
    fig2, ax2 = plt.subplots()
    ax2.scatter(df_filtered['z'], df_filtered['h0_estimate'], c=df_filtered['ndiasources'], alpha=0.5)
    if len(df_elite) > 1:
        m, b = np.polyfit(df_elite['z'], df_elite['h0_estimate'], 1)
        ax2.plot(df_filtered['z'], m*df_filtered['z'] + b, color='orange', label="Elite-Trend")
    ax2.legend()
    st.pyplot(fig2)

# --- 8. CHRONOLOGISCHE STABILISIERUNG ---
st.write("### Chronologische Stabilisierung (Konvergenz)")
df_konv = df_filtered.sort_values('lastdiasourcemjdtai').copy()
df_konv['running_median'] = df_konv['h0_estimate'].expanding().median()
df_konv['running_std'] = df_konv['h0_estimate'].expanding().std()
df_konv['running_n'] = np.arange(1, len(df_konv) + 1)
df_konv['stderr'] = df_konv['running_std'] / np.sqrt(df_konv['running_n'])

fig3, ax3 = plt.subplots(figsize=(12, 4))
ax3.plot(df_konv['lastdiasourcemjdtai'], df_konv['running_median'], color='purple', linewidth=3, label="Laufender Median")
ax3.fill_between(df_konv['lastdiasourcemjdtai'], 
                 df_konv['running_median'] - df_konv['stderr'], 
                 df_konv['running_median'] + df_konv['stderr'], 
                 color='purple', alpha=0.2, label="Fehlerbereich")

ax3.axhline(67.4, color='red', linestyle='--', alpha=0.5, label="Planck")
ax3.axhline(73.0, color='green', linestyle='--', alpha=0.5, label="SH0ES")
ax3.set_xlabel("Zeit (MJD)")
ax3.set_ylabel("H0")
ax3.legend(loc='upper left', ncol=3)
st.pyplot(fig3)

# --- 9. IMPRESSUM ---
st.divider()
imp_col1, imp_col2 = st.columns([2, 1])
with imp_col1:
    st.markdown("""
    #### Impressum & Kontakt
    **Herausgeber:** Rolf Bense | Achtern Wehrt Hoff 1 | 21635 Jork  
    📧 rolf.bense@web.de
    """)
with imp_col2:
    st.caption("© 2026 age-of-the-universe.com | Daten via Vera C. Rubin Observatory & Lasair Broker")