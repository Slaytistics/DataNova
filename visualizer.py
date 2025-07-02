import plotly.express as px
import pandas as pd

def plot_top_column(df, column_name, top_n=10, label_column=None):
    """
    Plots a bar chart of the top N rows based on a numeric column.
    """
    if column_name not in df.columns:
        raise ValueError(f"'{column_name}' is not in the DataFrame.")

    df_sorted = df.sort_values(by=column_name, ascending=False).head(top_n)
    x_col = label_column if label_column else df_sorted.columns[0]

    fig = px.bar(
        df_sorted,
        x=x_col,
        y=column_name,
        text=column_name,
        title=f"🔝 Top {top_n} {x_col} by {column_name}",
        color_discrete_sequence=["#4B8BBE"]
    )

    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        hovertemplate=f"{x_col}: %{{x}}<br>{column_name}: %{{y}}<extra></extra>"
    )

    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=column_name,
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        height=500,
        margin=dict(t=50, b=50)
    )

    return fig
