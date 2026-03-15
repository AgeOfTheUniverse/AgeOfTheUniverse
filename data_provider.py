import streamlit as st
import pandas as pd
import lasair

def fetch_lasair_data():
    """Holt Live-Daten von der Lasair-API oder nutzt Backup-CSV."""
    try:
        token = st.secrets["LASAIR_TOKEN"]
        endpoint = 'https://lasair-lsst.lsst.ac.uk/api'
        L = lasair.lasair_client(token, endpoint=endpoint)
        
        selected = 'objectId, z, h0_estimate, nDiaSources, lastDiaSourceMjdTai'
        tables = 'objects'
        conditions = 'h0_estimate IS NOT NULL AND z > 0'
        
        results = L.query(selected, tables, conditions, limit=1000)
        
        if results and isinstance(results, list):
            # Logik zum Entpacken der 'doc' Struktur
            if len(results) > 0 and 'doc' in results[0]:
                df = pd.DataFrame([r['doc'] for r in results])
            else:
                df = pd.DataFrame(results)
            
            df.columns = [c.lower() for c in df.columns]
            # Wichtige Spalten prüfen und bereinigen
            valid_cols = [c for c in ['z', 'h0_estimate', 'ndiasources', 'lastdiasourcemjdtai'] if c in df.columns]
            return df.dropna(subset=valid_cols)
            
    except Exception as e:
        st.sidebar.warning(f"API-Fehler: {e}")
    
    return pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv')