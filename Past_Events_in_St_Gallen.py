import streamlit as st
from datetime import datetime
import json
from bs4 import BeautifulSoup
import google.generativeai as genai

# ------------------------ Utility Functions ------------------------

# Defining function to clean HTML content in the data
def clean_html(html):
    return BeautifulSoup(html, "html.parser").get_text()

# Defining a function to filter articles based on the date range
def filter_articles(file_name, timestamp_start, timestamp_end):
    with open(file_name, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    filtered = []
    for article in data:
        parsed_datetime = datetime.fromisoformat(article['published'])
        date_only = datetime(parsed_datetime.year, parsed_datetime.month, parsed_datetime.day)
        if timestamp_start <= date_only <= timestamp_end:
            title = article['title']
            description = clean_html(article['description'])
            filtered.append({"title": title, "description": description})
    return filtered

def summarize_text(text):
    try:
        response = model.generate_content(
            'This is a text on what happened in the city of St. Gallen, summarize it into one article and report on what happened in St. Gallen: ' + text
        )
        return response.text
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

# ------------------------ Streamlit App ------------------------

# Page Configuration
st.set_page_config(page_title="SG News Filter", page_icon="📰", layout="wide")

# Defining the Sidebar for the API Key
st.sidebar.title("🔐 API Configuration")
api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")

# Setting Main Title and Description
st.title("📰 What Happened in St. Gallen?")
st.markdown("### Filter news articles from multiple sources by selecting a date range and get a summary powered by Gemini AI.")

# Defining the date input fields
st.subheader("📅 Select Date Range")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime(2024, 11, 15))
with col2:
    end_date = st.date_input("End Date", datetime(2024, 11, 17))

# Converting dates to datetime format
timestamp_start = datetime.combine(start_date, datetime.min.time())
timestamp_end = datetime.combine(end_date, datetime.min.time())

# Define list of file names and their labels
datasets = {
    "Stadtpolizei St. Gallen - Medienmitteilungen": "newsfeed-stadtpolizei-stgallen-medienmitteilungen@stadt-stgallen.json",
    "Stadtverwaltung St. Gallen": "newsfeed-stadtverwaltung-stgallen@stadt-stgallen.json",
    "Kanton St. Gallen - Medienmitteilungen": "newsfeed-medienmitteilungen-kanton-stgallen.json"
}

# Selectors for datasets
st.subheader("🗂️ Select Datasets to Filter")
selected_datasets = []
for label, file_name in datasets.items():
    if st.checkbox(f"{label}", value=True):
        selected_datasets.append(file_name)

# Display field if API key is not provided
if not api_key:
    st.error('Enter your API key to filter', icon="⚠️")

# Check if API key is provided
if api_key:
    # Initialize Gemini API with API key
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Filter and summarize results when the user clicks the button "Filter Articles"
    if st.button("🔍 Filter Articles", use_container_width=True):
        with st.spinner("Filtering articles..."):
            filtered_articles = []
            for file_name in selected_datasets:
                filtered_articles.extend(filter_articles(file_name, timestamp_start, timestamp_end))
        
        if filtered_articles:
            # Display number of articles in date range
            st.success(f"✅ Found {len(filtered_articles)} articles.")
            st.markdown("### Summarizing all articles...")
            
            # Combine all articles
            combined_text = " ".join(article["description"] for article in filtered_articles)
            
            # Summarize the combined text
            with st.spinner("Summarizing articles..."):
                summary = summarize_text(combined_text)
            
            st.subheader("📝 Summary of All Articles")
            st.write(summary)

            # Showing expander to view all individual articles
            with st.expander("📚 View All Articles"):
                for i, article in enumerate(filtered_articles, start=1):
                    st.write(f"**{i}. {article['title']}**")
                    st.write(article["description"])
                    st.write("---")
        else:
            st.warning("⚠️ No articles found in the selected date range.")
else:
    st.sidebar.warning("Please provide your Gemini API key to proceed.")
