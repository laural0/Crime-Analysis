import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
import io

crime_df = pd.read_csv("initialData/estat_crim_off_cat_en.csv")
crime_df = crime_df[crime_df["unit"] == "Per hundred thousand inhabitants"]

crime_df.drop(columns=["DATAFLOW"], inplace=True)

st.markdown('<h1 class="custom-title">Crimes in Europe</h1>', unsafe_allow_html=True)

st.header("Dataset Preview:")
st.dataframe(crime_df.head())

st.header("JSON:")
df_json = crime_df[:3].to_json(orient='records')
st.json(df_json)

selected_year = st.sidebar.slider("Select Year",
                                  int(crime_df["TIME_PERIOD"].min()),
                                  int(crime_df["TIME_PERIOD"].max()),
                                  step=1)

filtered_data = crime_df[crime_df["TIME_PERIOD"] == selected_year]

# Define a fixed color mapping for crime types
color_mapping = {
    "Acts against computer systems": "#E57373",  # Red
    "Bribery": "#FFB74D",  # Orange
    "Attempted intentional homicide": "#4DB6AC",  # Teal
    "Intentional homicide": "#1E88E5",  # Blue
    "Kidnapping": "#81C784",  # Green
    "Robbery": "#DCE775",  # Yellow-green
    "Rape": "#9575CD",  # Purple
    "Sexual assault": "#F06292",  # Pink
    "Sexual violence": "#BA68C8",  # Violet
    "Unlawful acts involving controlled drugs or precursors": "#8D6E63",  # Brown
    "Burglary of private residential premises": "#FF8A65",  # Light Red-Orange
    "Burglary": "#A1887F",  # Taupe
    "Serious assault": "#64B5F6",  # Light Blue
    "Theft": "#7986CB",  # Indigo
    "Fraud": "#4DB6AC",  # Cyan
    "Corruption": "#AED581",  # Light Green
    "Theft of a motorized vehicle or parts thereof": "#FDD835",  # Bright Yellow
    "Sexual exploitation": "#FF7043",  # Deep Orange
    "Money laundering": "#BDBDBD",  # Grey
    "Participation in an organized criminal group": "#90A4AE",  # Blue Grey
    "Child pornography": "#FFD54F"  # Amber
}

# Stacked bar plot
fig = px.bar(filtered_data,
             x="geo",
             y="OBS_VALUE",
             color="iccs",  # Different crime types stacked
             barmode="stack",
             labels={"geo": "Countries", "OBS_VALUE": "Offences per 1000 inhabitants"},
             title=f"Crime Data for European Countries {selected_year}",
             color_discrete_map=color_mapping)

fig.update_layout(xaxis_tickangle=-45,
                  legend_title="Types of Offences",
                  height=700,
                  width=4000)

st.plotly_chart(fig)

# Pie Chart - Crime Distribution by Type
st.header("Crime Distribution in Europe")

crime_pie = filtered_data.groupby("iccs")["OBS_VALUE"].sum().reset_index()

fig_pie = px.pie(crime_pie,
                 names="iccs",
                 values="OBS_VALUE",
                 title=f"Crime Type Distribution in {selected_year}",
                 color="iccs",
                 color_discrete_map=color_mapping)

st.plotly_chart(fig_pie)

# Country map

merged_df = pd.read_csv("merged.csv")

# Filter the merged data by the selected year (merge with crime_df based on country and year)
merged_df = merged_df[merged_df["TIME_PERIOD"] == selected_year]

# Load the shapefile for the countries
shapefile_path = "external_source/gdp_map_countries/ne_110m_admin_0_countries.shp"
world = gpd.read_file(shapefile_path)

# Merge the geo-data with the crime data for the selected year
merged_geo = world.merge(merged_df, how='left', left_on='NAME', right_on='geo')

# Create the map
m = folium.Map(location=[20, 0], zoom_start=2)

# Function to choose color based on cases per 100k
def color_cases(cases_per_100k):
    if cases_per_100k < 1:
        return 'green'
    elif cases_per_100k < 5:
        return 'yellow'
    elif cases_per_100k < 10:
        return 'orange'
    else:
        return 'red'

# Add GeoJson data to the map
for _, row in merged_geo.iterrows():
    geo = row['geometry']
    cases_per_100k = row['No of cases']  # Cases per 100,000 for the selected year
    folium.GeoJson(
        geo,
        style_function=lambda x: {
            'fillColor': color_cases(cases_per_100k),
            'color': 'black',  # Border color
            'weight': 2,  # Border weight
            'fillOpacity': 0.5
        },
        tooltip=folium.Tooltip(f"<b>{row['NAME']}</b><br>{cases_per_100k} cases per 100,000 inhabitants", sticky=True)
    ).add_to(m)

# Save the map to an HTML file
map_html = io.BytesIO()
m.save(map_html, close_file=False)  # Save to BytesIO
map_html.seek(0)

# Display the map in Streamlit using st.components.v1.html
st.components.v1.html(map_html.getvalue().decode(), height=600)
