import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from helper_modules import *
import numpy as np
import math
import geopandas as gpd

# ------------------------ tema 2

################## Stergem coloane irelevante/nule, le dam rename si pastram o singura unitate de masura

# pris_df = pd.read_csv("initialData/estat_crim_pris_off_en.csv")
# pris_df = (pris_df.drop(
#     columns=["STRUCTURE", "STRUCTURE_NAME", "STRUCTURE_ID", "iccs", "Time", "geo", "Observation value", "OBS_FLAG",
#              "Observation status (Flag) V2 structure", "CONF_STATUS", "unit",
#              "Confidentiality status (flag)", "freq", "Sex"])
#            .rename(columns={"International classification of crime for statistical purposes (ICCS)": "iccs",
#                             "Geopolitical entity (reporting)": "geo", "Unit of measure": "unit",
#                             "Time frequency": "freq"})
#            .set_index("iccs"))
#
# #
# pris_df = pris_df[pris_df["sex"] != "T"]
# pris_df = pris_df[pris_df["unit"] == "Per hundred thousand inhabitants"]
#
# crime_df = pd.read_csv("initialData/estat_crim_off_cat_en.csv")
# crime_df = crime_df.drop(columns=["DATAFLOW", "OBS_FLAG", "CONF_STATUS"]).set_index("iccs")
# crime_df = crime_df[crime_df["unit"] == "Per hundred thousand inhabitants"]
#
# pris_df.to_csv("estat_crim_pris_off_en_cleaned.csv")
# crime_df.to_csv("estat_crim_off_cat_en_cleaned.csv")

################## Inner merge intre fisiere

# pris_df = pd.read_csv("estat_crim_pris_off_en_cleaned.csv")
# crime_df = pd.read_csv("estat_crim_off_cat_en_cleaned.csv")
#
# crime_df.rename(columns={"OBS_VALUE": "No of cases"}, inplace=True)
# pris_df.rename(columns={"OBS_VALUE": "Male/Female prisoners"}, inplace=True)
#
# merged_df = pris_df.merge(crime_df, on=['iccs', 'geo', 'TIME_PERIOD', 'unit'])
#
# # obs - pentru observatii M si F, se va duplica coloana 'No of cases'
# # rezolvam prin pivotare
#
# merged_df = merged_df.pivot_table(
#     index=["iccs", "geo", "TIME_PERIOD", "No of cases"],
#     columns="sex",
#     values="Male/Female prisoners"
# )
#
# merged_df.columns.name = None
# merged_df.rename(columns={"F": "female_prisoners", "M": "male_prisoners"}, inplace=True)
#
# merged_df.to_csv("merged.csv")

################## Fill valori nule

merged_df = pd.read_csv("merged.csv")
print(merged_df.info())  # 5 valori nule

merged_df['female_prisoners'] = merged_df.groupby(['geo', 'iccs'])['female_prisoners'].transform(
    lambda x: x.fillna(x.median()))


################## Analizez distributia coloanelor numerice (histograma)

numerical_cols = merged_df.select_dtypes(include=[np.float64]).columns
print(numerical_cols)

n_cols = 3
n_rows = math.ceil(len(numerical_cols) / n_cols)
plt.figure(figsize=(6 * n_cols, 4 * n_rows))

for i, col in enumerate(numerical_cols):
    plt.subplot(n_rows, n_cols,
                i + 1)  # Creăm un subplot în grila de n_rows x n_cols; i+1 pentru indexarea subgraficelor începând de la 1
    plt.hist(merged_df[col], bins=30, edgecolor='black',
             color='skyblue')  # Construim histograma pentru coloana curentă, eliminând valorile lipsă
    plt.title(f'Distribuția: {col}')  # Setăm titlul graficului cu numele coloanei
    plt.xlabel(col)  # Etichetă pentru axa x, indicând numele variabilei
    plt.ylabel('Frecvență')  # Etichetă pentru axa y, indicând frecvența valorilor
plt.tight_layout()  # Ajustăm automat spațiile dintre subgrafice pentru a evita suprapunerea
plt.show()  # Afișăm figura cu histogramele

################## Analizez distributia si relatiile dintre coloanele numerice (pair plot)

plot_pairplot_numeric(merged_df, numerical_cols)

################## Analizez outlierii (boxplot)

relevant_cols = ['No of cases', 'female_prisoners', 'male_prisoners']
plt.figure(figsize=(10, 5))

for i, col in enumerate(relevant_cols):
    plt.subplot(1, len(relevant_cols), i + 1)
    sns.boxplot(x=merged_df[col])
    plt.title(f"{col}")
    plt.xlabel("")

plt.suptitle("Boxplots pentru variabilele selectate", fontsize=14)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()

