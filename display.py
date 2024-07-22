import streamlit as st

def display_chat():
	for sender, time, message in st.session_state["chat"]:
		if sender == "user":
			st.write(
				f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>',
				unsafe_allow_html=True
			)
		else:
			st.write(
				f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>',
				unsafe_allow_html=True
			)