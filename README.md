# 🤖 Chatbot Inteligente para WhatsApp

Este projeto é um **chatbot inteligente para WhatsApp**, desenvolvido com o framework **WAHA (WhatsApp HTTP API)**, que permite integrar bots ao WhatsApp por meio de uma API local.  

O chatbot possui integração com modelos de linguagem da **Groq** (para respostas extremamente rápidas) e com a **plataforma Hugging Face**, utilizando **IA generativa** para compreensão de linguagem natural, análise de intenção e respostas mais humanas.

Essa arquitetura híbrida oferece um atendimento automatizado mais preciso, rápido e flexível — ideal para sistemas de **suporte técnico**, **registro de chamados**, **FAQ** e muito mais.

---

## ⚙️ Configuração Inicial

### 1. Clone o Repositório

```bash
git clone https://github.com/DouglasEd
cd seu-projeto
```

### 2. Configure o Ambiente

#### Linux:

```bash
cp .env.example .env
```

#### Windows:

```cmd
copy .env.example .env
```

### 3. Obtenha os Tokens

- Crie uma conta na [Groq](https://groq.com) e na [Hugging Face](https://huggingface.co).
- Gere os **tokens de API** de cada serviço.
- Preencha os campos correspondentes no arquivo `.env`.

Também no `.env`, informe o **número de telefone de fallback** — este será o número que receberá as mensagens que o bot não conseguir responder (ex: dúvidas fora do contexto ou problemas técnicos).

---

## 🐳 Executando com Docker

### 1. Inicie o WAHA

```bash
docker compose up waha
```

Depois, acesse a interface do WAHA, vá até a seção de **Sessões** e escaneie o **QR Code** com o WhatsApp que será usado no bot.

### 2. Inicie a API do Bot

```bash
docker compose up api
```

Pronto! Agora todas as mensagens recebidas no WhatsApp serão processadas pela API e respondidas automaticamente usando o modelo da Groq.

---

## ✨ Personalização

### Template Comportamental

No arquivo `/bot/ai-bot.py`, localize o seguinte trecho:

```python
<context>
{context}
</context>
'''
```

Altere o conteúdo para definir o **comportamento do bot**, por exemplo:

```text
Você é um tradutor de português para alemão.
```

Além disso, você pode trocar o modelo utilizado alterando esta linha:

```python
self.__chat = ChatGroq(model='meta-llama/llama-4-scout-17b-16e-instruct')
```

Você pode usar qualquer modelo compatível com a Groq ou Hugging Face.

---

## 📚 Configuração de Contexto (RAG)

Se quiser que o chatbot use documentos como **base de conhecimento**, adicione os arquivos na pasta:

```bash
/rag/data/
```

Exemplo: documentos com informações institucionais, cronogramas de eventos, cardápios, etc.

Depois, execute o comando abaixo para que o sistema faça o **processamento semântico (RAG)** dos documentos:

```bash
python /app/rag/rag.py
```

O conteúdo será usado como contexto para que o bot possa responder perguntas específicas.

---

## ✅ Status

- [x] Integração com WhatsApp via WAHA  
- [x] Conexão com modelos da Groq e Hugging Face  
- [x] Suporte a RAG (Retrieval-Augmented Generation)  
- [x] Docker Compose para execução simplificada  
- [x] Personalização de contexto e comportamento  

---

## 👨‍💻 Autor

Desenvolvido por **Douglas Édipo**  
🔗 https://www.linkedin.com/in/douglas-edipo-correa-batista-152842231/ </br>
✉️ douglas.edipo3@gmail.com
