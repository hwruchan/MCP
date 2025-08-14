from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import pandas as pd
import pymysql

# FastMCP 서버 생성
mcp = FastMCP("smuchat")

# 기존 도구들
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


# 데이터베이스와 통합된 기본 프롬프트
@mcp.prompt()
def default_prompt(message: str) -> list[base.Message]:
    return [
        base.AssistantMessage(
            "You are a smart agent with an ability to use tools. \n"
            "You will be given a question and you will use the tools to answer the question. \n"
            "Pick the most relevant tool to answer the question. \n"
            "If you are failed to answer the question, try different tools to get context. \n"
            "Your answer should be very polite and professional."
        ),
        base.UserMessage(message),
    ]

# FastMCP 서버 실행
if __name__ == "__main__":
    mcp.run(transport="stdio")

