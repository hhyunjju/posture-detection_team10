from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# from django.http import HttpResponse
# -----------
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import CSVLoader
import dotenv
dotenv.load_dotenv()
import time

persist_directory = './'
embedding = OpenAIEmbeddings()

# load from disk
vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding)

retriever = vectorstore.as_retriever()

from langchain.agents.agent_toolkits import create_retriever_tool

tool = create_retriever_tool(
    retriever,
    "BarunJaseDowoomi_customer_service_guide",
    "Searches and returns information regarding the customer service guide.",
)
tools = [tool]

from langchain.chat_models import ChatOpenAI
llm = ChatOpenAI(temperature=0, model='gpt-3.5-turbo-1106')

# This is needed for both the memory and the prompt
memory_key = "history"

from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)

memory = AgentTokenBufferMemory(memory_key=memory_key, llm=llm)

from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder

system_message = SystemMessage(
    content=(
        "You are a customer service agent for '바른자세 도우미' Web application. "
        "Do your best to answer the questions within the scope of our service. "
        "Please do not provide answers that deviate from the subject matter. "
        "Feel free to use any tools available to look up "
        "relevant information, only if necessary"
        "If you don't know the answer, just say you don't know. Don't try to make up an answer."
        "Make sure to answer in Korean"
    )
)

prompt = OpenAIFunctionsAgent.create_prompt(
    system_message=system_message,
    extra_prompt_messages=[MessagesPlaceholder(variable_name=memory_key)],
)

agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    return_intermediate_steps=True,
)

# result = agent_executor({"input": "사용요금 조회는 어떻게 하죠"})
# result["output"]

# ----------- ㄴ---여기까지: langchain model 만들기 -------------

# GPT-3.5 모델과 히스토리를 기반으로 답변 생성하는 response 함수 정의------
from langchain.schema import AIMessage, HumanMessage, SystemMessage
def response(message, history, additional_input_info):
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    # 새로운 사용자 메시지 추가
    history_langchain_format.append(HumanMessage(content=message))
    
    # AgentExecutor를 사용하여 응답 생성
    result = agent_executor({"input": message, "history": history_langchain_format})
    
    # LangChain의 출력에서 AI의 마지막 메시지 가져오기
    ai_response = result['output']
    return ai_response

#-------AJAX 요청을 처리하는 뷰-----------------
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(["POST", "GET"])
def chatbot_view(request):
    if request.method == "GET":
        # GET 요청 시, 챗봇 페이지 렌더링
        return render(request, 'chatbot/chatbot.html')

    if request.method == "POST":
        # POST 요청 처리 (AJAX 요청)
        data = json.loads(request.body)
        user_message = data['message']

        # LangChain 챗봇 응답 로직
        ai_response = response(user_message, [], None)

        # 응답 반환
        return JsonResponse({'response': ai_response})

