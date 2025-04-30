import os
import time
import streamlit as st
from openai import OpenAI

# Inicializar o cliente com a API key vinda dos secrets
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# IDs dos assistentes
assistant_id = "asst_HYy30iBYGiLODLmzv0OaxkWE"  # substitua pelo seu se necessário

# Cria uma nova thread de conversa
def criar_thread():
    return client.beta.threads.create()

# Envia mensagem (com ou sem imagem) e retorna resposta
def enviar_mensagem(thread_id, assistant_id, mensagem_usuario, imagem=None):
    conteudo = [{"type": "text", "text": mensagem_usuario}]

    if imagem:
        uploaded_file = client.files.create(file=imagem, purpose="vision")
        conteudo.append({
            "type": "image_file",
            "image_file": {"file_id": uploaded_file.id}
        })

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=conteudo
    )

    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

    while run.status in ["queued", "in_progress"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    if run.status == "completed":
        mensagens = client.beta.threads.messages.list(thread_id=thread_id)
        return list(mensagens)[0].content[0].text.value
    else:
        return f"Erro: {run.status}"

# Interface com Streamlit
def main():
    st.title("🤖 Chatbot CEMIG")

    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = criar_thread().id
    if "historico" not in st.session_state:
        st.session_state["historico"] = []

    input_usuario = st.text_input("Você:")
    imagem_usuario = st.file_uploader("Enviar imagem (opcional):", type=["png", "jpg", "jpeg"])

    if st.button("Enviar"):
        if input_usuario or imagem_usuario:
            st.session_state["historico"].insert(0, f"<p style='background-color:#ADD8E6;padding:10px;border-radius:5px;'><strong>Você:</strong> {input_usuario}</p>")

            resposta = enviar_mensagem(
                st.session_state["thread_id"],
                assistant_id,
                input_usuario,
                imagem=imagem_usuario
            )

            st.session_state["historico"].insert(0, f"<p><strong>Chatbot:</strong> {resposta}</p>")

    for msg in st.session_state["historico"]:
        st.markdown(msg, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
