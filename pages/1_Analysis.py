import os
import streamlit as st

from dotenv import load_dotenv

from modules.omr_processor import load_omr_excel
from modules.pdf_processor import (
    load_answer_key,
    extract_question_text
)
from modules.grading import grade_students
from modules.analytics import analyze_results
from modules.excel_export import create_excel_file
from modules.agent import answer_question


load_dotenv()

st.set_page_config(
    page_title="시험 분석",
    layout="wide"
)


# ---------------------------------
# Session State 초기화
# ---------------------------------

if "grading_df" not in st.session_state:
    st.session_state.grading_df = None

if "summary" not in st.session_state:
    st.session_state.summary = None

if "question_df" not in st.session_state:
    st.session_state.question_df = None

if "most_wrong" not in st.session_state:
    st.session_state.most_wrong = None

if "question_pdf_text" not in st.session_state:
    st.session_state.question_pdf_text = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "analysis_completed" not in st.session_state:
    st.session_state.analysis_completed = False


# ---------------------------------
# 사이드바: 파일 업로드 및 분석
# ---------------------------------

with st.sidebar:

    st.header("시험 데이터 업로드")

    question_file = st.file_uploader(
        "문제지 PDF",
        type=["pdf"],
        key="question_file"
    )

    omr_file = st.file_uploader(
        "OMR 결과 엑셀",
        type=["xlsx"],
        key="omr_file"
    )

    answer_file = st.file_uploader(
        "정답 PDF",
        type=["pdf"],
        key="answer_file"
    )

    st.divider()

    # 분석 시작 버튼
    analyze_button = st.button(
        "분석 시작",
        type="primary",
        use_container_width=True
    )

    # ---------------------------------
    # 분석 실행
    # ---------------------------------

    if analyze_button:

        if not question_file or not omr_file or not answer_file:

            st.error(
                "문제지 PDF, OMR 엑셀, 정답 PDF를 모두 업로드해주세요."
            )

        else:

            # 새로운 분석을 시작하므로 기존 결과 초기화
            st.session_state.analysis_completed = False
            st.session_state.grading_df = None
            st.session_state.summary = None
            st.session_state.question_df = None
            st.session_state.most_wrong = None
            st.session_state.question_pdf_text = {}
            st.session_state.chat_history = []

            try:

                with st.spinner("시험 데이터를 분석하고 있습니다..."):

                    # 1. OMR 데이터 읽기
                    omr_df = load_omr_excel(omr_file)

                    # 2. 정답 PDF 읽기
                    answer_df = load_answer_key(answer_file)

                    # 3. 자동 채점
                    grading_df = grade_students(
                        omr_df,
                        answer_df
                    )

                    # 4. 성적 분석
                    summary, question_df, most_wrong = (
                        analyze_results(grading_df)
                    )

                    # 5. 오답 상위 3개 문항의 원문 추출
                    question_texts = {}

                    for question_number in most_wrong["문항"]:

                        question_number = int(question_number)

                        question_texts[question_number] = (
                            extract_question_text(
                                question_file,
                                question_number
                            )
                        )

                    # 6. 결과 저장
                    st.session_state.grading_df = grading_df
                    st.session_state.summary = summary
                    st.session_state.question_df = question_df
                    st.session_state.most_wrong = most_wrong
                    st.session_state.question_pdf_text = question_texts

                    # 분석 완료 상태 변경
                    st.session_state.analysis_completed = True

                st.success("채점 및 분석이 완료되었습니다.")

            except Exception as e:

                st.session_state.analysis_completed = False

                st.error(
                    f"분석 중 오류가 발생했습니다: {e}"
                )

    # ---------------------------------
    # Excel 다운로드
    # ---------------------------------

    st.divider()

    st.subheader("분석 결과 다운로드")

    if st.session_state.analysis_completed:

        excel_file = create_excel_file(
            st.session_state.grading_df,
            st.session_state.summary,
            st.session_state.question_df,
            st.session_state.most_wrong
        )

        st.download_button(
            label="엑셀 파일 다운로드",
            data=excel_file,
            file_name="시험_성적_분석_결과.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    else:

        st.button(
            "엑셀 파일 다운로드",
            disabled=True,
            use_container_width=True
        )

        st.caption("시험 분석을 완료하면 다운로드할 수 있습니다.")


# ---------------------------------
# 메인 화면: AI 채팅창
# ---------------------------------

st.title("AI 성적 분석 도우미")

st.caption(
    "시험 성적에 대해 질문하거나 오답 문항을 바탕으로 "
    "유사 문제를 요청할 수 있습니다."
)

if not st.session_state.analysis_completed:

    st.info(
        "채팅 기능을 이용하려면 왼쪽 사이드바에서 "
        "시험 자료를 업로드하고 분석을 먼저 완료해주세요."
    )

else:

    # ---------------------------------
    # 이전 대화 표시
    # ---------------------------------

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ---------------------------------
    # 사용자 입력
    # ---------------------------------

    user_question = st.chat_input(
        "성적에 대해 질문해보세요."
    )

    if user_question:

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.markdown(user_question)

        # API Key 확인
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key and "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]

        if not api_key:

            response_text = (
                "OpenAI API Key가 설정되지 않았습니다. "
                "환경변수를 확인해주세요."
            )

        else:

            with st.chat_message("assistant"):

                with st.spinner("답변을 생성하고 있습니다..."):

                    try:

                        # 방금 입력한 질문은 제외하고 이전 대화만 전달
                        previous_history = (
                            st.session_state.chat_history[:-1]
                        )

                        response_text = answer_question(
                            question=user_question,
                            chat_history=previous_history,
                            grading_df=st.session_state.grading_df,
                            summary=st.session_state.summary,
                            question_df=st.session_state.question_df,
                            most_wrong=st.session_state.most_wrong,
                            question_pdf_text=st.session_state.question_pdf_text,
                            api_key=api_key
                        )

                    except Exception as e:

                        response_text = (
                            f"답변 생성 중 오류가 발생했습니다: {e}"
                        )

                st.markdown(response_text)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response_text
        })

        st.rerun()
