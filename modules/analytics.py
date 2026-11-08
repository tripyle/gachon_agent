import pandas as pd


def analyze_results(grading_df):
    """
    채점 결과를 분석하여 전체 통계와 문항별 통계를 반환한다.
    """

    # 총점 데이터
    scores = grading_df["총점"]

    # 전체 성적 통계
    summary = {
        "학생 수": len(grading_df),
        "평균": round(scores.mean(), 2),
        "중앙값": round(scores.median(), 2),
        "표준편차": round(scores.std(ddof=0), 2),
        "최고점": int(scores.max()),
        "최저점": int(scores.min())
    }

    # 문항별 정답 여부 열 추출
    question_columns = [
        col for col in grading_df.columns
        if col.endswith("_정오")
    ]

    question_stats = []

    for col in question_columns:
        question_num = int(col.split("_")[0][1:])

        correct_count = (grading_df[col] == "O").sum()
        incorrect_count = (grading_df[col] == "X").sum()
        total_count = len(grading_df)

        question_stats.append({
            "문항": question_num,
            "정답자": int(correct_count),
            "오답자": int(incorrect_count),
            "정답률(%)": round(correct_count / total_count * 100, 2),
            "오답률(%)": round(incorrect_count / total_count * 100, 2)
        })

    question_df = pd.DataFrame(question_stats)

    # 오답자가 많은 상위 3개 문항
    most_wrong = (
        question_df
        .sort_values(
            by=["오답자", "문항"],
            ascending=[False, True]
        )
        .head(3)
        .reset_index(drop=True)
    )

    return summary, question_df, most_wrong
