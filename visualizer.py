import plotly.express as px
import pandas as pd

def plot_top_column(df, column_name, label_column=None):
    """
    Plots a bar chart of the top 10 rows in a DataFrame based on a numeric column.

    Args:
        df (pd.DataFrame): Input DataFrame.
        column_name (str): Numeric column to sort and plot.
        label_column (str, optional): Column to use for x-axis labels. Defaults to the first column.

    Returns:
        fig (plotly.graph_objs._figure.Figure): A Plotly bar chart figure.
    """
    if column_name not in df.columns:
        raise ValueError(f"'{column_name}' is not a column in the DataFrame.")

    if label_column and label_column not in df.columns:
        raise ValueError(f"'{label_column}' is not a column in the DataFrame.")

    # Sort and select top 10 by the specified column
    df_sorted = df.sort_values(by=column_name, ascending=False).head(10)

    # Default to first column if label_column is not provided
    x_col = label_column if label_column else df_sorted.columns[0]

    # Create the bar chart
    fig = px.bar(
        df_sorted,
        x=x_col,
        y=column_name,
        text=column_name,
        title=f"🔝 Top 10 {x_col} by {column_name}",
        color_discrete_sequence=["#4B8BBE"]
    )

    # Enhance appearance
    fig.update_traces(
        texttemplate="%{text:.2s}",
        textposition="outside"
    )
    fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        xaxis_title=x_col,
        yaxis_title=column_name,
        margin=dict(t=50, b=50),
        height=500
    )

    return fig
