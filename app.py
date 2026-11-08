import streamlit as st
from dotenv import load_dotenv
import base64

load_dotenv()

st.set_page_config(
    page_title="학원 평가 도우미",
    layout="wide"
)

# 로고 이미지 읽기
with open("symbolmark.jpg", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

# 로고와 제목을 하나의 컨테이너에서 중앙 정렬
st.markdown(
    f"""
    <style>
    .landing-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-top: 100px;
    }}

    .landing-logo {{
        width: 220px;
        height: auto;
        display: block;
    }}

    .main-title {{
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        margin-top: 25px;
    }}
    </style>

    <div class="landing-container">
        <img class="landing-logo" src="data:image/jpeg;base64,{encoded_image}">
        <div class="main-title">학원 평가 도우미</div>
    </div>
    """,
    unsafe_allow_html=True
)
