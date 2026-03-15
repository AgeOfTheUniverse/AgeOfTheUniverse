import numpy as np
import pandas as pd

def calculate_universe_age(h0, correction_factor=1.0):
    """Berechnet Weltalter: t = (1/H0) * Umrechnung * Korrektur."""
    if h0 <= 0: return 0
    return (977.8 / h0) * correction_factor

def get_rolling_stats(df):
    """Berechnet laufende Statistiken für den Zeit-Plot."""
    # Suche Spalten unabhängig von Groß/Kleinschreibung
    time_col = next((c for c in df.columns if c.lower() == 'lastdiasourcemjdtai'), None)
    h0_col = next((c for c in df.columns if c.lower() == 'h0_estimate'), None)

    if not time_col or not h0_col:
        return df

    df_sorted = df.sort_values(time_col).copy()
    df_sorted['running_median'] = df_sorted[h0_col].expanding().median()
    df_sorted['running_std'] = df_sorted[h0_col].expanding().std()
    df_sorted['running_n'] = np.arange(1, len(df_sorted) + 1)
    df_sorted['stderr'] = df_sorted['running_std'] / np.sqrt(df_sorted['running_n'])
    return df_sorted