import streamlit as st
import pandas as pd
from datetime import datetime
import json, os, re, random
from io import BytesIO

st.set_page_config(page_title="HIREREADY-IA V10.1 FIX", page_icon="💎", layout="wide")

st.markdown("""
<style>
.stApp{background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);}
h1,h2,h3{color:#0B4DA2!important; font-weight:800!important;}
.hero{background: linear-gradient(135deg, #0B4DA2 0%, #1e40af 50%, #7AC143 100%); color:white; padding:25px; border-radius:20px; text-align:center; margin-bottom:20px;}
.hero h2{color:white!important; margin:0;}
.mod-card{background:white; border-radius:16px; padding:20px; box-shadow:0 4px 12px rgba(0,0,0,0.06); border-left:6px solid #0B4DA2; margin-bottom:15px;}
.kpi-card{background:white; border-radius:16px; padding:18px; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.06);}
[data-testid="stSidebar"]{background: linear-gradient(180deg, #0B4DA2 0%, #0f172a 100%);}
[data-testid="stSidebar"] *{color:white!important;}
</style>
""", unsafe_allow_html=True)

USUARIOS_FILE = "usuarios_admin.json"
REGISTROS_FILE = "registros_farmart.json"
CARGOS_FILE = "cargos.json"
PREGUNTAS_FILE = "preguntas_banco.json"
VACANTES_FILE = "vacantes.json"
TALENT_FILE = "talent_pool.json"
ASIGNACIONES_FILE = "asignaciones.json"

def cargar_json(p, default=None):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default if default is not None else []

def guardar_json(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

USUARIOS_CORRECTOS = [
    {"usuario": "admin", "clave": "admin123", "rol": "Super Admin", "nombre": "Admin Simple"},
    {"usuario": "admi", "clave": "admin123", "rol": "Super Admin", "nombre": "Admin Simple"},
    {"usuario": "ADMIN", "clave": "admin123", "rol": "Super Admin", "nombre": "Admin Simple"},
    {"usuario": "admin@hireready.ia", "clave": "HireReady2026*", "rol": "Super Admin", "nombre": "Admin Principal"},
    {"usuario": "rrhh@hireready.ia", "clave": "HireReady2026*", "rol": "RRHH", "nombre": "RRHH HireReady"},
]

def init_all():
    guardar_json(USUARIOS_FILE, USUARIOS_CORRECTOS)
    if not os.path.exists(CARGOS_FILE):
        guardar_json(CARGOS_FILE, CARGOS_DEFAULT)
    if not os.path.exists(PREGUNTAS_FILE):
        guardar_json(PREGUNTAS_FILE, BANCO_ENTREVISTA)
    if not os.path.exists(VACANTES_FILE):
        guardar_json(VACANTES_FILE, [])
    if not os.path.exists(TALENT_FILE):
        guardar_json(TALENT_FILE, [])
    if not os.path.exists(REGISTROS_FILE):
        guardar_json(REGISTROS_FILE, [])
    if not os.path.exists(ASIGNACIONES_FILE):
        guardar_json(ASIGNACIONES_FILE, [])

CARGOS_DEFAULT = ["Personal de Nómina","Tesorería","Auxiliar de bodega de carga","Auxiliar de farmacia","Mensajero de moto","Conductor de carro","Quimico farmaceutico","Regente de farmacia","Auditoria y facturación","Contadores público","Auxiliares contables","Revisores fiscales","Auxiliares de servicios generales","Recursos Humanos","Auxiliares de archivo","Auditores médicos","Operadores logísticos","Ingenieros ambientales","Ingeniero de sistemas","Ingenieros de software","Desarrolladores fullstack","Auxiliares de recursos humanos","Abogados","Alta gerencia","Auxiliares administrativas","Ingenieros especialistas TIC / Ciberseguridad"]

def gen_preguntas(cargo, n=25):
    base = []
    for i in range(n):
        base.append({"q": f"{cargo} - P{i+1}: Procedimiento correcto Farmart caso {i+1}?", "op": [f"Correcto para {cargo}", "Incorrecto con riesgo", "Omitir"], "r": 0, "tema": f"Tema {i+1}"})
    return base

BANCO_ENTREVISTA = {}
for c in CARGOS_DEFAULT:
    BANCO_ENTREVISTA[c] = gen_preguntas(c, 25)

TEST_PSICO = {
    "Psicotecnica_25": [{"q": f"Psicotécnica {i+1}: Situación ética {i+1}", "op": ["Ética correcta", "Incorrecta", "Omitir"], "r": 0, "alerta": "ALERTA si no es A"} for i in range(25)],
    "Psicologica_25": [{"q": f"Psicológica {i+1}: Rasgo {i+1}", "op": ["Perfil ideal", "No ideal", "Riesgo"], "r": 0, "alerta": "ALERTA si no es A"} for i in range(25)],
    "Imagenes_5": [{"q": f"IMAGEN {i+1}: Que ves?", "op": ["Analizo con calma", "Me asusta", "No veo nada"], "r": 0, "interpreta": "Analitico"} for i in range(5)],
    "Incomodas_Bobas_5": [{"q": f"Pregunta incómoda/boba {i+1}", "op": ["Respuesta profesional", "Respuesta evasiva", "Respuesta riesgosa"], "r": 0, "interpreta": "Profesional"} for i in range(5)]
}

init_all()

def generar_pdf_tecnico(registro):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph("<b>HIREREADY-IA V10.1 - INFORME TECNICO PARA HV</b>", styles['Title']))
        story.append(Spacer(1, 12))
        porc = registro.get('porcentaje', 0)
        if porc >= 90:
            rango = "90-100% ALTAMENTE CONFIABLE"
        elif porc >= 80:
            rango = "80-89% CONFIABLE CON RECOMENDACIONES"
        else:
            rango = "NO CONFIABLE"
        story.append(Paragraph(f"Candidato: {registro.get('nombre','')} CC {registro.get('cedula','')} Cargo: {registro.get('cargo','')} Porcentaje: {porc}% Rango: {rango} Estado: {registro.get('estado','')}", styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer
    except:
        return BytesIO(b"PDF Tecnico")

def generar_pdf_psicologico(registro):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"<b>INFORME PSICOLOGICO {registro.get('nombre','')} {registro.get('porcentaje','')}%</b>", styles['Title'])]
        doc.build(story)
        buffer.seek(0)
        return buffer
    except:
        return BytesIO(b"PDF Psicologico")

if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None
    st.session_state.user_type = None
if "modulo" not in st.session_state:
    st.session_state.modulo = None
if "asignacion_actual" not in st.session_state:
    st.session_state.asignacion_actual = None

if not st.session_state.auth:
    st.markdown('<div class="hero"><h2>💎 HIREREADY-IA V10.1 FIX - FARMART</h2><p>Login arreglado: acepta admin, ADMI, Admin</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="mod-card" style="border-left-color:#7AC143;"><h3>👤 SOY CANDIDATO - Ingreso por CÉDULA</h3></div>', unsafe_allow_html=True)
        cedula_login = st.text_input("📇 CÉDULA para iniciar prueba *", placeholder="Ej: 1234567890")
        if st.button("🚀 INGRESAR A MIS PRUEBAS ASIGNADAS", use_container_width=True, type="primary"):
            asignaciones = cargar_json(ASIGNACIONES_FILE, [])
            mi_asig = [a for a in asignaciones if a.get('cedula') == cedula_login and a.get('estado')!= 'COMPLETADO']
            if not mi_asig:
                st.error("❌ No tienes pruebas asignadas. El admin debe asignarte primero.")
            else:
                st.session_state.auth = True
                st.session_state.user_type = "candidate"
                st.session_state.cedula_real = cedula_login
                asig = mi_asig[0]
                st.session_state.asignacion_actual = asig
                st.session_state.nombre = asig.get('nombre', 'Candidato')
                st.session_state.cargo_sel = asig.get('cargo', 'Personal de Nómina')
                st.session_state.sede = asig.get('sede', 'Cali')
                st.session_state.tel = asig.get('telefono', '')
                st.rerun()

    with col2:
        st.markdown('<div class="mod-card" style="border-left-color:#0B4DA2;"><h3>🔐 SOY RRHH / ADMIN - LOGIN ARREGLADO</h3><p>Ahora acepta: admin, ADMI, Admin, ADMIN</p></div>', unsafe_allow_html=True)
        u = st.text_input("Usuario", placeholder="admin o ADMI")
        p = st.text_input("Clave", type="password", placeholder="admin123")
        if st.button("🔐 INGRESAR PANEL RRHH", use_container_width=True):
            users = cargar_json(USUARIOS_FILE, [])
            u_norm = u.strip().lower()
            found = None
            for user in users:
                if user["usuario"].lower() == u_norm and user["clave"] == p:
                    found = user
                    break
            if found:
                st.session_state.auth = True
                st.session_state.user = found
                st.session_state.user_type = "admin"
                st.rerun()
            else:
                st.error("❌ Usuario o clave incorrecta. Prueba: admin / admin123 o ADMI / admin123")
                st.info(f"Usuarios disponibles: {users}")

else:
    if st.session_state.user_type == "candidate":
        asig = st.session_state.asignacion_actual
        st.markdown(f'<div class="hero"><h2>👤 {asig.get("nombre","")} | {asig.get("cargo","")}</h2></div>', unsafe_allow_html=True)
        if st.button("🚪 Salir"):
            st.session_state.auth = False
            st.session_state.user_type = None
            st.rerun()
        st.info(f"Pruebas asignadas: {', '.join(asig.get('modulos', []))}")
        if st.button("📋 Presentar Entrevista General (25)"):
            st.session_state.modulo = "entrevista"
        if st.session_state.modulo == "entrevista":
            st.subheader("Entrevista General 25")
            banco = cargar_json(PREGUNTAS_FILE, BANCO_ENTREVISTA)
            preguntas = banco.get(asig.get('cargo',''), [])[:25]
            resp = []
            for i, pr in enumerate(preguntas):
                r = st.radio(f"{i+1}. {pr['q']}", pr["op"], key=f"ent{i}", index=None)
                if r is not None:
                    resp.append(pr["op"].index(r) == pr["r"])
            if st.button("✅ Finalizar y PDF Técnico"):
                if len(resp) < len(preguntas):
                    st.warning(f"Faltan {len(preguntas)-len(resp)}")
                else:
                    aciertos = sum(resp)
                    porc = aciertos / len(preguntas) * 100
                    registro = {"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "cedula": asig.get('cedula',''), "nombre": asig.get('nombre',''), "cargo": asig.get('cargo',''), "sede": asig.get('sede',''), "telefono": asig.get('telefono',''), "modulo": "Entrevista General", "aciertos": aciertos, "total": len(preguntas), "porcentaje": round(porc,1), "estado": "APTO" if porc>=70 else "NO APTO", "fuente": "Asignacion RRHH", "agente": "Agente Entrevista"}
                    regs = cargar_json(REGISTROS_FILE, [])
                    regs.append(registro)
                    guardar_json(REGISTROS_FILE, regs)
                    pdf_buf = generar_pdf_tecnico(registro)
                    st.success(f"{porc:.1f}%")
                    st.download_button("📄 Descargar PDF Técnico HV", pdf_buf, file_name=f"Tecnico_{asig.get('cedula','')}.pdf", mime="application/pdf")
    else:
        st.sidebar.success(f"🔐 {st.session_state.user['nombre']}")
        if st.sidebar.button("🚪 Cerrar sesión"):
            st.session_state.auth = False
            st.session_state.user = None
            st.session_state.user_type = None
            st.rerun()
        menu = st.sidebar.selectbox("Menú", ["📊 Dashboard", "📝 Asignar Pruebas por Cédula", "💎 Talent Pool"])
        if menu == "📝 Asignar Pruebas por Cédula":
            st.header("📝 Asignar Pruebas por Cédula")
            cedula_asig = st.text_input("📇 Cédula *")
            nombre_asig = st.text_input("👤 Nombre *")
            cargo_asig = st.selectbox("💼 Cargo", CARGOS_DEFAULT)
            sede_asig = st.text_input("📍 Ciudad")
            tel_asig = st.text_input("📱 WhatsApp")
            modulos_asig = st.multiselect("🧩 Módulos", ["Entrevista General", "Test Psicologico Laboral"], default=["Entrevista General"])
            if st.button("✅ ASIGNAR PRUEBAS", type="primary"):
                asignaciones = cargar_json(ASIGNACIONES_FILE, [])
                nueva = {"fecha_asignacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "cedula": cedula_asig, "nombre": nombre_asig, "cargo": cargo_asig, "sede": sede_asig, "telefono": tel_asig, "modulos": modulos_asig, "asignado_por": st.session_state.user['nombre'], "estado": "PENDIENTE"}
                asignaciones.append(nueva)
                guardar_json(ASIGNACIONES_FILE, asignaciones)
                st.success(f"✅ Asignado a {nombre_asig} CC {cedula_asig}")
                st.balloons()
            st.dataframe(pd.DataFrame(cargar_json(ASIGNACIONES_FILE, [])), use_container_width=True)
        elif menu == "📊 Dashboard":
            regs = cargar_json(REGISTROS_FILE, [])
            st.dataframe(pd.DataFrame(regs), use_container_width=True)
            if regs:
                st.download_button("📥 CSV", pd.DataFrame(regs).to_csv(index=False).encode(), "informe.csv")
        elif menu == "💎 Talent Pool":
            st.dataframe(pd.DataFrame(cargar_json(TALENT_FILE, [])), use_container_width=True)
