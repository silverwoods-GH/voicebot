import openai
import os
import uuid
import logging

# OpenAI API 키 설정하기
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
	raise ValueError("OpenAI API 키가 설정되지 않았습니다. 환경 변수를 확인하세요.")
else:
	client = openai.OpenAI(api_key=api_key)

def synthesize_speech(text):
	try:
		response = client.audio.speech.create(
			model="tts-1",
			voice="nova",
			input=text
		)
		temp_filename = f"{uuid.uuid4()}.mp3"
		response.stream_to_file(temp_filename)
		return temp_filename
	except Exception as e:
		logging.error(f"TTS 오류 발생: {e}")
		raise ValueError(f"텍스트를 음성으로 변환하는 중 오류가 발생했습니다. 다시 시도해주세요.<br>{e}")

def TTS(text):
	return synthesize_speech(text)