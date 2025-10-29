import plotly.graph_objects as go

def create_degradation_chart(predictions):
    """
    Create Plotly line chart showing tire degradation

    Args:
        predictions: list of dicts with {"lap": int, "predicted_time": float}

    Returns:
        plotly.graph_objects.Figure
    """
    if not predictions or not isinstance(predictions, list):
        raise ValueError("Invalid predictions data for chart rendering.")

    laps = [p["lap"] for p in predictions]
    times = [p["predicted_time"] for p in predictions]

    n = len(laps)
    if n == 0:
        raise ValueError("Predictions list is empty.")

    # Calculate color zone thresholds
    zone1_end = int(n * 0.33)
    zone2_end = int(n * 0.66)
    y_min, y_max = min(times), max(times)

    # Create figure
    fig = go.Figure()

    # Add background zones
    fig.add_shape(
        type="rect", x0=laps[0], x1=laps[zone1_end],
        y0=y_min, y1=y_max,
        fillcolor="rgba(0,255,0,0.1)", line_width=0,
        layer="below", name="Optimal"
    )
    fig.add_shape(
        type="rect", x0=laps[zone1_end], x1=laps[zone2_end],
        y0=y_min, y1=y_max,
        fillcolor="rgba(255,255,0,0.15)", line_width=0,
        layer="below", name="Degrading"
    )
    fig.add_shape(
        type="rect", x0=laps[zone2_end], x1=laps[-1],
        y0=y_min, y1=y_max,
        fillcolor="rgba(255,0,0,0.1)", line_width=0,
        layer="below", name="Critical"
    )

    # Add prediction line
    fig.add_trace(go.Scatter(
        x=laps,
        y=times,
        mode="lines+markers",
        name="Predicted Lap Time",
        line=dict(color="royalblue", width=3),
        marker=dict(size=6),
        hovertemplate="Lap %{x}<br>Time: %{y:.3f}s<extra></extra>"
    ))

    # Layout styling
    fig.update_layout(
        title="🏎️ Tire Degradation Prediction",
        xaxis_title="Lap Number",
        yaxis_title="Predicted Lap Time (s)",
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=50, r=50, t=60, b=50),
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.5)"),
    )

    return fig
