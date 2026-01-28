import pandas as pd

def generate_figma_design_spec(data_dict):
    """
    Converts raw data analysis into a structured JSON 'Design Spec'.
    This spec is used by the frontend to draw Canvas reports and 
    by Figma plugins to generate UI frames.
    """
    file_name = data_dict.get("fileName", "DataNova_Report")
    rows = data_dict.get("row_count", 0)
    cols = data_dict.get("column_count", 0)
    summary = data_dict.get("summary", "Analysis pending...")

    # We define the visual hierarchy here so the frontend stays light.
    spec = {
        "metadata": {
            "title": f"Report: {file_name}",
            "brand": "DataNova AI",
            "theme_color": "#F97316"
        },
        "structure": [
            {
                "frame_name": "Header & KPI",
                "elements": [
                    {"type": "text", "value": "Executive Data Summary", "style": "heading"},
                    {"type": "metric", "label": "Total Observations", "value": f"{rows:,}"},
                    {"type": "metric", "label": "Data Dimensions", "value": f"{cols} Columns"}
                ]
            },
            {
                "frame_name": "AI Narrative",
                "elements": [
                    {"type": "paragraph", "value": summary}
                ]
            }
        ],
        "figma_config": {
            "version": "2.0",
            "import_path": "JSON to Design Plugin",
            "instructions": "Download JSON and upload to Figma via the plugin to see these frames."
        }
    }
    
    return spec

def create_export_metadata(df):
    """
    Optional helper to extract specific column metadata for 
    advanced Figma table components.
    """
    return {
        "columns": df.columns.tolist(),
        "sample_size": len(df.head(5)),
        "data_types": df.dtypes.astype(str).to_dict()
    }