import streamlit as st
import pandas as pd
import lasair

def fetch_lasair_data():
    try:
        token = st.secrets["LASAIR_TOKEN"]
        L = lasair.lasair_client(token, endpoint='https://lasair-lsst.lsst.ac.uk/api')
        
        # Wir versuchen es ohne Filter und mit einer sehr großen Zahl, 
        # um zu sehen, ob überhaupt neuere Objekte existieren
        selected = 'objectId, z, h0_estimate, nDiaSources, lastDiaSourceMjdTai'
        tables = 'objects'
        # Wir entfernen h0_estimate > 0 erst mal, um zu sehen ob ÜBERHAUPT neue SN da sind
        conditions = "ORDER BY lastDiaSourceMjdTai DESC"
        
        results = L.query(selected, tables, conditions, limit=2000)
        
        if results:
            df = pd.DataFrame([r['doc'] if 'doc' in r else r for r in results])
            df.columns = [c.lower() for c in df.columns]
            
            # Diagnose-Ausgabe nur für dich in der Sidebar (kannst du später löschen)
            latest_mjd = df['lastdiasourcemjdtai'].max()
            st.sidebar.write(f"Raw Max MJD: {latest_mjd}") 
            
            return df
            
    except Exception as e:
        st.sidebar.warning(f"API-Fehler: {e}")
    
    return pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv').rename(columns=str.lower)