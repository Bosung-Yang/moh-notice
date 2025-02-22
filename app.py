import streamlit as st

import pandas as pd
import os
import mykey
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts import PromptTemplate
os.environ['OPENAI_API_KEY'] = mykey.my_openai()

from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter


model = ChatOpenAI(
    model= 'gpt-4o', #"gpt-3.5-turbo",
    max_tokens=2048,
    temperature=0.1,
)
loader = TextLoader('pp-notice.csv')
docs = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=10)
embeddings = OpenAIEmbeddings()
split_docs = text_splitter.split_documents(docs)
db = FAISS.from_documents(split_docs, embeddings)
retreieved = db.as_retriever()

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

df = pd.read_csv('pp-notice.csv')

examples = []

for i in range(len(df[:30]) ):
    examples.append(
        {
            'instruction' : '다음 내용들로 명훈 스타일 공지를 작성해주세요',
            'notice_date' : df['notice_date'].iloc[i],
            'broad_time' : df['broad_time'].iloc[i],
            'want_say' : df['want_say'].iloc[i],
            'todo' : df['todos'].iloc[i],
            'youtube': df['youtube'].iloc[i],
            'answer': df['content'].iloc[i]
        }
    )

example_prompt = PromptTemplate.from_template(
    """instruction: {instruction} 
    notice_date: {notice_date}
    broad_time: {broad_time}
    want_say : {want_say}
    todo: {todo}
    youtube: {youtube}
    answer: {answer}
    """
)

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="instruction: \n {instruction} \n notice_date: {notice_date} \n broad_time: {broad_time} \n want_say : {want_say} \n todo: {todo} \n youtube: {youtube} \n answer:",
    input_variables=["instruction", "notice_date", "broad_time", "todo", "youtube"],
)

chain = (
    {"context": retreieved, "instruction": RunnablePassthrough(), "notice_date" : RunnablePassthrough(), \
     "broad_time" : RunnablePassthrough(), "want_say" : RunnablePassthrough(), "todo" : RunnablePassthrough(),\
     "youtube" : RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

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

answer = chain.invoke(
    f"instruction : 다음 내용들로 명훈 스타일 공지를 작성해주세요. \
             notice_date : {date} \
             broad_time : {broad_time} \
             want_say : {want_say}\
             todo : {todo} \
             youtube : {youtube}")

st.write(answer)
