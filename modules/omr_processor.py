import pandas as pd
import re


def load_omr_excel(file):
    """
    OMR 엑셀 파일을 읽고 학생별 답안 데이터를 정리한다.

    예상 구조:
    학생명 | Q01 | Q02 | Q03 | ...
    900학생 | 3   | 2   | 1   | ...
    """

    df = pd.read_excel(file, dtype={"학생명": str})

    # 열 이름의 불필요한 공백 제거
    df.columns = df.columns.astype(str).str.strip()

    # 학생 식별자 열 확인
    if "학생명" not in df.columns:
        raise ValueError("'학생명' 열을 찾을 수 없습니다.")

    # 문제 번호 열 추출
    question_columns = [
        col for col in df.columns
        if re.fullmatch(r"Q\d+", col)
    ]

    if not question_columns:
        raise ValueError("Q01, Q02 형식의 문제 열을 찾을 수 없습니다.")

    # 문제 번호 순서대로 정렬
    question_columns.sort(key=lambda x: int(x[1:]))

    # 학생 식별자 누락 확인
    if df["학생명"].isna().any():
        raise ValueError("학생명이 비어 있는 행이 있습니다.")

    # 답안 숫자형 변환
    for col in question_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

        if df[col].isna().any():
            raise ValueError(f"{col} 열에 숫자가 아닌 값이 있습니다.")

        # 객관식 답안은 1~5 범위
        if not df[col].between(1, 5).all():
            raise ValueError(f"{col} 열에 1~5 범위를 벗어난 답안이 있습니다.")

        # 정수형으로 변환
        df[col] = df[col].astype(int)

    return df
