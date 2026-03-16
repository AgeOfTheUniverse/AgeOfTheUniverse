import streamlit as st

def render_about_project():
    st.title("Science & Methodology")
    
    # Section 1: The Hardware
    st.subheader("1. The Vera C. Rubin Observatory")
    st.write("""
    The data for this analysis is provided by the **Vera C. Rubin Observatory** (formerly known as LSST) 
    via the **Lasair** broker. Located on the Cerro Pachón ridge in North-Central Chile, this observatory 
    features a 8.4-meter primary mirror and the largest digital camera ever constructed for astronomy. 
    It is designed to conduct a deep, 10-year survey of the southern sky.
    """)

    # Section 2: The Data
    st.subheader("2. Data Streams & Standard Candles")
    st.write("""
    The telescope provides real-time alerts of transient events. For this project, we focus on 
    **Type Ia Supernovae (SN Ia)**. These events are "Standard Candles" because their intrinsic 
    brightness is remarkably consistent. 
    
    The API provides us with:
    * **Redshift (z):** How much the light is stretched by the expansion of space.
    * **Apparent Magnitude:** How bright the supernova appears from Earth.
    * **nDiaSources:** A quality indicator representing the number of detections.
    """)

    # Section 3: The Math (Hier sind die Ergänzungen eingeflossen)
    st.subheader("3. Calculating $H_0$ and the Age of the Universe")
    
    st.markdown("""
    **Step A: Determining the Hubble Constant ($H_0$)** We use the distance-redshift relation. By comparing the known intrinsic brightness of a SN Ia 
    with its observed brightness, we calculate the **Luminosity Distance ($D_L$)**. 
    The Hubble Constant is derived via Hubble's Law:
    $$v = H_0 \cdot d$$
    In this app, we approximate the velocity ($v$) from the Redshift ($z$) and use the distance ($d$) 
    from the supernova's light curve:
    $$H_0 \\approx \\frac{c \\cdot z}{D_L}$$
    *(where $c$ is the speed of light).*

    **Step B: Estimating the Age of the Universe ($t_0$)** The age is fundamentally related to the inverse of the Hubble Constant, known as the **Hubble Time**:
    $$t_H = \\frac{1}{H_0}$$
    However, because the expansion rate changes over time due to **Dark Matter** and **Dark Energy**, 
    we apply a correction factor ($f \approx 0.96$ for a flat $\Lambda$CDM model) to determine the 
    actual age:
    $$t_0 = f \\cdot \\frac{1}{H_0}$$
    """)

    st.divider()

    # Section 4: Technical Selection (Neu hinzugefügt für mehr Transparenz)
    st.subheader("4. Technical Selection & Quality")
    st.write("""
    To ensure scientific accuracy, this dashboard updates automatically and allows you to filter 
    the data:
    * **Redshift Filter:** Minimizes "peculiar velocity" noise from galaxies too close to us.
    * **Elite Selection:** Focuses on the top-tier percentile of data quality (nDiaSources) 
      to provide a more stable median.
    """)
    
    st.info("The benchmarks for Planck (67.4) and SH0ES (73.0) represent the 'Hubble Tension' – "
            "one of the most exciting mysteries in modern cosmology.")