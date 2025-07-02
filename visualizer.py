import plotly.express as px
import pandas as pd

def plot_top_column(df, column_name, label_column=None):
    """
    Plots a bar chart of the top 10 rows in a DataFrame based on a numeric column.

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_name (str): Numeric column to sort and plot.
        label_column (str, optional): Label for x-axis. Defaults to first column.

    Returns:
        fig: Plotly figure object.
    """
    df_sorted = df.sort_values(by=column_name, ascending=False).head(10)
    x_col = label_column if label_column else df_sorted.columns[0]

    fig = px.bar(
        df_sorted,
        x=x_col,
        y=column_name,
        title=f"Top 10 {x_col} by {column_name}",
        text=column_name,
        color_discrete_sequence=["#4B8BBE"]
    )

    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    return fig
