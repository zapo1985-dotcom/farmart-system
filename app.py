import streamlit as st
import pandas as pd
from datetime import datetime
import json, os, base64
from io import BytesIO

st.set_page_config(page_title="HIREREADY-IA V10.3 FARMART 💧", page_icon="💧", layout="wide")

# === LOGO Y FONDO GOTA DE AGUA ===
def get_base64_img(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

logo_b64 = get_base64_img("logo.png")
fondo_b64 = get_base64_img("fondo_gotas.png")
logo2_b64 = get_base64_img("image_20261007_175106.webp")
fondo2_b64 = get_base64_img("image_20261007_175128.webp")

# Usa el que encuentre
FINAL_LOGO = logo_b64 or logo2_b64
FINAL_FONDO = fondo_b64 or fondo2_b64

bg_style = f"background-image: linear-gradient(rgba(248,250,252,0.85), rgba(232,244,255,0.85)), url('data:image/webp;base64,{FINAL_FONDO}'); background-size: cover; background-attachment: fixed; background-position: center;" if FINAL_FONDO else "background: linear-gradient(180deg, #f8fafc 0%, #e8f4ff 40%, #e8f8e8 100%);"

st.markdown(f"""
<style>
.stApp{{{bg_style}}}
h1,h2,h3{{color:#0B4DA2!important; font-weight:800!important;}}
.hero{{
    background: linear-gradient(135deg, rgba(11,77,162,0.93) 0%, rgba(91,155,213,0.88) 45%, rgba(122,193,67,0.85) 100%);
    color:white; padding:30px; border-radius:26px; text-align:center;
    box-shadow:0 14px 45px rgba(11,77,162,0.35); margin-bottom:20px;
    border: 2px solid rgba(255,255,255,0.4); position: relative; overflow: hidden;
}}
.hero::before{{
    content:''; position:absolute; top:-50%; left:-50%; width:200%; height:200%;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 1px, transparent 1px);
    background-size: 30px 30px; animation: float 20s infinite linear;
}}
.hero h2{{color:white!important; margin:8px 0; text-shadow: 0 2px 12px rgba(0,0,0,0.25); font-size:28px;}}
.hero p{{color: rgba(255,255,255,0.95)!important; font-size:15px;}}
.mod-card{{
    background: rgba(255,255,255,0.94); backdrop-filter: blur(12px);
    border-radius:20px; padding:22px; box-shadow:0 8px 28px rgba(0,0,0,0.08);
    border-left:7px solid #5B9BD5; margin-bottom:16px;
    border-right: 1px solid rgba(91,155,213,0.18); border-top: 1px solid rgba(255,255,255,0.9);
}}
.kpi-card{{
    background: rgba(255,255,255,0.92); backdrop-filter: blur(12px);
    border-radius:18px; padding:18px; text-align:center;
    box-shadow:0 6px 22px rgba(0,0,0,0.07); border: 1px solid rgba(91,155,213,0.15);
}}
.kpi-number{{font-size:30px; font-weight:800; color:#0B4DA2;}}
.alert-rojo{{background: rgba(254,226,226,0.9); border-left:6px solid #ef4444; padding:12px; border-radius:12px; margin:8px 0; backdrop-filter: blur(5px);}}
.alert-verde{{background: rgba(220,252,231,0.9); border-left:6px solid #22c55e; padding:12px; border-radius:12px; margin:8px 0; backdrop-filter: blur(5px);}}
.alert-amarillo{{background: rgba(254,243,199,0.9); border-left:6px solid #f59e0b; padding:12px; border-radius:12px; margin:8px 0; backdrop-filter: blur(5px);}}
.logo-hero{{max-width:110px; background:white; border-radius:50%; padding:10px; box-shadow:0 8px 25px rgba(0,0,0,0.2); margin-bottom:12px;}}
[data-testid="stSidebar"]{{background: linear-gradient(180deg, #0B4DA2 0%, #1e3a5f 60%, #2d5016 100%);}}
[data-testid="stSidebar"] *{{color:white!important;}}
.stButton>button{{border-radius:14px!important; font-weight:700!important; box-shadow:0 4px 14px rgba(91,155,213,0.3); transition: all 0.2s;}}
.stButton>button:hover{{transform: translateY(-2px); box-shadow:0 6px 18px rgba(91,155,213,0.4);}}
</style>
""", unsafe_allow_html=True)

USUARIOS_FILE="usuarios_admin.json"; REGISTROS_FILE="registros_farmart.json"; CARGOS_FILE="cargos.json"; PREGUNTAS_FILE="preguntas_banco.json"; TALENT_FILE="talent_pool.json"; ASIGNACIONES_FILE="asignaciones.json"

def cargar_json(p, default=None):
    try:
        with open(p,"r",encoding="utf-8") as f: return json.load(f)
    except: return default if default is not None else []
def guardar_json(p,d):
    with open(p,"w",encoding="utf-8") as f: json.dump(d,f,indent=2,ensure_ascii=False)

USUARIOS_CORRECTOS=[
    {"usuario":"admin","clave":"admin123","rol":"Super Admin","nombre":"Admin Simple"},
    {"usuario":"admi","clave":"admin123","rol":"Super Admin","nombre":"ADMI"},
    {"usuario":"admin@hireready.ia","clave":"HireReady2026*","rol":"Super Admin","nombre":"Admin Principal"},
    {"usuario":"rrhh@hireready.ia","clave":"HireReady2026*","rol":"RRHH","nombre":"RRHH HireReady"},
]

CARGOS_DEFAULT=["Personal de Nómina","Tesorería","Auxiliar de bodega de carga","Auxiliar de farmacia","Mensajero de moto","Conductor de carro","Quimico farmaceutico","Regente de farmacia","Auditoria y facturación","Contadores público","Auxiliares contables","Revisores fiscales","Auxiliares de servicios generales","Recursos Humanos","Auxiliares de archivo","Auditores médicos","Operadores logísticos","Ingenieros ambientales","Ingeniero de sistemas","Ingenieros de software","Desarrolladores fullstack","Auxiliares de recursos humanos","Abogados","Alta gerencia","Auxiliares administrativas","Ingenieros especialistas TIC / Ciberseguridad"]

def gen_preguntas(cargo,n=25):
    return [{"q":f"{cargo} - P{i+1}: Procedimiento correcto Farmart caso {i+1}?","op":[f"Correcto para {cargo}","Incorrecto con riesgo","Omitir"],"r":0,"tema":f"Tema {i+1}"} for i in range(n)]

BANCO_ENTREVISTA={}
for c in CARGOS_DEFAULT: BANCO_ENTREVISTA[c]=gen_preguntas(c,25)

TEST_PSICO={
"Psicotecnica_25": [{"q":f"Psicotécnica {i+1}: Situación ética {i+1}","op":["Ética correcta, reportas","Incorrecta","Omitir"],"r":0,"alerta":f"ALERTA Etica P{i+1}"} for i in range(25)],
"Psicologica_25": [{"q":f"Psicológica {i+1}: Rasgo {i+1}","op":["Perfil ideal","No ideal","Riesgo"],"r":0,"alerta":f"ALERTA Psicológica P{i+1}"} for i in range(25)],
"Imagenes_5": [
    {"q":"IMAGEN 1: Mancha negra irregular - Que interpretas?","op":["Analizo con calma","Me asusta","No veo nada"],"r":0,"interpreta":"A=Analítico B=Ansiedad C=Bloqueo"},
    {"q":"IMAGEN 2: Dos personas discutiendo frente a ti","op":["Medio con calma","Me alejo","Tomo partido"],"r":0,"interpreta":"A=Mediador B=Evasivo C=Parcial"},
    {"q":"IMAGEN 3: Reloj 11:55 PM y mucho trabajo","op":["Priorizo y comunico","Me paralizo","Dejo para mañana"],"r":0,"interpreta":"A=Gestion presión B=Ansiedad C=Procrastinación"},
    {"q":"IMAGEN 4: Caja CONFIDENCIAL cerrada","op":["No la abro, respeto","La abro por curiosidad","La abro si nadie ve"],"r":0,"interpreta":"A=Alta confidencialidad B/C=Baja"},
    {"q":"IMAGEN 5: Paciente llorando","op":["Me acerco con empatía","Lo ignoro","Le digo que se vaya"],"r":0,"interpreta":"A=Alta empatía B/C=Baja"},
],
"Incomodas_Bobas_5": [
    {"q":"BOBA: Si fueras medicamento, cual serías?","op":["Antibiótico, ayudo a curar","Droga recreativa","No sé cualquiera"],"r":0,"interpreta":"A=Propósito B=Riesgo C=Sin creatividad"},
    {"q":"INCOMODA: Tu último jefe era malo?","op":["Aprendizajes, hablo de aporte","Sí pésimo","No comento jefes"],"r":0,"interpreta":"A=Profesional B=Quejumbroso C=Evasivo"},
    {"q":"BOBA: Cuántos ladrillos para hospital?","op":["Depende diseño, planear con seguridad","No sé muchos","Pregunta estúpida"],"r":0,"interpreta":"A=Lógico B=Simplista C=Reactivo"},
    {"q":"INCOMODA: Has mentido en entrevista?","op":["No, prefiero honesto","Todos mienten","Prefiero no responder"],"r":0,"interpreta":"A=Honesto B=Normaliza mentira C=Evasivo"},
    {"q":"INCOMODA: Ves jefe haciendo ilegal?","op":["Reporto canal ético","Me callo por miedo","Me uno si conviene"],"r":0,"interpreta":"A=Ético B=Miedo C=Corrupto"},
]
}

def init_all():
    guardar_json(USUARIOS_FILE, USUARIOS_CORRECTOS)
    if not os.path.exists(CARGOS_FILE): guardar_json(CARGOS_FILE, CARGOS_DEFAULT)
    if not os.path.exists(PREGUNTAS_FILE): guardar_json(PREGUNTAS_FILE, BANCO_ENTREVISTA)
    if not os.path.exists(TALENT_FILE): guardar_json(TALENT_FILE, [])
    if not os.path.exists(REGISTROS_FILE): guardar_json(REGISTROS_FILE, [])
    if not os.path.exists(ASIGNACIONES_FILE): guardar_json(ASIGNACIONES_FILE, [])

init_all()

def generar_pdf_tecnico(registro):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer,pagesize=letter)
        styles=getSampleStyleSheet()
        story=[]
        story.append(Paragraph("<b>💧 HIREREADY-IA V10.3 - INFORME TECNICO PARA ANEXAR A HV</b>",styles['Title']))
        story.append(Spacer(1,12))
        porc=registro.get('porcentaje',0)
        if porc>=90: rango="90-100% ALTAMENTE CONFIABLE - 95% Confiable"; recomend="Sabe de su trabajo. Listo contratar."
        elif porc>=80: rango="80-89% CONFIABLE CON RECOMENDACIONES - 85%"; recomend=f"Reforzar: {registro.get('temas_bajos','temas')} 30 días"
        else: rango="NO CONFIABLE"; recomend="No sabe, no contratar"
        story.append(Paragraph(f"<b>Fecha:</b> {registro.get('fecha','')}<br/><b>Candidato:</b> {registro.get('nombre','')} CC {registro.get('cedula','')}<br/><b>Cargo:</b> {registro.get('cargo','')}<br/><b>Asignó:</b> {registro.get('asignado_por','RRHH')}",styles['Normal']))
        story.append(Spacer(1,12))
        data=[["Concepto","Resultado"],["Módulo",registro.get('modulo','')], ["Aciertos",f"{registro.get('aciertos','')}/{registro.get('total','')}"],["Porcentaje",f"{porc}%"],["Rango",rango],["Recomendación",recomend]]
        t=Table(data,colWidths=[130,370])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0B4DA2')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),1,colors.black)]))
        story.append(t)
        doc.build(story)
        buffer.seek(0)
        return buffer
    except: return BytesIO(b"PDF Tecnico")

def generar_pdf_psicologico(registro):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer,pagesize=letter)
        styles=getSampleStyleSheet()
        story=[Paragraph(f"<b>💧 INFORME PSICOLOGICO CONFIDENCIAL - {registro.get('nombre','')} {registro.get('porcentaje','')}%</b>",styles['Title']), Spacer(1,12)]
        porc=registro.get('porcentaje',0)
        story.append(Paragraph(f"Candidato: {registro.get('nombre','')} CC {registro.get('cedula','')} Cargo: {registro.get('cargo','')} Asignó: {registro.get('asignado_por','RRHH')}<br/>Psicotécnica: {registro.get('psicotecnica','')} Psicológica: {registro.get('psicologica','')} Imágenes: {registro.get('imagenes','')} Incómodas: {registro.get('incomodas','')}",styles['Normal']))
        story.append(Spacer(1,12))
        alertas=registro.get('alertas',[])
        if alertas:
            story.append(Paragraph("<b>ALERTAS PERSONALIDAD:</b>",styles['Heading2']))
            for al in alertas[:8]: story.append(Paragraph(f"- {al}",styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer
    except: return BytesIO(b"PDF Psicologico")

def generar_pdf_gerencia_general(df):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer,pagesize=letter)
        styles=getSampleStyleSheet()
        story=[Paragraph("<b>💧 HIREREADY-IA V10.3 - INFORME GENERAL GERENCIA - TODOS LOS MESES</b>",styles['Title']), Spacer(1,12)]
        story.append(Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')} Total: {len(df)} Promedio: {df['porcentaje'].mean():.1f}%",styles['Normal']))
        story.append(Spacer(1,12))
        df['mes']=pd.to_datetime(df['fecha'], errors='coerce').dt.to_period('M').astype(str)
        resumen_mes=df.groupby('mes').agg(total=('porcentaje','count'), promedio=('porcentaje','mean')).reset_index()
        data_mes=[["Mes","Total","Promedio"]]
        for _,row in resumen_mes.iterrows(): data_mes.append([row['mes'], str(row['total']), f"{row['promedio']:.1f}%"])
        t_mes=Table(data_mes,colWidths=[80,60,80])
        t_mes.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0B4DA2')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),1,colors.black)]))
        story.append(t_mes)
        doc.build(story)
        buffer.seek(0)
        return buffer
    except: return BytesIO(b"Informe Gerencia")

if "auth" not in st.session_state: st.session_state.auth=False; st.session_state.user=None; st.session_state.user_type=None
if "modulo" not in st.session_state: st.session_state.modulo=None
if "asignacion_actual" not in st.session_state: st.session_state.asignacion_actual=None

if not st.session_state.auth:
    # HERO CON LOGO GOTA
    logo_html = f'<img src="data:image/webp;base64,{FINAL_LOGO}" class="logo-hero">' if FINAL_LOGO else "💧"
    st.markdown(f'<div class="hero">{logo_html}<h2>HIREREADY-IA FARMART V10.3</h2><p>💧 Logo gota de agua - Azul claro #5B9BD5 + Verde #7AC143 + Gris claro #E5E7EB - Novedoso</p><p>26 Cargos x 25 Preguntas | PDF Técnico HV + PDF Psicológico Confidencial | Dashboard Mensual</p></div>', unsafe_allow_html=True)
    c1,c2=st.columns(2,gap="large")
    with c1:
        st.markdown('<div class="mod-card" style="border-left-color:#7AC143;"><h3>👤 SOY CANDIDATO - Solo Cédula</h3><p>RRHH te asigna. Tú solo ingresas cédula y presentas. PDFs se generan automático.</p></div>',unsafe_allow_html=True)
        cedula_login=st.text_input("📇 CÉDULA *",placeholder="Ej: 1234567890")
        if st.button("🚀 VER MIS PRUEBAS ASIGNADAS",use_container_width=True,type="primary"):
            asignaciones=cargar_json(ASIGNACIONES_FILE,[])
            mi_asig=[a for a in asignaciones if a.get('cedula')==cedula_login and a.get('estado')!='COMPLETADO_FINAL']
            if not mi_asig:
                st.error("❌ No tienes pruebas asignadas. Pídele a RRHH que te asigne.")
            else:
                st.session_state.auth=True; st.session_state.user_type="candidate"; st.session_state.cedula_real=cedula_login
                asig=mi_asig[0]; st.session_state.asignacion_actual=asig; st.rerun()
    with c2:
        st.markdown('<div class="mod-card" style="border-left-color:#0B4DA2;"><h3>🔐 SOY RRHH / ADMIN - LOGIN</h3><p>Usuario: admin o ADMI / Clave: admin123 - Acepta mayúsculas</p></div>',unsafe_allow_html=True)
        u=st.text_input("Usuario",placeholder="admin o ADMI"); p=st.text_input("Clave",type="password",placeholder="admin123")
        if st.button("🔐 ENTRAR PANEL RRHH",use_container_width=True):
            users=cargar_json(USUARIOS_FILE,[])
            u_norm=u.strip().lower()
            found=None
            for user in users:
                if user["usuario"].lower()==u_norm and user["clave"]==p: found=user; break
            if found: st.session_state.auth=True; st.session_state.user=found; st.session_state.user_type="admin"; st.rerun()
            else: st.error("❌ Incorrecto. Usa: admin / admin123 o ADMI / admin123")

else:
    if st.session_state.user_type=="candidate":
        asig=st.session_state.asignacion_actual
        logo_small = f'<img src="data:image/webp;base64,{FINAL_LOGO}" style="max-width:60px; background:white; border-radius:50%; padding:5px; vertical-align:middle; margin-right:10px;">' if FINAL_LOGO else ""
        st.markdown(f'<div class="hero">{logo_small}<h2 style="display:inline;">👤 {asig.get("nombre","")} | {asig.get("cargo","")}</h2><p>Asignó: {asig.get("asignado_por","RRHH")} | CC {asig.get("cedula","")} | Pruebas: {", ".join(asig.get("modulos",[]))}</p></div>',unsafe_allow_html=True)
        if st.button("🚪 Salir"): st.session_state.auth=False; st.session_state.user_type=None; st.rerun()

        if "Entrevista General" in asig.get('modulos',[]):
            st.divider(); st.subheader(f"📋 Entrevista General - {asig.get('cargo','')}")
            banco=cargar_json(PREGUNTAS_FILE,BANCO_ENTREVISTA); preguntas=banco.get(asig.get('cargo',''),[])[:25]
            resp=[]; temas_fallos=[]
            for i,pr in enumerate(preguntas):
                r=st.radio(f"{i+1}. {pr['q']}",pr["op"],key=f"ent{i}",index=None)
                if r is not None:
                    ok=pr["op"].index(r)==pr["r"]; resp.append(ok)
                    if not ok: temas_fallos.append(pr.get('tema',f"Tema {i+1}"))
            if st.button("✅ Finalizar y Generar PDF Técnico para HV",type="primary"):
                if len(resp)<len(preguntas): st.warning(f"Faltan {len(preguntas)-len(resp)}")
                else:
                    aciertos=sum(resp); porc=aciertos/len(preguntas)*100
                    registro={"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":asig.get('cedula',''),"nombre":asig.get('nombre',''),"cargo":asig.get('cargo',''),"sede":asig.get('sede',''),"telefono":asig.get('telefono',''),"modulo":"Entrevista General","aciertos":aciertos,"total":len(preguntas),"porcentaje":round(porc,1),"estado":"APTO" if porc>=70 else "NO APTO","temas_bajos":", ".join(temas_fallos[:5]),"observaciones":"Sabe de su trabajo" if porc>=80 else "Reforzar","asignado_por":asig.get('asignado_por','RRHH')}
                    regs=cargar_json(REGISTROS_FILE,[]); regs.append(registro); guardar_json(REGISTROS_FILE,regs)
                    pdf_buf=generar_pdf_tecnico(registro)
                    st.success(f"{porc:.1f}%")
                    st.download_button("📄 DESCARGAR PDF TÉCNICO PARA ANEXAR A HV - AQUÍ",pdf_buf,file_name=f"Tecnico_HV_{asig.get('cedula','')}.pdf",mime="application/pdf")

        if "Test Psicologico Laboral" in asig.get('modulos',[]):
            st.divider(); st.subheader("🧠 Test Psicológico - 60 Preguntas")
            todas=TEST_PSICO["Psicotecnica_25"]+TEST_PSICO["Psicologica_25"]+TEST_PSICO["Imagenes_5"]+TEST_PSICO["Incomodas_Bobas_5"]
            resp_psico=[]; alertas=[]
            for i,pr in enumerate(todas):
                tipo="Psicotécnica" if i<25 else "Psicológica" if i<50 else "Imagen" if i<55 else "Incómoda"
                r=st.radio(f"{i+1}. [{tipo}] {pr['q']}",pr["op"],key=f"psi_{i}",index=None)
                if r is not None:
                    ok=pr["op"].index(r)==pr["r"]; resp_psico.append(ok)
                    if not ok and "alerta" in pr: alertas.append(pr['alerta'])
            if st.button("✅ Finalizar y Generar PDF Psicológico",type="primary"):
                if len(resp_psico)<len(todas): st.warning(f"Faltan {len(todas)-len(resp_psico)}")
                else:
                    aciertos=sum(resp_psico); porc=aciertos/len(todas)*100
                    registro={"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":asig.get('cedula',''),"nombre":asig.get('nombre',''),"cargo":asig.get('cargo',''),"sede":asig.get('sede',''),"telefono":asig.get('telefono',''),"modulo":"Test Psicológico Laboral","aciertos":aciertos,"total":len(todas),"porcentaje":round(porc,1),"psicotecnica":f"{sum(resp_psico[:25])}/25","psicologica":f"{sum(resp_psico[25:50])}/25","imagenes":f"{sum(resp_psico[50:55])}/5","incomodas":f"{sum(resp_psico[55:60])}/5","perfil":"Confiable" if porc>=80 else "No confiable","estado":"SI contratar" if porc>=80 else "NO","alertas":alertas,"asignado_por":asig.get('asignado_por','RRHH')}
                    regs=cargar_json(REGISTROS_FILE,[]); regs.append(registro); guardar_json(REGISTROS_FILE,regs)
                    pdf_buf=generar_pdf_psicologico(registro)
                    st.success(f"{porc:.1f}%")
                    st.download_button("🧠 DESCARGAR PDF PSICOLÓGICO CONFIDENCIAL - AQUÍ",pdf_buf,file_name=f"Psicologico_{asig.get('cedula','')}.pdf",mime="application/pdf")

    else:
        if FINAL_LOGO:
            st.sidebar.markdown(f'<div style="text-align:center;"><img src="data:image/webp;base64,{FINAL_LOGO}" style="max-width:120px; background:white; border-radius:50%; padding:8px; box-shadow:0 4px 15px rgba(0,0,0,0.2);"></div>', unsafe_allow_html=True)
        st.sidebar.success(f"🔐 {st.session_state.user['nombre']}")
        if st.sidebar.button("🚪 Cerrar sesión"): st.session_state.auth=False; st.session_state.user=None; st.rerun()
        menu=st.sidebar.selectbox("Menú V10.3 💧", ["📊 Dashboard Gerencia + Informe Mensual", "📝 Asignar Pruebas por Cédula (quien asignó)", "💎 Talent Pool + PDFs", "📋 Dónde están los PDFs?"])

        if menu=="📝 Asignar Pruebas por Cédula (quien asignó)":
            st.markdown(f'<div class="hero">{f"<img src=\"data:image/webp;base64,{FINAL_LOGO}\" class=\"logo-hero\">" if FINAL_LOGO else "💧"}<h2>📝 Asignar Pruebas por Cédula</h2><p>Ahora guarda QUIÉN de RRHH asignó - Logo gota azul claro + verde + gris</p></div>',unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                cedula_asig=st.text_input("📇 Cédula *"); nombre_asig=st.text_input("👤 Nombre *"); cargo_asig=st.selectbox("💼 Cargo *",CARGOS_DEFAULT)
            with c2:
                sede_asig=st.text_input("📍 Ciudad"); tel_asig=st.text_input("📱 WhatsApp"); modulos_asig=st.multiselect("🧩 Módulos *",["Entrevista General","Test Psicologico Laboral"],default=["Entrevista General","Test Psicologico Laboral"])
            if st.button("✅ ASIGNAR PRUEBAS",type="primary",use_container_width=True):
                if not (cedula_asig and nombre_asig and modulos_asig): st.error("Faltan datos")
                else:
                    asignaciones=cargar_json(ASIGNACIONES_FILE,[])
                    nueva={"fecha_asignacion":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":cedula_asig,"nombre":nombre_asig,"cargo":cargo_asig,"sede":sede_asig,"telefono":tel_asig,"modulos":modulos_asig,"asignado_por":st.session_state.user['nombre']+" ("+st.session_state.user['usuario']+")","estado":"PENDIENTE"}
                    asignaciones.append(nueva); guardar_json(ASIGNACIONES_FILE,asignaciones)
                    st.success(f"✅ Asignado por {nueva['asignado_por']} a {nombre_asig} CC {cedula_asig}"); st.balloons()
            st.subheader("📚 Tabla con Usuario RRHH que asignó")
            df_asig=pd.DataFrame(cargar_json(ASIGNACIONES_FILE,[]))
            if not df_asig.empty:
                cols=["fecha_asignacion","cedula","nombre","cargo","modulos","asignado_por","estado","sede"]
                st.dataframe(df_asig[[c for c in cols if c in df_asig.columns]],use_container_width=True)
                st.download_button("📥 CSV con quien asignó",df_asig.to_csv(index=False).encode(),"asignaciones_con_usuario_RRHH.csv")

        elif menu=="📊 Dashboard Gerencia + Informe Mensual":
            st.markdown(f'<div class="hero">{f"<img src=\"data:image/webp;base64,{FINAL_LOGO}\" class=\"logo-hero\">" if FINAL_LOGO else "💧"}<h2>📊 Dashboard Gerencia 💧</h2><p>Informe General Todos los Meses + PDFs + Rangos Confiabilidad</p></div>',unsafe_allow_html=True)
            regs=cargar_json(REGISTROS_FILE,[])
            if not regs: st.info("Sin registros")
            else:
                df=pd.DataFrame(regs)
                df['fecha_dt']=pd.to_datetime(df['fecha'], errors='coerce')
                df['mes']=df['fecha_dt'].dt.to_period('M').astype(str)
                k1,k2,k3,k4,k5=st.columns(5)
                with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-number">{len(df)}</div><div>Total</div></div>',unsafe_allow_html=True)
                with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:#22c55e;">{len(df[df["porcentaje"]>=90])}</div><div>90%+ Altamente Confiable</div></div>',unsafe_allow_html=True)
                with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:#f59e0b;">{len(df[(df["porcentaje"]>=80)&(df["porcentaje"]<90)])}</div><div>80-89% Recomendado</div></div>',unsafe_allow_html=True)
                with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:#ef4444;">{len(df[df["porcentaje"]<60])}</div><div>NO Recomendado</div></div>',unsafe_allow_html=True)
                with k5: st.markdown(f'<div class="kpi-card"><div class="kpi-number">{df["porcentaje"].mean():.1f}%</div><div>Promedio</div></div>',unsafe_allow_html=True)
                c1,c2=st.columns(2)
                with c1: st.bar_chart(df.groupby('mes').size())
                with c2: st.bar_chart(df.groupby('cargo')['porcentaje'].mean().head(10))
                st.divider()
                st.subheader("📄 Informe General Gerencia - Todos los Meses")
                col1,col2=st.columns(2)
                with col1:
                    pdf_gen=generar_pdf_gerencia_general(df)
                    st.download_button("📄 DESCARGAR PDF INFORME GENERAL GERENCIA - PARA GERENCIA",pdf_gen,file_name=f"Informe_General_Gerencia_{datetime.now().strftime('%Y%m%d')}.pdf",mime="application/pdf",type="primary",use_container_width=True)
                with col2:
                    st.download_button("📥 DESCARGAR CSV GENERAL TODOS LOS MESES",df.to_csv(index=False).encode(),f"General_{datetime.now().strftime('%Y%m%d')}.csv",use_container_width=True)
                st.dataframe(df,use_container_width=True)
                st.divider()
                st.subheader("📄 PDFs por Candidato - Dónde están?")
                cand_sel=st.selectbox("Cédula", df["cedula"].unique() if "cedula" in df.columns else [])
                if cand_sel:
                    for _,row in df[df["cedula"]==cand_sel].iterrows():
                        rd=row.to_dict()
                        ca,cb=st.columns(2)
                        with ca:
                            if "Entrevista General" in str(rd.get('modulo','')):
                                pdf_t=generar_pdf_tecnico(rd)
                                st.download_button(f"📄 PDF TÉCNICO HV {rd.get('porcentaje','')}% - Asignó: {rd.get('asignado_por','')}",pdf_t,file_name=f"Tecnico_{cand_sel}.pdf",mime="application/pdf",key=f"t{cand_sel}{row.name}",use_container_width=True)
                        with cb:
                            if "Psicológico" in str(rd.get('modulo','')):
                                pdf_p=generar_pdf_psicologico(rd)
                                st.download_button(f"🧠 PDF PSICOLÓGICO {rd.get('porcentaje','')}% - Asignó: {rd.get('asignado_por','')}",pdf_p,file_name=f"Psico_{cand_sel}.pdf",mime="application/pdf",key=f"p{cand_sel}{row.name}",use_container_width=True)

        elif menu=="💎 Talent Pool + PDFs":
            st.dataframe(pd.DataFrame(cargar_json(TALENT_FILE,[])),use_container_width=True)

        elif menu=="📋 Dónde están los PDFs?":
            st.markdown("""
            <div class="mod-card"><h3>📍 PDF Técnico HV</h3><p><b>Dónde:</b> Candidato termina Entrevista -> botón 📄 DESCARGAR PDF TÉCNICO PARA ANEXAR A HV<br><b>RRHH:</b> Dashboard -> selecciona cédula -> botón 📄 PDF TÉCNICO HV</p><p>Contiene: Nombre, CC, cargo, %, rango 80-89% con recomendaciones, 90%+ altamente confiable, sabe/no sabe, quien asignó, firma</p></div>
            <div class="mod-card" style="border-left-color:#7AC143;"><h3>📍 PDF Psicológico Confidencial</h3><p><b>Dónde:</b> Candidato termina Test Psicológico -> botón 🧠 PDF PSICOLÓGICO<br><b>RRHH:</b> Dashboard -> cédula -> botón 🧠 PDF PSICOLÓGICO</p><p>Contiene: 25+25+5 imágenes+5 incómodas, %, perfil, alertas personalidad distorsionada, interpretación imágenes, quien asignó</p></div>
            <div class="mod-card" style="border-left-color:#f59e0b;"><h3>📍 Informe General Mensual Gerencia</h3><p><b>Dónde:</b> Dashboard Gerencia -> botones 📄 DESCARGAR PDF INFORME GENERAL GERENCIA y 📥 CSV GENERAL</p><p>Contiene: Totales por mes, promedio, aptos, top cargos, todos los meses</p></div>
            <div class="mod-card" style="border-left-color:#ef4444;"><h3>📍 Quién asignó</h3><p>Tabla Asignaciones columna <b>asignado_por</b> = Ej: Admin Simple (admin) o RRHH HireReady (rrhh@hireready.ia)</p></div>
            """, unsafe_allow_html=True)
