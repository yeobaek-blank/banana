from mcp.server.fastmcp import FastMCP
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# MCP 서비스 인스턴스 생성
mcp = FastMCP("My_MOS")

# CSV 파일 경로를 main.py와 같은 폴더로 지정
CSV_PATH = os.path.join(os.path.dirname(__file__), "통합문서1.csv")

# 데이터 리소스 등록
@mcp.resource("resource://csvfile")
def load_data():
    return pd.read_csv(CSV_PATH, encoding="utf-8")

# 핵심 분석 도구 등록
@mcp.tool()
def analyze_keyword(params):
    keyword = params.get("keyword", "").strip()
    if not keyword:
        return {"error": "키워드가 입력되지 않았습니다."}

    df = load_data()
    search_columns = [
        "Authors", "Author Full Names", "Article Title",
        "Source Title", "Book Series Title", "Language",
        "Author Keywords", "Abstract", "Publication Year"
    ]
    found_cols = [col for col in search_columns if col in df.columns]
    if not found_cols:
        return {"error": "검색 가능한 컬럼이 없습니다."}

    mask = np.zeros(len(df), dtype=bool)
    for col in found_cols:
        mask |= df[col].fillna("").astype(str).str.contains(keyword, case=False, na=False)
    filtered = df[mask]

    # 표 결과
    table_cols = [c for c in ["Article Title", "Authors"] if c in filtered.columns]
    if not table_cols:
        table_cols = filtered.columns[:2].tolist()

    # 시각화 (그래프를 파일로 저장; 필요시 경로 반환)
    if "Publication Year" in filtered.columns and not filtered.empty:
        counts = filtered["Publication Year"].value_counts().sort_index()
        plt.figure(figsize=(10, 5))
        counts.plot(kind="bar")
        plt.title(f'연도별 "{keyword}" 논문 수')
        plt.xlabel("연도")
        plt.ylabel("논문 수")
        plt.tight_layout()
        graph_path = os.path.join(os.path.dirname(__file__), "trend.png")
        plt.savefig(graph_path)
        plt.close()
    else:
        graph_path = ""

    return {
        "count": len(filtered),
        "table": filtered[table_cols].head(20).to_dict(orient="records"),
        "trend_img": graph_path
    }

# FastMCP 엔트리포인트 (명령형/서비스형 둘 다 지원)
def main(params):
    return analyze_keyword(params)

if __name__ == "__main__":
    # params = {"keyword": "North Korea"}
    # print(main(params))
    print("Starting MCP server...")
    mcp.run(transport="stdio")

