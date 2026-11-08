import pandas as pd


def grade_students(omr_df, answer_df):
    """
    OMR 답안과 정답 데이터를 비교하여 학생별 채점 결과를 반환한다.

    반환 형식:
    학생명 | Q01_정오 | Q02_정오 | ... | 총점
    """

    # OMR 데이터에서 문항 열 추출
    question_columns = [
        col for col in omr_df.columns
        if col.startswith("Q") and col[1:].isdigit()
    ]

    question_columns.sort(key=lambda x: int(x[1:]))

    # 정답 데이터에서 문항별 정답과 배점 추출
    answer_map = dict(
        zip(answer_df["question"], answer_df["answer"])
    )

    points_map = dict(
        zip(answer_df["question"], answer_df["points"])
    )

    # OMR과 정답 데이터의 문항 번호가 일치하는지 확인
    omr_questions = {int(col[1:]) for col in question_columns}
    answer_questions = set(answer_map.keys())

    if omr_questions != answer_questions:
        raise ValueError(
            "OMR 문항과 정답 PDF의 문항 구성이 일치하지 않습니다."
        )

    # 채점 결과 DataFrame 생성
    result_df = omr_df[["학생명"]].copy()

    # 학생별 총점 초기화
    total_scores = pd.Series(0, index=omr_df.index)

    # 문항별 채점
    for col in question_columns:
        question_num = int(col[1:])

        # 학생 답안과 정답 비교
        is_correct = omr_df[col] == answer_map[question_num]

        # 정오 여부 기록
        result_df[f"{col}_정오"] = is_correct.map({
            True: "O",
            False: "X"
        })

        # 정답인 경우 배점 추가
        total_scores += is_correct.astype(int) * points_map[question_num]

    # 총점 추가
    result_df["총점"] = total_scores

    return result_df
