import streamlit as st
import pandas as pd
import lasair

def fetch_lasair_data():
    """Test-Version ohne Backup, um Fehler zu erzwingen."""
    try:
        # 1. Prüfen, ob das Secret überhaupt da ist
        if "LASAIR_TOKEN" not in st.secrets:
            st.error("FEHLER: LASAIR_TOKEN fehlt in den Streamlit Secrets!")
            st.stop()

        token = st.secrets["LASAIR_TOKEN"]
        L = lasair.lasair_client(token, endpoint='https://lasair-lsst.lsst.ac.uk/api')
        
        # 2. Eine absolut minimalistische Abfrage
        selected = 'objectId, z, h0_estimate, nDiaSources, lastDiaSourceMjdTai'
        tables = 'objects'
        # Keine Conditions, kein Order By - nur purer Datenabruf
        results = L.query(selected, tables, "", limit=500)
        
        if results and len(results) > 0:
            df = pd.DataFrame([r['doc'] if 'doc' in r else r for r in results])
            df.columns = [c.lower() for c in df.columns]
            return df
        else:
            st.warning("API verbunden, aber Ergebnisliste ist leer.")
            st.stop()
            
    except Exception as e:
        # Wir geben den Fehler groß im Hauptfenster aus, nicht in der Sidebar
        st.error(f"🚨 KRITISCHER API-FEHLER: {e}")
        st.info("Hinweis: Das Backup wurde deaktiviert, um diesen Fehler zu finden.")
        st.stop()

    # Das Backup ist vorübergehend deaktiviert!
    # return pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv')