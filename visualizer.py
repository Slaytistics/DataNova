import plotly.express as px

def plot_top_column(df, column, top_n=10):
    if not column or column not in df.columns:
        fig = px.bar(title="No valid column selected")
        fig.update_layout(
            plot_bgcolor='rgba(20,20,20,0.8)',
            paper_bgcolor='rgba(10,10,10,0.7)',
            font_color='white',
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
        title=f"Top {top_n} values in {column}",
        text='Count' 
    )

    fig.update_traces(
        marker_color='rgba(0, 180, 255, 0.9)', 
        textfont=dict(color='white')           
    )

    fig.update_layout(
        plot_bgcolor='rgba(20,20,20,0.8)',
        paper_bgcolor='rgba(10,10,10,0.7)',
        font=dict(
            color='white',                
            family='Inter',
            size=14
        ),
        title_font=dict(
            color='white',
            size=20
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            color='white'                  
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False,
            color='white'                      
        ),
    )

    return fig
