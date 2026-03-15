import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def plot_h0_distribution(df_elite, h0_median):
    fig, ax = plt.subplots()
    sns.histplot(df_elite['h0_estimate'], kde=True, ax=ax, color="skyblue")
    ax.axvline(h0_median, color="orange", linewidth=2, label=f"Median: {h0_median:.1f}")
    ax.set_title("H₀ Verteilung (Elite)")
    ax.legend()
    return fig

def plot_h0_redshift(df_filtered, col_n):
    fig, ax = plt.subplots()
    scatter = ax.scatter(df_filtered['z'], df_filtered['h0_estimate'], alpha=0.4, c=df_filtered[col_n], cmap='viridis')
    ax.set_xlabel("Rotverschiebung (z)")
    ax.set_ylabel("H₀")
    plt.colorbar(scatter, label="Datenqualität")
    return fig

def plot_convergence(df_k, time_col):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_k[time_col], df_k['running_median'], color='purple', linewidth=2)
    ax.fill_between(df_k[time_col], df_k['running_median'] - df_k['stderr'], 
                     df_k['running_median'] + df_k['stderr'], alpha=0.2, color='purple')
    ax.axhline(67.4, color='red', linestyle='--', alpha=0.5, label="Planck")
    ax.axhline(73.0, color='green', linestyle='--', alpha=0.5, label="SH0ES")
    ax.set_title("Chronologische Konvergenz")
    ax.legend()
    return fig