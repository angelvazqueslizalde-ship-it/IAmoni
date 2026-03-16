import streamlit as st
from google import genai
from google.genai import types
import json
import os
import re
from datetime import datetime

# ═══════════════════════════════════════════════
#  CONFIGURACIÓN
# ═══════════════════════════════════════════════
st.set_page_config(
    page_title="Moni – Tu Mentora IA",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

PERFILES_DIR = "perfiles"
os.makedirs(PERFILES_DIR, exist_ok=True)

# ═══════════════════════════════════════════════
#  CSS GLOBAL
# ═══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }

.stApp { background: linear-gradient(135deg, #e8f4f8 0%, #fef9ef 50%, #f0f0ff 100%); }

/* Sidebar oscuro */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }
[data-testid="stSidebar"] hr { border-color: #30363d !important; }

/* Tarjetas */
.card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    margin-bottom: 12px;
    border: 1px solid rgba(0,0,0,0.06);
}
.card-dark {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
}

/* Título degradado */
.titulo-moni {
    font-size: 2.4rem;
    font-weight: 900;
    background: linear-gradient(90deg, #0ea5e9, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}

/* Badges de modo */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.3px;
}
.badge-niv  { background:#fff0f0; border:1.5px solid #f87171; color:#dc2626 !important; }
.badge-prof { background:#f0fff4; border:1.5px solid #4ade80; color:#16a34a !important; }
.badge-voc  { background:#faf0ff; border:1.5px solid #c084fc; color:#7c3aed !important; }
.badge-gen  { background:#f0f9ff; border:1.5px solid #60a5fa; color:#2563eb !important; }

/* Pantalla de bienvenida */
.hero {
    text-align: center;
    padding: 60px 20px 40px;
}
.hero-sub {
    font-size: 1.15rem;
    color: #64748b;
    margin: 8px 0 40px;
}

/* Botones de rol */
.role-btn-container {
    display: flex;
    gap: 20px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 20px;
}
.role-card {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 20px;
    padding: 30px 40px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    min-width: 200px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}
.role-card:hover {
    border-color: #0ea5e9;
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(14,165,233,0.15);
}
.role-icon { font-size: 3rem; margin-bottom: 10px; }
.role-title { font-size: 1.1rem; font-weight: 800; color: #1e293b; }
.role-desc  { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }

/* Métricas del maestro */
.metric-box {
    background: white;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.metric-num  { font-size: 2rem; font-weight: 900; color: #0ea5e9; }
.metric-label{ font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }

/* Ocultar elementos de Streamlit */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

/* Botón cerrar sesión del header */
button[kind="secondary"] {
    border-radius: 10px !important;
    border: 1.5px solid #ef4444 !important;
    color: #ef4444 !important;
    font-weight: 700 !important;
    background: #fff5f5 !important;
}
button[kind="secondary"]:hover {
    background: #fef2f2 !important;
    border-color: #dc2626 !important;
}

/* ── FIX UNIVERSAL: BOTÓN DE SIDEBAR (MÓVIL, TABLET Y PC) ── */
[data-testid="collapsedControl"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background-color: #f0f9ff !important;
    border: 2px solid #0ea5e9 !important;
    border-radius: 10px !important;
    z-index: 999999 !important;
    width: 45px !important;  
    height: 45px !important; 
    margin: 10px !important; 
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 10px rgba(14, 165, 233, 0.2) !important;
}
[data-testid="collapsedControl"] svg {
    fill: #0ea5e9 !important;
    color: #0ea5e9 !important;
    width: 26px !important;
    height: 26px !important;
}
[data-testid="collapsedControl"]:hover,
[data-testid="collapsedControl"]:active {
    background-color: #0ea5e9 !important;
    transform: scale(1.05) !important;
}
[data-testid="collapsedControl"]:hover svg,
[data-testid="collapsedControl"]:active svg {
    fill: white !important;
    color: white !important;
}

/* Evitar que la cabecera invisible tape el botón */
header[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 99998 !important;
}

/* ── FIX CRÍTICO: texto visible en el chat ── */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em,
[data-testid="stChatMessage"] code {
    color: #1e293b !important;
}

/* Fondo blanco para los mensajes del chat */
[data-testid="stChatMessage"] {
    background: white !important;
    border-radius: 14px !important;
    padding: 10px 16px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
}

/* Mensaje del usuario con fondo ligeramente diferente */
[data-testid="stChatMessage"][data-testid*="user"] {
    background: #f0f9ff !important;
}

/* Texto general del área principal */
.stMarkdown p, .stMarkdown li, .stMarkdown span { color: #1e293b !important; }
section[data-testid="stMain"] p { color: #1e293b !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  PROMPT DE MONI
# ═══════════════════════════════════════════════
INSTRUCCIONES_MONI = """
Eres Moni, una mentora educativa IA muy amable, paciente y motivadora. Acompañas a estudiantes mexicanos de secundaria y preparatoria (12–18 años). Tu objetivo es que cada alumno aprenda mejor y, al terminar la prepa, pueda elegir su carrera con evidencia real.

══════════════════════════════════════
INICIO DE SESIÓN
══════════════════════════════════════
Ya conoces el nombre y grado del alumno porque se registró. Salúdalo por su nombre desde el primer mensaje. Si es su primera vez, hazle la entrevista inicial de forma natural y conversacional:
1. ¿Qué materias se te dificultan más? (con empatía, no juicio)
2. ¿Cuáles son tus materias favoritas o qué temas te apasionan?
3. ¿Ya tienes idea de qué carrera te gustaría estudiar?

══════════════════════════════════════
MODOS DE OPERACIÓN (detéctalos automáticamente)
══════════════════════════════════════

🔴 MODO NIVELACIÓN — activado cuando el alumno pregunta sobre una materia difícil o muestra confusión:
- Escribe exactamente al inicio: "📚 Modo nivelación activado ✨"
- Sé ultra paciente. Explica desde lo más básico.
- NUNCA des la respuesta directa. Usa preguntas guía, analogías, ejemplos similares.
- Divide el problema en pasos pequeños. Celebra cada avance.
- Si no entiende tras 2 intentos, cambia completamente tu estrategia.

🟢 MODO PROFUNDIZACIÓN — activado cuando el alumno pregunta sobre algo que le apasiona:
- Escribe exactamente al inicio: "🚀 Modo profundización activado ✨"
- Ofrece datos curiosos, conexiones con el mundo real, retos adicionales.
- Conéctalo con carreras y aplicaciones profesionales reales.
- Hazlo sentir como experto en formación.

🟣 MODO VOCACIONAL — activado cuando el alumno pregunta sobre carreras o su futuro:
- Escribe exactamente al inicio: "🌟 Orientación vocacional ✨"
- Conecta sus fortalezas observadas en la conversación con carreras concretas.
- Da 2-3 opciones con descripción del día a día de cada una.
- Sé honesto: si requiere fortalecer algo, díselo con amabilidad y da un plan.

══════════════════════════════════════
REGLAS DE ORO
══════════════════════════════════════
✅ Personaliza SIEMPRE con el nombre del alumno.
✅ Usa emojis estratégicamente para hacer el aprendizaje divertido.
✅ Si el alumno está frustrado, primero valida su emoción, luego explica.
✅ Conecta lo académico con sus sueños y su vida real.
❌ NUNCA des la solución directa a tareas o ejercicios.
❌ NUNCA uses lenguaje condescendiente.
❌ NUNCA ignores información que el alumno haya compartido sobre sí mismo.
"""

# ═══════════════════════════════════════════════
#  FUNCIONES DE PERFIL (MEMORIA)
# ═══════════════════════════════════════════════
def id_alumno(nombre, grado):
    """Genera un ID único y seguro para el alumno evitando Path Traversal."""
    # Quita acentos para el ID de archivo, asegurando compatibilidad
    nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', nombre.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n'))
    grado_limpio = re.sub(r'[^a-zA-Z0-9]', '', grado.lower())
    return f"{nombre_limpio}_{grado_limpio}"

def ruta_perfil(alumno_id):
    return os.path.join(PERFILES_DIR, f"{alumno_id}.json")

def cargar_perfil(alumno_id):
    """Carga el perfil del alumno si existe."""
    ruta = ruta_perfil(alumno_id)
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def guardar_perfil(alumno_id, perfil):
    """Guarda el perfil del alumno en disco."""
    ruta = ruta_perfil(alumno_id)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(perfil, f, ensure_ascii=False, indent=2)

def crear_perfil_nuevo(nombre, grado):
    """Crea un perfil nuevo para el alumno."""
    return {
        "nombre": nombre,
        "grado": grado,
        "primera_sesion": datetime.now().strftime("%Y-%m-%d"),
        "ultima_sesion": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_sesiones": 1,
        "mensajes_totales": 0,
        "modos": {"nivelacion": 0, "profundizacion": 0, "vocacional": 0},
        "historial": []
    }

def actualizar_perfil(perfil, messages):
    """Actualiza estadísticas del perfil con la sesión actual."""
    perfil["ultima_sesion"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    perfil["mensajes_totales"] += len([m for m in messages if m["role"] == "user"])

    for msg in messages:
        if msg["role"] == "assistant":
            contenido = msg["content"].lower()
            if "modo nivelación" in contenido or "modo nivelacion" in contenido:
                perfil["modos"]["nivelacion"] += 1
            elif "modo profundización" in contenido or "modo profundizacion" in contenido:
                perfil["modos"]["profundizacion"] += 1
            elif "orientación vocacional" in contenido or "orientacion vocacional" in contenido:
                perfil["modos"]["vocacional"] += 1

    # Guardar resumen del historial (últimos 100 mensajes)
    perfil["historial"] = messages[-100:] if len(messages) > 100 else messages
    return perfil

def listar_perfiles():
    """Lista todos los perfiles guardados."""
    perfiles = []
    if not os.path.exists(PERFILES_DIR):
        return perfiles
    for archivo in os.listdir(PERFILES_DIR):
        if archivo.endswith(".json"):
            ruta = os.path.join(PERFILES_DIR, archivo)
            with open(ruta, "r", encoding="utf-8") as f:
                try:
                    perfiles.append(json.load(f))
                except:
                    pass
    return sorted(perfiles, key=lambda x: x.get("ultima_sesion", ""), reverse=True)

# ═══════════════════════════════════════════════
#  FUNCIÓN: DETECTAR MODO ACTIVO
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
    return "general"

# ═══════════════════════════════════════════════
#  ESTADO INICIAL
# ═══════════════════════════════════════════════
if "vista" not in st.session_state:
    st.session_state.vista = "inicio"          # inicio | alumno_login | chat | maestro_login | dashboard
if "perfil_activo" not in st.session_state:
    st.session_state.perfil_activo = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "es_primera_vez" not in st.session_state:
    st.session_state.es_primera_vez = False

# ═══════════════════════════════════════════════
#  API KEY (desde secrets o variable de entorno)
# ═══════════════════════════════════════════════
def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except:
        return os.environ.get("GEMINI_API_KEY", "")

# ════════════════════════════════════════════════════════════
#  VISTA 1: PANTALLA DE INICIO
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
        st.markdown("""
        <div style="text-align:center; margin-bottom:24px;">
            <p style="color:#475569; font-size:1rem;">¿Cómo quieres entrar?</p>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            <div class="role-card">
                <div class="role-icon">🎒</div>
                <div class="role-title">Soy alumno</div>
                <div class="role-desc">Chatea con Moni y aprende</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Entrar como alumno", key="btn_alumno", use_container_width=True):
                st.session_state.vista = "alumno_login"
                st.rerun()

        with col_b:
            st.markdown("""
            <div class="role-card">
                <div class="role-icon">👨‍🏫</div>
                <div class="role-title">Soy maestro</div>
                <div class="role-desc">Ver panel de seguimiento</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Entrar como maestro", key="btn_maestro", use_container_width=True):
                st.session_state.vista = "maestro_login"
                st.rerun()

        # Características
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card" style="margin-top:20px;">
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:0.85rem; color:#475569;">
                <div>📚 <b>Nivelación</b> — te explica sin darte la tarea resuelta</div>
                <div>🚀 <b>Profundización</b> — retos extra en lo que te apasiona</div>
                <div>🌟 <b>Orientación vocacional</b> — carreras según tu perfil real</div>
                <div>🧠 <b>Memoria</b> — te recuerda en cada sesión</div>
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
            <p style="color:#64748b; font-size:0.9rem;">Moni te recordará cada vez que entres</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_alumno"):
            nombre = st.text_input("Tu nombre", placeholder="Ej: Valeria López")
            grado = st.selectbox("Tu grado actual", [
                "1° Secundaria", "2° Secundaria", "3° Secundaria",
                "1° Semestre Prepa", "2° Semestre Prepa", "3° Semestre Prepa",
                "4° Semestre Prepa", "5° Semestre Prepa", "6° Semestre Prepa"
            ])
            submitted = st.form_submit_button("¡Entrar con Moni! 🚀", use_container_width=True)

        if submitted:
            # Validación estricta del nombre agregada aquí
            if not nombre.strip():
                st.error("Por favor escribe tu nombre.")
            elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', nombre.strip()):
                st.error("❌ El nombre solo puede contener letras y espacios, sin números ni símbolos.")
            else:
                nombre = nombre.strip().title()
                alumno_id = id_alumno(nombre, grado)
                perfil_existente = cargar_perfil(alumno_id)

                if perfil_existente:
                    # Alumno ya conocido
                    perfil_existente["ultima_sesion"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    perfil_existente["total_sesiones"] = perfil_existente.get("total_sesiones", 1) + 1
                    st.session_state.perfil_activo = perfil_existente
                    # Cargar historial previo
                    st.session_state.messages = perfil_existente.get("historial", [])
                    st.session_state.es_primera_vez = False
                else:
                    # Alumno nuevo
                    perfil_nuevo = crear_perfil_nuevo(nombre, grado)
                    st.session_state.perfil_activo = perfil_nuevo
                    st.session_state.messages = []
                    st.session_state.es_primera_vez = True

                guardar_perfil(alumno_id, st.session_state.perfil_activo)
                st.session_state.vista = "chat"
                st.rerun()

        if st.button("← Volver", key="back_from_alumno"):
            st.session_state.vista = "inicio"
            st.rerun()

# ════════════════════════════════════════════════════════════
#  VISTA 3: CHAT CON MONI
# ════════════════════════════════════════════════════════════
elif st.session_state.vista == "chat":

    perfil = st.session_state.perfil_activo
    nombre = perfil["nombre"]
    grado  = perfil["grado"]
    alumno_id = id_alumno(nombre, grado)

    # ── SIDEBAR ──────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding:16px 0 8px;">
            <div style="font-size:2.5rem;">👋</div>
            <div style="font-size:1.1rem; font-weight:800;">{nombre}</div>
            <div style="font-size:0.8rem; color:#8b949e;">{grado}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Estadísticas
        modos = perfil.get("modos", {})
        sesiones = perfil.get("total_sesiones", 1)
        mensajes = perfil.get("mensajes_totales", 0)

        st.markdown("**📊 Tu progreso**")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class="card-dark" style="text-align:center;">
                <div style="font-size:1.4rem; font-weight:900;">{sesiones}</div>
                <div style="font-size:0.65rem; color:#8b949e;">SESIONES</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="card-dark" style="text-align:center;">
                <div style="font-size:1.4rem; font-weight:900;">{mensajes}</div>
                <div style="font-size:0.65rem; color:#8b949e;">MENSAJES</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<span class="badge badge-niv">📚 Nivelación: {modos.get("nivelacion",0)}</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<span class="badge badge-prof">🚀 Profund.: {modos.get("profundizacion",0)}</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<span class="badge badge-voc">🌟 Vocacional: {modos.get("vocacional",0)}</span>', unsafe_allow_html=True)

        st.markdown("---")

        # Modo activo
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

        # Exportar perfil
        perfil_export = json.dumps(perfil, ensure_ascii=False, indent=2)
        st.download_button(
            "⬇️ Exportar mi perfil",
            data=perfil_export,
            file_name=f"perfil_{alumno_id}.json",
            mime="application/json",
            use_container_width=True
        )

        if st.button("🚪 Cerrar sesión", use_container_width=True):
            # Guardar antes de salir
            perfil_actualizado = actualizar_perfil(perfil, st.session_state.messages)
            guardar_perfil(alumno_id, perfil_actualizado)
            st.session_state.vista = "inicio"
            st.session_state.perfil_activo = None
            st.session_state.messages = []
            st.rerun()

    # ── CHAT PRINCIPAL ────────────────────────────────────
    # ── BARRA SUPERIOR FIJA (siempre visible, funciona en móvil) ──
    col_t, col_b = st.columns([3, 1])
    with col_t:
        st.markdown(f'<p class="titulo-moni">🤖 Hola, {nombre}!</p>', unsafe_allow_html=True)
        st.markdown(f"*{grado} · Tu mentora inteligente*")
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Cerrar sesión", key="logout_top", use_container_width=True):
            perfil_actualizado = actualizar_perfil(perfil, st.session_state.messages)
            guardar_perfil(alumno_id, perfil_actualizado)
            st.session_state.vista = "inicio"
            st.session_state.perfil_activo = None
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    # ── BARRA DE MODO (siempre visible aunque el sidebar esté cerrado) ──
    modo_actual = detectar_modo(st.session_state.messages)
    modos_info = {
        "nivelacion":     ("📚", "Modo Nivelación", "#fef2f2", "#ef4444"),
        "profundizacion": ("🚀", "Modo Profundización", "#f0fdf4", "#22c55e"),
        "vocacional":     ("🌟", "Orientación Vocacional", "#faf5ff", "#a855f7"),
        "general":        ("💬", "Conversación General", "#f0f9ff", "#0ea5e9"),
    }
    icono_m, label_m, bg_m, color_m = modos_info.get(modo_actual, modos_info["general"])
    modos_d = perfil.get("modos", {})
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between;
                background:{bg_m}; border:1.5px solid {color_m}33;
                border-radius:12px; padding:10px 18px; margin-bottom:12px;">
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:1.2rem;">{icono_m}</span>
            <span style="font-weight:800; color:{color_m}; font-size:0.9rem;">{label_m}</span>
        </div>
        <div style="display:flex; gap:12px; font-size:0.78rem; color:#64748b;">
            <span>📚 <b>{modos_d.get('nivelacion',0)}</b></span>
            <span>🚀 <b>{modos_d.get('profundizacion',0)}</b></span>
            <span>🌟 <b>{modos_d.get('vocacional',0)}</b></span>
            <span style="color:#94a3b8;">Sesión #{perfil.get('total_sesiones',1)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Mensaje de bienvenida automático (sin que el alumno escriba)
    api_key = get_api_key()

    if not st.session_state.messages and api_key:
        es_nuevo = st.session_state.es_primera_vez

        if es_nuevo:
            bienvenida = f"""¡Hola, **{nombre}**! 🎉✨ Soy **Moni**, tu mentora inteligente.

Estoy aquí para acompañarte en {grado} y en todo lo que viene después. Voy a ayudarte con las materias que se te dificulten, potenciar las que te apasionan y, cuando llegue el momento, orientarte en qué carrera va mejor contigo. 🎯

Para conocerte mejor, cuéntame: **¿qué materias se te hacen más difíciles?** No te preocupes, no te voy a juzgar, al contrario, ¡para eso estoy! 😊"""
        else:
            ultima = perfil.get("ultima_sesion", "antes")
            sesion_num = perfil.get("total_sesiones", 2)
            bienvenida = f"""¡Hola de nuevo, **{nombre}**! 🌟 ¡Qué bueno que regresaste!

Esta es tu sesión **#{sesion_num}** conmigo. Recuerdo todo lo que hemos trabajado juntos. 💪

**¿En qué te puedo ayudar hoy?** ¿Tienes alguna duda de alguna materia, quieres explorar algo que te interese, o quieres platicar sobre tu futuro? Aquí estoy. 😊"""

        with st.chat_message("assistant"):
            st.markdown(bienvenida)
        st.session_state.messages.append({"role": "assistant", "content": bienvenida})
        st.session_state.es_primera_vez = False

        # Guardar bienvenida en perfil
        perfil_actualizado = actualizar_perfil(perfil, st.session_state.messages)
        guardar_perfil(alumno_id, perfil_actualizado)
        st.session_state.perfil_activo = perfil_actualizado
        st.rerun()

    # Input del usuario
    if api_key:
        prompt = st.chat_input(f"Escríbele a Moni, {nombre}... 💬")

        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Contexto del perfil para Gemini
            contexto_perfil = f"""
INFORMACIÓN DEL ALUMNO:
- Nombre: {nombre}
- Grado: {grado}
- Sesión número: {perfil.get('total_sesiones', 1)}
- Primera sesión: {perfil.get('primera_sesion', 'hoy')}
- Interacciones previas de nivelación: {perfil.get('modos', {}).get('nivelacion', 0)}
- Interacciones previas de profundización: {perfil.get('modos', {}).get('profundizacion', 0)}
{"- Es alumno NUEVO, esta es su primera sesión." if perfil.get('total_sesiones', 1) == 1 else f"- Alumno RECURRENTE con {perfil.get('total_sesiones',1)} sesiones."}
"""
            instrucciones_completas = INSTRUCCIONES_MONI + "\n\n" + contexto_perfil

            # Construir historial para Gemini
            historial_gemini = []
            for msg in st.session_state.messages:
                rol = "user" if msg["role"] == "user" else "model"
                historial_gemini.append({
                    "role": rol,
                    "parts": [{"text": msg["content"]}]
                })

            with st.chat_message("assistant"):
                with st.spinner("Moni está pensando... 🤔"):
                    try:
                        client = genai.Client(api_key=api_key)
                        respuesta = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=historial_gemini,
                            config=types.GenerateContentConfig(
                                system_instruction=instrucciones_completas
                            )
                        )
                        texto = respuesta.text
                        st.markdown(texto)
                        st.session_state.messages.append({"role": "assistant", "content": texto})

                        # Guardar perfil actualizado
                        perfil_actualizado = actualizar_perfil(
                            st.session_state.perfil_activo,
                            st.session_state.messages
                        )
                        guardar_perfil(alumno_id, perfil_actualizado)
                        st.session_state.perfil_activo = perfil_actualizado

                    except Exception as e:
                        st.error(f"Algo salió mal: {e}")
            st.rerun()
    else:
        st.error("⚠️ No se encontró la API key de Gemini. Configúrala en los Secrets de Streamlit.")

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
            password = st.text_input("Contraseña docente", type="password",
                                     placeholder="Ingresa la contraseña")
            submitted = st.form_submit_button("Entrar al panel 📊", use_container_width=True)

        if submitted:
            # Contraseña desde secrets o default para demo
            try:
                password_correcta = st.secrets["TEACHER_PASSWORD"]
            except:
                password_correcta = "moni2025"  # Default para demo

            if password == password_correcta:
                st.session_state.vista = "dashboard"
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta.")
                st.info("💡 **Demo:** usa la contraseña `moni2025`")

        if st.button("← Volver", key="back_from_maestro"):
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
        st.markdown("**🔍 Filtros**")

        perfiles_todos = listar_perfiles()
        grados_disponibles = list(set([p.get("grado", "Sin grado") for p in perfiles_todos]))
        grados_disponibles.insert(0, "Todos los grados")
        filtro_grado = st.selectbox("Filtrar por grado", grados_disponibles)

        st.markdown("---")

        # Exportar todos los perfiles
        if perfiles_todos:
            todos_json = json.dumps(perfiles_todos, ensure_ascii=False, indent=2)
            st.download_button(
                "⬇️ Exportar todos los perfiles",
                data=todos_json,
                file_name=f"perfiles_grupo_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )

        if st.button("🚪 Cerrar sesión", use_container_width=True):
            st.session_state.vista = "inicio"
            st.rerun()

    # ── DASHBOARD PRINCIPAL ───────────────────────────────
    st.markdown('<p class="titulo-moni">📊 Panel del Maestro</p>', unsafe_allow_html=True)
    st.markdown("*Seguimiento de aprendizaje por alumno*")
    st.markdown("---")

    perfiles = listar_perfiles()

    # Filtrar por grado
    if filtro_grado != "Todos los grados":
        perfiles = [p for p in perfiles if p.get("grado") == filtro_grado]

    if not perfiles:
        st.markdown("""
        <div class="card" style="text-align:center; padding:40px;">
            <p style="font-size:3rem;">📭</p>
            <p style="font-weight:700; color:#475569;">Aún no hay alumnos registrados</p>
            <p style="color:#94a3b8; font-size:0.9rem;">Los perfiles aparecerán aquí cuando los alumnos inicien sesión con Moni.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── MÉTRICAS GLOBALES ──
        total_alumnos  = len(perfiles)
        total_sesiones = sum(p.get("total_sesiones", 0) for p in perfiles)
        total_msgs     = sum(p.get("mensajes_totales", 0) for p in perfiles)
        total_niv      = sum(p.get("modos", {}).get("nivelacion", 0) for p in perfiles)
        total_prof     = sum(p.get("modos", {}).get("profundizacion", 0) for p in perfiles)
        total_voc      = sum(p.get("modos", {}).get("vocacional", 0) for p in perfiles)

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        for col, num, label, color in [
            (c1, total_alumnos,  "Alumnos",      "#0ea5e9"),
            (c2, total_sesiones, "Sesiones",      "#8b5cf6"),
            (c3, total_msgs,     "Mensajes",      "#f59e0b"),
            (c4, total_niv,      "📚 Nivelac.",   "#ef4444"),
            (c5, total_prof,     "🚀 Profund.",   "#22c55e"),
            (c6, total_voc,      "🌟 Vocacional", "#a855f7"),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-num" style="color:{color};">{num}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── TABLA DE ALUMNOS ──
        col_lista, col_detalle = st.columns([1, 1.8])

        with col_lista:
            st.markdown("### 👥 Alumnos")

            alumno_seleccionado = None
            for i, p in enumerate(perfiles):
                nombre_p = p.get("nombre", "Sin nombre")
                grado_p  = p.get("grado", "")
                sesiones_p = p.get("total_sesiones", 0)
                ultima_p   = p.get("ultima_sesion", "")[:10]

                # Indicador de actividad
                niv_p  = p.get("modos", {}).get("nivelacion", 0)
                prof_p = p.get("modos", {}).get("profundizacion", 0)

                if st.button(
                    f"**{nombre_p}** · {grado_p}\n📅 {ultima_p} · {sesiones_p} sesiones",
                    key=f"alumno_{i}",
                    use_container_width=True
                ):
                    st.session_state["alumno_detalle"] = p

        with col_detalle:
            st.markdown("### 🔍 Detalle del alumno")

            detalle = st.session_state.get("alumno_detalle", None)

            if not detalle:
                st.markdown("""
                <div class="card" style="text-align:center; padding:30px;">
                    <p style="font-size:2rem;">👈</p>
                    <p style="color:#94a3b8;">Selecciona un alumno para ver su perfil completo</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                nombre_d   = detalle.get("nombre", "")
                grado_d    = detalle.get("grado", "")
                primera_d  = detalle.get("primera_sesion", "")
                ultima_d   = detalle.get("ultima_sesion", "")
                sesiones_d = detalle.get("total_sesiones", 0)
                msgs_d     = detalle.get("mensajes_totales", 0)
                modos_d    = detalle.get("modos", {})

                st.markdown(f"""
                <div class="card">
                    <div style="font-size:1.4rem; font-weight:900; color:#1e293b;">{nombre_d}</div>
                    <div style="font-size:0.85rem; color:#64748b; margin-top:4px;">{grado_d}</div>

                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:16px; font-size:0.82rem;">
                        <div><b>Primera sesión:</b><br>{primera_d}</div>
                        <div><b>Última sesión:</b><br>{ultima_d[:16]}</div>
                        <div><b>Total sesiones:</b><br>{sesiones_d}</div>
                        <div><b>Mensajes enviados:</b><br>{msgs_d}</div>
                    </div>

                    <div style="margin-top:16px;">
                        <b style="font-size:0.85rem; color:#475569;">DISTRIBUCIÓN DE MODOS</b>
                        <div style="margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;">
                            <span class="badge badge-niv">📚 Nivelación: {modos_d.get('nivelacion',0)}</span>
                            <span class="badge badge-prof">🚀 Profundización: {modos_d.get('profundizacion',0)}</span>
                            <span class="badge badge-voc">🌟 Vocacional: {modos_d.get('vocacional',0)}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Últimos mensajes
                historial = detalle.get("historial", [])
                if historial:
                    st.markdown("**📝 Últimas interacciones:**")
                    ultimos = historial[-6:]
                    for msg in ultimos:
                        rol   = msg.get("role", "")
                        texto = msg.get("content", "")[:180]
                        if len(msg.get("content", "")) > 180:
                            texto += "..."
                        icono = "🧑" if rol == "user" else "🤖"
                        st.markdown(f"""
                        <div style="background:{'#f8fafc' if rol=='user' else '#f0f9ff'};
                                    border-left: 3px solid {'#94a3b8' if rol=='user' else '#0ea5e9'};
                                    padding: 8px 12px; border-radius: 0 8px 8px 0;
                                    margin-bottom:6px; font-size:0.8rem; color:#374151;">
                            {icono} {texto}
                        </div>
                        """, unsafe_allow_html=True)

                # Exportar perfil individual
                alumno_json = json.dumps(detalle, ensure_ascii=False, indent=2)
                st.download_button(
                    f"⬇️ Exportar perfil de {nombre_d}",
                    data=alumno_json,
                    file_name=f"perfil_{nombre_d.lower().replace(' ','_')}.json",
                    mime="application/json",
                    use_container_width=True
                )
