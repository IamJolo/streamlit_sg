import streamlit as st
from datetime import datetime
import json
from bs4 import BeautifulSoup
import google.generativeai as genai

#------------------------ Utility Functions ------------------------

#Defining function to clean HTML content in the data using BeautifulSoup
def clean_html(html):
    return BeautifulSoup(html, "html.parser").get_text()

#Defining a function to filter articles based on the date range
def filter_articles(file_name, timestamp_start, timestamp_end):
    with open(file_name, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    filtered = []
    #Loop through each article in the dataset
    for article in data:
        parsed_datetime = datetime.fromisoformat(article['published'])
        date_only = datetime(parsed_datetime.year, parsed_datetime.month, parsed_datetime.day)
        
        #Check if the articles date falls within the specified start and end dates
        if timestamp_start <= date_only <= timestamp_end:
            title = article['title']
            description = clean_html(article['description'])
            filtered.append({"title": title, "description": description})
    return filtered

#Defining a function to summarize articles using the Gemini API
def summarize_text(text):
    try:
        response = model.generate_content(
            'This is a text on what happened in the city of St. Gallen, summarize it into one article and report on what happened in St. Gallen: ' + text
        )
        return response.text
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

#------------------------ Streamlit App ------------------------

#Setting Page Configuration
st.set_page_config(page_title="SG News Filter", page_icon="📰", layout="wide")

#Defining the Sidebar for the API Key
st.sidebar.title("🔐 API Configuration")
api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")

#Setting Main Title and Description
st.title("📰 What Happened in St. Gallen?")
st.write("""What Happened in St. Gallen allows you to explore recent news from St. Gallen.  By providing a Gemini API key, entering a specific date 
range and selecting from several sources, including the St. Gallen Police, City Administration, and Canton of St. Gallen you receive an AI summary 
of what happended in St. Gallen.
""")

#Defining the date input fields next to each other
st.subheader("📅 Select Date Range")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime(2024, 11, 15))
with col2:
    end_date = st.date_input("End Date", datetime(2024, 11, 17))

#Convert the selected start date to a full datetime object at the start of the day
timestamp_start = datetime.combine(start_date, datetime.min.time())
timestamp_end = datetime.combine(end_date, datetime.min.time())

#Define dictionary of file names and their labels
datasets = {
    "St. Gallen City Police - Media releases": "newsfeed-stadtpolizei-stgallen-medienmitteilungen@stadt-stgallen.json",
    "City administration of St. Gallen - Media releases": "newsfeed-stadtverwaltung-stgallen@stadt-stgallen.json",
    "Canton of St. Gallen - Media releases": "newsfeed-medienmitteilungen-kanton-stgallen.json"
}

#Iterate through each dataset label and file name in the datasets dictionary and display a checkbox for each dataset, checked by default
st.subheader("🗂️ Select Datasets to Filter")
selected_datasets = []
for label, file_name in datasets.items():
    if st.checkbox(f"{label}", value=True):
        selected_datasets.append(file_name)

#Display error field if API key is not provided
if not api_key:
    st.error('Enter your API key to filter', icon="⚠️")

#Check if API key is provided
if api_key:
    #Initialize Gemini API with API key
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    #Filter and summarize results when the user clicks the button "Filter Articles"
    if st.button("🔍 Filter Articles", use_container_width=True):
        with st.spinner("Filtering articles..."):
            filtered_articles = []
            for file_name in selected_datasets:
                filtered_articles.extend(filter_articles(file_name, timestamp_start, timestamp_end))
        
        if filtered_articles:
            #Display number of articles in date range
            st.success(f"✅ Found {len(filtered_articles)} articles.")
            st.markdown("### Summarizing all articles...")
            
            #Combine all articles into one text
            combined_text = " ".join(article["description"] for article in filtered_articles)
            
            #Summarize the combined text
            with st.spinner("Summarizing articles..."):
                summary = summarize_text(combined_text)
            
            #Subheader and displaying summary
            st.subheader("📝 Summary of All Articles")
            st.write(summary)

            #Showing expander to view all individual articles
            with st.expander("📚 View All Articles"):
                for i, article in enumerate(filtered_articles, start=1):
                    st.write(f"**{i}. {article['title']}**")
                    st.write(article["description"])
                    st.write("---")
        else:
            #Warning if no articles where found
            st.warning("⚠️ No articles found in the selected date range.")
else:
    st.sidebar.warning("Please provide your Gemini API key to proceed.")

#Display Footer
st.markdown("""
    <p style="text-align: center; color: grey;">Skills: Programming - Introduction Level | A Project for exploring St. Gallen</p>
    """, unsafe_allow_html=True)