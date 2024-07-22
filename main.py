import streamlit as st
import os
import logging
from audiorecorder import audiorecorder
from datetime import datetime
import stt
import tts
import chat
import audio
import display

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

##### 메인 함수 #####

def main():
	st.set_page_config(page_title="음성 챗봇 프로그램", layout="wide")
	st.header("음성 챗봇 프로그램")
	st.markdown("---")

	with st.expander("음성 챗봇 프로그램에 관하여", expanded=True):
		st.write("""
		- 음성 번역 챗봇 프로그램의 UI는 스트림릿을 활용합니다.
		- STT(Speech-To-Text)는 OpenAI의 Whisper를 활용합니다.
		- 답변은 OpenAI의 GPT 모델을 활용합니다.
		- TTS(Text-To-Speech)는 OpenAI의 TTS를 활용합니다.
		""")

	system_content = "You are a thoughtful assistant. Respond to all input in 25 words and answer in korean"

	if "chat" not in st.session_state:
		st.session_state["chat"] = []
	if "messages" not in st.session_state:
		st.session_state["messages"] = [{"role": "system", "content": system_content}]
	if "check_reset" not in st.session_state:
		st.session_state["check_reset"] = False
	if "audio_file" not in st.session_state:
		st.session_state["audio_file"] = None

	with st.sidebar:
		model = st.radio(label="GPT 모델", options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
		st.markdown("---")
		if st.button(label="초기화"):
			st.session_state["chat"] = []
			st.session_state["messages"] = [{"role": "system", "content": system_content}]
			st.session_state["check_reset"] = True
			if st.session_state["audio_file"]:
				if os.path.exists(st.session_state["audio_file"]):
					os.remove(st.session_state["audio_file"])
				st.session_state["audio_file"] = None

	col1, col2 = st.columns(2)
	with col1:
		st.subheader("질문하기")
		audio_input = audiorecorder()
		if (audio_input.duration_seconds > 0) and (st.session_state["check_reset"] == False):
			st.audio(audio_input.export().read())
			question = stt.STT(audio_input)
			now = datetime.now().strftime("%H:%M")
			st.session_state["chat"].append(("user", now, question))
			st.session_state["messages"].append({"role": "user", "content": question})

	with col2:
		st.subheader("질문/답변")
		if (audio_input.duration_seconds > 0) and (st.session_state["check_reset"] == False):
			response = chat.ask_gpt(st.session_state["messages"], model)
			st.session_state["messages"].append({"role": "assistant", "content": response})
			now = datetime.now().strftime("%H:%M")
			st.session_state["chat"].append(("bot", now, response))

			display.display_chat()

			st.session_state["audio_file"] = tts.TTS(response)
			if st.session_state["audio_file"]:
				audio.play_audio(st.session_state["audio_file"])

				if st.button("다시 듣기"):
					audio.play_audio(st.session_state["audio_file"])
				if st.button("파일 삭제"):
					if os.path.exists(st.session_state["audio_file"]):
						os.remove(st.session_state["audio_file"])
					st.session_state["audio_file"] = None

		else:
			st.session_state["check_reset"] = False

if __name__ == "__main__":
	main()
