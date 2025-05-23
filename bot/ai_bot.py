import os

from decouple import config

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from datetime import datetime
import traceback

os.environ['GROQ_API_KEY'] = config('GROQ_API_KEY')


class AIBot:

    def __init__(self):
        try:
            self.__chat = ChatGroq(model='meta-llama/llama-4-scout-17b-16e-instruct')
            self.__retriever = self.__build_retriever()
        except Exception as e:
            print("Erro ao iniciar AIBot:", e)
            traceback.print_exc()
            raise e
    
    def __build_retriever(self):
        try:
            persist_directory = '/app/chroma_data'
            embedding = HuggingFaceEmbeddings()

            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embedding,
            )
            return vector_store.as_retriever(search_kwargs={'k': 10})

        except Exception as e:
            print("Erro ao construir o retriever:", e)
            traceback.print_exc()
            raise e
            
    def __build_messages(self, history_messages, question):
        messages = []
        for message in history_messages:
            message_class = HumanMessage if message.get('fromMe') else AIMessage
            messages.append(message_class(content=message.get('body')))
        messages.append(HumanMessage(content=question))
        return messages

    def invoke(self, history_messages, question):
        INDICADORES_FALHA = [
            "não tenho essa informação",
            "não encontrei dados",
            "não sei responder",
            "não posso ajudar com isso",
            "não foi possível localizar",
            "desculpe",
            "lamento",
            "suporte"
        ]
        enviar_suporte= False
        data_hoje = f"Hoje é {datetime.now().strftime('%d/%m/%Y')}\n"
        SYSTEM_TEMPLATE = data_hoje + '''
        Template Comportamental do bot
        <context>
        {context}
        </context>
        '''

        docs = self.__retriever.invoke(question)
        question_answering_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    SYSTEM_TEMPLATE,
                ),
                MessagesPlaceholder(variable_name='messages'),
            ]
        )
        document_chain = create_stuff_documents_chain(self.__chat, question_answering_prompt)
        response = document_chain.invoke(
            {
                'context': docs,
                'messages': self.__build_messages(history_messages, question),
            }
        )
        if any(f in response.lower() for f in INDICADORES_FALHA):
            enviar_suporte = True
            resposta_padrao = (
                "Não encontrei uma resposta para sua pergunta neste momento. "
                "Encaminharei sua solicitação para o suporte. Por favor, aguarde alguns minutos."
                "Nosso horário de atendimento é das 8h às 12h30."
            )
            return resposta_padrao, enviar_suporte
        return response, enviar_suporte
