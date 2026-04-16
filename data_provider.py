import streamlit as st
import pandas as pd
import lasair

def fetch_lasair_data():
    try:
        token = st.secrets["LASAIR_TOKEN"]
        L = lasair.lasair_client(token, endpoint='https://lasair-lsst.lsst.ac.uk/api')
        
        selected = 'objectId, z, h0_estimate, nDiaSources, lastDiaSourceMjdTai'
        tables = 'objects'
        # Wir lassen die h0-Bedingung weg, um zu sehen, ob ÜBERHAUPT Daten kommen
        conditions = "ORDER BY lastDiaSourceMjdTai DESC"
        
        results = L.query(selected, tables, conditions, limit=2000)
        
        if results:
            df = pd.DataFrame([r['doc'] if 'doc' in r else r for r in results])
            df.columns = [c.lower() for c in df.columns]
            return df
            
    except Exception as e:
        st.error(f"Kritischer API-Fehler: {e}")
        st.stop() # Die App hält hier an, damit wir den Fehler lesen können
    
    return pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv').rename(columns=str.lower)