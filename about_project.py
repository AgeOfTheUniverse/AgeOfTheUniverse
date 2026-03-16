import streamlit as st

def render_about_project():
    st.header("About the Project")
    
    # Section 1: The Telescope
    st.subheader("1. The Vera C. Rubin Observatory")
    st.write("""
    The data for this analysis is provided by the **Vera C. Rubin Observatory** (formerly known as LSST) 
    via the **Lasair** broker. Located on the Cerro Pachón ridge in North-Central Chile, this observatory 
    features a 8.4-meter primary mirror and the largest digital camera ever constructed for astronomy. 
    It is designed to conduct a deep, 10-year survey of the southern sky.
    """)

    # Section 2: Data Provided
    st.subheader("2. Data Streams & Type Ia Supernovae")
    st.write("""
    The telescope provides real-time alerts of transient events. For this project, we focus on 
    **Type Ia Supernovae (SN Ia)**. These events are "Standard Candles" because their intrinsic 
    brightness is remarkably consistent. 
    
    The API provides us with:
    * **Redshift (z):** How much the light is stretched by the expansion of space.
    * **Apparent Magnitude:** How bright the supernova appears from Earth.
    * **nDiaSources:** A quality indicator representing the number of detections.
    """)

    # Section 3: Calculations
    st.subheader("3. Calculating $H_0$ and the Age of the Universe")
    
    st.markdown("""
    **Step A: Determining the Hubble Constant ($H_0$)** We use the distance-redshift relation. By comparing the known intrinsic brightness of a SN Ia 
    with its observed brightness, we calculate the **Luminosity Distance ($D_L$)**. 
    The Hubble Constant is then derived via:
    $$H_0 \\approx \\frac{c \\cdot z}{D_L}$$
    *(where $c$ is the speed of light).*

    **Step B: Estimating the Age of the Universe ($t_0$)** The age is inversely proportional to $H_0$. However, the expansion rate changes over time 
    due to Dark Matter and Dark Energy. We apply a correction factor (typically $\\approx 0.96$ 
    for a flat $\Lambda$CDM model):
    $$t_0 = f \\cdot \\frac{1}{H_0}$$
    With $H_0$ in km/s/Mpc, the result is converted into billions of years.
    """)
    
    st.info("Note: This dashboard updates automatically as new SN Ia candidates are confirmed by the Rubin survey.")