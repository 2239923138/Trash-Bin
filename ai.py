from flask import Flask, render_template, request
from openai import OpenAI
import os
from pathlib import Path

api_key = os.environ["DEEPSEEK_API_KEY"]
client = OpenAI(base_url="https://api.deepseek.com", api_key=api_key)

def retrieval(query):
    context = ""
    path_list = list(Path("my_knowledge").glob("*.txt"))
    for path in path_list:
        if path.stem in query:
            context += path.read_text(encoding="utf-8") 
            context += "\n\n"
    return context

def augmented(query, context=""):
    if not context:
        return f"请回答下面问题:{query}，如果问题与计算机编程算法无关，请让我问重新问与算法相关的问题,如果有关，请回答我，要求：生成一段话即可，尽量简洁，最后给出一个相关网站的网页让我深入学习。"
    else:
        prompt = f"""请根据上下文信息回答问题，如果上下文信息不足以回答问题，请直接说“根据上下文的信息我无法回答”
        上下文:
        {context}

        问题：{query}"""
        return prompt

def generation(prompt):
    completion = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content

app = Flask(__name__)

def get_answer(question):
    context = retrieval(question)
    prompt = augmented(question, context)
    return generation(prompt)

@app.route('/', methods=['GET', 'POST'])
def index():
    query = None
    answer = None
    if request.method == 'POST':
        query = request.form.get('query')  # 获取前端输入的问题
        if query:
            answer = get_answer(query)  # 调用回答逻辑生成回应
    # 渲染模板，把问题和回答传给前端页面
    return render_template('ai_.html', query=query, answer=answer)

if __name__ == '__main__':
    app.run(debug=True)  # 调试模式，方便开发时看报错，生产环境需调整
