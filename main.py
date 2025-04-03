import streamlit as st
import requests
from fpdf import FPDF
from docx import Document
import openai
import PyPDF2
from docx.shared import Inches
import io
import zipfile
import os
from pathlib import Path
import csv
import pandas as pd
openai.api_key = st.secrets["api"]["OPENAI_API_KEY"]


def get_response(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


# Function to fetch medical and pharma-related data from GPT-3
# Function to fetch data from GPT-3 based on domain and query
def fetch_gpt_response(domain, query):
    prompt = f"""
    Please provide reliable and accurate data related to the following query in the domain of {domain}.
    Don't answer queries or provide CSV data for any other domain except the one provided by the user.
    The data should include at least 15 to 20 entries and be formatted as a CSV.
    The data must be accurate and trustworthy.

    Query: {query}

    The result should be in CSV format with headers and rows.
    """
    response = get_response(prompt)  # Fetch response from GPT-3
    return response

# Function to create SCORM package
def create_scorm_package(csv_content):
    # Create an in-memory binary stream for the zip file
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        # Add the CSV content to the zip file
        zip_file.writestr("medical_pharma_data.csv", csv_content)

        # Add imsmanifest.xml to the zip file
        imsmanifest_content = """<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="scorm_2004" version="1.0">
    <organizations>
        <organization identifier="org_1">
            <title>Medical and Pharma SCORM Package</title>
        </organization>
    </organizations>
    <resources>
        <resource identifier="res_1" type="webcontent" href="index.html">
            <file href="medical_pharma_data.csv"/>
            <file href="index.html"/>
        </resource>
    </resources>
</manifest>"""
        zip_file.writestr("imsmanifest.xml", imsmanifest_content)

        # Add index.html to the zip file
        index_html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Medical and Pharma Data</title>
</head>
<body>
    <h1>Welcome to the Medical and Pharma SCORM Package</h1>
    <p>This package contains reliable medical and pharmaceutical data.</p>
</body>
</html>
"""
        zip_file.writestr("index.html", index_html_content)

    # Rewind the buffer to the beginning
    zip_buffer.seek(0)
    return zip_buffer

# Function to convert CSV string to DataFrame
def csv_to_dataframe(csv_string):
    try:
        df = pd.read_csv(io.StringIO(csv_string))
        return df
    except Exception as e:
        return None  # Handle invalid CSV cases



# Set up the page configuration (must be the first command)
st.set_page_config(page_title="CSV Content Generation", layout="wide", page_icon="📚")

# Title Section with enhanced visuals
st.markdown(
    """
    <h1 style="text-align: center; font-size: 2.5rem; color: #4A90E2;">📚 AI-Powered CSV Content Generation</h1>
    <p style="text-align: center; font-size: 1.1rem; color: #555;">Streamline your content creation process with AI technology.</p>
    """,
    unsafe_allow_html=True,
)
# Horizontal line
st.markdown("---")

# Content Generation Instructions
with st.expander("1️⃣ **CSV Content Generation Instructions**", expanded=True):
    st.markdown("""
        - Generate CSV data related to medical or pharmaceutical queries.
        - **Steps**:
          1. Enter your query in the text area provided.
          2. Click the **Generate CSV File** button to generate data.
          3. Download the generated data as a **CSV SCORM Package**.
        """)

# Horizontal line
st.markdown("---")

st.header("🔍 CSV Content Generation")

# User selects the domain first
domain = st.text_input("Enter the domain in which the answer is required:", placeholder="Example: Medical, Pharmaceutical, Finance, etc.")

# Ensure session state exists for response storage
if "generated_response" not in st.session_state:
    st.session_state.generated_response = None

if domain:
    query = st.text_area(
        "Enter your query below:",
        height=200,
        placeholder=f"Enter any query related to the {domain} domain",
    )
    
    if query:
        # Check if a new query has been entered
        if query != st.session_state.get("last_query"):
            # Fetch response and store in session state
            st.session_state.generated_response = fetch_gpt_response(domain, query)
            st.session_state.last_query = query  # Update last query

        # Convert response to CSV format and display
        csv_data = st.session_state.generated_response
        df = csv_to_dataframe(csv_data)

        if df is not None:
            st.subheader("CSV Data Preview")
            st.dataframe(df)  # Display CSV as table

            # Provide a button to download the CSV file
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download CSV File",
                data=csv_buffer.getvalue(),
                file_name=f"{domain.lower().replace(' ', '_')}_data.csv",
                mime="text/csv"
            )

            # Button to generate and download the CSV as a SCORM package
            if st.button("Generate SCORM Package"):
                scorm_package = create_scorm_package(csv_data)

                st.download_button(
                    label="Download CSV File as SCORM Package",
                    data=scorm_package.getvalue(),
                    file_name=f"{domain.lower().replace(' ', '_')}_scorm.zip",
                    mime="application/zip"
                )
        else:
            st.warning("⚠ The generated response is not in a valid CSV format.")

# Horizontal line
st.markdown("---")

# Footer
st.caption("Developed by **Corbin Technology Solutions**")
