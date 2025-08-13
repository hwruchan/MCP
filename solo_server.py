import pymysql
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

@mcp.tool()
def plot_histogram(csv_path: str, column: str, bins: int = 10) -> str:
    """
    Generate and save a density histogram for a specific column in a CSV file.

    Args:
        csv_path (str): The file path to the CSV file.
        column (str): The name of the column to visualize.
        bins (int, optional): Number of histogram bins. Defaults to 10.

    Returns:
        str: The file path to the saved density histogram image.
    """
    df = pd.read_csv(csv_path)
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in CSV.")

    plt.figure(figsize=(8, 6))
    sns.histplot(
        df[column].dropna(),
        bins=bins,
        kde=True,
        stat="density",
        edgecolor="black",
        alpha=0.6,
    )
    plt.xlabel(column)
    plt.ylabel("Density")
    plt.title(f"Density Histogram of {column}")

    output_path = f"{column}_density_hist.png"
    plt.savefig(output_path)
    plt.close()

    return output_path

# MySQL 데이터베이스를 조회하는 새로운 도구 추가
@mcp.tool()
def query_db(table_name: str, column_name: str) -> dict:
    """
    데이터베이스에서 특정 테이블의 지정된 열(column)을 조회하여 통계 정보를 반환하는 도구.
    
    Args:
        table_name (str): 조회할 테이블 이름.
        column_name (str): 조회할 컬럼 이름.
        
    Returns:
        dict: 지정된 컬럼에 대한 통계 정보를 반환.
    """
    # DB 연결 설정
    DB_HOST = 'oneteam-db.chigywqq0qt3.ap-northeast-2.rds.amazonaws.com'
    DB_USER = 'admin'
    DB_PASSWORD = 'Oneteam2025!'
    DB_NAME = 'oneteam_DB'
    DB_PORT = 3306

    # MySQL 연결
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # 쿼리 작성 및 실행
        query = f"SELECT {column_name} FROM {table_name}"
        cursor.execute(query)
        
        # 결과를 DataFrame으로 변환
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=[column_name])

        # 통계 정보 계산
        summary_stats = df[column_name].describe().to_dict()

        return summary_stats
    
    except pymysql.MySQLError as e:
        return {"error": f"Database error: {e}"}
    finally:
        # DB 연결 종료
        cursor.close()
        conn.close()

# 데이터베이스와 통합된 기본 프롬프트
@mcp.prompt()
def default_prompt(message: str) -> list[base.Message]:
    return [
        base.AssistantMessage(
            """<ROLE>
            You are a smart agent with an ability to use tools. 
            You will be given a question and you will use the tools to answer the question.
            Pick the most relevant tool to answer the question. 
            If you are failed to answer the question, try different tools to get context.
            Your answer should be very polite and professional.
            Tools run on the same machine and CAN read local file paths
            </ROLE>

            ----

            <INSTRUCTIONS>
            Step 1: Analyze the question
            - Analyze user's question and final goal.
            - If the user's question is consist of multiple sub-questions, split them into smaller sub-questions.

            Step 2: Pick the most relevant tool
            - Pick the most relevant tool to answer the question.
            - If you are failed to answer the question, try different tools to get context.

            Step 3: Answer the question
            - Answer the question in the same language as the question.
            - Your answer should be very polite and professional.

            Step 4: Provide the source of the answer(if applicable)
            - If you've used the tool, provide the source of the answer.
            - Valid sources are either a website(URL) or a document(PDF, etc).

            Guidelines:
            - If you've used the tool, your answer should be based on the tool's output(tool's output is more important than your own knowledge).
            - If you've used the tool, and the source is valid URL, provide the source(URL) of the answer.
            - Skip providing the source if the source is not URL.
            - Answer in the same language as the question.
            - Answer should be concise and to the point.
            - Avoid response your output with any other information than the answer and the source.  
            </INSTRUCTIONS>

            ----

            <OUTPUT_FORMAT>
            (concise answer to the question)

            **Source**(if applicable)
            - (source1: valid URL)
            - (source2: valid URL)
            - ...
            </OUTPUT_FORMAT>
            """
        ),
        base.UserMessage(message),
    ]

# FastMCP 서버 실행
if __name__ == "__main__":
    mcp.run(transport="stdio")
