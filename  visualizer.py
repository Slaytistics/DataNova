import plotly.express as px

def plot_top_column(df, column_name, label_column=None):
    df_sorted = df.sort_values(by=column_name, ascending=False).head(10)
    x_col = label_column if label_column else df_sorted.columns[0]

    fig = px.bar(df_sorted, x=x_col, y=column_name,
                 title=f"Top 10 {x_col} by {column_name}")
    return fig
