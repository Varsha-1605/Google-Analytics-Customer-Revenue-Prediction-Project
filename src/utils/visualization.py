"""Visualization utilities for the dashboard."""

import plotly.express as px
import plotly.graph_objects as go

def create_metric_card(label, value, prefix="", suffix=""):
    """Create a formatted metric card."""
    return {
        "label": label,
        "value": f"{prefix}{value:,.2f}{suffix}"
    }

def create_time_series(df, x, y, title):
    """Create a time series plot."""
    return px.line(
        df,
        x=x,
        y=y,
        title=title
    )

def create_bar_chart(x, y, title, orientation='v'):
    """Create a bar chart."""
    return px.bar(
        x=x,
        y=y,
        title=title,
        orientation=orientation
    )

def create_pie_chart(values, names, title):
    """Create a pie chart."""
    return px.pie(
        values=values,
        names=names,
        title=title
    )

def create_heatmap(data, x, y, values, title):
    """Create a heatmap."""
    return px.imshow(
        data,
        title=title,
        labels=dict(x=x, y=y, color=values)
    )

def create_scatter_plot(df, x, y, color=None, size=None, title=""):
    """Create a scatter plot."""
    return px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=size,
        title=title
    )

def format_currency(value):
    """Format currency values."""
    return f"${value:,.2f}"

def format_percentage(value):
    """Format percentage values."""
    return f"{value:.1f}%"

def format_number(value):
    """Format large numbers."""
    return f"{value:,}"