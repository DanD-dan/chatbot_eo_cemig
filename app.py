import time
import openai
from dotenv import find_dotenv, load_dotenv
import streamlit as st

# Carregar variáveis de ambiente
_ = load_dotenv(find_dotenv())

client = openai.Client()

# IDs dos assistentes e vector store
vector_store_id = "vs_Br4EKmbwd6ivBxoDor4zfpxh"
assistant_id = "asst_HYy30iBYGiLODLmzv0OaxkWE"

# Função para criar uma nova thread de conversa
def criar_thread():
    return client.beta.threads.create()

# Função para enviar a mensagem ao assistente e obter a resposta
def enviar_mensagem(thread_id, assistant_id, mensagem_usuario, imagem=None):
    conteudo = [{"type": "text", "text": mensagem_usuario}]

    # Se uma imagem foi enviada, adiciona ao conteúdo
    if imagem:
        conteudo.append({
            "type": "image_file",
            "image_file": {
                "file_id": client.files.create(file=imagem, purpose="vision").id
            }
        })

    # Enviar a mensagem (com ou sem imagem)
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=conteudo
    )

    # Criar o "run" para processar a mensagem
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    # Aguardar até o processamento estar completo
    while run.status in ["queued", "in_progress", "cancelling"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

    # Verificar se o processamento foi concluído
    if run.status == "completed":
        mensagens = client.beta.threads.messages.list(thread_id=thread_id)
        return list(mensagens)[0].content[0].text.value
    else:
        return f"Erro: {run.status}"

# Função principal do chatbot para Streamlit
def main():
    st.title("Chatbot CEMIG")

    # Inicializar a thread do chatbot (uma por sessão)
    if 'thread_id' not in st.session_state:
        st.session_state['thread_id'] = criar_thread().id

    # Inicializar o histórico de mensagens
    if 'historico' not in st.session_state:
        st.session_state['historico'] = []

    # Entrada de texto
    input_usuario = st.text_input("Você: ", "")

    # Upload de imagem
    imagem_usuario = st.file_uploader("Enviar imagem (opcional):", type=["png", "jpg", "jpeg"])

    # Botão de envio
    if st.button("Enviar"):
        if input_usuario or imagem_usuario:
            st.session_state['historico'].insert(0, f"<p style='background-color:#ADD8E6;padding:10px;border-radius:5px;'><strong>Você:</strong> {input_usuario}</p>")

            resposta = enviar_mensagem(
                st.session_state['thread_id'],
                assistant_id,
                input_usuario,
                imagem=imagem_usuario
            )

            st.session_state['historico'].insert(0, f"<p><strong>Chatbot:</strong> {resposta}</p>")

    # Exibir histórico em ordem decrescente
    for mensagem in st.session_state['historico']:
        st.markdown(mensagem, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
