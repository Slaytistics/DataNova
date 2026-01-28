import os
import pandas as pd

def generate_figma_design_spec(data_dict):
    """
    Transforms analysis data into a structured design specification 
    that the frontend uses to build Figma frames.
    """
    file_name = data_dict.get("fileName", "Untitled_Report")
    rows = data_dict.get("row_count", 0)
    cols = data_dict.get("column_count", 0)
    summary = data_dict.get("summary", "No summary provided.")
    
    # Define a professional color palette
    palette = {
        "primary": "#F97316",  # Orange
        "secondary": "#8B5CF6", # Purple
        "bg": "#F8FAFC",
        "text": "#1E293B"
    }

    spec = {
        "metadata": {
            "title": f"Design Spec: {file_name}",
            "generated_at": "2026-01-29"
        },
        "frames": [
            {
                "id": "frame_1",
                "name": "Executive Dashboard",
                "layout": "grid",
                "layers": [
                    {"type": "heading", "text": "DataNova Analytics", "color": palette["primary"]},
                    {"type": "subheading", "text": f"Dataset: {file_name}", "color": palette["text"]},
                    {"type": "stat_card", "label": "Total Records", "value": f"{rows:,}"},
                    {"type": "stat_card", "label": "Features", "value": f"{cols}"}
                ]
            },
            {
                "id": "frame_2",
                "name": "AI Insights Summary",
                "layers": [
                    {"type": "paragraph", "text": summary, "font_size": 16}
                ]
            }
        ]
    }
    return spec