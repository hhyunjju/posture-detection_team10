from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
# from django.http import HttpResponse
# -----------
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import CSVLoader
import dotenv
dotenv.load_dotenv()
import time

persist_directory = str(settings.BASE_DIR)
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
        "You are a customer service agent for '바른자세 도우미' Web service. "
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

#-------AJAX 요청을 처리하는 뷰-----------------
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_http_methods(["POST", "GET"])
def chatbot_view(request):

    if request.method == "GET":
        request.session['chat_history'] = []  # 세션에 대화 히스토리 초기화
        # GET 요청 시, 챗봇 페이지 렌더링
        return render(request, 'chatbot/chatbot.html')

    if request.method == "POST":
        # POST 요청 처리 (AJAX 요청)
        data = json.loads(request.body)
        user_message = data['message']

        # 현재 세션에서 대화 히스토리 가져오기
        history = request.session.get('chat_history', [])
        
        # LangChain 챗봇 응답 로직
        ai_response = agent_executor({"input": user_message, "history": history})['output']
        # 새 대화 내용을 히스토리에 추가
        history.append((user_message, ai_response))
        request.session['chat_history'] = history  # 세션에 히스토리 업데이트
        
        # 응답 반환
        return JsonResponse({'response': ai_response})

