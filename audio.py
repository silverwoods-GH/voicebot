import streamlit as st
import base64
import os
import logging

def play_audio(filename):
	try:
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
		st.error(f"오디오 재생 중 오류가 발생했습니다. 다시 시도해주세요.<br>{e}")