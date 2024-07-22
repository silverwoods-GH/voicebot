import openai
import os
import logging

# OpenAI API 키 설정하기
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
	raise ValueError("OpenAI API 키가 설정되지 않았습니다. 환경 변수를 확인하세요.")
else:
	client = openai.OpenAI(api_key=api_key)

def ask_gpt(messages, model):
	try:
		response = client.chat.completions.create(
			model=model,
			messages=messages
		)
		return response.choices[0].message.content
	except Exception as e:
		logging.error(f"GPT 오류 발생: {e}")
		raise ValueError(f"GPT 응답 생성 중 오류가 발생했습니다. 다시 시도해주세요.<br>{e}")