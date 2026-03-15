import numpy as np
import pandas as pd

def calculate_universe_age(h0, correction_factor=1.0):
    """Berechnet das Weltalter basierend auf H0."""
    if h0 <= 0: return 0
    # 977.8 ist der Umrechnungsfaktor zu Mrd. Jahren
    return (977.8 / h0) * correction_factor

def get_rolling_stats(df):
    """Berechnet den laufenden Median und den statistischen Fehler."""
    # WICHTIG: Die Spalte muss hier kleingeschrieben sein
    col_time = 'lastdiasourcemjdtai' 
    
    if col_time not in df.columns:
        # Falls die Spalte doch großgeschrieben ist, hier abfangen
        available = [c for c in df.columns if c.lower() == col_time]
        if available:
            col_time = available[0]
        else:
            return df # Sicherheits-Fallback, falls Spalte fehlt

    df_sorted = df.sort_values(col_time).copy()
    df_sorted['running_median'] = df_sorted['h0_estimate'].expanding().median()
    df_sorted['running_std'] = df_sorted['h0_estimate'].expanding().std()
    df_sorted['running_n'] = np.arange(1, len(df_sorted) + 1)
    df_sorted['stderr'] = df_sorted['running_std'] / np.sqrt(df_sorted['running_n'])
    return df_sorted

def apply_filters(df, z_min, h0_range):
    return df[(df['z'] > z_min) & (df['h0_estimate'].between(h0_range[0], h0_range[1]))].copy()

def get_elite_data(df, percentile):
    if df.empty: return df, 0, 0
    # Nutze kleingeschriebene Spaltennamen aus deinem data_provider
    col = 'ndiasources' if 'ndiasources' in df.columns else 'nDiaSources'
    schwelle = np.percentile(df[col], percentile)
    df_elite = df[df[col] >= schwelle].copy()
    return df_elite, df_elite['h0_estimate'].median(), df['h0_estimate'].median()