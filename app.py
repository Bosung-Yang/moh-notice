import streamlit as st

st.title('명예훈장 공지 생성 봇')

if 'noticebtn' not in st.session_state:
    st.session_state.noticebtn = False

def handle_notice():
    st.session_state.noticebtn = True

with st.form(key='notice_form'):
    date = st.text_input('날짜', key='date')
    broad_time = st.text_input('방송시간', key='broad_time')
    want_say = st.text_input('할 말', key='want_say')
    todo = st.text_input('컨텐츠', key='todo')
    youtube = st.text_input('유튜브 업로드 영상', key='youtube')
    submit = st.form_submit_button('공지 작성')

if st.session_state.noticebtn:
    st.write(f'날짜: {date}')
    st.write(f'방송시간: {broad_time}')
    st.write(f'할 말: {want_say}')
    st.write(f'컨텐츠: {todo}')
    st.write(f'유튜브 업로드 영상: {youtube}')
    st.write('공지 작성 완료')