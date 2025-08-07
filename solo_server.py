from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import pandas as pd
from datetime import datetime

mcp = FastMCP("soloTest")


@mcp.tool()
def describe_column(csv_path: str, column: str) -> dict:
    """
    Get summary statistics (count, mean, std, min, max, etc.) for a specific column in a CSV file.

    Args:
        csv_path (str): The file path to the CSV file.
        column (str): The name of the column to compute statistics for.

    Returns:
        dict: A dictionary containing summary statistics of the specified column.
    """
    df = pd.read_csv(csv_path)
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in CSV.")
    return df[column].describe().to_dict()


@mcp.prompt()
def default_prompt(message: str) -> list[base.Message]:
    return [
        base.AssistantMessage(
            "You are a helpful data analysis assistant. \n"
            "Please clearly organize and return the results of the tool calling and the data analysis."
        ),
        base.UserMessage(message),
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")