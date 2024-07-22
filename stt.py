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

def save_temp_audio(audio):
	temp_filename = f"{uuid.uuid4()}.mp3"
	audio.export(temp_filename, format="mp3")
	return temp_filename

def transcribe_audio(temp_filename):
	with open(temp_filename, "rb") as audio_file:
		transcription = client.audio.transcriptions.create(
			model="whisper-1",
			file=audio_file
		)
	return transcription.text

def STT(audio):
	try:
		temp_filename = save_temp_audio(audio)
		text = transcribe_audio(temp_filename)
		os.remove(temp_filename)
		return text
	except Exception as e:
		logging.error(f"STT 오류 발생: {e}")
		raise ValueError(f"음성 인식 중 오류가 발생했습니다. 다시 시도해주세요.<br>{e}")