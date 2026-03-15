import numpy as np

def calculate_universe_age(h0, correction_factor=1.0):
    """Berechnet das Weltalter basierend auf H0."""
    if h0 <= 0: return 0
    # 977.8 ist der Umrechnungsfaktor zu Mrd. Jahren
    return (977.8 / h0) * correction_factor

def get_rolling_stats(df):
    """Berechnet laufenden Median und Fehler für die Zeitreihe."""
    df_sorted = df.sort_values('lastdiasourcemjdtai').copy()
    df_sorted['running_median'] = df_sorted['h0_estimate'].expanding().median()
    df_sorted['running_std'] = df_sorted['h0_estimate'].expanding().std()
    df_sorted['running_n'] = np.arange(1, len(df_sorted) + 1)
    df_sorted['stderr'] = df_sorted['running_std'] / np.sqrt(df_sorted['running_n'])
    return df_sorted