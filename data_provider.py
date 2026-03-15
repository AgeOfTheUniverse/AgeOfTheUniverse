import streamlit as st
import pandas as pd
import lasair

def fetch_lasair_data():
    """Holt Daten von Lasair oder nutzt Backup-CSV."""
    try:
        token = st.secrets["LASAIR_TOKEN"]
        L = lasair.lasair_client(token, endpoint='https://lasair-lsst.lsst.ac.uk/api')
        
        selected = 'objectId, z, h0_estimate, nDiaSources, lastDiaSourceMjdTai'
        tables = 'objects'
        conditions = ''
        
        results = L.query(selected, tables, conditions, limit=1000)
        
        if results and isinstance(results, list):
            if len(results) > 0 and isinstance(results[0], dict) and 'doc' in results[0]:
                df = pd.DataFrame([r['doc'] for r in results])
            else:
                df = pd.DataFrame(results)
            
            # WICHTIG: Alles auf klein für die Konsistenz
            df.columns = [c.lower() for c in df.columns]
            return df#.dropna(subset=['h0_estimate', 'z'])
            
    except Exception as e:
        st.sidebar.warning(f"API-Fehler: {e}")
    
    # Backup laden falls API scheitert
    df_backup = pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv')
    df_backup.columns = [c.lower() for c in df_backup.columns]
    return df_backup