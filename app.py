import streamlit as st
import anthropic

# ── Configuración de página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Asistente PEP — GCBA",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header { padding: 1rem 0 0.5rem; border-bottom: 1px solid #e0dfd8; margin-bottom: 1rem; }
    .main-header h1 { font-size: 1.4rem; font-weight: 600; color: #1a1a18; margin: 0; }
    .main-header p  { font-size: 0.8rem; color: #888; margin: 0; }
    .source-badge {
        display: inline-block; font-size: 0.7rem; font-weight: 500;
        padding: 2px 10px; border-radius: 20px; margin: 2px 3px 2px 0;
    }
    .disclaimer { font-size: 0.75rem; color: #aaa; text-align: center; margin-top: 0.5rem; }
    div[data-testid="stChatMessage"] { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Base de documentos ─────────────────────────────────────────────────────────
DOCS = [
    {
        "id": 1,
        "titulo": "Ley 471 – Relaciones Laborales en la CABA",
        "area": "RRHH",
        "ministerio": "Jefatura de Gabinete",
        "tipo": "Ley",
        "fecha": "2000-09-26",
        "contenido": """La Ley 471 regula las relaciones laborales del personal que presta servicios bajo relación de dependencia en la Administración Pública de la Ciudad Autónoma de Buenos Aires.

LICENCIAS:
- Artículo 68: El agente tiene derecho a licencia sin goce de haberes por razones particulares de hasta 12 meses. Debe solicitarse con 30 días de anticipación ante el área de RRHH del organismo.
- Artículo 69: Licencia por enfermedad de largo tratamiento: hasta 2 años con goce de haberes, y hasta 1 año adicional sin goce.
- Artículo 70: Licencia por maternidad: 90 días corridos a partir del alumbramiento.
- Artículo 71: Licencia por paternidad: 10 días hábiles.
- Artículo 72: Licencia gremial: hasta 30 días por año calendario para representantes sindicales.

CARRERA ADMINISTRATIVA:
- Artículo 34: El ingreso a la carrera se realiza exclusivamente por el nivel más bajo del escalafón mediante concurso público.
- Artículo 45: La antigüedad se computa desde la fecha de incorporación efectiva al servicio.

DISCIPLINA:
- Artículo 82: Las sanciones son: llamado de atención, apercibimiento, suspensión (hasta 30 días), cesantía, exoneración.
- Artículo 85: Toda sanción debe ser precedida de sumario administrativo con derecho a defensa.""",
    },
    {
        "id": 2,
        "titulo": "Resolución 1142/MHFGC/2021 – Procedimiento de Licencias",
        "area": "RRHH",
        "ministerio": "Ministerio de Hacienda y Finanzas",
        "tipo": "Resolución",
        "fecha": "2021-06-15",
        "contenido": """Reglamenta los procedimientos para la tramitación de licencias del personal del GCBA.

PROCEDIMIENTO LICENCIA SIN GOCE:
1. El agente presenta solicitud mediante formulario F-LGH-04 en el sistema SADE.
2. El jefe inmediato debe dictaminar en 5 días hábiles.
3. La Dirección de RRHH aprueba o rechaza en 10 días hábiles.
4. Para prórrogas interviene la Subsecretaría de Gestión de RRHH.
5. La resolución debe notificarse al agente con 48 horas de anticipación.

FORMULARIOS:
- F-LGH-04: Solicitud de licencia sin goce.
- F-LGH-07: Prórroga de licencia sin goce.
- F-CERT-01: Certificado médico.

Todas las tramitaciones se realizan en SADE. No se aceptan expedientes en papel desde enero 2022.""",
    },
    {
        "id": 3,
        "titulo": "Decreto 638/GCBA/2019 – Estructura del Ministerio de Educación",
        "area": "Educación",
        "ministerio": "Ministerio de Educación",
        "tipo": "Decreto",
        "fecha": "2019-04-10",
        "contenido": """Establece la estructura orgánica del Ministerio de Educación de la CABA.

AUTORIDADES:
- Ministro/a: máxima autoridad, dicta resoluciones ministeriales.
- Subsecretario/a de Gestión Educativa: supervisión escolar y desarrollo curricular.
- Director General de Educación Primaria (DGEPU): gestiona 440 escuelas primarias.
- Director General de Educación Media (DGEM): gestiona 125 escuelas secundarias.

COMPETENCIAS:
- Competencia exclusiva sobre el diseño curricular jurisdiccional.
- Las designaciones de directores escolares requieren resolución ministerial.
- Las habilitaciones de escuelas privadas requieren autorización de la Subsecretaría.""",
    },
    {
        "id": 4,
        "titulo": "Ley 70 – Administración Financiera y Control del Sector Público",
        "area": "Presupuesto",
        "ministerio": "Ministerio de Hacienda y Finanzas",
        "tipo": "Ley",
        "fecha": "1998-03-05",
        "contenido": """Regula el sistema de administración financiera y control del GCBA.

PRESUPUESTO:
- Art. 44: Modificaciones que incrementan el gasto total requieren aprobación legislativa.
- Art. 45: Compensaciones entre partidas del mismo programa: hasta 5% del crédito vigente, autoriza el Subsecretario de Presupuesto.
- Art. 46: Reestructuraciones entre programas requieren resolución conjunta del Jefe de Gabinete y Ministro de Hacienda.

CONTRATACIONES:
- Hasta 100.000 UMAs: contratación directa.
- Entre 100.000 y 500.000 UMAs: licitación privada.
- Más de 500.000 UMAs: licitación pública obligatoria.
- Toda contratación debe publicarse en el BAC (Buenos Aires Compras).

SISTEMA SIGAF: único medio válido para registrar compromisos, devengamiento y pagos.""",
    },
    {
        "id": 5,
        "titulo": "Circular RRHH-09/2023 – Programa de Especialistas Profesionales (PEP)",
        "area": "RRHH",
        "ministerio": "Jefatura de Gabinete",
        "tipo": "Circular",
        "fecha": "2023-08-01",
        "contenido": """Establece condiciones y procedimientos del PEP del Gobierno de la Ciudad.

DESCRIPCIÓN:
El PEP incorpora profesionales universitarios para fortalecer las capacidades técnicas de los equipos del GCBA. Cuenta con 2000 participantes activos.

CONDICIONES DE INGRESO:
- Título universitario de grado (mínimo 4 años).
- Edad máxima al ingreso: 40 años.
- Residencia en CABA o GBA.
- Aprobación del proceso de selección (entrevistas, evaluación técnica y psicotécnica).

MODALIDAD:
Contratación de locación de servicios, con renovaciones semestrales sujetas a evaluación de desempeño.

DERECHOS Y OBLIGACIONES:
- Jornada: 35 horas semanales.
- Honorarios: Categoría A (recién graduados), B (hasta 3 años exp.), C (más de 3 años).
- Capacitación obligatoria: 40 horas anuales en INAP o instituciones reconocidas.
- Informe trimestral de avance al referente institucional.
- Rotación posible tras 12 meses, con aprobación de ambos referentes.""",
    },
    {
        "id": 6,
        "titulo": "Resolución 452/MSGC/2022 – Protocolo de Atención en Centros de Salud",
        "area": "Salud",
        "ministerio": "Ministerio de Salud",
        "tipo": "Resolución",
        "fecha": "2022-03-14",
        "contenido": """Establece protocolos de atención y derivación en la red de salud del GCBA.

RED DE SALUD:
- Nivel 1: CeSAC – 45 centros. Puerta de entrada al sistema público.
- Nivel 2: Hospitales de mediana complejidad – 12 hospitales.
- Nivel 3: Hospitales de alta complejidad – 8 hospitales.

DERIVACIÓN: mediante el sistema SISA. Todo paciente ingresa por Nivel 1 salvo urgencias.

PROFESIONALES PEP EN SALUD:
Prestan funciones en planificación sanitaria, epidemiología y gestión de programas de salud pública.
No ejercen funciones asistenciales directas salvo matrícula habilitante vigente.""",
    },
]

TIPO_COLORES = {
    "Ley":        ("🔵", "#e6f1fb", "#0C447C"),
    "Resolución": ("🟢", "#eaf3de", "#3B6D11"),
    "Decreto":    ("🟡", "#faeeda", "#854F0B"),
    "Circular":   ("🟣", "#EEEDFE", "#534AB7"),
    "Manual":     ("🩷", "#FBEAF0", "#993556"),
    "Otro":       ("⚪", "#f1efea", "#5F5E5A"),
}

# ── Búsqueda ───────────────────────────────────────────────────────────────────
def search_docs(query, docs, ministerio_filter):
    q = query.lower()
    words = [w for w in q.split() if len(w) > 3]
    pool = docs if ministerio_filter == "Todos" else [d for d in docs if d["ministerio"] == ministerio_filter]
    scored = []
    for doc in pool:
        text = (doc["titulo"] + " " + doc["contenido"] + " " + doc["area"] + " " + doc["ministerio"]).lower()
        score = sum(text.count(w) for w in words)
        if q in text:
            score += 10
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:3]]

# ── Claude ─────────────────────────────────────────────────────────────────────
def ask_claude(user_message, relevant_docs, history, ministerio_filter):
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "⚠️ Falta la API key. Configurala en Streamlit Cloud → Settings → Secrets."

    ctx = "\n\n---\n\n".join(
        f"[FUENTE: {d['titulo']} | {d['tipo']} | {d['ministerio']} | {d['fecha']}]\n{d['contenido']}"
        for d in relevant_docs
    ) if relevant_docs else "No se encontraron documentos relevantes para esta consulta."

    area_note = f"\nFILTRO ACTIVO: el usuario consulta sobre \"{ministerio_filter}\"." if ministerio_filter != "Todos" else ""

    system = f"""Sos el asistente institucional del PEP (Programa de Especialistas Profesionales) del Gobierno de la Ciudad Autónoma de Buenos Aires.

REGLAS:
1. Respondé ÚNICAMENTE basándote en los documentos provistos.
2. Si la información no está disponible respondé: "Esta información no se encuentra en el repositorio. Consultá directamente con el área competente."
3. Citá la fuente al final: Fuente: [nombre del documento].
4. Español rioplatense, tono profesional. Usá "vos".
5. Si hay pasos de un procedimiento, listalos numerados.
6. No inventes artículos, fechas ni procedimientos.
{area_note}

DOCUMENTOS DISPONIBLES:
{ctx}"""

    messages = [{"role": m["role"], "content": m["content"]} for m in history[-6:]]

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=system,
        messages=messages,
    )
    return response.content[0].text

# ── Estado de sesión ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "docs" not in st.session_state:
    st.session_state.docs = DOCS.copy()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏛️ Asistente PEP")
    st.caption("Gobierno de la Ciudad de Buenos Aires")
    st.divider()

    ministerios = ["Todos"] + sorted(set(d["ministerio"] for d in st.session_state.docs))
    filtro = st.selectbox("Filtrar por área", ministerios)

    st.divider()
    st.caption(f"📂 {len(st.session_state.docs)} documentos en el repositorio")

    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    vista = st.radio("Vista", ["💬 Consultas", "📁 Repositorio"], label_visibility="collapsed")

# ── Vista: CHAT ────────────────────────────────────────────────────────────────
if vista == "💬 Consultas":
    st.markdown('<div class="main-header"><h1>💬 Consultas al repositorio PEP</h1><p>Las respuestas se generan exclusivamente a partir de los documentos cargados</p></div>', unsafe_allow_html=True)

    # Sugerencias
    if not st.session_state.messages:
        st.markdown("**Preguntas frecuentes:**")
        cols = st.columns(2)
        sugs = [
            "¿Cómo solicito licencia sin goce de haberes?",
            "¿Cuáles son mis obligaciones como profesional PEP?",
            "¿Qué es el SIGAF y para qué se usa?",
            "¿Cómo se tramita una modificación presupuestaria?",
        ]
        for i, sug in enumerate(sugs):
            if cols[i % 2].button(sug, use_container_width=True, key=f"sug_{i}"):
                st.session_state.messages.append({"role": "user", "content": sug})
                with st.spinner("Consultando el repositorio..."):
                    relevant = search_docs(sug, st.session_state.docs, filtro)
                    reply = ask_claude(sug, relevant, st.session_state.messages, filtro)
                st.session_state.messages.append({"role": "assistant", "content": reply, "sources": relevant})
                st.rerun()

    # Historial de mensajes
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
            if msg.get("sources"):
                src_html = '<div style="margin-top:6px">'
                for s in msg["sources"]:
                    emoji, bg, color = TIPO_COLORES.get(s["tipo"], TIPO_COLORES["Otro"])
                    src_html += f'<span class="source-badge" style="background:{bg};color:{color}">{emoji} {s["tipo"]} · {s["titulo"].split("–")[0].strip()[:30]}</span>'
                src_html += "</div>"
                st.markdown(src_html, unsafe_allow_html=True)

    # Input
    if prompt := st.chat_input("Escribí tu consulta sobre normativa, procesos o competencias..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Consultando el repositorio..."):
                relevant = search_docs(prompt, st.session_state.docs, filtro)
                reply = ask_claude(prompt, relevant, st.session_state.messages, filtro)
            st.markdown(reply)
            if relevant:
                src_html = '<div style="margin-top:6px">'
                for s in relevant:
                    emoji, bg, color = TIPO_COLORES.get(s["tipo"], TIPO_COLORES["Otro"])
                    src_html += f'<span class="source-badge" style="background:{bg};color:{color}">{emoji} {s["tipo"]} · {s["titulo"].split("–")[0].strip()[:30]}</span>'
                src_html += "</div>"
                st.markdown(src_html, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": reply, "sources": relevant})

    st.markdown('<p class="disclaimer">Las respuestas se generan exclusivamente a partir de los documentos del repositorio institucional</p>', unsafe_allow_html=True)

# ── Vista: REPOSITORIO ─────────────────────────────────────────────────────────
else:
    st.markdown('<div class="main-header"><h1>📁 Repositorio de documentos</h1><p>Administrá los documentos que usa el agente para responder</p></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        busqueda = st.text_input("🔍 Buscar en el repositorio", placeholder="Nombre, área, ministerio...")
    with col2:
        st.write("")
        st.write("")
        agregar = st.button("➕ Agregar documento", use_container_width=True)

    # Formulario agregar
    if agregar:
        st.session_state["show_form"] = not st.session_state.get("show_form", False)

    if st.session_state.get("show_form", False):
        with st.form("form_nuevo_doc"):
            st.markdown("**Nuevo documento**")
            c1, c2 = st.columns(2)
            titulo = c1.text_input("Título *")
            area = c2.text_input("Área temática")
            ministerio = c1.text_input("Ministerio / Repartición")
            tipo = c2.selectbox("Tipo", ["Ley", "Resolución", "Decreto", "Circular", "Manual", "Otro"])
            fecha = c1.date_input("Fecha")
            contenido = st.text_area("Contenido * (pegá el texto completo)", height=200)
            submitted = st.form_submit_button("✅ Agregar al repositorio")
            if submitted:
                if titulo and contenido:
                    st.session_state.docs.append({
                        "id": max(d["id"] for d in st.session_state.docs) + 1,
                        "titulo": titulo, "area": area,
                        "ministerio": ministerio, "tipo": tipo,
                        "fecha": str(fecha), "contenido": contenido,
                    })
                    st.session_state["show_form"] = False
                    st.success("✅ Documento agregado correctamente.")
                    st.rerun()
                else:
                    st.error("El título y el contenido son obligatorios.")

    # Lista de documentos
    filtered_docs = [
        d for d in st.session_state.docs
        if not busqueda or busqueda.lower() in (d["titulo"] + d["area"] + d["ministerio"] + d["contenido"]).lower()
    ]

    st.caption(f"{len(filtered_docs)} documentos {'encontrados' if busqueda else 'en el repositorio'}")

    for doc in filtered_docs:
        emoji, bg, color = TIPO_COLORES.get(doc["tipo"], TIPO_COLORES["Otro"])
        with st.expander(f"{emoji} **{doc['titulo']}** — {doc['ministerio']} ({doc['fecha']})"):
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"**Área:** {doc['area']} | **Tipo:** {doc['tipo']} | **Fecha:** {doc['fecha']}")
                st.text(doc["contenido"])
            with col_b:
                if st.button("🗑️ Eliminar", key=f"del_{doc['id']}"):
                    st.session_state.docs = [d for d in st.session_state.docs if d["id"] != doc["id"]]
                    st.rerun()
