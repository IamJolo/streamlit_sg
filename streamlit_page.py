import streamlit as st
from datetime import datetime
import json
from bs4 import BeautifulSoup

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
st.title("What happend in SG")
st.write("Filter news articles from multiple sources based on a date range.")

# Input fields for start and end date
start_date = st.date_input("Start Date", datetime(2024, 11, 15))
end_date = st.date_input("End Date", datetime(2024, 11, 21))

# Convert dates to datetime format
timestamp_start = datetime.combine(start_date, datetime.min.time())
timestamp_end = datetime.combine(end_date, datetime.min.time())

# File names to process
file_names = [
    "newsfeed-stadtpolizei-stgallen-medienmitteilungen@stadt-stgallen.json",
    "newsfeed-stadtverwaltung-stgallen@stadt-stgallen.json",
    "newsfeed-medienmitteilungen-kanton-stgallen.json"
]

# Filter and display results when the user clicks a button
if st.button("Filter Articles"):
    filtered_articles = []
    for file_name in file_names:
        filtered_articles.extend(filter_articles(file_name, timestamp_start, timestamp_end))
    
    # Display the filtered articles
    if filtered_articles:
        st.write(f"Found {len(filtered_articles)} articles:")
        for i, article in enumerate(filtered_articles, start=1):
            st.subheader(f"{i}. {article['title']}")
            st.write(article["description"])
            st.write("------")
    else:
        st.write("No articles found in the selected date range.")
