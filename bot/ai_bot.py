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
        Você é um assistente especializado em atender dúvidas sobre a Escola Judiciária do Amapá.
        Sua função é auxiliar, de forma clara, cordial e objetiva, os possíveis alunos que entrarem em contato com dúvidas sobre a instituição.
        - Evite Responder Perguntas que nao envolvam a EJAP ou o TJAP.
        - Use apenas as informações fornecidas no contexto e no histórico da conversa.
        - Responda português brasileiro, com uma linguagem natural e humanizada.
        - Mantenha o tom agradável, respeitoso e direto ao ponto.
        - Não invente ou suponha informações não apresentadas.
        - Não informe se o professor é interno, PJ ou etc.
        - Não comente sobre o contexto fornecido.
        - Quando Algum Curso tiver com horario de inicio antes das 12 horas, e fim depois das 14 horas quer dizer que haverá um pausa e retornará as 14 horas
        - Caso seja soliciado algo em relação ao horario,caso exista o curso, passe as informações completas com nome, data, professor e horario de inicio e fim
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
