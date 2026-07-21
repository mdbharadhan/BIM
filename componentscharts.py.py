import plotly.express as px
import pandas as pd

def render_health_distribution_chart(df: pd.DataFrame):
    """Renders a custom Plotly bar chart for structural health indices."""
    if df.empty:
        return None
    fig = px.bar(
        df, 
        x='element_tag', 
        y='health_index', 
        color='health_index',
        color_continuous_scale='RdYlGn', 
        range_y=[0, 100],
        title="Structural Integrity Telemetry"
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

def render_model_storage_chart(df: pd.DataFrame):
    """Renders a custom Plotly pie chart for BIM model file allocations."""
    if df.empty:
        return None
    fig = px.pie(
        df, 
        names='file_name', 
        values='file_size_mb', 
        hole=0.4,
        title="Storage Allocation by Model File (MB)"
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig