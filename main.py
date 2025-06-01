import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from helper_modules import *
import numpy as np
import math
import geopandas as gpd
from sklearn.preprocessing import LabelEncoder

# Curatare date

pris_df = pd.read_csv("initialData/estat_crim_pris_off_en.csv")
pris_df = (pris_df.drop(
    columns=["STRUCTURE", "STRUCTURE_NAME", "STRUCTURE_ID", "iccs", "Time", "geo", "Observation value", "OBS_FLAG",
             "Observation status (Flag) V2 structure", "CONF_STATUS", "unit",
             "Confidentiality status (flag)", "freq", "Sex"])
           .rename(columns={"International classification of crime for statistical purposes (ICCS)": "iccs",
                            "Geopolitical entity (reporting)": "geo", "Unit of measure": "unit",
                            "Time frequency": "freq"})
           .set_index("iccs"))

pris_df = pris_df[pris_df["sex"] != "T"]
pris_df = pris_df[pris_df["unit"] == "Per hundred thousand inhabitants"]

crime_df = pd.read_csv("initialData/estat_crim_off_cat_en.csv")
crime_df = crime_df.drop(columns=["DATAFLOW", "OBS_FLAG", "CONF_STATUS"]).set_index("iccs")
crime_df = crime_df[crime_df["unit"] == "Per hundred thousand inhabitants"]

pris_df.to_csv("cleanedData/estat_crim_pris_off_en_cleaned.csv")
crime_df.to_csv("cleanedData/estat_crim_off_cat_en_cleaned.csv")


# Merge fisiere

crime_df.rename(columns={"OBS_VALUE": "No of cases"}, inplace=True)
pris_df.rename(columns={"OBS_VALUE": "Male/Female prisoners"}, inplace=True)

merged_df = pris_df.merge(crime_df, on=['iccs', 'geo', 'TIME_PERIOD', 'unit'])


# obs - pentru observatii M si F, se va duplica coloana 'No of cases'
# rezolvam prin pivotare

merged_df = merged_df.pivot_table(
        index=["iccs", "geo", "TIME_PERIOD", "No of cases"],
        columns="sex",
        values="Male/Female prisoners"
    )

merged_df.columns.name = None
merged_df.rename(columns={"F": "female_prisoners", "M": "male_prisoners"}, inplace=True)
merged_df.to_csv("merged.csv")


# Encodare variabile categorice
merged_df = pd.read_csv("merged.csv")


le_geo = LabelEncoder()
merged_df['geo_encoded'] = le_geo.fit_transform(merged_df['geo'])

le_iccs = LabelEncoder()
merged_df['iccs_encoded'] = le_iccs.fit_transform(merged_df['iccs'])

merged_df.set_index('iccs')


# Tratare valori lipsa


print(merged_df.info())  # 5 valori nule

merged_df['female_prisoners'] = merged_df.groupby(['geo', 'iccs'])['female_prisoners'].transform(
    lambda x: x.fillna(x.median()))


# -------ANALIZA

# Salvare coloane numerice

numerical_cols = merged_df.select_dtypes(include=[np.float64]).columns

# Histograma distributii inainte de IQR

n_cols = 3
n_rows = math.ceil(len(numerical_cols) / n_cols)
plt.figure(figsize=(6 * n_cols, 4 * n_rows))
for i, col in enumerate(numerical_cols):
    plt.subplot(n_rows, n_cols, i + 1)
    plt.hist(merged_df[col], bins=30, edgecolor='black', color='skyblue')
    plt.title(f'Distributia: {col}')
    plt.xlabel(col)
    plt.ylabel('Frecventa')
plt.tight_layout()
plt.show()

# Boxplot inainte de IQR

plt.figure(figsize=(10, 5))
for i, col in enumerate(['No of cases', 'female_prisoners', 'male_prisoners']):
    plt.subplot(1, 3, i + 1)
    sns.boxplot(x=merged_df[col])
    plt.title(col)
plt.suptitle("Boxplots")
plt.tight_layout()
plt.show()


# Eliminare outliers (IQR)

def remove_outliers_iqr(df, col):
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return df[(df[col] >= lower) & (df[col] <= upper)]

# Aplicam IQR

for col in ['No of cases', 'female_prisoners', 'male_prisoners']:
    merged_df = remove_outliers_iqr(merged_df, col)


# Histograma distributii dupa IQR

n_cols = 3
n_rows = math.ceil(len(numerical_cols) / n_cols)
plt.figure(figsize=(6 * n_cols, 4 * n_rows))
for i, col in enumerate(numerical_cols):
    plt.subplot(n_rows, n_cols, i + 1)
    plt.hist(merged_df[col], bins=30, edgecolor='black', color='skyblue')
    plt.title(f'Distributia: {col} dupa IQR')
    plt.xlabel(col)
    plt.ylabel('Frecventa')
plt.tight_layout()
plt.show()


# Boxplot dupa IQR

plt.figure(figsize=(10, 5))
for i, col in enumerate(['No of cases', 'female_prisoners', 'male_prisoners']):
    plt.subplot(1, 3, i + 1)
    sns.boxplot(x=merged_df[col])
    plt.title(col)
plt.suptitle("Boxplots dupa IQR")
plt.tight_layout()
plt.show()



# Media infractiunilor pe tara

crime_mean_by_country = merged_df.groupby("geo")["No of cases"].mean().reset_index()
crime_mean_by_country.columns = ["Country", "Average crime rate"]
crime_mean_by_country = crime_mean_by_country.sort_values(by="Average crime rate", ascending=False)



# Bar chart pentru rata medie a criminalitatii
plt.figure(figsize=(16, 8))
plt.bar(crime_mean_by_country["Country"], crime_mean_by_country["Average crime rate"],
        color='skyblue', edgecolor='black')
plt.title("Rata medie a criminalitatii pe tara")
plt.xlabel("Tara")
plt.ylabel("Cazuri la 100.000 locuitori")
plt.xticks(rotation=60, ha='right')
plt.tick_params(axis='x', labelsize=8)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()


# Raportul F/M la inchisoare

merged_df["f_to_m_ratio"] = merged_df["female_prisoners"] / merged_df["male_prisoners"]



# Eliminare valori nule (inf, 0, NaN)

merged_df = merged_df.replace([np.inf, -np.inf], np.nan)
merged_df = merged_df.dropna(subset=["f_to_m_ratio"])
merged_df = merged_df[merged_df["f_to_m_ratio"] > 0]


# Calcul medie raport F/M pe țară

gender_ratio_by_country = merged_df.groupby("geo")["f_to_m_ratio"].mean().reset_index()
gender_ratio_by_country = gender_ratio_by_country.sort_values(by="f_to_m_ratio", ascending=False)

print(gender_ratio_by_country)

# Bar chart raport F/M

plt.figure(figsize=(16, 8))
plt.bar(gender_ratio_by_country["geo"], gender_ratio_by_country["f_to_m_ratio"], color='orchid', edgecolor='black')
plt.title("Raportul mediu femei/barbati in inchisoare pe tara")
plt.xlabel("Tara")
plt.ylabel("Raport F/M mediu")
plt.xticks(rotation=60, ha='right')
plt.tick_params(axis='x', labelsize=8)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Salvam datasetul

merged_df.to_csv("result/merged_final.csv", index=False)
