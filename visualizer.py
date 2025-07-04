import plotly.express as px

def plot_top_column(df, column, top_n=10):
    # ✅ Handle edge cases
    if not column or column not in df.columns:
        fig = px.bar(title="No valid column selected")
        fig.update_layout(
            plot_bgcolor='rgba(20,20,20,0.8)',
            paper_bgcolor='rgba(10,10,10,0.7)',
            font_color='#f0f0f0',
            font_family='Inter',
            title_font_size=20
        )
        return fig

    top_values = df[column].value_counts().nlargest(top_n).reset_index()
    top_values.columns = [column, 'Count']

    fig = px.bar(
        top_values,
        x=column,
        y='Count',
        title=f"Top {top_n} values in {column}"
    )

    fig.update_layout(
        plot_bgcolor='rgba(20,20,20,0.8)',
        paper_bgcolor='rgba(10,10,10,0.7)',
        font_color='#f0f0f0',
        font_family='Inter',
        title_font_size=20,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            color='#f0f0f0'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False,
            color='#f0f0f0'
        ),
    )

    fig.update_traces(marker_color='rgba(0, 180, 255, 0.9)')

    return fig
