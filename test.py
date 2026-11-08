
import streamlit as st

from modules.omr_processor import load_omr_excel
from modules.pdf_processor import load_answer_key
from modules.grading import grade_students


st.title("파일 처리 및 채점 테스트")

omr_file = st.file_uploader("OMR 엑셀", type=["xlsx"])
answer_file = st.file_uploader("정답 PDF", type=["pdf"])

if st.button("파일 처리 및 채점"):
    if omr_file and answer_file:
        try:
            # 파일 읽기
            omr_df = load_omr_excel(omr_file)
            answer_df = load_answer_key(answer_file)

            # 채점
            grading_df = grade_students(omr_df, answer_df)

            st.subheader("OMR 데이터")
            st.dataframe(omr_df)

            st.subheader("정답 데이터")
            st.dataframe(answer_df)

            st.subheader("학생별 채점 결과")
            st.dataframe(grading_df)

            st.success("채점이 완료되었습니다.")

        except Exception as e:
            st.error(f"오류 발생: {e}")

    else:
        st.warning("OMR 엑셀과 정답 PDF를 모두 업로드해주세요.")
