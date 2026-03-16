# 🌟 Moni – Tu Mentora Inteligente

Herramienta de IA educativa para acompañamiento personalizado de estudiantes de secundaria a preparatoria.

## 🚀 Características

- **3 modos automáticos:** Nivelación 📚, Profundización 🚀, Orientación Vocacional 🌟
- **Memoria entre sesiones:** Moni recuerda a cada alumno en cada visita
- **Panel del maestro:** Seguimiento completo de todos los alumnos
- **Sin API key visible:** Los alumnos no necesitan ninguna clave
- **Perfiles exportables:** Cada alumno puede descargar su historial

## ⚙️ Configuración en Streamlit Cloud

Ve a **Settings → Secrets** y agrega:

GEMINI_API_KEY = "tu-api-key-de-gemini-aquí"
TEACHER_PASSWORD = "la-contraseña-del-maestro"

## 📁 Estructura del proyecto

- app.py — Código principal
- requirements.txt — Dependencias
- README.md — Este archivo
- perfiles/ — Perfiles de alumnos (se crean automáticamente)

## 🏫 Flujo de uso

1. Alumno entra con su nombre y grado → Moni lo recuerda
2. Moni detecta automáticamente si necesita nivelación, profundización o guía vocacional
3. Maestro entra con contraseña → ve el panel con todos los alumnos y su progreso

## 📖 Basado en

- Erikson (1968) – Identidad y desarrollo adolescente
- VanLehn (2011) – Efectividad de los sistemas de tutoría inteligente
- Gómez Amaiquema (2024) – IA y aprendizaje personalizado
- SEP / Prepa en Línea (2025) – IA en educación mexicana
