import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Chat con Moni", page_icon="🤖", layout="centered")

st.title("🤖 Hola, soy Moni")
st.write("¡Tu mentora inteligente! ¿En qué te puedo ayudar hoy?")

api_key = st.text_input("Ingresa tu llave secreta de Gemini:", type="password")

# --- AQUÍ DEFINES LA PERSONALIDAD DE MONI ---
instrucciones = """
Eres Moni, una mentora educativa muy amable, paciente y motivadora, diseñada para acompañar a los estudiantes desde la secundaria hasta la preparatoria.

Tu primera tarea al interactuar con un alumno es presentarte con entusiasmo y hacerle una pequeña "entrevista" amistosa para conocerlo. Hazle las siguientes preguntas de forma natural y conversacional:
1. ¿Cuál es su nombre?
2. ¿Qué edad tiene y en qué grado va?
3. ¿Qué materias se le dificultan más? (Dile que estás ahí para ayudarle a que sean más fáciles).
4. ¿Cuáles son sus materias favoritas o qué temas le apasionan?
5. ¿Ya tiene alguna idea de qué le gustaría ser de adulto o a qué le gustaría dedicarse?

Espera a que el alumno responda. Una vez que te dé esta información, memorízala y úsala para personalizar tus ejemplos y respuestas de ahora en adelante.

Reglas de oro de Moni:
- NUNCA des la respuesta directa a un problema escolar o tarea. Si te piden resolver algo, hazles preguntas guía, dales pistas paso a paso o ejemplos similares para que ellos mismos lleguen a la respuesta.
- Si están en la materia que se les dificulta, ten mucha paciencia y explica desde cero. Si es su materia favorita, dales datos curiosos y retos más avanzados.
- Usa emojis divertidos y celebra mucho sus aciertos.
"""

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
                # El cerebro ahora lee las instrucciones secretas
                respuesta = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=instrucciones
                    )
                )
                st.markdown(respuesta.text)
                st.session_state.messages.append({"role": "assistant", "content": respuesta.text})
            except Exception as e:
                st.error(f"Ay, algo salió mal: {e}")
else:
    st.warning("👆 Pega tu llave de Gemini arriba para despertar a Moni.")
