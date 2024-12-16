import streamlit as st
from PIL import Image

#Configuring the page and setting the title
st.set_page_config(page_title="St. Gallen Information Hub", page_icon="🗺️", layout="wide")

#Display the image at the top of the page
image = Image.open('IMG_St_Gallen.jpg')  # Ensure the image is in the same directory or provide the correct path
st.image(image)

#Title for the landing page
st.title("Welcome to the St. Gallen Information Hub")

#Displaying text of the website
st.write("""
Welcome to the **St. Gallen Information Hub** – your website for discovering important news and exploring in St. Gallen, Switzerland.

This website is designed for residents, visitors, and anyone interested in staying informed about events, points of interest, and public updates in St. Gallen.

The platform offers two main features to help you navigate the city:

1. **Recent News and Events** – Filter and read  announcement from various public sources, such as the St. Gallen Police, City Administration, and the Canton of St. Gallen. Choose your preferred date range and access summarized updates powered by Gemini AI.
2. **Explore Points of Interest** – Discover important locations around St. Gallen, including cultural sites, educational institutions, parks, and more. Visualize these locations using an interactive 3D map, making it easy to find what you're looking for in the city.

Whether you’re a long-time resident, a newcomer, or a visitor, this platform makes it easy to stay connected and informed about your surroundings.

To use this platform, you’ll need to enter your Gemini API key to access the news summarizing feature.
""")

#Display Footer
st.markdown("""
    <p style="text-align: center; color: grey;">Skills: Programming - Introduction Level | A Project for exploring St. Gallen</p>
    """, unsafe_allow_html=True)
