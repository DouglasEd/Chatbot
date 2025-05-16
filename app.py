from flask import Flask, request, jsonify
from decouple import config
from datetime import datetime
from comandos.comandos_adm import ComandosAdm
from bot.ai_bot import AIBot
from services.waha import Waha
from comandos.comandos_adm import ComandosAdm


app = Flask(__name__)
numero_suporte= config('NUMERO_SUPORTE')

@app.route('/chatbot/webhook/', methods=['POST'])
def webhook():
    data = request.json
    try:
        payload = data.get('payload', {})
        chat_id = payload.get('from')
        hasmedia = payload.get('hasMedia')
        received_message = payload.get('body')

        # Verificando se os dados essenciais estão presentes
        if not chat_id:
            return jsonify({'status': 'error', 'message': 'Campos obrigatórios ausentes.'}), 400
    except Exception as e:
        print(f"Erro ao extrair dados: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Erro ao extrair dados: {str(e)}'}), 400

    is_group = '@g.us' in chat_id
    if is_group:
        return jsonify({'status': 'success', 'message': 'Mensagem de grupo ignorada.'}), 200
    
    try:
        if ComandosAdm.verificar_numero_parado(chat_id[:-5]):
            return jsonify({'status': 'success'}), 200
        else:
            
            if received_message.startswith('/') and chat_id[:-5] == numero_suporte:
                ComandosAdm.comandos(received_message)
                return jsonify({'status': 'success'}), 200
            
            waha = Waha()
            ai_bot = AIBot()
            
            waha.start_typing(chat_id=chat_id)
            
            if hasmedia:
                mensagem= (
                    f"Bom dia! No momento, nosso chatbot só entende mensagens de texto. Ele não consegue processar imagens, vídeos ou áudios."
                )
                waha.send_message(chat_id=chat_id,message=mensagem)
                waha.stop_typing(chat_id=chat_id)
                return jsonify({'status': 'success'}), 200
            
            history_messages = waha.get_history_messages(chat_id=chat_id, limit=10)
            response_message, enviar_para_suporte = ai_bot.invoke(history_messages=history_messages, question=received_message)
            

            if not response_message:
                return jsonify({'status': 'error', 'message': 'Resposta do bot inválida.'}), 500
            if enviar_para_suporte:
                data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                mensagem = (
                    f"[BOT - Encaminhamento Automático]\n"
                    f"Data/Hora: {data_hora}\n"
                    f"Usuário: {chat_id[:-5]}\n"
                    f"Mensagem original: \"{received_message}\"\n"
                    f"A resposta não foi encontrada pelo assistente. Verificar e responder manualmente."
                )
                if int(datetime.now().strftime('%H'))>=8 and int(datetime.now().strftime('%H'))<=12:
                    ComandosAdm.comandos(f'/stop {chat_id[:-5]}')
                waha.send_message(chat_id=f'{numero_suporte}@c.us', message=mensagem)
            waha.send_message(chat_id=chat_id, message=response_message)
            waha.stop_typing(chat_id=chat_id)

            return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Erro ao processar mensagem: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Erro ao processar mensagem: {str(e)}'}), 500
