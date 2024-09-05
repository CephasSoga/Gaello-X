from pathlib import Path
import plotly.graph_objs as go
import plotly.io as pio

from utils.paths import constructPath
from utils.envHandler import getenv
from utils.paths import getFileSystemPath

APP_BASE_PATH = getFileSystemPath(getenv('APP_BASE_PATH'))

def chartWithSense(dates: list[str], values: list[int], width=120, height=60):
    """
    Generates a line chart with a sense of trend based on the given dates and values.

    Args:
        dates (list[str]): A list of dates in string format.
        values (list[int]): A list of corresponding values.
        width (int, optional): The width of the chart in pixels. Defaults to 120.
        height (int, optional): The height of the chart in pixels. Defaults to 60.

    Returns:
        Path: The path to the saved chart image.

    Raises:
        None

    Description:
        This function generates a line chart with a sense of trend based on the given dates and values.
        The color of the line is determined by the trend of the last two values. If the second last value
        is greater than the last value, the line is colored red, otherwise it is colored green.

        The chart is saved as a PNG image with the name "chart_with_sense" in the "static/charts" directory
        of the APP_BASE_PATH. The directory is created if it does not exist.

        The chart has no axis labels, tick labels, or grid lines. The background is transparent.

        The chart is saved with the specified width and height.

        The function returns the path to the saved chart image.
    """
    if  not dates or not values:
        return ""
    
    if (not dates and values) or (dates and not values):
        raise ValueError("Both dates and values must be provided")
    
    
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
    outputPath = constructPath(Path(APP_BASE_PATH), 'static', 'charts',f"{name}{suffix}{extension}")
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