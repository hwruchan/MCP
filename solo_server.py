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

@mcp.tool()
def query_smu_notices_by_keyword(keyword: str) -> dict:
    """
    'smu_notices' 테이블에서 'title' 컬럼에 특정 키워드를 포함하는 행을 조회하여 결과를 반환하는 도구.
    
    Args:
        keyword (str): 'title' 컬럼에서 찾을 키워드.
        
        dict: 키워드가 포함된 'title' 컬럼을 가진 행들 반환.
    """
    # DB 연결 설정
    DB_HOST = 'oneteam-db.chigywqq0qt3.ap-northeast-2.rds.amazonaws.com'
    DB_USER = 'admin'
    DB_PASSWORD = 'Oneteam2025!'
    DB_NAME = 'oneteam_DB'
    DB_PORT = 3306

    # MySQL 연결
    conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
    cursor = conn.cursor()

        # 쿼리 작성: 'title' 컬럼에서 키워드를 포함하는 행을 찾는 쿼리
    query = f"SELECT * FROM smu_notices WHERE title LIKE %s"
    cursor.execute(query, ('%' + keyword + '%',))
        
        # 결과를 DataFrame으로 변환
    data = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=column_names)

        # 결과 반환
    return df.to_dict(orient='records')
    


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
