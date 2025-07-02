import plotly.express as px

def plot_top_column(df, column_name, label_column=None):
    """
    Creates a bar chart of the top 10 rows in a DataFrame based on a numeric column.
    
    Args:
        df (pd.DataFrame): Input dataframe
        column_name (str): Column to sort and plot (must be numeric)
        label_column (str, optional): Column to use as X-axis labels. If None, uses first column.
    
    Returns:
        fig (plotly.graph_objects.Figure): Plotly bar chart figure
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

    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    return fig
