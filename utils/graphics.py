from pathlib import Path
import plotly.graph_objs as go
import plotly.io as pio

from utils.paths import constructPath
from utils .envHandler import getenv

APP_BASE_PATH = getenv('APP_BASE_PATH')

def chartWithSense(dates: list[str], values: list[int], width=120, height=60):
    color = "red" if values[-2] > values[-1] else "green"
    
    trace = go.Scatter(
        x=dates,
        y=values,
        mode="lines",
        marker=dict(
            size=12,
            color=color
        ),
        fill = "tozeroy"
    )

    fig = go.Figure(data=[trace])

    fig.update_layout(
        xaxis=dict(
            title='',
            showticklabels=False,
            showline=False,  # Remove x-axis line
            zeroline=False,  # Remove zero line
            rangeslider=dict(visible=False),  # Disable the range slider
            gridcolor='rgba(0,0,0,0)'  # Remove x-axis grid lines
        ),
        yaxis=dict(
            title='',
            showticklabels=False,
            showline=False,  # Remove y-axis line
            zeroline=False,  # Remove zero line
            gridcolor='rgba(0,0,0,0)'  # Remove y-axis grid lines
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        width=width,
        height=height,
        margin=dict(l=0, r=0, t=0, b=0, pad=0),  # Set all margins to zero
        autosize=False,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',  # Ensure the paper background is transparent
    )

    name = "chart_with_sense"
    suffix = ""
    extension = ".png"
    outputPath = constructPath(Path(APP_BASE_PATH), 'static/charts/', f"{name}{suffix}{extension}")
    outputPath.parent.mkdir(parents=True, exist_ok=True)

    # Save the image with specified dimensions
    pio.write_image(fig, file=str(outputPath), width=width, height=height, scale=1)

    return outputPath

if __name__ == '__main__':
    # Example usage
    dates = ["2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029"]  # Replace with your date data
    values = [94, 88, 200, 100, 25, 122, 48, 99]  # Replace with your value data
    chart_path = chartWithSense(dates, values, 300, 300)
    print(f"Chart saved at: {chart_path}")