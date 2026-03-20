import streamlit as st
from google import genai
from google.genai import types
import json
import os
import re
import hashlib
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image
import io

st.set_page_config(
    page_title="Moni – Tu Mentora IA",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

PERFILES_DIR = "perfiles"
os.makedirs(PERFILES_DIR, exist_ok=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background: linear-gradient(135deg, #e8f4f8 0%, #fef9ef 50%, #f0f0ff 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #161b22 100%); }
[data-testid="stSidebar"] * { color: #e6edf3 !important; }
[data-testid="stSidebar"] hr { border-color: #30363d !important; }
.card {
    background: white; border-radius: 16px; padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07); margin-bottom: 12px;
    border: 1px solid rgba(0,0,0,0.06);
}
.card-dark {
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 12px 16px; margin-bottom: 8px;
}
.titulo-moni {
    font-size: 2.4rem; font-weight: 900;
    background: linear-gradient(90deg, #0ea5e9, #8b5cf6, #ec4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1;
}
.badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.3px; }
.badge-niv  { background:#fff0f0; border:1.5px solid #f87171; color:#dc2626 !important; }
.badge-prof { background:#f0fff4; border:1.5px solid #4ade80; color:#16a34a !important; }
.badge-voc  { background:#faf0ff; border:1.5px solid #c084fc; color:#7c3aed !important; }
.badge-gen  { background:#f0f9ff; border:1.5px solid #60a5fa; color:#2563eb !important; }
.badge-pts  { background:#fffbeb; border:1.5px solid #f59e0b; color:#b45309 !important; }
.hero { text-align: center; padding: 60px 20px 40px; }
.hero-sub { font-size: 1.15rem; color: #64748b; margin: 8px 0 40px; }
.role-card {
    background: white; border: 2px solid #e2e8f0; border-radius: 20px;
    padding: 30px 40px; text-align: center; min-width: 200px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}
.role-icon  { font-size: 3rem; margin-bottom: 10px; }
.role-title { font-size: 1.1rem; font-weight: 800; color: #1e293b; }
.role-desc  { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }
.metric-box { background: white; border-radius: 14px; padding: 16px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.metric-num   { font-size: 2rem; font-weight: 900; color: #0ea5e9; }
.metric-label { font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
button[kind="secondary"] {
    border-radius: 10px !important; border: 1.5px solid #ef4444 !important;
    color: #ef4444 !important; font-weight: 700 !important; background: #fff5f5 !important;
}
button[kind="secondary"]:hover { background: #fef2f2 !important; border-color: #dc2626 !important; }
[data-testid="collapsedControl"] {
    position: fixed !important; top: 15px !important; left: 15px !important;
    background-color: #0ea5e9 !important; border-radius: 8px !important;
    padding: 6px !important; z-index: 999999 !important; display: flex !important;
    visibility: visible !important; opacity: 1 !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important; cursor: pointer !important;
}
[data-testid="collapsedControl"] svg { fill: white !important; color: white !important; width: 26px !important; height: 26px !important; }
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span, [data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] strong, [data-testid="stChatMessage"] em,
[data-testid="stChatMessage"] code { color: #1e293b !important; }
[data-testid="stChatMessage"] {
    background: white !important; border-radius: 14px !important;
    padding: 10px 16px !important; margin-bottom: 8px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatMessage"][data-testid*="user"] { background: #f0f9ff !important; }
.stMarkdown p, .stMarkdown li, .stMarkdown span { color: #1e293b !important; }
section[data-testid="stMain"] p { color: #1e293b !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  PROMPT DE MONI
# ═══════════════════════════════════════════════
INSTRUCCIONES_MONI = """
Eres Moni, una mentora educativa IA muy amable, paciente y motivadora. Acompañas a estudiantes mexicanos de secundaria y preparatoria (12-18 años). Tu objetivo es que cada alumno aprenda mejor y, al terminar la prepa, pueda elegir su carrera con evidencia real.

INICIO DE SESION
Ya conoces el nombre y grado del alumno porque se registro. Saludalo por su nombre desde el primer mensaje. Si es su primera vez, hazle la entrevista inicial de forma natural y conversacional:
1. Que materias se te dificultan mas? (con empatia, no juicio)
2. Cuales son tus materias favoritas o que temas te apasionan?
3. Ya tienes idea de que carrera te gustaria estudiar?

CONTEXTO MEXICANO — MUY IMPORTANTE
Siempre que puedas, usa ejemplos de la vida cotidiana mexicana para explicar conceptos:
- Matematicas: "Imaginate que vas al tianguis y tienes que calcular el cambio de 200 pesos..."
- Historia: "Como cuando los Aztecas usaban el sistema vigesimal para contar..."
- Fisica: "Como la trayectoria de un balon en un partido de futbol..."
- Quimica: "Como cuando el molcajete tritura especias y cambia su forma fisica..."
- Biologia: "Como los nopales del desierto que guardan agua para sobrevivir..."
- Tabasco: Menciona el rio Grijalva, el cacao, el chocolate, la selva lacandona cuando sea relevante.
Adapta los ejemplos al contexto cultural mexicano. Esto hace que el aprendizaje sea mas relevante y cercano.

MODOS DE OPERACION (detectalos automaticamente)

MODO NIVELACION — activado cuando el alumno pregunta sobre una materia dificil o muestra confusion:
- Escribe exactamente al inicio: "📚 Modo nivelación activado ✨"
- Usa la TECNICA SOCRATICA: en lugar de explicar directamente, responde con preguntas que obliguen al alumno a pensar con lo que ya sabe:
  * "Que crees que pasaria si...?"
  * "Ya viste algo parecido en tu vida diaria?"
  * "Si tuvieras que explicarselo a un amigo, por donde empezarias?"
  * "Que parte del problema ya entiendes?"
- Divide el problema en pasos pequenos mediante preguntas guia.
- NUNCA des la respuesta directa. Guia con preguntas y ejemplos del contexto mexicano.
- Celebra cada avance con mucho entusiasmo.
- Si tras 2 intentos el alumno sigue sin entender, cambia completamente tu estrategia de preguntas.

MODO PROFUNDIZACION — activado cuando el alumno pregunta sobre algo que le apasiona:
- Escribe exactamente al inicio: "🚀 Modo profundización activado ✨"
- Ofrece datos curiosos, conexiones con el mundo real y retos adicionales.
- Al final incluye UN RETO: "🏆 Reto de sabiduría: [pregunta desafiante]"
- Si el alumno resuelve el reto correctamente: "🌟 ¡Ganaste puntos de sabiduría! ¡Excelente razonamiento!"
- Conecta siempre con aplicaciones profesionales reales en Mexico.

MODO VOCACIONAL — activado cuando el alumno pregunta sobre carreras o su futuro:
- Escribe exactamente al inicio: "🌟 Orientación vocacional ✨"
- Conecta sus fortalezas observadas con carreras concretas en Mexico.
- Da 2-3 opciones con descripcion del dia a dia y universidades mexicanas.
- Menciona el mercado laboral mexicano actual para esa carrera.

REGLAS DE ORO
- Personaliza SIEMPRE con el nombre del alumno.
- Usa emojis estrategicamente para hacer el aprendizaje divertido.
- Si el alumno esta frustrado, primero valida su emocion, luego guia con preguntas.
- NUNCA des la solucion directa a tareas o ejercicios.
- NUNCA uses lenguaje condescendiente.
- Usa el tuteo y lenguaje natural mexicano (esta bien decir "orale", "chido", "sale").
"""

# ═══════════════════════════════════════════════
#  ANÁLISIS DE SENTIMIENTO
# ═══════════════════════════════════════════════
FRUSTRACION_KEYWORDS = [
    "no entiendo", "no comprendo", "me cuesta", "difícil", "dificil",
    "no puedo", "me rindo", "frustrado", "estresado", "odio", "horrible",
    "no sirve", "es muy complicado", "me pierdo", "no sé", "ayuda por favor",
    "no le entiendo", "estoy perdido", "no tengo idea", "me duele la cabeza"
]

def analizar_sentimiento(texto):
    texto_lower = texto.lower()
    for palabra in FRUSTRACION_KEYWORDS:
        if palabra in texto_lower:
            return "frustrado"
    if "!!" in texto or "??" in texto:
        return "frustrado"
    if texto.count('!') > 2 or texto.count('?') > 2:
        return "frustrado"
    if re.search(r'\b[A-Z]{4,}\b', texto):
        return "frustrado"
    return "neutral"

# ═══════════════════════════════════════════════
#  RECURSOS DE ESTUDIO
# ═══════════════════════════════════════════════
RECURSOS_ESTUDIO = {
    "matematicas": [
        {"tipo": "video",      "titulo": "Khan Academy: Álgebra",  "url": "https://es.khanacademy.org/math/algebra"},
        {"tipo": "video",      "titulo": "Julio Profe (YouTube)",  "url": "https://www.youtube.com/user/julioprofe"},
        {"tipo": "ejercicios", "titulo": "ThatQuiz - Práctica",    "url": "https://www.thatquiz.org/es/"},
    ],
    "fisica": [
        {"tipo": "video", "titulo": "Khan Academy: Física",        "url": "https://es.khanacademy.org/science/physics"},
        {"tipo": "video", "titulo": "Física en 3 minutos",         "url": "https://www.youtube.com/user/3minutosdeciencia"},
    ],
    "quimica": [
        {"tipo": "video", "titulo": "Khan Academy: Química",       "url": "https://es.khanacademy.org/science/chemistry"},
        {"tipo": "video", "titulo": "Breaking Vlad (YouTube)",     "url": "https://www.youtube.com/c/BreakingVlad"},
    ],
    "historia": [
        {"tipo": "video", "titulo": "Academia Play (YouTube)",     "url": "https://www.youtube.com/user/AcademiaPlay"},
        {"tipo": "video", "titulo": "Khan Academy: Historia",      "url": "https://es.khanacademy.org/humanities/history"},
    ],
    "español": [
        {"tipo": "video",      "titulo": "Educatina (YouTube)",    "url": "https://www.youtube.com/user/Educatina"},
        {"tipo": "ejercicios", "titulo": "Ortografía interactiva", "url": "https://www.reglasdeortografia.com/"},
    ],
    "ingles": [
        {"tipo": "video",      "titulo": "BBC Learning English",   "url": "https://www.youtube.com/user/bbclearningenglish"},
        {"tipo": "ejercicios", "titulo": "Duolingo",               "url": "https://es.duolingo.com/"},
    ],
    "biologia": [
        {"tipo": "video", "titulo": "Khan Academy: Biología",      "url": "https://es.khanacademy.org/science/biology"},
        {"tipo": "video", "titulo": "Amoeba Sisters (YouTube)",    "url": "https://www.youtube.com/user/AmoebaSisters"},
    ],
}

MATERIAS_SINONIMOS = {
    "matematicas": ["matemáticas","mate","álgebra","geometría","cálculo","trigonometría","aritmética","ecuaciones","fracciones"],
    "fisica":      ["física","fisica","movimiento","velocidad","fuerza","newton","gravedad"],
    "quimica":     ["química","quimica","tabla periódica","reacciones","átomos","moléculas"],
    "historia":    ["historia","histórico","revolución","guerra","civilización","imperio"],
    "español":     ["español","lengua","literatura","gramática","ortografía","redacción","escritura"],
    "ingles":      ["inglés","ingles","vocabulario","verbos","idioma"],
    "biologia":    ["biología","biologia","células","ecosistema","cuerpo humano","genética"],
}

def extraer_materias_de_mensaje(texto):
    texto_lower = texto.lower()
    materias_detectadas = set()
    for materia, sinonimos in MATERIAS_SINONIMOS.items():
        for sinonimo in sinonimos:
            if sinonimo in texto_lower:
                materias_detectadas.add(materia)
                break
    return list(materias_detectadas)

def actualizar_perfil_dinamico(perfil, mensaje_usuario):
    materias = extraer_materias_de_mensaje(mensaje_usuario)
    if not materias:
        return perfil
    sentimiento = analizar_sentimiento(mensaje_usuario)
    msg_lower   = mensaje_usuario.lower()
    for materia in materias:
        if sentimiento == "frustrado":
            if materia not in perfil.get("debilidades", []):
                perfil.setdefault("debilidades", []).append(materia)
        if any(p in msg_lower for p in ["amo", "me gusta", "me encanta", "me apasiona", "es chido", "me llama"]):
            if materia not in perfil.get("intereses", []):
                perfil.setdefault("intereses", []).append(materia)
            if materia in perfil.get("debilidades", []):
                perfil["debilidades"].remove(materia)
    return perfil

def detectar_puntos_ganados(respuesta_moni):
    indicadores = ["ganaste puntos de sabiduría", "puntos de sabiduría", "¡ganaste puntos", "ganaste puntos"]
    respuesta_lower = respuesta_moni.lower()
    return any(ind in respuesta_lower for ind in indicadores)

# ═══════════════════════════════════════════════
#  CLASE MANEJADOR DE PERFILES
# ═══════════════════════════════════════════════
class ManejadorPerfiles:

    def __init__(self, directorio="perfiles"):
        self.directorio = directorio
        os.makedirs(directorio, exist_ok=True)
        self.max_historial = 50

    def id_alumno(self, nombre, grado):
        nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '',
            nombre.lower()
            .replace('á','a').replace('é','e').replace('í','i')
            .replace('ó','o').replace('ú','u').replace('ñ','n'))[:20]
        grado_limpio = re.sub(r'[^a-zA-Z0-9]', '', grado.lower())[:10]
        return f"{nombre_limpio}_{grado_limpio}"

    def ruta_perfil(self, alumno_id):
        return os.path.join(self.directorio, f"{alumno_id}.json")

    def cargar_perfil(self, alumno_id):
        ruta = self.ruta_perfil(alumno_id)
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None

    def crear_perfil_nuevo(self, nombre, grado, pin):
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        return {
            "nombre": nombre,
            "grado": grado,
            "pin_hash": pin_hash,
            "primera_sesion": datetime.now().strftime("%Y-%m-%d"),
            "ultima_sesion": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_sesiones": 1,
            "mensajes_totales": 0,
            "modos": {"nivelacion": 0, "profundizacion": 0, "vocacional": 0},
            "fortalezas": [],
            "debilidades": [],
            "intereses": [],
            "notas_maestro": "",
            "ultimo_indice_contado": 0,
            "ultimo_reporte": "",
            "puntos_sabiduria": 0,
            "historial": []
        }

    def verificar_pin(self, perfil, pin):
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        return perfil.get("pin_hash") == pin_hash

    def guardar_perfil(self, alumno_id, perfil, messages=None):
        if messages is not None:
            perfil["ultima_sesion"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            ultimo_idx = perfil.get("ultimo_indice_contado", 0)
            mensajes_nuevos_usuario = [
                m for m in messages[ultimo_idx:] if m["role"] == "user"
            ]
            perfil["mensajes_totales"] = perfil.get("mensajes_totales", 0) + len(mensajes_nuevos_usuario)
            puntos_sumados = False
            for msg in messages[ultimo_idx:]:
                if msg["role"] == "assistant":
                    contenido = msg["content"].lower()
                    if "modo nivelación" in contenido or "modo nivelacion" in contenido:
                        perfil["modos"]["nivelacion"] += 1
                    elif "modo profundización" in contenido or "modo profundizacion" in contenido:
                        perfil["modos"]["profundizacion"] += 1
                    elif "orientación vocacional" in contenido or "orientacion vocacional" in contenido:
                        perfil["modos"]["vocacional"] += 1
                    if not puntos_sumados and detectar_puntos_ganados(msg["content"]):
                        perfil["puntos_sabiduria"] = perfil.get("puntos_sabiduria", 0) + 10
                        puntos_sumados = True
            perfil["ultimo_indice_contado"] = len(messages)
            perfil["historial"] = (
                messages[-self.max_historial:]
                if len(messages) > self.max_historial else messages
            )
        ruta = self.ruta_perfil(alumno_id)
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(perfil, f, ensure_ascii=False, indent=2)
            return True
        except IOError:
            return False

    def listar_perfiles(self, limite=100):
        perfiles = []
        if not os.path.exists(self.directorio):
            return perfiles
        for archivo in os.listdir(self.directorio)[:limite]:
            if archivo.endswith(".json"):
                ruta = os.path.join(self.directorio, archivo)
                try:
                    with open(ruta, "r", encoding="utf-8") as f:
                        perfiles.append(json.load(f))
                except (json.JSONDecodeError, IOError):
                    continue
        return sorted(perfiles, key=lambda x: x.get("ultima_sesion", ""), reverse=True)


manejador = ManejadorPerfiles(PERFILES_DIR)

# ═══════════════════════════════════════════════
#  DETECCIÓN DE MODO
# ═══════════════════════════════════════════════
def detectar_modo(messages):
    for msg in reversed(messages):
        if msg["role"] == "assistant":
            txt = msg["content"].lower()
            if "modo nivelación" in txt or "modo nivelacion" in txt:
                return "nivelacion"
            if "modo profundización" in txt or "modo profundizacion" in txt:
                return "profundizacion"
            if "orientación vocacional" in txt or "orientacion vocacional" in txt:
                return "vocacional"
            break
    user_msgs = [m["content"].lower() for m in messages if m["role"] == "user"][-3:]
    texto_combinado = " ".join(user_msgs)
    keywords = {
        "nivelacion": ["no entiendo","me cuesta","difícil","dificil","ayuda","explica","como se hace","no le entiendo","no comprendo","me pierdo","no se","tarea","ejercicio","examen","reprobé","no puedo","estoy perdido"],
        "profundizacion": ["quiero saber más","curiosidad","profundizar","mas alla","investigar","me apasiona","me encanta","dato curioso","como funciona","origen de","historia de","quiero aprender mas","es interesante"],
        "vocacional": ["carrera","universidad","trabajo","futuro","profesion","que estudiar","que ser","quiero ser","me gustaria ser","no se que estudiar","facultad","titulo","empleo","salida laboral","vocacion"]
    }
    puntuacion = {modo: 0 for modo in keywords}
    for modo, palabras in keywords.items():
        for palabra in palabras:
            if palabra in texto_combinado:
                puntuacion[modo] += 1
    mejor_modo = max(puntuacion, key=puntuacion.get)
    return mejor_modo if puntuacion[mejor_modo] >= 2 else "general"

# ═══════════════════════════════════════════════
#  API KEYS CON ROTACIÓN AUTOMÁTICA
# ═══════════════════════════════════════════════
def get_api_keys():
    keys = []
    for i in range(1, 6):
        nombre = "GEMINI_API_KEY" if i == 1 else f"GEMINI_API_KEY_{i}"
        try:
            key = st.secrets[nombre]
            if key:
                keys.append(key)
        except Exception:
            key = os.environ.get(nombre, "")
            if key:
                keys.append(key)
    return keys

# ═══════════════════════════════════════════════
#  LLAMAR A GEMINI
# ═══════════════════════════════════════════════
MAX_MENSAJES_API = 20

def llamar_gemini(messages, instrucciones, imagen_adjunta=None):
    keys = get_api_keys()
    if not keys:
        return None, "❌ No hay API keys configuradas en Secrets."
    for key in keys:
        try:
            client = genai.Client(api_key=key)
            messages_api = messages[-MAX_MENSAJES_API:] if len(messages) > MAX_MENSAJES_API else messages
            historial_gemini = []
            for i, msg in enumerate(messages_api):
                rol = "user" if msg["role"] == "user" else "model"
                if i == len(messages_api) - 1 and imagen_adjunta and rol == "user":
                    img = Image.open(imagen_adjunta)
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="JPEG")
                    img_bytes.seek(0)
                    imagen_part = types.Part.from_bytes(data=img_bytes.getvalue(), mime_type="image/jpeg")
                    historial_gemini.append(types.Content(role=rol, parts=[types.Part.from_text(text=msg["content"]), imagen_part]))
                else:
                    historial_gemini.append(types.Content(role=rol, parts=[types.Part.from_text(text=msg["content"])]))
            respuesta = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=historial_gemini,
                config=types.GenerateContentConfig(system_instruction=instrucciones, temperature=0.7)
            )
            return respuesta.text, None
        except Exception as e:
            error = str(e).lower()
            if "quota" in error or "rate" in error or "429" in error:
                continue
            elif "api key" in error:
                return None, "❌ API key inválida."
            else:
                return None, f"❌ Error inesperado: {str(e)}"
    return None, "⏳ Todas las keys alcanzaron su límite. Intenta más tarde."

# ═══════════════════════════════════════════════
#  GENERAR REPORTE VOCACIONAL
# ═══════════════════════════════════════════════
def generar_reporte_vocacional(perfil, messages):
    keys = get_api_keys()
    if not keys:
        return None, "❌ No hay API keys configuradas."
    resumen = "".join(f"- Alumno: {m['content'][:150]}\n" for m in messages if m["role"] == "user")
    modos = perfil.get("modos", {})
    puntos = perfil.get("puntos_sabiduria", 0)
    prompt = f"""
Eres un orientador vocacional experto en el sistema educativo mexicano.

DATOS DEL ALUMNO:
- Nombre: {perfil.get('nombre')}
- Grado: {perfil.get('grado')}
- Primera sesion: {perfil.get('primera_sesion')}
- Total sesiones: {perfil.get('total_sesiones')}
- Mensajes: {perfil.get('mensajes_totales')}
- Puntos de sabiduria: {puntos}
- Modo nivelacion: {modos.get('nivelacion', 0)} veces
- Modo profundizacion: {modos.get('profundizacion', 0)} veces
- Modo vocacional: {modos.get('vocacional', 0)} veces
- Intereses: {', '.join(perfil.get('intereses', [])) or 'No registrados'}
- Areas de mejora: {', '.join(perfil.get('debilidades', [])) or 'No registradas'}

CONVERSACIONES:
{resumen[:2000]}

Genera reporte con estas secciones exactas:

🌟 REPORTE VOCACIONAL DE {perfil.get('nombre', '').upper()}
{'='*40}

📚 TU PERFIL COMO APRENDIZ
[2-3 oraciones sobre como aprende este alumno]

⭐ TUS PUNTOS DE SABIDURÍA: {puntos} puntos
[1 oracion motivadora sobre sus puntos]

💪 TUS FORTALEZAS DETECTADAS
[3-4 fortalezas especificas]

🌱 TUS ÁREAS DE CRECIMIENTO
[2-3 areas de esfuerzo y superacion]

🎯 CARRERAS QUE VAN CONTIGO (en Mexico)
[3 carreras con: por que encaja, materias clave, universidades mexicanas]

✨ MENSAJE PARA TU FUTURO
[Parrafo motivacional en espanol mexicano natural]

Habla de tu directamente. Tono calido y honesto. Contexto mexicano.
"""
    for key in keys:
        try:
            client = genai.Client(api_key=key)
            respuesta = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
                config=types.GenerateContentConfig(system_instruction="Eres orientador vocacional experto en educacion mexicana.", temperature=0.7)
            )
            return respuesta.text, None
        except Exception as e:
            error = str(e).lower()
            if "quota" in error or "rate" in error or "429" in error:
                continue
            else:
                return None, f"❌ Error: {str(e)}"
    return None, "⏳ Todas las keys alcanzaron su límite."

# ═══════════════════════════════════════════════
#  CACHÉ DEL DASHBOARD
# ═══════════════════════════════════════════════
@st.cache_data(ttl=300)
def get_perfiles_cached():
    return manejador.listar_perfiles()

# ═══════════════════════════════════════════════
#  ESTADO INICIAL
# ═══════════════════════════════════════════════
for key, default in {
    "vista": "inicio",
    "perfil_activo": None,
    "messages": [],
    "es_primera_vez": False,
    "alumno_detalle": None,
    "reporte_generado": None,
    "frustrado": False,
    "ultima_imagen": None,
    "mensaje_counter": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ════════════════════════════════════════════════════════════
#  VISTA 1: INICIO
# ════════════════════════════════════════════════════════════
if st.session_state.vista == "inicio":

    st.markdown("""
    <div class="hero">
        <p style="font-size:4rem; margin-bottom:0;">🌟</p>
        <p class="titulo-moni">Hola, soy Moni</p>
        <p class="hero-sub">Tu mentora inteligente · De la secundaria a tu proyecto de vida</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""<div class="role-card"><div class="role-icon">🎒</div><div class="role-title">Soy alumno</div><div class="role-desc">Chatea con Moni y aprende</div></div>""", unsafe_allow_html=True)
            if st.button("Entrar como alumno", key="btn_alumno", use_container_width=True):
                st.session_state.vista = "alumno_login"
                st.rerun()
        with col_b:
            st.markdown("""<div class="role-card"><div class="role-icon">👨‍🏫</div><div class="role-title">Soy maestro</div><div class="role-desc">Ver panel de seguimiento</div></div>""", unsafe_allow_html=True)
            if st.button("Entrar como maestro", key="btn_maestro", use_container_width=True):
                st.session_state.vista = "maestro_login"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card" style="margin-top:20px;">
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:0.85rem; color:#475569;">
                <div>📚 <b>Nivelación socrática</b> — aprende pensando, no memorizando</div>
                <div>🚀 <b>Profundización</b> — retos y puntos de sabiduría ⭐</div>
                <div>🌟 <b>Orientación vocacional</b> — carreras según tu perfil real</div>
                <div>🔐 <b>Privacidad</b> — tu perfil protegido con PIN</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  VISTA 2: LOGIN DEL ALUMNO
# ════════════════════════════════════════════════════════════
elif st.session_state.vista == "alumno_login":

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin-bottom:24px;">
            <p style="font-size:2.5rem; margin:0;">🎒</p>
            <p style="font-size:1.5rem; font-weight:800; color:#1e293b; margin:4px 0;">¿Quién eres?</p>
            <p style="color:#64748b; font-size:0.9rem;">Moni te recordará cada vez que entres 🔐</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_alumno"):
            nombre = st.text_input("Tu nombre", placeholder="Ej: Valeria López")
            grado  = st.selectbox("Tu grado actual", [
                "1° Secundaria", "2° Secundaria", "3° Secundaria",
                "1° Semestre Prepa", "2° Semestre Prepa", "3° Semestre Prepa",
                "4° Semestre Prepa", "5° Semestre Prepa", "6° Semestre Prepa"
            ])
            pin = st.text_input("Tu PIN de 4 dígitos 🔐", type="password", max_chars=4, placeholder="Si es tu primera vez, elige uno nuevo")
            submitted = st.form_submit_button("¡Entrar con Moni! 🚀", use_container_width=True)

        if submitted:
            if not nombre.strip():
                st.error("Por favor escribe tu nombre.")
            elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', nombre.strip()):
                st.error("❌ El nombre solo puede tener letras y espacios, sin símbolos.")
            elif not pin.strip() or not pin.strip().isdigit() or len(pin.strip()) != 4:
                st.error("❌ El PIN debe ser exactamente 4 números.")
            else:
                nombre_clean = nombre.strip().title()
                alumno_id    = manejador.id_alumno(nombre_clean, grado)
                perfil_exist = manejador.cargar_perfil(alumno_id)
                if perfil_exist:
                    if manejador.verificar_pin(perfil_exist, pin.strip()):
                        perfil_exist["ultima_sesion"]  = datetime.now().strftime("%Y-%m-%d %H:%M")
                        perfil_exist["total_sesiones"] = perfil_exist.get("total_sesiones", 1) + 1
                        perfil_exist.setdefault("puntos_sabiduria", 0)
                        perfil_exist.setdefault("intereses", [])
                        perfil_exist.setdefault("debilidades", [])
                        st.session_state.perfil_activo  = perfil_exist
                        st.session_state.messages       = perfil_exist.get("historial", [])
                        st.session_state.es_primera_vez = False
                        st.session_state.mensaje_counter = 0
                        st.session_state.vista = "chat"
                        st.rerun()
                    else:
                        st.error("❌ PIN incorrecto. Solo tú conoces tu PIN.")
                else:
                    perfil_nuevo = manejador.crear_perfil_nuevo(nombre_clean, grado, pin.strip())
                    st.session_state.perfil_activo  = perfil_nuevo
                    st.session_state.messages       = []
                    st.session_state.es_primera_vez = True
                    st.session_state.mensaje_counter = 0
                    st.session_state.vista = "chat"
                    st.rerun()

        if st.button("← Volver", key="back_alumno"):
            st.session_state.vista = "inicio"
            st.rerun()


# ════════════════════════════════════════════════════════════
#  VISTA 3: CHAT CON MONI
# ════════════════════════════════════════════════════════════
elif st.session_state.vista == "chat":

    perfil    = st.session_state.perfil_activo
    nombre    = perfil["nombre"]
    grado     = perfil["grado"]
    alumno_id = manejador.id_alumno(nombre, grado)
    puntos    = perfil.get("puntos_sabiduria", 0)

    def _cerrar_sesion_alumno():
        manejador.guardar_perfil(alumno_id, perfil, st.session_state.messages)
        get_perfiles_cached.clear()
        st.session_state.vista = "inicio"
        st.session_state.perfil_activo = None
        st.session_state.messages = []
        st.session_state.reporte_generado = None
        st.session_state.mensaje_counter = 0
        st.rerun()

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding:16px 0 8px;">
            <div style="font-size:2.5rem;">👋</div>
            <div style="font-size:1.1rem; font-weight:800;">{nombre}</div>
            <div style="font-size:0.8rem; color:#8b949e;">{grado}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        modos    = perfil.get("modos", {})
        sesiones = perfil.get("total_sesiones", 1)
        mensajes = perfil.get("mensajes_totales", 0)

        st.markdown("**📊 Tu progreso**")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class="card-dark" style="text-align:center;"><div style="font-size:1.4rem;font-weight:900;">{sesiones}</div><div style="font-size:0.65rem;color:#8b949e;">SESIONES</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="card-dark" style="text-align:center;"><div style="font-size:1.4rem;font-weight:900;">{mensajes}</div><div style="font-size:0.65rem;color:#8b949e;">MENSAJES</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<span class="badge badge-pts">⭐ Puntos de sabiduría: {puntos}</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<span class="badge badge-niv">📚 Nivelación: {modos.get("nivelacion",0)}</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<span class="badge badge-prof">🚀 Profund.: {modos.get("profundizacion",0)}</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<span class="badge badge-voc">🌟 Vocacional: {modos.get("vocacional",0)}</span>', unsafe_allow_html=True)
        st.markdown("---")

        if perfil.get("intereses"):
            st.markdown("**💚 Tus intereses:**")
            st.markdown(", ".join([f"`{i}`" for i in perfil["intereses"]]))
            st.markdown("<br>", unsafe_allow_html=True)

        if perfil.get("debilidades"):
            st.markdown("**📚 Recursos para ti**")
            for materia in perfil["debilidades"]:
                recursos = RECURSOS_ESTUDIO.get(materia, [])
                if recursos:
                    with st.expander(f"🔍 {materia.capitalize()}"):
                        for r in recursos:
                            st.markdown(f"- [{r['titulo']}]({r['url']})  _({r['tipo']})_")

        modo = detectar_modo(st.session_state.messages)
        badges_map = {
            "nivelacion":     '<span class="badge badge-niv">📚 Nivelación activa</span>',
            "profundizacion": '<span class="badge badge-prof">🚀 Profundización activa</span>',
            "vocacional":     '<span class="badge badge-voc">🌟 Vocacional activa</span>',
            "general":        '<span class="badge badge-gen">💬 Conversación general</span>',
        }
        st.markdown("**Modo actual:**")
        st.markdown(badges_map.get(modo, ""), unsafe_allow_html=True)
        st.markdown("---")

        perfil_export = json.dumps({k: v for k, v in perfil.items() if k != "pin_hash"}, ensure_ascii=False, indent=2)
        st.download_button("⬇️ Exportar mi perfil", data=perfil_export, file_name=f"perfil_{alumno_id}.json", mime="application/json", use_container_width=True)

        st.markdown("---")
        st.markdown("**📶 ¿Sin internet en casa?**")
        texto_offline  = f"📚 Apuntes de Moni para {nombre}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n⭐ Puntos: {puntos}\n" + "="*40 + "\n\n"
        for msg in st.session_state.messages:
            rol_txt = "Tú" if msg["role"] == "user" else "🤖 Moni"
            contenido_limpio = msg["content"].replace("\n\n*[El alumno adjuntó una imagen de su tarea]*", " [Imagen enviada]")
            texto_offline += f"{rol_txt}:\n{contenido_limpio}\n\n" + "-"*40 + "\n\n"
        st.download_button("💾 Descargar clase offline", data=texto_offline, file_name=f"Apuntes_Moni_{nombre.replace(' ','_')}.txt", mime="text/plain", use_container_width=True)

        st.markdown("---")
        st.markdown("**🎓 Reporte vocacional**")
        if perfil.get("total_sesiones", 1) < 3:
            st.markdown(f"""<div style="background:#fef9ef;border:1px solid #f59e0b;border-radius:10px;padding:10px;font-size:0.78rem;color:#92400e;">💡 Completa al menos 3 sesiones. Llevas <b>{perfil.get('total_sesiones',1)}</b>.</div>""", unsafe_allow_html=True)
        else:
            if st.button("📋 Generar mi reporte", key="btn_reporte", use_container_width=True):
                with st.spinner("Analizando tu perfil... 🔍"):
                    reporte, error_r = generar_reporte_vocacional(perfil, st.session_state.messages)
                    if error_r:
                        st.error(error_r)
                    else:
                        st.session_state.reporte_generado = reporte
                        perfil["ultimo_reporte"] = reporte
                        manejador.guardar_perfil(alumno_id, perfil, st.session_state.messages)
                        get_perfiles_cached.clear()
            if st.session_state.get("reporte_generado"):
                st.download_button("⬇️ Descargar mi reporte", data=st.session_state.reporte_generado, file_name=f"Reporte_Vocacional_{nombre.replace(' ','_')}.txt", mime="text/plain", use_container_width=True)

        st.markdown("---")
        if st.button("🚪 Cerrar sesión", key="logout_sidebar", use_container_width=True):
            _cerrar_sesion_alumno()

    col_t, col_b = st.columns([3, 1])
    with col_t:
        st.markdown(f'<p class="titulo-moni">🤖 Hola, {nombre}!</p>', unsafe_allow_html=True)
        st.markdown(f"*{grado} · Tu mentora inteligente*")
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Cerrar sesión", key="logout_top", use_container_width=True):
            _cerrar_sesion_alumno()

    st.markdown("---")

    modo_actual = detectar_modo(st.session_state.messages)
    modos_info  = {
        "nivelacion":     ("📚", "Modo Nivelación Socrática", "#fef2f2", "#ef4444"),
        "profundizacion": ("🚀", "Modo Profundización",       "#f0fdf4", "#22c55e"),
        "vocacional":     ("🌟", "Orientación Vocacional",    "#faf5ff", "#a855f7"),
        "general":        ("💬", "Conversación General",      "#f0f9ff", "#0ea5e9"),
    }
    icono_m, label_m, bg_m, color_m = modos_info.get(modo_actual, modos_info["general"])
    modos_d = perfil.get("modos", {})
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                background:{bg_m};border:1.5px solid {color_m}33;
                border-radius:12px;padding:10px 18px;margin-bottom:12px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.2rem;">{icono_m}</span>
            <span style="font-weight:800;color:{color_m};font-size:0.9rem;">{label_m}</span>
        </div>
        <div style="display:flex;gap:12px;font-size:0.78rem;color:#64748b;">
            <span>⭐ <b>{puntos} pts</b></span>
            <span>📚 <b>{modos_d.get('nivelacion',0)}</b></span>
            <span>🚀 <b>{modos_d.get('profundizacion',0)}</b></span>
            <span>🌟 <b>{modos_d.get('vocacional',0)}</b></span>
            <span style="color:#94a3b8;">Sesión #{perfil.get('total_sesiones',1)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        texto_rapido = f"📚 Apuntes de Moni para {nombre}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n⭐ Puntos: {puntos}\n" + "="*40 + "\n\n"
        for msg in st.session_state.messages:
            rol_txt = "Tú" if msg["role"] == "user" else "🤖 Moni"
            texto_rapido += f"{rol_txt}:\n{msg['content']}\n\n" + "-"*40 + "\n\n"
        st.download_button("💾 Descargar clase", data=texto_rapido, file_name=f"Apuntes_{nombre.replace(' ','_')}.txt", mime="text/plain", use_container_width=True)
    with bc2:
        if perfil.get("total_sesiones", 1) >= 3:
            if st.button("📋 Generar reporte", key="btn_reporte_main", use_container_width=True):
                with st.spinner("Analizando tu perfil... 🔍"):
                    reporte, error_r = generar_reporte_vocacional(perfil, st.session_state.messages)
                    if error_r:
                        st.error(error_r)
                    else:
                        st.session_state.reporte_generado = reporte
                        perfil["ultimo_reporte"] = reporte
                        manejador.guardar_perfil(alumno_id, perfil, st.session_state.messages)
        else:
            st.markdown(f"""<div style="background:#fef9ef;border:1px solid #f59e0b;border-radius:10px;padding:8px;font-size:0.75rem;color:#92400e;text-align:center;">📋 Reporte desde sesión 3<br>(llevas {perfil.get('total_sesiones',1)})</div>""", unsafe_allow_html=True)
    with bc3:
        if st.session_state.get("reporte_generado"):
            st.download_button("⬇️ Descargar reporte", data=st.session_state.reporte_generado, file_name=f"Reporte_{nombre.replace(' ','_')}.txt", mime="text/plain", use_container_width=True)
        else:
            st.download_button("⬇️ Exportar perfil", data=json.dumps({k: v for k, v in perfil.items() if k != "pin_hash"}, ensure_ascii=False, indent=2), file_name=f"perfil_{alumno_id}.json", mime="application/json", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    reporte_mostrar = st.session_state.get("reporte_generado") or perfil.get("ultimo_reporte")
    if reporte_mostrar:
        st.markdown("""<div style="background:linear-gradient(135deg,#faf5ff,#f0f9ff);border:2px solid #a855f7;border-radius:16px;padding:20px;margin-bottom:16px;">""", unsafe_allow_html=True)
        st.markdown(reporte_mostrar)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("✖️ Cerrar reporte", key="cerrar_reporte"):
            st.session_state.reporte_generado = None
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    keys_disponibles = get_api_keys()

    if not st.session_state.messages and keys_disponibles:
        if st.session_state.es_primera_vez:
            bienvenida = f"""¡Hola, **{nombre}**! 🎉✨ Soy **Moni**, tu mentora inteligente.

Estoy aquí para acompañarte en {grado} y en todo lo que viene después. Voy a ayudarte con las materias que se te dificulten usando preguntas que te hagan pensar, potenciar las que te apasionan con retos para ganar ⭐ **puntos de sabiduría**, y orientarte sobre tu carrera cuando llegue el momento. 🎯

Para conocerte mejor, cuéntame: **¿qué materias se te hacen más difíciles?** No te preocupes, ¡para eso estoy! 😊"""
        else:
            sesion_num = perfil.get("total_sesiones", 2)
            bienvenida = f"""¡Hola de nuevo, **{nombre}**! 🌟 ¡Qué bueno que regresaste!

Esta es tu sesión **#{sesion_num}** conmigo. Llevas **{puntos} puntos de sabiduría** ⭐ acumulados. ¡Sigue así! 💪

**¿En qué te puedo ayudar hoy?** 😊"""

        with st.chat_message("assistant"):
            st.markdown(bienvenida)
        st.session_state.messages.append({"role": "assistant", "content": bienvenida})
        st.session_state.es_primera_vez = False
        manejador.guardar_perfil(alumno_id, perfil, st.session_state.messages)
        st.session_state.perfil_activo = perfil
        st.rerun()

    if keys_disponibles:
        with st.expander("📷 ¿Tienes una foto de tu tarea? Súbela aquí"):
            foto_tarea = st.file_uploader("Sube una imagen (JPG o PNG, máx 5MB)", type=["jpg","jpeg","png"], key="uploader_foto")
            if foto_tarea:
                if foto_tarea.size > 5 * 1024 * 1024:
                    st.error("❌ La imagen es demasiado grande (máx 5MB).")
                    foto_tarea = None
                    st.session_state.ultima_imagen = None
                else:
                    st.success("✅ ¡Imagen lista! Ahora escríbele a Moni qué necesitas.")
                    st.session_state.ultima_imagen = foto_tarea
            else:
                st.session_state.ultima_imagen = None

        prompt = st.chat_input(f"Escríbele a Moni, {nombre}... 💬")

        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)
                if st.session_state.ultima_imagen:
                    st.image(st.session_state.ultima_imagen, width=200)

            texto_historial = prompt
            if st.session_state.ultima_imagen:
                texto_historial += "\n\n*[El alumno adjuntó una imagen de su tarea]*"

            st.session_state.messages.append({"role": "user", "content": texto_historial})
            st.session_state.mensaje_counter += 1

            sentimiento = analizar_sentimiento(prompt)
            st.session_state.frustrado = (sentimiento == "frustrado")
            perfil = actualizar_perfil_dinamico(perfil, prompt)
            st.session_state.perfil_activo = perfil

            contexto_perfil = f"""
INFORMACION DEL ALUMNO:
- Nombre: {nombre}
- Grado: {grado}
- Sesion numero: {perfil.get('total_sesiones', 1)}
- Primera sesion: {perfil.get('primera_sesion', 'hoy')}
- Puntos de sabiduria: {perfil.get('puntos_sabiduria', 0)}
- Veces en modo nivelacion: {perfil.get('modos', {}).get('nivelacion', 0)}
- Veces en modo profundizacion: {perfil.get('modos', {}).get('profundizacion', 0)}
- Materias de interes: {', '.join(perfil.get('intereses', [])) or 'Ninguna aun'}
- Materias de mejora: {', '.join(perfil.get('debilidades', [])) or 'Ninguna aun'}
{"- Es alumno NUEVO, primera sesion." if perfil.get('total_sesiones', 1) == 1 else f"- Alumno RECURRENTE con {perfil.get('total_sesiones',1)} sesiones."}
"""
            contexto_adicional = "\n\nEL ALUMNO PARECE FRUSTRADO. Primero valida su emoción con empatía, luego usa preguntas socráticas simples." if st.session_state.get("frustrado") else ""
            instrucciones_completas = INSTRUCCIONES_MONI + "\n\n" + contexto_perfil + contexto_adicional

            with st.chat_message("assistant"):
                spinner_msg = "Moni está viendo tu imagen... 🤔" if st.session_state.ultima_imagen else "Moni está pensando... 🤔"
                with st.spinner(spinner_msg):
                    texto, error = llamar_gemini(st.session_state.messages, instrucciones_completas, imagen_adjunta=st.session_state.ultima_imagen)
                    if error:
                        st.error(error)
                    else:
                        st.markdown(texto)
                        st.session_state.messages.append({"role": "assistant", "content": texto})
                        if detectar_puntos_ganados(texto):
                            st.balloons()
                        manejador.guardar_perfil(alumno_id, perfil, st.session_state.messages)
                        st.session_state.perfil_activo = perfil

            st.session_state.ultima_imagen = None
            st.rerun()
    else:
        st.warning("⚠️ No hay API keys configuradas. Contacta al administrador.")


# ════════════════════════════════════════════════════════════
#  VISTA 4: LOGIN DEL MAESTRO
# ════════════════════════════════════════════════════════════
elif st.session_state.vista == "maestro_login":

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin-bottom:24px;">
            <p style="font-size:2.5rem; margin:0;">👨‍🏫</p>
            <p style="font-size:1.5rem; font-weight:800; color:#1e293b; margin:4px 0;">Acceso docente</p>
            <p style="color:#64748b; font-size:0.9rem;">Panel de seguimiento de alumnos</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_maestro"):
            password  = st.text_input("Contraseña docente", type="password")
            submitted = st.form_submit_button("Entrar al panel 📊", use_container_width=True)

        if submitted:
            try:
                password_correcta = st.secrets["TEACHER_PASSWORD"]
            except Exception:
                password_correcta = "moni2025"
            if password == password_correcta:
                st.session_state.vista = "dashboard"
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta.")
                st.info("💡 Demo: usa `moni2025`")

        if st.button("← Volver", key="back_maestro"):
            st.session_state.vista = "inicio"
            st.rerun()


# ════════════════════════════════════════════════════════════
#  VISTA 5: DASHBOARD DEL MAESTRO
# ════════════════════════════════════════════════════════════
elif st.session_state.vista == "dashboard":

    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:16px 0 8px;">
            <div style="font-size:2.5rem;">👨‍🏫</div>
            <div style="font-size:1rem; font-weight:800;">Panel Docente</div>
            <div style="font-size:0.75rem; color:#8b949e;">Seguimiento de alumnos</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        # ── BOTÓN DEMO ──────────────────────────────
        st.markdown("**🧪 Modo demo**")
        if st.button("👥 Crear alumnos de demo", use_container_width=True):
            try:
                with open("demo_data.json", "r", encoding="utf-8") as df:
                    demos = json.load(df)
                os.makedirs("perfiles", exist_ok=True)
                creados = 0
                for d in demos:
                    n = d["nombre"].lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n').replace(' ','')
                    g = d["grado"].lower().replace(' ','').replace('°','').replace('º','')
                    alumno_id_demo = f"{n[:20]}_{g[:10]}"
                    pin_hash_val   = hashlib.sha256(d["pin"].encode()).hexdigest()
                    primera = (datetime.now() - timedelta(days=d["dias"])).strftime("%Y-%m-%d")
                    ultima  = (datetime.now() - timedelta(days=d["dias"]//2)).strftime("%Y-%m-%d %H:%M")
                    perfil_demo = {
                        "nombre": d["nombre"], "grado": d["grado"],
                        "pin_hash": pin_hash_val,
                        "primera_sesion": primera, "ultima_sesion": ultima,
                        "total_sesiones": d["sesiones"], "mensajes_totales": d["mensajes"],
                        "modos": {"nivelacion": d["niv"], "profundizacion": d["prof"], "vocacional": d["voc"]},
                        "puntos_sabiduria": d["puntos"],
                        "fortalezas": [], "debilidades": d["deb"], "intereses": d["int"],
                        "notas_maestro": "", "ultimo_reporte": "",
                        "ultimo_indice_contado": len(d["historial"]),
                        "historial": d["historial"]
                    }
                    ruta_demo = os.path.join("perfiles", f"{alumno_id_demo}.json")
                    with open(ruta_demo, "w", encoding="utf-8") as pf:
                        json.dump(perfil_demo, pf, ensure_ascii=False, indent=2)
                    creados += 1
                get_perfiles_cached.clear()
                st.success(f"✅ {creados} alumnos de demo creados.")
                st.info("PINs → Valeria:1234 | Carlos:5678 | Ana:9012 | Diego:3456 | Sofía:7890")
                st.rerun()
            except FileNotFoundError:
                st.error("❌ No se encontró demo_data.json. Súbelo a tu repo de GitHub.")

        st.markdown("---")
        st.markdown("**🔍 Filtros**")

        perfiles_todos     = get_perfiles_cached()
        grados_disponibles = sorted(set(p.get("grado", "Sin grado") for p in perfiles_todos))
        grados_disponibles.insert(0, "Todos los grados")
        filtro_grado = st.selectbox("Filtrar por grado", grados_disponibles)
        busqueda     = st.text_input("🔎 Buscar alumno", placeholder="Nombre...")

        st.markdown("---")
        if perfiles_todos:
            todos_json = json.dumps([{k: v for k, v in p.items() if k != "pin_hash"} for p in perfiles_todos], ensure_ascii=False, indent=2)
            st.download_button("⬇️ Exportar todos", data=todos_json, file_name=f"perfiles_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json", use_container_width=True)

        if st.button("🚪 Cerrar sesión", use_container_width=True):
            st.session_state.vista = "inicio"
            st.rerun()

    st.markdown('<p class="titulo-moni">📊 Panel del Maestro</p>', unsafe_allow_html=True)
    st.markdown("*Seguimiento de aprendizaje por alumno*")
    st.markdown("---")

    perfiles = list(perfiles_todos)
    if filtro_grado != "Todos los grados":
        perfiles = [p for p in perfiles if p.get("grado") == filtro_grado]
    if busqueda.strip():
        perfiles = [p for p in perfiles if busqueda.lower() in p.get("nombre", "").lower()]

    if not perfiles:
        st.markdown("""
        <div class="card" style="text-align:center; padding:40px;">
            <p style="font-size:3rem;">📭</p>
            <p style="font-weight:700; color:#475569;">No hay alumnos que coincidan</p>
            <p style="color:#94a3b8; font-size:0.9rem;">Presiona "Crear alumnos de demo" en el sidebar para poblar el panel.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        total_alumnos  = len(perfiles)
        total_sesiones = sum(p.get("total_sesiones", 0) for p in perfiles)
        total_msgs     = sum(p.get("mensajes_totales", 0) for p in perfiles)
        total_niv      = sum(p.get("modos", {}).get("nivelacion", 0) for p in perfiles)
        total_prof     = sum(p.get("modos", {}).get("profundizacion", 0) for p in perfiles)
        total_pts      = sum(p.get("puntos_sabiduria", 0) for p in perfiles)

        cols = st.columns(6)
        for col, num, label, color in [
            (cols[0], total_alumnos,  "Alumnos",    "#0ea5e9"),
            (cols[1], total_sesiones, "Sesiones",   "#8b5cf6"),
            (cols[2], total_msgs,     "Mensajes",   "#f59e0b"),
            (cols[3], total_niv,      "Nivelación", "#ef4444"),
            (cols[4], total_prof,     "Profund.",   "#22c55e"),
            (cols[5], total_pts,      "⭐ Puntos",  "#b45309"),
        ]:
            with col:
                st.markdown(f"""<div class="metric-box"><div class="metric-num" style="color:{color};">{num}</div><div class="metric-label">{label}</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if len(perfiles) > 1:
            st.markdown("### 📈 Distribución de modos por alumno")
            df_modos = pd.DataFrame([{
                "Alumno": p.get("nombre",""), "Nivelación": p.get("modos",{}).get("nivelacion",0),
                "Profundización": p.get("modos",{}).get("profundizacion",0),
                "Vocacional": p.get("modos",{}).get("vocacional",0), "⭐ Puntos": p.get("puntos_sabiduria",0),
            } for p in perfiles])
            st.bar_chart(df_modos.set_index("Alumno"))
            st.markdown("---")

        col_lista, col_detalle = st.columns([1, 1.8])

        with col_lista:
            st.markdown("### 👥 Alumnos")
            for i, p in enumerate(perfiles):
                pts_p = p.get("puntos_sabiduria", 0)
                if st.button(f"**{p.get('nombre','Sin nombre')}** · {p.get('grado','')}\n📅 {p.get('ultima_sesion','')[:10]} · {p.get('total_sesiones',0)} ses. · ⭐{pts_p}pts", key=f"alumno_{i}", use_container_width=True):
                    st.session_state.alumno_detalle = p

        with col_detalle:
            st.markdown("### 🔍 Detalle del alumno")
            detalle = st.session_state.alumno_detalle

            if not detalle:
                st.markdown("""<div class="card" style="text-align:center;padding:30px;"><p style="font-size:2rem;">👈</p><p style="color:#94a3b8;">Selecciona un alumno de la lista</p></div>""", unsafe_allow_html=True)
            else:
                nombre_d    = detalle.get("nombre","")
                grado_d     = detalle.get("grado","")
                primera_d   = detalle.get("primera_sesion","")
                ultima_d    = detalle.get("ultima_sesion","")
                sesiones_d  = detalle.get("total_sesiones",0)
                msgs_d      = detalle.get("mensajes_totales",0)
                modos_d     = detalle.get("modos",{})
                debilidades = detalle.get("debilidades",[])
                intereses_d = detalle.get("intereses",[])
                puntos_d    = detalle.get("puntos_sabiduria",0)

                st.markdown(f"""
                <div class="card">
                    <div style="font-size:1.4rem;font-weight:900;color:#1e293b;">{nombre_d}</div>
                    <div style="font-size:0.85rem;color:#64748b;margin-top:4px;">{grado_d}</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px;font-size:0.82rem;color:#374151;">
                        <div><b>Primera sesión:</b><br>{primera_d}</div>
                        <div><b>Última sesión:</b><br>{ultima_d[:16]}</div>
                        <div><b>Total sesiones:</b><br>{sesiones_d}</div>
                        <div><b>Mensajes enviados:</b><br>{msgs_d}</div>
                    </div>
                    <div style="margin-top:12px;"><span class="badge badge-pts">⭐ Puntos de sabiduría: {puntos_d}</span></div>
                    <div style="margin-top:16px;">
                        <b style="font-size:0.85rem;color:#475569;">MODOS DE USO</b>
                        <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;">
                            <span class="badge badge-niv">📚 Nivelación: {modos_d.get('nivelacion',0)}</span>
                            <span class="badge badge-prof">🚀 Profundización: {modos_d.get('profundizacion',0)}</span>
                            <span class="badge badge-voc">🌟 Vocacional: {modos_d.get('vocacional',0)}</span>
                        </div>
                    </div>
                    <div style="margin-top:12px;font-size:0.82rem;color:#374151;">
                        <b>💚 Intereses:</b> {', '.join(intereses_d) if intereses_d else 'Ninguno registrado'}
                    </div>
                    <div style="margin-top:6px;font-size:0.82rem;color:#374151;">
                        <b>📚 Áreas de mejora:</b> {', '.join(debilidades) if debilidades else 'Ninguna registrada'}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                historial = detalle.get("historial", [])
                if historial:
                    st.markdown("**📝 Últimas interacciones:**")
                    for msg in historial[-6:]:
                        rol   = msg.get("role","")
                        texto = msg.get("content","")[:180]
                        if len(msg.get("content","")) > 180:
                            texto += "..."
                        icono = "🧑" if rol == "user" else "🤖"
                        st.markdown(f"""<div style="background:{'#f8fafc' if rol=='user' else '#f0f9ff'};border-left:3px solid {'#94a3b8' if rol=='user' else '#0ea5e9'};padding:8px 12px;border-radius:0 8px 8px 0;margin-bottom:6px;font-size:0.8rem;color:#374151;">{icono} {texto}</div>""", unsafe_allow_html=True)

                alumno_json = json.dumps({k: v for k, v in detalle.items() if k != "pin_hash"}, ensure_ascii=False, indent=2)
                st.download_button(f"⬇️ Exportar perfil de {nombre_d}", data=alumno_json, file_name=f"perfil_{nombre_d.lower().replace(' ','_')}.json", mime="application/json", use_container_width=True)
