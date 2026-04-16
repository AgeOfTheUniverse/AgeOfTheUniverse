import streamlit as st
import pandas as pd
import lasair

def fetch_lasair_data():
    """Holt Live-Daten von Lasair mit robustem Spalten-Naming."""
    try:
        token = st.secrets["LASAIR_TOKEN"]
        L = lasair.lasair_client(token, endpoint='https://lasair-lsst.lsst.ac.uk/api')
        
        selected = 'objectId, z, h0_estimate, nDiaSources, lastDiaSourceMjdTai'
        tables = 'objects'
        # Wir laden 2000, um genug Rohdaten für die graue Linie zu haben
        conditions = "ORDER BY lastDiaSourceMjdTai DESC"
        
        results = L.query(selected, tables, conditions, limit=2000)
        
        if results:
            df = pd.DataFrame([r['doc'] if 'doc' in r else r for r in results])
            # FIX: Erst in String umwandeln, dann lower()
            df.columns = [str(c).lower() for c in df.columns]
            return df
            
    except Exception as e:
        # Nur eine kleine Warnung in der Sidebar, falls die API mal hakt
        st.sidebar.warning(f"Live-Update verzögert: {e}")
    
    # Backup laden, falls die API oder die Verarbeitung scheitert
    df_backup = pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv')
    df_backup.columns = [str(c).lower() for c in df_backup.columns]
    return df_backup