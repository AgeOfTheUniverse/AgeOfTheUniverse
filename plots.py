import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime, timedelta

def plot_h0_distribution(df_elite, h0_median):
    fig, ax = plt.subplots()
    sns.histplot(df_elite['h0_estimate'], kde=True, ax=ax, color="skyblue", element="step")
    
    ax.axvline(h0_median, color="orange", linewidth=3, label=f"Your Median: {h0_median:.1f}")
    ax.axvline(67.4, color="gray", linestyle="--", linewidth=1.5, label="Planck (67.4)")
    ax.axvline(73.0, color="red", linestyle=":", linewidth=1.5, label="SH0ES (73.0)")
    
    ax.set_title("H₀ Distribution (Elite Selection)")
    ax.set_xlabel("H₀ (km/s/Mpc)")
    ax.set_ylabel("Count")
    ax.legend()
    return fig

def plot_h0_redshift(df_filtered, col_n, h0_median):
    fig, ax = plt.subplots()
    scatter = ax.scatter(df_filtered['z'], df_filtered['h0_estimate'], 
                         alpha=0.5, c=df_filtered[col_n], cmap='viridis')
    
    ax.axhline(h0_median, color="orange", linewidth=2, label=f"Median: {h0_median:.1f}")
    ax.set_xlabel("Redshift (z)")
    ax.set_ylabel("H₀ (km/s/Mpc)")
    ax.set_title("H₀ vs. Redshift")
    plt.colorbar(scatter, label="Data Quality (nDiaSources)")
    return fig

def plot_convergence(df_k, time_col):
    fig, ax = plt.subplots(figsize=(10, 4))
    
    def mjd_to_datetime(mjd):
        return datetime(1858, 11, 17) + timedelta(days=float(mjd))
    
    plot_dates = [mjd_to_datetime(x) for x in df_k[time_col]]
    
    ax.plot(plot_dates, df_k['running_median'], color='purple', linewidth=2.5, label="Rolling Median")
    ax.fill_between(plot_dates, df_k['running_median'] - df_k['stderr'], 
                     df_k['running_median'] + df_k['stderr'], alpha=0.15, color='purple')
    
    ax.axhline(67.4, color="gray", linestyle="--", label="Planck (67.4)")
    ax.axhline(73.0, color="red", linestyle=":", label="SH0ES (73.0)")
    
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    
    ax.set_title("Chronological Convergence")
    ax.set_ylabel("H₀ (km/s/Mpc)")
    ax.legend(loc="upper left")
    return fig

def plot_discovery_stats(df_raw):
    """Shows the cumulative growth of discovered objects."""
    fig, ax = plt.subplots(figsize=(10, 4)) # Etwas höher für bessere Lesbarkeit
    
    # Identify time column
    time_col = next((c for c in df_raw.columns if c.lower() == 'lastdiasourcemjdtai'), None)
    
    if time_col and not df_raw.empty:
        # Sort data by time
        df_sorted = df_raw.sort_values(time_col)
        # Create cumulative count
        df_sorted['cumulative_count'] = range(1, len(df_sorted) + 1)
        
        # Convert MJD to datetime
        plot_dates = [datetime(1858, 11, 17) + timedelta(days=float(x)) for x in df_sorted[time_col]]
        
        ax.plot(plot_dates, df_sorted['cumulative_count'], color='#1f77b4', linewidth=2, label="Confirmed SN Ia")
        ax.fill_between(plot_dates, df_sorted['cumulative_count'], alpha=0.2, color='#1f77b4')
        
        # Formatting
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
        fig.autofmt_xdate()
        
        ax.set_title("Cumulative Discoveries over Time", fontsize=12)
        ax.set_ylabel("Total Count")
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig