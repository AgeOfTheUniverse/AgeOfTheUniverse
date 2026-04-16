import streamlit as st
import pandas as pd
import lasair

def fetch_lasair_data():
    """Holt die aktuellsten Daten von Lasair."""
    try:
        token = st.secrets["LASAIR_TOKEN"]
        L = lasair.lasair_client(token, endpoint='https://lasair-lsst.lsst.ac.uk/api')
        
        # 1. Spalten definieren
        selected = 'objectId, z, h0_estimate, nDiaSources, lastDiaSourceMjdTai'
        tables = 'objects'
        
        # 2. Bedingungen: Nur Objekte mit Daten und Sortierung nach Datum (DESC = Absteigend)
        # Wir fragen die neuesten 1000 Objekte ab, die einen H0-Wert haben
        conditions = "h0_estimate > 0 AND z > 0 ORDER BY lastDiaSourceMjdTai DESC"
        
        results = L.query(selected, tables, conditions, limit=1000)
        
        if results and isinstance(results, list):
            if len(results) > 0 and isinstance(results[0], dict) and 'doc' in results[0]:
                df = pd.DataFrame([r['doc'] for r in results])
            else:
                df = pd.DataFrame(results)
            
            df.columns = [c.lower() for c in df.columns]
            return df
            
    except Exception as e:
        st.sidebar.warning(f"API-Fehler: {e}")
    
    # Backup laden falls API scheitert
    df_backup = pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv')
    df_backup.columns = [c.lower() for c in df_backup.columns]
    return df_backup