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
def fetch_medical_pharma_data(query):
    prompt = f"""
    Please provide reliable and accurate medical and pharmaceutical data related to the following query.
    The data should include at least 15 to 20 entries and be formatted as a CSV for the medical and pharmaceutical domain only.
    The data must be accurate and trustworthy.

    Query: {query}

    The result should be in CSV format with headers and rows.
    """
    response = get_response(prompt)
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

# Text area for the user to enter the query
query = st.text_area(
    "Enter your query:",
    height=200
)

# Check if the user has entered a query
if query:
    # Fetch the response using a function to generate data
    response = fetch_medical_pharma_data(query)

    # Display the generated data in a text area
    st.subheader("Generated Medical & Pharma Data (CSV format)")
    st.text_area(
        "Generated Data",
        value=response,
        height=300
    )

    # Button to generate and download the CSV as a SCORM package
    if st.button("Generate CSV File"):
        # Generate the SCORM package from the response
        scorm_package = create_scorm_package(response)

        # Provide a download button for the SCORM package
        st.download_button(
            label="Download CSV File as SCORM Package",
            data=scorm_package.getvalue(),
            file_name="medical_pharma_scorm.zip",
            mime="application/zip"
        )

# Horizontal line
st.markdown("---")

# Footer
st.caption("Developed by **Corbin Technology Solutions**")
