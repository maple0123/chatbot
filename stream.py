import streamlit as st
import requests
import json
import time

# 设置页面布局模式为宽屏
st.set_page_config(layout="wide")

st.title("Chatbot")

bot_welcome_message = {
    "role": "assistant",
    "content": """你好，我是一个智能的对话机器人，也是本次测验的主考官。
    接下来的评估有些特别的是我们将通过对话的形式进行，我将在每道题后给予即时的反馈。
    放轻松，让我们开始吧。在测试开始之前，请告诉我你的姓名。"""
}

questions = [
    {"title": """下列句子中被括号括起来的词语使用不恰当的一项是<br>
    A.岁月可能会模糊记忆，但英雄的名字永远（镌刻）在历史的丰碑上，铭记于人们心中。<br>
    B.对于网络词语的使用，有人极力排斥，有人欣然接受，更多的人保持着（谨慎）的态度<br>
    C.无数科技工作者默默奉献，（殚精竭虑），无怨无悔，创造了我国航天事业的辉煌<br>
    D.电视连续剧《人世间》的演员把角色演绎得真实可信，（栩栩如生），深受观众好评""", "image": None},
    {"title": """阅读下列材料，完成问题<br>
    段直字正卿，泽州晋城人。至元十一年，河北、河东、山东盗贼充斥，直聚其乡党族属，结垒自保。世祖命大将略地晋城，直以其众归之，幕府承制，署直潞州元帅府右监军。其后论功行赏，分土世守，命直佩金符，为泽州长官。<br>
    泽民多避兵未还者，直命籍其田庐于亲戚邻人之户，且约曰:“俟业主至，当析而归之，逃民闻之多来还者命归其田庐如约民得安业。素无产者，则出粟赈之:为他郡所俘掠者，出财购之:以兵死而暴露者，收而瘗之。<br>
    未几，泽为乐土。""", "image": None}
]

models = ['gpt-4-gizmo-g-Iyo44m2HS','gpt-4-gizmo-g-jPmOrTDmw']
headers = {
    "Authorization": "Bearer sk-yF53eKUK0CpyVTnxIAXifrkEg2I0Yff18En9GwAfpsDo7luC"
}

if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
    st.session_state.all_history = []

if 'history' not in st.session_state or not st.session_state.history:
    st.session_state.history = [bot_welcome_message]

col1, col2= st.columns([1,1])

with col1:
    question = questions[st.session_state.current_question_index]
    st.markdown(question["title"], unsafe_allow_html=True)
    if question["image"]:
        st.image(question["image"], use_column_width=True)

with col2:
    messages_placeholder = st.empty()

    with messages_placeholder.container(height=400):
        for message in st.session_state.history:
            with st.chat_message(message['role']):
                st.markdown(f"{message['content']}")

    input_text = st.chat_input("你的回答 ", key="input_text")

    def get_response(input_text):
        st.session_state.history.append({"role": "user", "content": input_text})

        messages = st.session_state.history
        model = models[st.session_state.current_question_index]
        data = {
            'model': "gpt-3.5-turbo-16k",
            'messages': messages,
            'stream': True
        }

        response = requests.post('https://api.gptgod.online/v1/chat/completions', headers=headers, json=data, stream=True)

        message = ""
        ai_reply = {"role": "assistant", "content": ""}
        st.session_state.history.append(ai_reply)

        messages_placeholder.empty()
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')

                if decoded_line == 'data: [DONE]':
                    break

                if decoded_line.startswith('data: '):
                    data_str = decoded_line.replace('data: ', '')
                    data_json = json.loads(data_str)
                    content = data_json['choices'][0]['delta'].get('content', '')
                    message += f'{content}'
                    ai_reply["content"] += f'{content}'

                    with messages_placeholder.container(height=400):
                        for msg in st.session_state.history:
                            with st.chat_message(msg['role']):
                                st.markdown(f"{msg['content']}")
                    time.sleep(0.05)  # 模拟人类打字速度

    def show_history():
        with messages_placeholder.container(height=400):
            for message in st.session_state.history:
                with st.chat_message(message['role']):
                    st.markdown(f"{message['content']}")

    if input_text:
        get_response(input_text)
        show_history()

    st.markdown("""
    <style>
    .css-button {
        position: relative;
        left:50px;  /* 调整这个值来控制位置 */
        top:50px;   /* 调整这个值来控制位置 */
    }
    </style>
    """, unsafe_allow_html=True)
    
    last_question = (st.session_state.current_question_index == len(questions) - 1)
    button_label = "完成考试" if last_question else "下一题"
    if st.button(button_label):
        st.session_state.all_history.append(st.session_state.history)
        st.session_state.history = []
        get_response("你好")
        show_history()
        if last_question:
            with open('chat_history.txt', 'w') as f:
                for idx, history in enumerate(st.session_state.all_history):
                    f.write(f"题目{idx + 1}的聊天记录:\n")
                    for msg in history:
                        f.write(f"{msg['role']}: {msg['content']}\n")
                    f.write("\n")
            st.success("考试完成！聊天记录已保存到文件。")
        else:
            st.session_state.current_question_index += 1
            st.experimental_rerun()
            
    st.markdown('<div class="custom-button"></div>', unsafe_allow_html=True)
