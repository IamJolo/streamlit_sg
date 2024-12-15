import streamlit as st
import pandas as pd
import pydeck as pdk
import json

# Page configuration
st.set_page_config(page_title="St. Gallen Points of Interest - 3D Map", page_icon="🗺️", layout="wide")

st.title("🗺️ 3D Visualization of Points of Interest in St. Gallen")

st.write("""Explore the city of St. Gallen through an interactive 3D map that 
visualizes various points of interest. By selecting different categories you can see their locations represented with visual markers 
on the map. When hovering your mouse over the market Name, Category, Address, Opening Hours and the Phone Number is displayed, if available """)

# Load JSON data from the file
@st.cache_data
def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Load new dataset
data_file = "points-of-interest-@stadt-stgallen.json"
data = load_data(data_file)

# Transform data into a DataFrame
def transform_data(data):
    records = []
    for entry in data:
        records.append({
            "lat": entry["geo_point_2d"]["lat"],
            "lon": entry["geo_point_2d"]["lon"],
            "category": entry["kategorie"],
            "name": entry["bezeichnun"],
            "address": entry.get("adresse", "No address provided"),  # Fallback if address is missing
            "zip_code": entry["plz"],
            "city": entry["ort"],
            "opening_hours": entry.get("oeffnungsz", "Not available"),  # Fallback if opening_hours are missing
            "phone": entry.get("telefon", "No phone number provided")  # Fallback if phone is missing
        })
    return pd.DataFrame(records)

df = transform_data(data)

# Dictionary to map categories to English
category_translation = {
    "Spielplatz": "Playground",
    "Bibliothek": "Library",
    "Museum": "Museum",
    "Park": "Park",
    "Sportplatz": "Sports Field",
    "Restaurant": "Restaurant",
    "Café": "Café",
    "Theater": "Theater",
    "Apotheke, Drogerie": "Pharmacy",
    "Drogerie": "Drugstore",
    "Aus- und Weiterbildung": "Education and Training",
    "Banken": "Banks",
    "Bar, Dancing, Disco": "Bar, Dancing, Disco",
    "Beratungsstellen": "Consulting Centers",
    "Friedhöfe": "Cemeteries",
    "Heime, Spitäler": "Homes, Hospitals",
    "Hotels": "Hotels",
    "Kantonale Verwaltung": "Cantonal Administration",
    "Kinder- und Jugendtreff": "Children and Youth Center",
    "Kindergärten": "Kindergartens",
    "Kino": "Cinema",
    "Krippen, FSA und Tagesbetreuungen": "Nurseries and daycare centers",
    "Kulturelles": "Cultural Sites",
    "Mobility": "Mobility",
    "Parkplätze, Parkhäuser": "Parking Lots and Parking Garages",
    "Post": "Post Office",
    "Religiöse Bauten": "Religious Buildings",
    "Restaurants": "Restaurants",
    "Schulhäuser": "School Buildings",
    "Spielgruppen": "Playgroups",
    "Spielplätze": "Playgrounds",
    "Sportanlagen": "Sports Facilities",
    "Stadtverwaltung": "City Administration",
    "Velostation Veloverleih": "Bike and Bike Rental Stations",
    "Verschiedenes": "Miscellaneous",
    "Öffentliche WC": "Public Restrooms"
}


# Translate categories in the DataFrame
df["category_en"] = df["category"].map(category_translation).fillna(df["category"])

# Sidebar for filtering options
st.sidebar.header("🔍 Filter by Category")

# Unique translated categories for selection using radio buttons
categories_en = sorted(df["category_en"].dropna().unique())
selected_category_en = st.sidebar.radio("Select Category", options=categories_en)

# Get the original category corresponding to the selected English category
selected_category = df[df["category_en"] == selected_category_en]["category"].iloc[0]

# Apply filters based on the selected category
filtered_df = df[df["category"] == selected_category]

# Display a message if no data is found in the selected filters
if filtered_df.empty:
    st.warning("⚠️ No points of interest found for the selected category.")
else:
    # Define a tooltip to show additional information, handle missing data gracefully
    tooltip = {
        "html": "<b>Name:</b> {name}<br><b>Category:</b> {category}<br><b>Address:</b> {address}<br><b>Opening Hours:</b> {opening_hours}<br><b>Phone:</b> {phone}",
        "style": {
            "backgroundColor": "grey",
            "color": "white",
            "fontSize": "12px",
            "padding": "10px"
        }
    }

    # Pydeck ColumnLayer configuration for 3D visualization
    layer = pdk.Layer(
        "ColumnLayer",
        data=filtered_df,
        get_position='[lon, lat]',
        get_elevation=500,  # Fixed elevation to give a 3D effect
        elevation_scale=2,
        radius=10,
        get_fill_color='[0, 0, 255, 160]',  # Blue color for columns
        pickable=True,
        auto_highlight=True
    )

    # Map configuration with 3D view and white background
    view_state = pdk.ViewState(
        latitude=filtered_df["lat"].mean(),
        longitude=filtered_df["lon"].mean(),
        zoom=12,
        pitch=50,  # Tilt the map for 3D view
        bearing=0
    )

    # White map style
    white_map_style = "mapbox://styles/mapbox/light-v10"

    # Render the map with the ColumnLayer and white background
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style=white_map_style,  # Set the map style to a white/light theme
        tooltip=tooltip  # Apply the tooltip
    ))
# Footer
st.markdown("""
    <p style="text-align: center; color: grey;">Skills: Programming - Introduction Level | A Project for exploring St. Gallen</p>
    """, unsafe_allow_html=True)