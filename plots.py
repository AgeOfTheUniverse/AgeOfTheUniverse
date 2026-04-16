import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime, timedelta
import pandas as pd

def plot_h0_distribution(df_elite, h0_median):
    fig, ax = plt.subplots(figsize=(8, 5))
    if not df_elite.empty:
        sns.histplot(df_elite['h0_estimate'], kde=True, ax=ax, color="skyblue", element="step")
    
    ax.axvline(h0_median, color="orange", linewidth=3, label=f"Your Median: {h0_median:.1f}")
    ax.axvline(67.4, color="gray", linestyle="--", linewidth=1.5, label="Planck (67.4)")
    ax.axvline(73.0, color="red", linestyle=":", linewidth=1.5, label="SH0ES (73.0)")
    
    ax.set_title("H₀ Distribution (Elite Selection)")
    ax.set_xlabel("H₀ (km/s/Mpc)")
    ax.legend()
    return fig

def plot_h0_redshift(df_filtered, col_n, h0_median):
    fig, ax = plt.subplots(figsize=(8, 5))
    if not df_filtered.empty:
        scatter = ax.scatter(df_filtered['z'], df_filtered['h0_estimate'], 
                             alpha=0.5, c=df_filtered[col_n], cmap='viridis')
        plt.colorbar(scatter, label="Data Quality (nDiaSources)")
    
    ax.axhline(h0_median, color="orange", linewidth=2, label=f"Median: {h0_median:.1f}")
    ax.set_xlabel("Redshift (z)")
    ax.set_ylabel("H₀ (km/s/Mpc)")
    ax.set_title("H₀ vs. Redshift")
    return fig

def plot_convergence(df_k, time_col):
    fig, ax = plt.subplots(figsize=(10, 4))
    
    def mjd_to_datetime(mjd):
        try: return datetime(1858, 11, 17) + timedelta(days=float(mjd))
        except: return datetime.now()
    
    if not df_k.empty:
        plot_dates = [mjd_to_datetime(x) for x in df_k[time_col]]
        ax.plot(plot_dates, df_k['running_median'], color='purple', linewidth=2.5, label="Rolling Median")
        if 'stderr' in df_k.columns:
            ax.fill_between(plot_dates, df_k['running_median'] - df_k['stderr'], 
                             df_k['running_median'] + df_k['stderr'], alpha=0.15, color='purple')
    
    ax.axhline(67.4, color="gray", linestyle="--", label="Planck (67.4)")
    ax.axhline(73.0, color="red", linestyle=":", label="SH0ES (73.0)")
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    ax.set_title("Chronological Convergence")
    ax.legend(loc="upper left")
    return fig

def plot_discovery_stats(df_raw):
    """Zeigt die Timeline der Entdeckungen (Rohdaten vs. Wissenschaft)."""
    fig, ax = plt.subplots(figsize=(10, 5))
    time_col = 'lastdiasourcemjdtai'
    
    if df_raw.empty or time_col not in df_raw.columns:
        ax.text(0.5, 0.5, "Waiting for data stream...", ha='center')
        return fig

    # Sortieren nach Zeit
    df_plot = df_raw.sort_values(time_col).reset_index()
    
    # 1. Graue Linie: Alle Alerts (Rohdaten)
    df_plot['all_count'] = range(1, len(df_plot) + 1)
    
    def to_date(mjd):
        return datetime(1858, 11, 17) + timedelta(days=float(mjd))
    
    dates_all = [to_date(x) for x in df_plot[time_col]]
    ax.plot(dates_all, df_plot['all_count'], label="Total Alerts (Raw)", color="gray", alpha=0.4, linestyle="--")

    # 2. Blaue Linie: Nur SN Ia (falls vorhanden)
    if 'h0_estimate' in df_plot.columns and 'z' in df_plot.columns:
        df_snia = df_plot[df_plot['h0_estimate'].notna() & (df_plot['h0_estimate'] > 0)].copy()
        if not df_snia.empty:
            df_snia['sn_count'] = range(1, len(df_snia) + 1)
            dates_sn = [to_date(x) for x in df_snia[time_col]]
            ax.plot(dates_sn, df_snia['sn_count'], label="Confirmed SN Ia", color="#1f77b4", linewidth=3)
    
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    ax.set_title("Detection Timeline")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig