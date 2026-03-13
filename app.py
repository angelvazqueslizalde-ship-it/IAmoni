import streamlit as st
from google import genai

st.set_page_config(page_title="Chat con Moni", page_icon="🤖", layout="centered")

st.title("🤖 Hola, soy Moni")
st.write("¡Tu mentora inteligente! ¿En qué te puedo ayudar hoy?")

api_key = st.text_input("Ingresa tu llave secreta de Gemini:", type="password")

if api_key:
    client = genai.Client(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Escribe tu mensaje aquí...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            try:
                # El cerebro actualizado de Google
                respuesta = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                st.markdown(respuesta.text)
                st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
            except Exception as e:
                st.error(f"Ay, algo salió mal: {e}")
else:
    st.warning("👆 Pega tu llave de Gemini arriba para despertar a Moni.")
