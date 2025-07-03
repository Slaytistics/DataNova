# figma_exporter.py

import base64

def export_to_figma(text, frame_name="Datalicious Summary"):
    """
    Simulates export to Figma by creating a downloadable .txt link.
    """
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="{frame_name}.txt">📥 Download Summary as .txt</a>'
    return href
