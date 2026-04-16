def fetch_lasair_data():
    try:
        token = st.secrets["LASAIR_TOKEN"]
        L = lasair.lasair_client(token, endpoint='https://lasair-lsst.lsst.ac.uk/api')
        
        # Wir laden jetzt einfach die letzten 2000 Objekte, egal welcher Typ
        selected = 'objectId, z, h0_estimate, nDiaSources, lastDiaSourceMjdTai'
        tables = 'objects'
        conditions = "ORDER BY lastDiaSourceMjdTai DESC"
        
        results = L.query(selected, tables, conditions, limit=2000)
        
        if results:
            df = pd.DataFrame([r['doc'] if 'doc' in r else r for r in results])
            df.columns = [c.lower() for c in df.columns]
            return df
    except Exception as e:
        st.sidebar.error(f"API-Fehler: {e}")
    return pd.read_csv('lasair_603TypeIaSupernovae_filter_results.csv').rename(columns=str.lower)