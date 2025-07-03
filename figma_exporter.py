import requests
import streamlit as st

def export_to_figma(text, frame_name="Datalicious Summary"):
    api_key = st.secrets["FIGMA_API_KEY"]
    file_id = st.secrets["FIGMA_FILE_ID"]

    headers = {
        "X-Figma-Token": api_key,
        "Content-Type": "application/json"
    }

    # Example: create a text node inside a frame
    payload = {
        "event_type": "TEXT_EXPORT",
        "description": "Exported from Datalicious",
        "client_meta": {
            "summary": text,
            "frame": frame_name
        }
    }

    # This is a placeholder — Figma API doesn't support direct write yet,
    # so you'd typically use a plugin or webhook to receive this data.
    # For now, simulate export by logging or sending to a webhook.
    print("🚀 Export payload:", payload)
    return "✅ Export simulated (Figma API write access is limited — consider using a plugin or webhook)."
