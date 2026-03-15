import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def plot_h0_distribution(df_elite, h0_median):
    """Histogramm der H0-Werte mit Referenzlinien."""
    fig, ax = plt.subplots()
    sns.histplot(df_elite['h0_estimate'], kde=True, ax=ax, color="skyblue", element="step")
    
    # Referenzlinien
    ax.axvline(h0_median, color="orange", linewidth=3, label=f"Dein Median: {h0_median:.1f}")
    ax.axvline(67.4, color="gray", linestyle="--", linewidth=1.5, label="Planck (67.4)")
    ax.axvline(73.0, color="red", linestyle=":", linewidth=1.5, label="SH0ES (73.0)")
    
    ax.set_title("H₀ Verteilung (Elite-Auswahl)")
    ax.set_xlabel("H₀ (km/s/Mpc)")
    ax.set_ylabel("Anzahl")
    ax.legend()
    return fig

def plot_h0_redshift(df_filtered, col_n, h0_median):
    """Scatterplot H0 vs. z mit der gewählten Median-Linie."""
    fig, ax = plt.subplots()
    scatter = ax.scatter(df_filtered['z'], df_filtered['h0_estimate'], 
                         alpha=0.5, c=df_filtered[col_n], cmap='viridis')
    
    # Horizontale Linie für deinen Median
    ax.axhline(h0_median, color="orange", linewidth=2, linestyle="-", label=f"Median: {h0_median:.1f}")
    
    ax.set_xlabel("Rotverschiebung (z)")
    ax.set_ylabel("H₀ (km/s/Mpc)")
    ax.set_title("H₀ vs. Rotverschiebung")
    plt.colorbar(scatter, label="Datenqualität (nDiaSources)")
    return fig

def plot_convergence(df_k, time_col):
    """Zeitliche Entwicklung des Rolling Median mit Unsicherheit."""
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Der Rolling Median
    ax.plot(df_k[time_col], df_k['running_median'], color='purple', linewidth=2.5, label="Rolling Median")
    ax.fill_between(df_k[time_col], df_k['running_median'] - df_k['stderr'], 
                     df_k['running_median'] + df_k['stderr'], alpha=0.15, color='purple')
    
    # Referenzlinien für den zeitlichen Vergleich
    ax.axhline(67.4, color="gray", linestyle="--", linewidth=1.5, label="Planck (67.4)")
    ax.axhline(73.0, color="red", linestyle=":", linewidth=1.5, label="SH0ES (73.0)")
    
    ax.set_title("Chronologische Konvergenz")
    ax.set_xlabel("Zeit (MJD)")
    ax.set_ylabel("H₀ (km/s/Mpc)")
    ax.legend(loc="upper left")
    return fig