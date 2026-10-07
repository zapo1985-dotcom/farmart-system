import streamlit as st
import pandas as pd
from datetime import datetime
import json, os, re
from io import BytesIO

st.set_page_config(page_title="HIREREADY-IA V9 Glass", page_icon="💎", layout="wide")

# === CSS GLASSMORPHISM EXACTO A TU IMAGEN ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
.stApp{
    background: radial-gradient(ellipse at top left, #1a0a2e 0%, #0f0c29 25%, #302b63 50%, #24243e 75%, #0f0c29 100%)!important;
    background-attachment: fixed!important;
    font-family:'Inter',sans-serif;
}
.stApp::before{
    content:""; position:fixed; top:0; left:0; width:100%; height:100%;
    background: radial-gradient(circle at 20% 30%, rgba(120, 0, 255, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 0, 100, 0.25) 0%, transparent 50%),
                radial-gradient(circle at 40% 80%, rgba(0, 100, 255, 0.2) 0%, transparent 50%);
    pointer-events:none; z-index:0;
}
.hero-glass{text-align:center; padding:20px; margin-bottom:30px; position:relative; z-index:1;}
.hero-glass h1{color:#a5b4fc!important; font-weight:800; font-size:32px; letter-spacing:2px; margin:0;}
.hero-glass p{color:#cbd5e1; font-size:14px; letter-spacing:1px;}

.glass-card{
    background: rgba(255, 255, 255, 0.08)!important;
    backdrop-filter: blur(20px)!important;
    -webkit-backdrop-filter: blur(20px)!important;
    border: 1px solid rgba(255, 255, 255, 0.18)!important;
    border-radius: 32px!important;
    padding: 40px 35px!important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.2)!important;
    position:relative; z-index:1;
    transition: all 0.4s ease;
}
.glass-card:hover{transform: translateY(-5px); box-shadow: 0 15px 45px rgba(0,0,0,0.4)!important; border-color: rgba(255,255,255,0.3)!important;}
.glass-avatar{
    width:110px; height:110px; border-radius:50%; background: rgba(255,255,255,0.1);
    margin:0 auto 20px auto; display:flex; align-items:center; justify-content:center;
    border:1px solid rgba(255,255,255,0.2); font-size:60px;
}
.glass-title{color:white!important; font-weight:700; font-size:26px; text-align:center; letter-spacing:1px; margin-bottom:5px;}
.glass-subtitle{color:#a5b4fc; text-align:center; font-size:13px; margin-bottom:30px;}

.glass-input{
    background: transparent!important;
    border:none!important;
    border-bottom:1px solid rgba(255,255,255,0.5)!important;
    border-radius:0!important;
    color:white!important;
    padding-left:40px!important;
}
.glass-input::placeholder{color:rgba(255,255,255,0.6)!important;}
.glass-icon{position:absolute; left:5px; top:8px; color:rgba(255,255,255,0.8); font-size:18px;}

.glass-btn{
    background: linear-gradient(90deg, #2a0845 0%, #6441a5 50%, #2a5298 100%)!important;
    color:white!important; border:none!important; border-radius:12px!important;
    padding:14px!important; font-weight:700!important; letter-spacing:2px!important;
    width:100%!important; margin-top:20px; box-shadow:0 4px 15px rgba(100,65,165,0.4)!important;
}
.glass-btn:hover{background: linear-gradient(90deg, #3a0a5e 0%, #7a52c5 50%, #3a6ab8 100%)!important; transform:scale(1.02);}

.glass-check{color:rgba(255,255,255,0.7); font-size:13px;}
.glass-forgot{color:#a5b4fc; font-size:13px; text-align:right; cursor:pointer;}
.glass-forgot:hover{color:white;}

.mod-card{background: rgba(255,255,255,0.9); border-radius:16px; padding:20px; box-shadow:0 4px 12px rgba(0,0,0,0.1); border-left:6px solid #6441a5; margin-bottom:15px;}
[data-testid="stSidebar"]{background: rgba(15, 12, 41, 0.9)!important; backdrop-filter: blur(20px);}
[data-testid="stSidebar"] *{color:white!important;}
.stButton>button{border-radius:12px!important; font-weight:700!important;}
</style>
""", unsafe_allow_html=True)

USUARIOS_FILE="usuarios_admin.json"; REGISTROS_FILE="registros_farmart.json"; CARGOS_FILE="cargos.json"; PREGUNTAS_FILE="preguntas_banco.json"; VACANTES_FILE="vacantes.json"; TALENT_FILE="talent_pool.json"

def cargar_json(p, default=None):
    try:
        with open(p,"r", encoding="utf-8") as f: return json.load(f)
    except: return default if default is not None else []
def guardar_json(p,d):
    with open(p,"w", encoding="utf-8") as f: json.dump(d,f,indent=2,ensure_ascii=False)

USUARIOS_CORRECTOS=[
    {"usuario":"admin","clave":"admin123","rol":"Super Admin","nombre":"Admin Simple","email":"admin@hireready.ia"},
    {"usuario":"admin@hireready.ia","clave":"HireReady2026*","rol":"Super Admin","nombre":"Admin Principal","email":"admin@hireready.ia"},
    {"usuario":"rrhh@hireready.ia","clave":"HireReady2026*","rol":"RRHH","nombre":"RRHH HireReady","email":"rrhh@hireready.ia"},
    {"usuario":"candidato@farmart.com","clave":"candidato123","rol":"Candidato","nombre":"Candidato Demo","email":"candidato@farmart.com"},
]
def init_users(): guardar_json(USUARIOS_FILE, USUARIOS_CORRECTOS)

CARGOS_DEFAULT=["Personal de Nómina","Tesorería","Auxiliar de bodega de carga","Auxiliar de farmacia","Mensajero de moto","Conductor de carro","Quimico farmaceutico","Regente de farmacia","Auditoria y facturación","Contadores público","Auxiliares contables","Revisores fiscales","Auxiliares de servicios generales","Recursos Humanos","Auxiliares de archivo","Auditores médicos","Operadores logísticos","Ingenieros ambientales","Ingeniero de sistemas","Ingenieros de software","Desarrolladores fullstack","Auxiliares de recursos humanos","Abogados","Alta gerencia","Auxiliares administrativas","Ingenieros especialistas TIC / Ciberseguridad"]

def generar_banco_completo():
    banco={}
    for cargo in CARGOS_DEFAULT:
        banco[cargo]=[{"q":f"{cargo} - P{i+1}: ¿Procedimiento correcto Farmart caso {i+1}?","op":[f"Correcto para {cargo}", "Incorrecto con riesgo", "Omitir"],"r":0} for i in range(25)]
    banco["Personal de Nómina"][0]={"q":"Seguridad social integral compone","op":["Salud, pensión, ARL, caja","Solo salud","Solo ARL"],"r":0}
    return banco

BANCO_ENTREVISTA_COMPLETO=generar_banco_completo()
TEST_PSICO_COMPLETO={"Psicotecnica_25":[{"q":f"Psicotécnica {i+1}: Situación ética {i+1}","op":["Ética correcta","Incorrecta","Omitir"],"r":0} for i in range(25)], "Psicologica_25":[{"q":f"Psicológica {i+1}: Rasgo {i+1}","op":["Perfil ideal","No ideal","Riesgo"],"r":0} for i in range(25)]}

if not os.path.exists(CARGOS_FILE): guardar_json(CARGOS_FILE, CARGOS_DEFAULT)
if not os.path.exists(PREGUNTAS_FILE): guardar_json(PREGUNTAS_FILE, BANCO_ENTREVISTA_COMPLETO)
if not os.path.exists(VACANTES_FILE): guardar_json(VACANTES_FILE, [])
if not os.path.exists(TALENT_FILE): guardar_json(TALENT_FILE, [])
if not os.path.exists(REGISTROS_FILE): guardar_json(REGISTROS_FILE, [])
init_users()

def generar_pdf_evaluacion(registro, detalles=""):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from io import BytesIO
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer, pagesize=letter)
        styles=getSampleStyleSheet()
        story=[Paragraph(f"<b>HIREREADY-IA V9 GLASS - REPORTE</b>", styles['Title']), Spacer(1,12)]
        story.append(Paragraph(f"<b>{registro.get('nombre','')} - {registro.get('cargo','')} - {registro.get('porcentaje','')}% - {registro.get('estado','')}</b>", styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer
    except:
        from io import BytesIO
        return BytesIO(f"REPORTE {registro.get('nombre','')} {registro.get('porcentaje','')}%".encode())

if "auth" not in st.session_state:
    st.session_state.auth=False; st.session_state.user=None; st.session_state.user_type=None
if "modulo" not in st.session_state:
    st.session_state.modulo=None

# === LOGIN GLASSMORPHISM V9 ===
if not st.session_state.auth:
    st.markdown("""
    <div class="hero-glass">
        <h1>💎 HIREREADY-IA • Farmart</h1>
        <p>Recruitment Platform • Secure Access • V9 Glassmorphism</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="glass-card">
            <div class="glass-avatar">👤</div>
            <div class="glass-title">CANDIDATO</div>
            <div class="glass-subtitle">Acceso para candidatos</div>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="glass-card" style="margin-top:-20px; padding-top:20px;">', unsafe_allow_html=True)
            email_cand = st.text_input("📧 Email ID", placeholder="Email ID", key="email_cand", label_visibility="collapsed")
            st.markdown('<div style="position:relative; margin-top:15px;"><span class="glass-icon">🔒</span>', unsafe_allow_html=True)
            pass_cand = st.text_input("Password", type="password", placeholder="Password", key="pass_cand", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
            col_check1, col_forgot1 = st.columns(2)
            with col_check1:
                remember_cand = st.checkbox("Remember me", key="remember_cand")
            with col_forgot1:
                st.markdown('<div class="glass-forgot">Forgot Password?</div>', unsafe_allow_html=True)

            if st.button("LOGIN", key="login_cand", use_container_width=True):
                users = cargar_json(USUARIOS_FILE, [])
                # Para candidatos permitimos login con email o con cédula demo
                found = next((x for x in users if (x.get("email")==email_cand or x["usuario"]==email_cand) and x["clave"]==pass_cand), None)
                # Si no encuentra, permitir acceso demo si pone cualquier email y candidato123
                if not found and email_cand and pass_cand:
                    # Modo demo candidato: cualquier email con clave candidato123 entra como candidato
                    if pass_cand=="candidato123" or email_cand=="candidato@farmart.com":
                        found={"usuario":email_cand,"nombre":"Candidato","rol":"Candidato","email":email_cand}
                if found:
                    st.session_state.auth=True
                    st.session_state.user=found
                    st.session_state.user_type="candidate"
                    st.session_state.cedula_real="1234567890"
                    st.session_state.nombre=found["nombre"]
                    st.session_state.cargo_sel="Personal de Nómina"
                    st.session_state.sede="Cali"
                    st.session_state.tel="573001234567"
                    st.rerun()
                else:
                    st.error("❌ Email o Password incorrecto. Demo: candidato@farmart.com / candidato123")

            st.markdown('<p style="color:rgba(255,255,255,0.5); font-size:11px; text-align:center; margin-top:15px;">Demo: candidato@farmart.com<br>candidato123</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass-card">
            <div class="glass-avatar">🔐</div>
            <div class="glass-title">ADMIN RRHH</div>
            <div class="glass-subtitle">Acceso para Recursos Humanos</div>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="glass-card" style="margin-top:-20px; padding-top:20px;">', unsafe_allow_html=True)
            email_admin = st.text_input("📧 Email ID", placeholder="Email ID", key="email_admin", label_visibility="collapsed")
            st.markdown('<div style="position:relative; margin-top:15px;"><span class="glass-icon">🔒</span>', unsafe_allow_html=True)
            pass_admin = st.text_input("Password", type="password", placeholder="Password", key="pass_admin", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
            col_check2, col_forgot2 = st.columns(2)
            with col_check2:
                remember_admin = st.checkbox("Remember me", key="remember_admin")
            with col_forgot2:
                st.markdown('<div class="glass-forgot">Forgot Password?</div>', unsafe_allow_html=True)

            if st.button("LOGIN", key="login_admin", use_container_width=True):
                users = cargar_json(USUARIOS_FILE, [])
                found = next((x for x in users if (x.get("email")==email_admin or x["usuario"]==email_admin) and x["clave"]==pass_admin), None)
                if found and found["rol"]!="Candidato":
                    st.session_state.auth=True
                    st.session_state.user=found
                    st.session_state.user_type="admin"
                    st.rerun()
                else:
                    st.error("❌ Email o Password incorrecto. Demo: admin@hireready.ia / HireReady2026*")

            st.markdown('<p style="color:rgba(255,255,255,0.5); font-size:11px; text-align:center; margin-top:15px;">Demo: admin / admin123<br>admin@hireready.ia / HireReady2026*</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # === USUARIO AUTENTICADO ===
    if st.session_state.user_type=="candidate":
        st.markdown(f'<div style="background:rgba(255,255,255,0.1); backdrop-filter:blur(10px); padding:15px; border-radius:15px; color:white; text-align:center;">👤 Bienvenido {st.session_state.user["nombre"]} | Candidato | <a style="color:#a5b4fc;" href="#" onclick="return false;">Cerrar sesión</a></div>', unsafe_allow_html=True)
        if st.button("🚪 Salir - Volver a Login Glass"):
            st.session_state.auth=False; st.session_state.user=None; st.session_state.user_type=None; st.rerun()

        st.markdown('<div class="mod-card"><h3>🧩 Tus Módulos de Evaluación - Sin Límite</h3></div>', unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1: b1=st.button("📋 Entrevista General (25)", use_container_width=True)
        with c2: b2=st.button("🧠 Test Psicológico (50)", use_container_width=True)
        with c3: b3=st.button("🎥 Videoentrevista IA (5)", use_container_width=True)

        if b1: st.session_state.modulo="entrevista"
        if b2: st.session_state.modulo="psicologico"
        if b3: st.session_state.modulo="video"

        if st.session_state.modulo=="entrevista":
            st.subheader("📋 Entrevista General - 25 Preguntas")
            banco=cargar_json(PREGUNTAS_FILE, BANCO_ENTREVISTA_COMPLETO)
            preguntas=banco.get(st.session_state.cargo_sel, [])[:25]
            resp=[]
            for i,p in enumerate(preguntas):
                r=st.radio(f"{i+1}. {p['q']}",p["op"],key=f"ent{i}",index=None)
                if r is not None: resp.append(p["op"].index(r)==p["r"])
            if st.button("✅ Finalizar y Generar PDF",type="primary"):
                if len(resp)<len(preguntas): st.warning(f"Faltan {len(preguntas)-len(resp)}")
                else:
                    aciertos=sum(resp); porc=aciertos/len(preguntas)*100
                    registro={"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":st.session_state.cedula_real,"nombre":st.session_state.nombre,"cargo":st.session_state.cargo_sel,"sede":st.session_state.sede,"telefono":st.session_state.tel,"modulo":"Entrevista General","aciertos":aciertos,"total":len(preguntas),"porcentaje":round(porc,1),"estado":"APTO" if porc>=70 else "NO APTO","fuente":"Glass V9","agente":"Agente Entrevista"}
                    regs=cargar_json(REGISTROS_FILE, []); regs.append(registro); guardar_json(REGISTROS_FILE, regs)
                    pdf_buffer=generar_pdf_evaluacion(registro, f"{aciertos}/{len(preguntas)}")
                    st.success(f"✅ {porc:.1f}% - {registro['estado']}")
                    st.download_button("📄 Descargar PDF Evaluación",pdf_buffer,file_name=f"Evaluacion_{st.session_state.cedula_real}.pdf",mime="application/pdf")

    elif st.session_state.user_type=="admin":
        st.sidebar.markdown('<div style="color:white; font-weight:800; font-size:22px;">💎 HIRE<span style="color:#a5b4fc;">READY</span>-IA V9</div>',unsafe_allow_html=True)
        st.sidebar.success(f"🔐 {st.session_state.user['nombre']}")
        if st.sidebar.button("🚪 Cerrar sesión"):
            st.session_state.auth=False; st.session_state.user=None; st.session_state.user_type=None; st.rerun()
        menu=st.sidebar.selectbox("Menú V9 Glass", ["📊 Dashboard Gerencia","🤖 Criba Inteligente","📋 Editar 25 Preguntas","💎 Talent Pool + PDF","🔧 Reset Usuarios"])

        if menu=="📊 Dashboard Gerencia":
            st.markdown('<div class="mod-card"><h2>📊 Dashboard Gerencia - Historial Completo</h2></div>',unsafe_allow_html=True)
            regs=cargar_json(REGISTROS_FILE, [])
            if not regs: st.info("Sin registros")
            else:
                df=pd.DataFrame(regs)
                st.dataframe(df,use_container_width=True)
                st.download_button("📥 Descargar CSV",df.to_csv(index=False).encode(),f"Informe_V9_{datetime.now().strftime('%Y%m%d')}.csv")

        elif menu=="🔧 Reset Usuarios":
            if st.button("🔄 RESETEAR USUARIOS V9",type="primary"):
                guardar_json(USUARIOS_FILE, USUARIOS_CORRECTOS)
                st.success("✅ Reseteado - admin/admin123 | admin@hireready.ia / HireReady2026* | candidato@farmart.com / candidato123")
                st.json(USUARIOS_CORRECTOS)
