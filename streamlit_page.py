import streamlit as st
from datetime import datetime
import json
from bs4 import BeautifulSoup
import google.generativeai as genai


# Function to clean HTML content in description
def clean_html(html):
    return BeautifulSoup(html, "html.parser").get_text()

# Function to filter articles based on the date range
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


# Streamlit App
st.title("What happened in SG")
st.write("Filter news articles from multiple sources based on a date range.")

# User input for OpenAI API key
api_key = st.text_input("Enter your OpenAI API Key", type="password")

# Input fields for start and end date
start_date = st.date_input("Start Date", datetime(2024, 11, 15))
end_date = st.date_input("End Date", datetime(2024, 11, 17))

# Convert dates to datetime format
timestamp_start = datetime.combine(start_date, datetime.min.time())
timestamp_end = datetime.combine(end_date, datetime.min.time())

# File names to process
file_names = [
    "newsfeed-stadtpolizei-stgallen-medienmitteilungen@stadt-stgallen.json",
    "newsfeed-stadtverwaltung-stgallen@stadt-stgallen.json",
    "newsfeed-medienmitteilungen-kanton-stgallen.json"
]

# Check if API key is provided
if api_key:
    # Initialize OpenAI client dynamically with user-provided key
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    def summarize_text(text):
        
        try:
            response = model.generate_content('Summarize this text: ' + text)
            return response.text
        except Exception as e:
            return f"Error summarizing text: {str(e)}"






    # Filter and display results when the user clicks a button
    if st.button("Filter Articles"):
        filtered_articles = []
        for file_name in file_names:
            filtered_articles.extend(filter_articles(file_name, timestamp_start, timestamp_end))
        
        # Summarize all articles into a single text
        if filtered_articles:
            st.write(f"Found {len(filtered_articles)} articles. Summarizing all articles into one summary...")
            
            # Combine all article descriptions
            combined_text = " ".join(article["description"] for article in filtered_articles)
            
            # Summarize the combined text
            with st.spinner("Summarizing all articles..."):
                summary = summarize_text(combined_text)
            
            st.write("Summary of all articles:")
            st.write(summary)
        else:
            st.write("No articles found in the selected date range.")
else:
    st.warning("Please provide your OpenAI API key to proceed.")
