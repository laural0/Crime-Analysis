import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
import io
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ======================= Incarcare date =======================
st.markdown('<h1 class="custom-title">Crimes in Europe</h1>', unsafe_allow_html=True)

merged_df = pd.read_csv("result/merged_final.csv")
crime_df = pd.read_csv("initialData/estat_crim_off_cat_en.csv")
pris_df = pd.read_csv("initialData/estat_crim_pris_off_en.csv")

st.header("Crimes Dataset Preview:")
st.dataframe(crime_df.head())

st.header("Prisoners Dataset Preview:")
st.dataframe(pris_df.head())


st.header("Final Dataset Preview:")
st.dataframe(merged_df.head())

st.header("JSON:")
df_json = merged_df[:3].to_json(orient='records')
st.json(df_json)

# ======================= Sidebar =======================
selected_year = st.sidebar.slider("Select Year",
                                  int(crime_df["TIME_PERIOD"].min()),
                                  int(crime_df["TIME_PERIOD"].max()),
                                  step=1)

filtered_data = crime_df[crime_df["TIME_PERIOD"] == selected_year]

# ======================= Bar chart stacked pe tipuri de infractiuni =======================
color_mapping = {
    "Acts against computer systems": "#E57373",
    "Bribery": "#FFB74D",
    "Attempted intentional homicide": "#4DB6AC",
    "Intentional homicide": "#1E88E5",
    "Kidnapping": "#81C784",
    "Robbery": "#DCE775",
    "Rape": "#9575CD",
    "Sexual assault": "#F06292",
    "Sexual violence": "#BA68C8",
    "Unlawful acts involving controlled drugs or precursors": "#8D6E63",
    "Burglary of private residential premises": "#FF8A65",
    "Burglary": "#A1887F",
    "Serious assault": "#64B5F6",
    "Theft": "#7986CB",
    "Fraud": "#4DB6AC",
    "Corruption": "#AED581",
    "Theft of a motorized vehicle or parts thereof": "#FDD835",
    "Sexual exploitation": "#FF7043",
    "Money laundering": "#BDBDBD",
    "Participation in an organized criminal group": "#90A4AE",
    "Child pornography": "#FFD54F"
}

fig = px.bar(filtered_data,
             x="geo",
             y="OBS_VALUE",
             color="iccs",
             barmode="stack",
             labels={"geo": "Countries", "OBS_VALUE": "Offences per 1000 inhabitants"},
             title=f"Crime Data for European Countries {selected_year}",
             color_discrete_map=color_mapping)

fig.update_layout(xaxis_tickangle=-45,
                  legend_title="Types of Offences",
                  height=700,
                  width=1200)
st.plotly_chart(fig)

# ======================= Pie Chart =======================
st.header("Crime Distribution in Europe")

crime_pie = filtered_data.groupby("iccs")["OBS_VALUE"].sum().reset_index()
fig_pie = px.pie(crime_pie,
                 names="iccs",
                 values="OBS_VALUE",
                 title=f"Crime Type Distribution in {selected_year}",
                 color="iccs",
                 color_discrete_map=color_mapping)
st.plotly_chart(fig_pie)

# ======================= Harta =======================
merged_df = merged_df[merged_df["TIME_PERIOD"] == selected_year]
shapefile_path = "external_source/gdp_map_countries/ne_110m_admin_0_countries.shp"
world = gpd.read_file(shapefile_path)
merged_geo = world.merge(merged_df, how='left', left_on='NAME', right_on='geo')

m = folium.Map(location=[20, 0], zoom_start=2)

def color_cases(cases_per_100k):
    if pd.isna(cases_per_100k):
        return 'gray'
    elif cases_per_100k < 1:
        return 'green'
    elif cases_per_100k < 5:
        return 'yellow'
    elif cases_per_100k < 10:
        return 'orange'
    else:
        return 'red'

for _, row in merged_geo.iterrows():
    geo = row['geometry']
    cases_per_100k = row['No of cases']
    folium.GeoJson(
        geo,
        style_function=lambda x, c=cases_per_100k: {
            'fillColor': color_cases(c),
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.5
        },
        tooltip=folium.Tooltip(f"<b>{row['NAME']}</b><br>{cases_per_100k} cases per 100,000 inhabitants", sticky=True)
    ).add_to(m)

map_html = io.BytesIO()
m.save(map_html, close_file=False)
map_html.seek(0)
st.components.v1.html(map_html.getvalue().decode(), height=600)

# ======================= Criminalitate medie pe tara =======================
merged_df2 = pd.read_csv("result/merged_final.csv")

st.header("Rata medie a criminalității pe țară")
crime_mean_by_country = merged_df2.groupby("geo")["No of cases"].mean().reset_index()
crime_mean_by_country.columns = ["Country", "Average crime rate"]
crime_mean_by_country = crime_mean_by_country.sort_values(by="Average crime rate", ascending=False)

fig_bar = px.bar(crime_mean_by_country,
                 x="Country",
                 y="Average crime rate",
                 title="Rata medie a criminalității pe țară (2008–2022)",
                 labels={"Average crime rate": "Cazuri la 100.000 locuitori"},
                 height=600)
fig_bar.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_bar)

# ======================= Raport F/M =======================
st.header("Raport femei/bărbați în închisoare pe țară")
gender_ratio_by_country = merged_df2.groupby("geo")["f_to_m_ratio"].mean().reset_index()
gender_ratio_by_country = gender_ratio_by_country.sort_values(by="f_to_m_ratio", ascending=False)

fig_ratio = px.bar(gender_ratio_by_country,
                   x="geo",
                   y="f_to_m_ratio",
                   title="Raport mediu femei/bărbați în închisoare pe țară (2008–2022)",
                   labels={"f_to_m_ratio": "Raport F/M mediu", "geo": "Țară"},
                   color_discrete_sequence=["orchid"],
                   height=600)
fig_ratio.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_ratio)

# ======================= Evolutie incarcerari in timp =======================
st.header("Evoluția ratelor de încarcerare în timp")
incarceration_trend = merged_df2.groupby("TIME_PERIOD")[["female_prisoners", "male_prisoners"]].mean().reset_index()
fig_trend = px.line(incarceration_trend,
                    x="TIME_PERIOD",
                    y=["female_prisoners", "male_prisoners"],
                    title="Evoluția medie anuală a încarcerării (per 100.000 locuitori)",
                    labels={"value": "Rată", "TIME_PERIOD": "An", "variable": "Sex"},
                    markers=True)
st.plotly_chart(fig_trend)


# ======================= Clusterizare KMeans =======================
cluster_df = merged_df2[["geo", "No of cases", "male_prisoners", "female_prisoners"]].copy()
cluster_df = cluster_df.groupby("geo").mean().reset_index()

features = cluster_df[["No of cases", "male_prisoners", "female_prisoners"]]

scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

kmeans = KMeans(n_clusters=3, random_state=42)
cluster_df["cluster"] = kmeans.fit_predict(scaled_features)

st.header("Clusterizare țări după criminalitate și încarcerare")

fig = px.scatter_3d(
    cluster_df,
    x="No of cases",
    y="male_prisoners",
    z="female_prisoners",
    color="cluster",
    text="geo",
    title="Gruparea țărilor în 3 clustere",
    labels={
        "No of cases": "Rata criminalității",
        "male_prisoners": "Prizonieri bărbați",
        "female_prisoners": "Prizonieri femei"
    }
)

fig.update_traces(marker=dict(size=6))
st.plotly_chart(fig)

for c in sorted(cluster_df["cluster"].unique()):
    countries = cluster_df[cluster_df["cluster"] == c]["geo"].tolist()
    st.write(f"**Cluster {c}** ({len(countries)} țări):", ", ".join(countries))