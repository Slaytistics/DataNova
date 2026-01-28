import requests
import streamlit as st

def export_to_figma(text, frame_name="Datalicious Summary"):
    api_key = st.secrets["FIGMA_API_KEY"]
    file_id = st.secrets["FIGMA_FILE_ID"]

    headers = {
        "X-Figma-Token": api_key,
        "Content-Type": "application/json"
    }

    
    payload = {
        "event_type": "TEXT_EXPORT",
        "description": "Exported from Datalicious",
        "client_meta": {
            "summary": text,
            "frame": frame_name
        }
    }

   
    print("🚀 Export payload:", payload)
    return "✅ Export simulated (Figma API write access is limited — consider using a plugin or webhook)."
