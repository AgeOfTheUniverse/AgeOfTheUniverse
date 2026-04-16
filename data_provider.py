import streamlit as st
import pandas as pd
import lasair

@st.cache_data(ttl=3600)
def fetch_lasair_data():
    """Holt Live-Daten von Lasair und bereitet sie sicher auf."""
    try:
        if "LASAIR_TOKEN" not in st.secrets:
            return load_backup_data()

        token = st.secrets["LASAIR_TOKEN"]
        L = lasair.lasair_client(token, endpoint='https://lasair-lsst.lsst.ac.uk/api')
        
        selected = 'objectId, z, h0_estimate, nDiaSources, lastDiaSourceMjdTai'
        tables = 'objects'
        conditions = "ORDER BY lastDiaSourceMjdTai DESC"
        
        results = L.query(selected, tables, conditions, limit=2000)
        
        if results:
            df = pd.DataFrame([r['doc'] if 'doc' in r else r for r in results])
            # Sicherstellen, dass alle Spaltennamen kleingeschriebene Strings sind
            df.columns = [str(c).lower() for c in df.columns]
            return df
            
    except Exception as e:
        st.sidebar.warning(f"Live-API connection issue: {e}")
    
    return load_backup_data()

def load_backup_data():
    """Hilfsfunktion zum Laden des Backups."""
    try:
        df_backup = pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv')
        df_backup.columns = [str(c).lower() for c in df_backup.columns]
        return df_backup
    except:
        return pd.DataFrame()