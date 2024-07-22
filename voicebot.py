import streamlit as st

import openai
import os

from audiorecorder import audiorecorder

from datetime import datetime
import base64

import tempfile
import uuid
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# OpenAI API 키 설정하기
api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=api_key)

##### 기능 구현 함수 #####
@st.cache_data(ttl=3600)  # 1시간 동안 캐시 유지
def STT(audio_data):
    try:
        # 고유한 파일 이름 생성
        temp_filename = f"{uuid.uuid4()}.mp3"
        speech.export(temp_filename, format="mp3")

        # OpenAI API를 사용하여 음성을 텍스트로 변환
        with open(temp_filename, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )

        # 임시 파일 삭제
        os.remove(temp_filename)
        return transcription.text
    except Exception as e:
        logging.error(f"STT 오류 발생: {e}")
        st.error(f"음성 인식 중 오류가 발생했습니다. 다시 시도해주세요.<br>{e}")
        return ""

@st.cache_data(ttl=3600)
def ask_gpt(prompt, model):
    try:
        # OpenAI API를 사용하여 GPT 모델로부터 응답 생성
        response = client.chat.completions.create(
            model=model, 
            messages=prompt
    )
    return response.choices[0].message.content
    except Exception as e:
        logging.error(f"GPT 오류 발생: {e}")
        st.error(f"GPT 응답 생성 중 오류가 발생했습니다. 다시 시도해주세요.")
        return ""

@st.cache_data(ttl=3600)
def TTS(text):
    try:
        # 고유한 파일 이름 생성
        filename = f"{uuid.uuid4()}.mp3"
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="nova",
            input=text
        ) as response:
            response.stream_to_file(filename)

        with open(filename, "wb") as f:
            f.write(response["audio_content"])
        return filename
    except Exception as e:
        logging.error(f"TTS 오류 발생: {e}")
        st.error(f"텍스트를 음성으로 변환하는 중 오류가 발생했습니다. 다시 시도해주세요.")
        return ""

def play_audio(filename):
    try:
        # 음성 파일을 읽어와서 Base64로 인코딩 후 재생
        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio controls>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        logging.error(f"오디오 재생 오류 발생: {e}")
        st.error(f"오디오 재생 중 오류가 발생했습니다. 다시 시도해주세요.")

def display_chat():
    # 채팅 내용을 화면에 표시
    for sender, time, message in st.session_state["chat"]:
        if sender == "user":
            st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', 
                     unsafe_allow_html=True)
        else:
            st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', 
                     unsafe_allow_html=True)

##### 메인 함수 #####
def main():
    st.set_page_config(page_title="음성 챗봇 프로그램", layout="wide")
    st.header("음성 챗봇 프로그램")
    st.markdown("---")

    # 프로그램에 대한 설명을 확장 가능한 섹션에 표시
    with st.expander("음성 챗봇 프로그램에 관하여", expanded=True):
        st.write("""     
        - 음성 번역 챗봇 프로그램의 UI는 스트림릿을 활용합니다.
        - STT(Speech-To-Text)는 OpenAI의 Whisper를 활용합니다. 
        - 답변은 OpenAI의 GPT 모델을 활용합니다. 
        - TTS(Text-To-Speech)는 OpenAI의 TTS를 활용합니다.
        """)

    # 시스템 초기 메시지 설정
    system_content = "You are a thoughtful assistant. Respond to all input in 25 words and answer in korean"
    
    # 세션 상태 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"] = []
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": system_content}]
    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False
    if "audio_file" not in st.session_state:
        st.session_state["audio_file"] = None

    # 사이드바 구성
    with st.sidebar:
        # GPT 모델 선택 라디오 버튼
        model = st.radio(label="GPT 모델", options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
        st.markdown("---")
        # 초기화 버튼
        if st.button(label="초기화"):
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system", "content": system_content}]
            st.session_state["check_reset"] = True
            if st.session_state["audio_file"]:
                os.remove(st.session_state["audio_file"])
                st.session_state["audio_file"] = None

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("질문하기")
        audio = audiorecorder()
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"]==False):
            audio_data = audio.export().read()
            st.audio(audio_data)
            question = STT(audio_data)
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"].append(("user", now, question))
            st.session_state["messages"].append({"role": "user", "content": question})

    with col2:
        st.subheader("질문/답변")
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"]==False):
            response = ask_gpt(tuple(st.session_state["messages"]), model)
            st.session_state["messages"].append({"role": "assistant", "content": response})
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"].append(("bot", now, response))

            display_chat()
            
            st.session_state["audio_file"] = TTS(response)
            if st.session_state["audio_file"]:
                play_audio(st.session_state["audio_file"])

                if st.button("다시 듣기"):
                    play_audio(st.session_state["audio_file"])
                if st.button("파일 삭제"):
                    os.remove(st.session_state["audio_file"])
                    st.session_state["audio_file"] = None
                    
        else:
            st.session_state["check_reset"] = False

if __name__=="__main__":
    main()
