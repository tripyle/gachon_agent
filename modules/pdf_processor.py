import fitz
import re
import pandas as pd


def load_answer_key(pdf_file):
    """
    정답 PDF에서 문항 번호, 정답, 배점을 추출한다.
    """

    # PDF 텍스트 추출
    pdf_bytes = pdf_file.getvalue()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    # 동그라미 숫자를 일반 숫자로 변환
    answer_mapping = {
        "①": 1,
        "②": 2,
        "③": 3,
        "④": 4,
        "⑤": 5
    }

    # 문항 번호 / 정답 / 배점 패턴 추출
    pattern = r"(?<!\d)(\d{1,2})\s*([①②③④⑤])\s*(\d)(?!\d)"

    matches = re.findall(pattern, text)

    if not matches:
        raise ValueError("PDF에서 정답 데이터를 추출하지 못했습니다.")

    records = []

    for question, answer, points in matches:
        records.append({
            "question": int(question),
            "answer": answer_mapping[answer],
            "points": int(points)
        })

    answer_df = pd.DataFrame(records)

    # 중복 문항 확인
    if answer_df["question"].duplicated().any():
        raise ValueError("정답 PDF에 중복된 문항 번호가 있습니다.")

    # 문항 번호 순서대로 정렬
    answer_df = answer_df.sort_values(
        "question"
    ).reset_index(drop=True)

    # 문항 번호 연속성 확인
    expected_questions = list(range(1, len(answer_df) + 1))

    if answer_df["question"].tolist() != expected_questions:
        raise ValueError("정답 PDF의 문항 번호가 연속적이지 않습니다.")

    return answer_df


def extract_question_text(pdf_file, question_number):
    """
    문제지 PDF에서 특정 문항 번호 주변의 텍스트를 추출한다.

    PDF의 텍스트 배치 방식에 따라 추출이 안 될 수도 있으므로
    결과를 확인한 뒤 유사 문제 생성에 사용한다.
    """

    pdf_bytes = pdf_file.getvalue()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    full_text = ""

    for page in document:
        full_text += page.get_text() + "\n"

    document.close()

    # 문항 번호가 문단 시작에 나타나는 위치 검색
    pattern = rf"(?m)^\s*{question_number}\.\s"

    match = re.search(pattern, full_text)

    if not match:
        return ""

    start = match.start()

    # 다음 문항 번호가 나타나는 위치 검색
    next_pattern = rf"(?m)^\s*{question_number + 1}\.\s"

    next_match = re.search(
        next_pattern,
        full_text[start + 1:]
    )

    if next_match:
        end = start + 1 + next_match.start()
        question_text = full_text[start:end]
    else:
        question_text = full_text[start:]

    return question_text.strip()

