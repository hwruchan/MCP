import pymysql
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import pandas as pd

# FastMCP 서버 생성
mcp = FastMCP("smuchat")


@mcp.tool()
def query_smu_notices_by_keyword(keyword: str) -> dict:
    """
    'smu_notices' 테이블에서 'title' 컬럼에 특정 키워드를 포함하는 행을 조회하여 결과를 반환하는 도구.
    
    Args:
        keyword (str): 'title' 컬럼에서 찾을 키워드.
        
    Returns:
        dict: 키워드가 포함된 'title' 컬럼을 가진 행들 반환.
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

        # 쿼리 작성: 'title' 컬럼에서 키워드를 포함하는 행을 찾는 쿼리
        query = f"SELECT * FROM smu_notices WHERE title LIKE %s"
        cursor.execute(query, ('%' + keyword + '%',))
        
        # 결과를 DataFrame으로 변환
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data, columns=column_names)

        # 결과 반환
        return df.to_dict(orient='records')
    
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

