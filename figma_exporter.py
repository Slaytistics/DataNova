from typing import Dict, Any
import pandas as pd


def generate_figma_design_spec(data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts analysis results into a structured JSON Design Spec
    usable by frontend canvas and Figma plugins.
    """

    file_name = data_dict.get("fileName", "DataNova_Report")
    rows = int(data_dict.get("row_count", 0))
    cols = int(data_dict.get("column_count", 0))
    summary = data_dict.get("summary", "Analysis pending...")

    # Limit summary size for UI frames
    if len(summary) > 800:
        summary = summary[:800] + "..."

    spec = {
        "metadata": {
            "title": f"Report: {file_name}",
            "brand": "DataNova AI",
            "theme_color": "#F97316",
            "version": "2.1"
        },
        "frames": [
            {
                "frame_name": "Header & KPIs",
                "elements": [
                    {"type": "heading", "value": "Executive Data Summary"},
                    {"type": "metric", "label": "Total Rows", "value": rows},
                    {"type": "metric", "label": "Total Columns", "value": cols}
                ]
            },
            {
                "frame_name": "AI Insights",
                "elements": [
                    {"type": "paragraph", "value": summary}
                ]
            }
        ],
        "export_instructions": {
            "tool": "Figma JSON to Design Plugin",
            "steps": [
                "Download this JSON file",
                "Open Figma",
                "Run 'JSON to Design' plugin",
                "Paste JSON to generate frames"
            ]
        }
    }

    return spec


def create_export_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract column metadata for advanced Figma table components.
    """
    return {
        "columns": df.columns.tolist(),
        "sample_size": int(len(df.head(5))),
        "data_types": df.dtypes.astype(str).to_dict(),
        "numeric_columns": df.select_dtypes(include=["number"]).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=["object"]).columns.tolist()
    }
