import streamlit as st
import pandas as pd
import lasair

@st.cache_data(ttl=3600)
def fetch_lasair_data():
    """Holt Live-Daten von Lasair und bereitet sie sicher auf."""
    try:
        if "LASAIR_TOKEN" not in st.secrets:
            st.error("LASAIR_TOKEN not found in secrets!")
            return pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv').rename(columns=str.lower)

        token = st.secrets["LASAIR_TOKEN"]
        L = lasair.lasair_client(token, endpoint='https://lasair-lsst.lsst.ac.uk/api')
        
        selected = 'objectId, z, h0_estimate, nDiaSources, lastDiaSourceMjdTai'
        tables = 'objects'
        # Wir laden 2000 Objekte, um die Entdeckungshistorie aktuell zu halten
        conditions = "ORDER BY lastDiaSourceMjdTai DESC"
        
        results = L.query(selected, tables, conditions, limit=2000)
        
        if results:
            df = pd.DataFrame([r['doc'] if 'doc' in r else r for r in results])
            # WICHTIG: Alle Spaltennamen sicher in kleingeschriebene Strings wandeln
            df.columns = [str(c).lower() for c in df.columns]
            return df
            
    except Exception as e:
        st.sidebar.warning(f"Live-API connection issue: {e}")
    
    # Sicherheits-Backup, falls die API streikt
    try:
        df_backup = pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv')
        df_backup.columns = [str(c).lower() for c in df_backup.columns]
        return df_backup
    except:
        return pd.DataFrame() # Letzter Ausweg: leerer DataFrame