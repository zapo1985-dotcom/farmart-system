import streamlit as st
import pandas as pd
from datetime import datetime
import json, os, random
from io import BytesIO

st.set_page_config(page_title="HIREREADY-IA V10.2 Gerencia", page_icon="💎", layout="wide")

st.markdown("""
<style>
.stApp{background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);}
h1,h2,h3{color:#0B4DA2!important; font-weight:800!important;}
.hero{background: linear-gradient(135deg, #0B4DA2 0%, #1e40af 50%, #7AC143 100%); color:white; padding:20px; border-radius:20px; text-align:center; margin-bottom:15px;}
.hero h2{color:white!important; margin:0;}
.mod-card{background:white; border-radius:16px; padding:18px; box-shadow:0 4px 12px rgba(0,0,0,0.06); border-left:6px solid #0B4DA2; margin-bottom:12px;}
.kpi-card{background:white; border-radius:16px; padding:15px; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.06);}
.kpi-number{font-size:28px; font-weight:800; color:#0B4DA2;}
.alert-rojo{background:#fee2e2; border-left:6px solid #ef4444; padding:12px; border-radius:10px; margin:8px 0;}
.alert-verde{background:#dcfce7; border-left:6px solid #22c55e; padding:12px; border-radius:10px; margin:8px 0;}
.alert-amarillo{background:#fef3c7; border-left:6px solid #f59e0b; padding:12px; border-radius:10px; margin:8px 0;}
[data-testid="stSidebar"]{background: linear-gradient(180deg, #0B4DA2 0%, #0f172a 100%);}
[data-testid="stSidebar"] *{color:white!important;}
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
"Psicotecnica_25": [{"q":f"Psicotécnica {i+1}: Situación ética {i+1} - Compañero hace X, tú?","op":["Ética correcta, reportas","Incorrecta","Omitir"],"r":0,"alerta":f"ALERTA Etica P{i+1}"} for i in range(25)],
"Psicologica_25": [{"q":f"Psicológica {i+1}: Rasgo {i+1}","op":["Perfil ideal","No ideal","Riesgo"],"r":0,"alerta":f"ALERTA Psicológica P{i+1}"} for i in range(25)],
"Imagenes_5": [
    {"q":"IMAGEN 1: Mancha negra irregular - Que interpretas?","op":["Analizo con calma, oportunidad analizar","Me asusta, es feo","No veo nada"],"r":0,"interpreta":"A=Analítico B=Ansiedad C=Bloqueo"},
    {"q":"IMAGEN 2: Dos personas discutiendo frente a ti","op":["Medio con calma, busco acuerdo","Me alejo, no me meto","Tomo partido por el que me cae mejor"],"r":0,"interpreta":"A=Mediador B=Evasivo C=Parcial"},
    {"q":"IMAGEN 3: Reloj 11:55 PM y mucho trabajo pendiente","op":["Priorizo crítico y comunico avance","Me paralizo de estrés","Dejo todo para mañana"],"r":0,"interpreta":"A=Gestion presión B=Ansiedad C=Procrastinación"},
    {"q":"IMAGEN 4: Caja etiquetada CONFIDENCIAL cerrada","op":["No la abro, respeto confidencialidad","La abro por curiosidad","La abro si nadie me ve"],"r":0,"interpreta":"A=Alta confidencialidad B/C=Baja"},
    {"q":"IMAGEN 5: Paciente llorando en farmacia","op":["Me acerco con empatía y ayudo","Lo ignoro no es mi problema","Le digo que se calme y se vaya"],"r":0,"interpreta":"A=Alta empatía B/C=Baja"},
],
"Incomodas_Bobas_5": [
    {"q":"PREGUNTA BOBA: Si fueras un medicamento, cual serías?","op":["Antibiótico, ayudo a curar con precisión","Droga recreativa","No sé cualquiera"],"r":0,"interpreta":"A=Propósito B=Riesgo C=Sin creatividad"},
    {"q":"INCOMODA: Tu último jefe era malo?","op":["Aprendizajes, prefiero hablar de aporte","Sí pésimo","No comento jefes"],"r":0,"interpreta":"A=Profesional B=Quejumbroso C=Evasivo"},
    {"q":"BOBA: Cuántos ladrillos para hacer hospital?","op":["Depende diseño, importante planear con seguridad","No sé muchos","Pregunta estúpida"],"r":0,"interpreta":"A=Lógico B=Simplista C=Reactivo"},
    {"q":"INCOMODA: Has mentido en entrevista?","op":["No, prefiero honesto aunque pierda","Todos mienten un poco","Prefiero no responder"],"r":0,"interpreta":"A=Honesto B=Normaliza mentira C=Evasivo"},
    {"q":"INCOMODA: Ves a tu jefe haciendo algo ilegal, que haces?","op":["Reporto canal ético con evidencia","Me callo por miedo","Me uno si me conviene"],"r":0,"interpreta":"A=Ético B=Miedo C=Corrupto"},
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
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer,pagesize=letter)
        styles=getSampleStyleSheet()
        story=[]
        story.append(Paragraph("<b>HIREREADY-IA V10.2 - INFORME TECNICO PARA ANEXAR A HV</b>",styles['Title']))
        story.append(Spacer(1,12))
        porc=registro.get('porcentaje',0)
        if porc>=90: rango="90-100% ALTAMENTE CONFIABLE - ALTAMENTE RECOMENDADO - 95% Confiable"; recomend="Sabe de su trabajo. Listo para contratar. Reforzar solo temas menores. Contratar sin restricciones."
        elif porc>=80: rango="80-89% CONFIABLE CON RECOMENDACIONES - 85% Confiable"; recomend=f"Recomendado con plan refuerzo 30 días en: {registro.get('temas_bajos','temas específicos')}. Supervisión quincenal."
        elif porc>=60: rango="60-79% EN OBSERVACION - 65% Confiable"; recomend="No recomendado para cargo crítico sin 60 días refuerzo intensivo y re-evaluación."
        else: rango="0-59% NO RECOMENDADO - 30% No confiable"; recomend="No sabe de su trabajo o graves vacíos. No contratar."
        story.append(Paragraph(f"<b>Fecha:</b> {registro.get('fecha','')}<br/><b>Candidato:</b> {registro.get('nombre','')} CC {registro.get('cedula','')}<br/><b>Cargo:</b> {registro.get('cargo','')}<br/><b>Sede:</b> {registro.get('sede','')} Tel:{registro.get('telefono','')}<br/><b>Asignó prueba:</b> {registro.get('asignado_por','RRHH')}",styles['Normal']))
        story.append(Spacer(1,12))
        data=[["Concepto","Resultado"],["Módulo",registro.get('modulo','')],["Aciertos",f"{registro.get('aciertos','')}/{registro.get('total','')}"],["Porcentaje",f"{porc}%"],["Rango Confiabilidad",rango],["Sabe de su trabajo?", "SI" if porc>=80 else "PARCIAL" if porc>=60 else "NO"],["Estado",registro.get('estado','')], ["Recomendación Contratación", recomend]]
        t=Table(data,colWidths=[140,360])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0B4DA2')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),1,colors.black),('FONTSIZE',(0,0),(-1,-1),9)]))
        story.append(t)
        story.append(Spacer(1,12))
        story.append(Paragraph(f"<b>Temas a reforzar:</b> {registro.get('temas_bajos','Ninguno crítico')}<br/><b>Observaciones:</b> {registro.get('observaciones','')}",styles['Normal']))
        story.append(Spacer(1,24))
        story.append(Paragraph("Firma RRHH ___________________ Gerencia ___________________<br/>Documento para anexar a HV si es seleccionado",styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        return BytesIO(f"INFORME TECNICO {registro.get('nombre','')} {registro.get('porcentaje','')}%".encode())

def generar_pdf_psicologico(registro):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer,pagesize=letter)
        styles=getSampleStyleSheet()
        story=[]
        story.append(Paragraph("<b>HIREREADY-IA V10.2 - INFORME PSICOLOGICO Y PSICOTECNICO CONFIDENCIAL</b>",styles['Title']))
        story.append(Spacer(1,12))
        porc=registro.get('porcentaje',0)
        story.append(Paragraph(f"<b>Candidato:</b> {registro.get('nombre','')} CC {registro.get('cedula','')}<br/><b>Fecha:</b> {registro.get('fecha','')}<br/><b>Cargo:</b> {registro.get('cargo','')}<br/><b>Asignó:</b> {registro.get('asignado_por','RRHH')}<br/><b>Psicotécnica:</b> {registro.get('psicotecnica','')}<br/><b>Psicológica:</b> {registro.get('psicologica','')}<br/><b>Imágenes:</b> {registro.get('imagenes','')}<br/><b>Incómodas/Bobas:</b> {registro.get('incomodas','')}",styles['Normal']))
        story.append(Spacer(1,12))
        alertas=registro.get('alertas',[])
        if alertas:
            story.append(Paragraph("<b>ALERTAS PERSONALIDAD DISTORSIONADA DETECTADAS:</b>",styles['Heading2']))
            for al in alertas[:10]: story.append(Paragraph(f"- {al}",styles['Normal']))
            story.append(Spacer(1,12))
        if porc>=90: rango_psico="PERFIL ALTAMENTE CONFIABLE - Sin distorsiones, alta ética, listo cargo crítico"
        elif porc>=80: rango_psico="PERFIL CONFIABLE CON OBSERVACIONES MENORES"
        elif porc>=60: rango_psico="PERFIL EN OBSERVACION - Posibles distorsiones, requiere entrevista profunda psicólogo"
        else: rango_psico="PERFIL NO CONFIABLE - ALERTA PERSONALIDAD DISTORSIONADA - No contratar sin evaluación clínica"
        data=[["Rango Psicológico",rango_psico],["Recomendación",registro.get('perfil','')],["Confidencialidad", "ALTA" if porc>=80 else "MEDIA" if porc>=60 else "BAJA - RIESGO"],["Confiable contratar?", "SI - 95% ALTAMENTE CONFIABLE" if porc>=90 else "SI con refuerzo 85%" if porc>=80 else "NO sin evaluación"]]
        t=Table(data,colWidths=[130,370])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#7AC143')),('GRID',(0,0),(-1,-1),1,colors.black)]))
        story.append(t)
        story.append(Spacer(1,12))
        story.append(Paragraph(f"<b>Interpretación imágenes:</b> {registro.get('interpretacion_imagenes','')}<br/><b>Interpretación incómodas/bobas:</b> {registro.get('interpretacion_incomodas','')}<br/><b>Observaciones:</b> {registro.get('observaciones','')}",styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        return BytesIO(f"INFORME PSICOLOGICO {registro.get('nombre','')} {porc}%".encode())

def generar_pdf_gerencia_general(df):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer,pagesize=letter)
        styles=getSampleStyleSheet()
        story=[]
        story.append(Paragraph("<b>HIREREADY-IA V10.2 - INFORME GENERAL GERENCIA - TODOS LOS MESES</b>",styles['Title']))
        story.append(Spacer(1,12))
        story.append(Paragraph(f"<b>Fecha informe:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/><b>Total entrevistados:</b> {len(df)}<br/><b>Promedio general:</b> {df['porcentaje'].mean():.1f}%<br/><b>Rango fechas:</b> {df['fecha'].min()} a {df['fecha'].max()}",styles['Normal']))
        story.append(Spacer(1,12))
        # Resumen por mes
        df['mes']=pd.to_datetime(df['fecha'], errors='coerce').dt.to_period('M').astype(str)
        resumen_mes=df.groupby('mes').agg(total=('porcentaje','count'), promedio=('porcentaje','mean'), apto=('porcentaje', lambda x: (x>=70).sum())).reset_index()
        data_mes=[["Mes","Total","Promedio","Aptos"]]
        for _,row in resumen_mes.iterrows(): data_mes.append([row['mes'], str(row['total']), f"{row['promedio']:.1f}%", str(row['apto'])])
        t_mes=Table(data_mes,colWidths=[80,60,80,60])
        t_mes.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0B4DA2')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),1,colors.black)]))
        story.append(Paragraph("<b>Resumen por Mes:</b>",styles['Heading2']))
        story.append(t_mes)
        story.append(Spacer(1,12))
        # Resumen por cargo
        resumen_cargo=df.groupby('cargo').agg(total=('porcentaje','count'), promedio=('porcentaje','mean')).reset_index().sort_values('total', ascending=False)
        data_cargo=[["Cargo","Total","Promedio"]]
        for _,row in resumen_cargo.head(10).iterrows(): data_cargo.append([row['cargo'][:30], str(row['total']), f"{row['promedio']:.1f}%"])
        t_cargo=Table(data_cargo,colWidths=[200,60,80])
        t_cargo.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#7AC143')),('GRID',(0,0),(-1,-1),1,colors.black)]))
        story.append(Paragraph("<b>Top 10 Cargos:</b>",styles['Heading2']))
        story.append(t_cargo)
        story.append(Spacer(1,24))
        story.append(Paragraph("Firma RRHH ___________________ Gerencia ___________________",styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        return BytesIO(f"INFORME GERENCIA {len(df)} registros".encode())

if "auth" not in st.session_state: st.session_state.auth=False; st.session_state.user=None; st.session_state.user_type=None
if "modulo" not in st.session_state: st.session_state.modulo=None
if "asignacion_actual" not in st.session_state: st.session_state.asignacion_actual=None

if not st.session_state.auth:
    st.markdown('<div class="hero"><h2>💎 HIREREADY-IA V10.2 - LOGIN ARREGLADO</h2><p>26 Cargos x 25 Preguntas | PDF HV + PDF Psicológico | Dashboard Gerencia Mensual</p></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2,gap="large")
    with c1:
        st.markdown('<div class="mod-card" style="border-left-color:#7AC143;"><h3>👤 SOY CANDIDATO - Solo Cédula</h3><p>RRHH te asigna pruebas por cargo. Tú solo ingresas cédula.</p></div>',unsafe_allow_html=True)
        cedula_login=st.text_input("📇 CÉDULA *",placeholder="Ej: 1234567890")
        if st.button("🚀 VER MIS PRUEBAS ASIGNADAS",use_container_width=True,type="primary"):
            asignaciones=cargar_json(ASIGNACIONES_FILE,[])
            mi_asig=[a for a in asignaciones if a.get('cedula')==cedula_login and a.get('estado')!='COMPLETADO_FINAL']
            if not mi_asig:
                regs=cargar_json(REGISTROS_FILE,[])
                tiene=[r for r in regs if r.get('cedula')==cedula_login]
                if tiene: st.warning(f"Ya tienes {len(tiene)} pruebas presentadas. Si RRHH te re-asignó, debe asignarte de nuevo.")
                else: st.error("❌ No tienes pruebas asignadas. Pídele a RRHH que te asigne en 'Asignar Pruebas por Cédula'")
            else:
                st.session_state.auth=True; st.session_state.user_type="candidate"; st.session_state.cedula_real=cedula_login
                asig=mi_asig[0]; st.session_state.asignacion_actual=asig; st.session_state.nombre=asig.get('nombre','Candidato'); st.session_state.cargo_sel=asig.get('cargo','Personal de Nómina'); st.session_state.sede=asig.get('sede','Cali'); st.session_state.tel=asig.get('telefono',''); st.rerun()
    with c2:
        st.markdown('<div class="mod-card" style="border-left-color:#0B4DA2;"><h3>🔐 SOY RRHH / ADMIN</h3><p>Usuario: admin o ADMI - Clave: admin123<br>Acepta mayúsculas y minúsculas</p></div>',unsafe_allow_html=True)
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
        st.markdown(f'<div class="hero"><h2>👤 {asig.get("nombre","")} | CC {asig.get("cedula","")} | {asig.get("cargo","")}</h2><p>Asignó: {asig.get("asignado_por","RRHH")} el {asig.get("fecha_asignacion","")} | Pruebas: {", ".join(asig.get("modulos",[]))}</p></div>',unsafe_allow_html=True)
        if st.button("🚪 Salir"): st.session_state.auth=False; st.session_state.user_type=None; st.session_state.asignacion_actual=None; st.rerun()

        if "Entrevista General" in asig.get('modulos',[]):
            st.divider(); st.subheader(f"📋 Entrevista General - {asig.get('cargo','')} - 25 Preguntas")
            banco=cargar_json(PREGUNTAS_FILE,BANCO_ENTREVISTA); preguntas=banco.get(asig.get('cargo',''),[])[:25]
            resp=[]; temas_fallos=[]
            for i,pr in enumerate(preguntas):
                r=st.radio(f"{i+1}. {pr['q']}",pr["op"],key=f"ent{i}",index=None)
                if r is not None:
                    ok=pr["op"].index(r)==pr["r"]; resp.append(ok)
                    if not ok: temas_fallos.append(pr.get('tema',f"Tema {i+1}"))
            if st.button("✅ Finalizar Entrevista y Generar PDF Técnico para HV",type="primary"):
                if len(resp)<len(preguntas): st.warning(f"Faltan {len(preguntas)-len(resp)}")
                else:
                    aciertos=sum(resp); porc=aciertos/len(preguntas)*100
                    if porc>=90: estado="90-100% ALTAMENTE CONFIABLE - ALTAMENTE RECOMENDADO"; obs="Sabe de su trabajo, altamente confiable, contratar sin restricciones"
                    elif porc>=80: estado="80-89% CONFIABLE CON RECOMENDACIONES"; obs=f"Reforzar: {', '.join(temas_fallos[:3])} 30 días"
                    elif porc>=60: estado="EN OBSERVACION"; obs="Requiere 60 días refuerzo"
                    else: estado="NO RECOMENDADO - NO CONFIABLE"; obs="No sabe de su trabajo"
                    registro={"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":asig.get('cedula',''),"nombre":asig.get('nombre',''),"cargo":asig.get('cargo',''),"sede":asig.get('sede',''),"telefono":asig.get('telefono',''),"modulo":"Entrevista General","aciertos":aciertos,"total":len(preguntas),"porcentaje":round(porc,1),"estado":estado,"temas_bajos":", ".join(temas_fallos[:5]) if temas_fallos else "Ninguno crítico","observaciones":obs,"fuente":"Asignación RRHH","agente":"Agente Entrevista","asignado_por":asig.get('asignado_por','RRHH')}
                    regs=cargar_json(REGISTROS_FILE,[]); regs.append(registro); guardar_json(REGISTROS_FILE,regs)
                    pdf_buf=generar_pdf_tecnico(registro)
                    if porc>=80: st.balloons(); st.success(f"✅ {porc:.1f}% - {estado}")
                    else: st.error(f"❌ {porc:.1f}% - {estado}")
                    st.download_button("📄 DESCARGAR PDF TÉCNICO PARA ANEXAR A HV - AQUÍ ESTÁ TU PDF",pdf_buf,file_name=f"Informe_Tecnico_HV_{asig.get('cedula','')}_{asig.get('cargo','')}.pdf",mime="application/pdf")

        if "Test Psicologico Laboral" in asig.get('modulos',[]) or "Test Psicológico Laboral" in asig.get('modulos',[]):
            st.divider(); st.subheader("🧠 Test Psicológico Laboral - 60 Preguntas - Imágenes + Incómodas/Bobas")
            todas=TEST_PSICO["Psicotecnica_25"]+TEST_PSICO["Psicologica_25"]+TEST_PSICO["Imagenes_5"]+TEST_PSICO["Incomodas_Bobas_5"]
            resp_psico=[]; alertas=[]; inter_img=[]; inter_inc=[]
            for i,pr in enumerate(todas):
                tipo="Psicotécnica" if i<25 else "Psicológica" if i<50 else "Imagen" if i<55 else "Incómoda/Boba"
                r=st.radio(f"{i+1}. [{tipo}] {pr['q']}",pr["op"],key=f"psi_{i}",index=None)
                if r is not None:
                    ok=pr["op"].index(r)==pr["r"]; resp_psico.append(ok)
                    if not ok and "alerta" in pr: alertas.append(f"{pr['q'][:50]} -> {pr['alerta']}")
                    if tipo=="Imagen": inter_img.append(f"{pr['interpreta']}")
                    if tipo=="Incómoda/Boba": inter_inc.append(f"{pr['interpreta']}")
            if st.button("✅ Finalizar Test Psicológico y Generar PDF Psicológico Confidencial",type="primary"):
                if len(resp_psico)<len(todas): st.warning(f"Faltan {len(todas)-len(resp_psico)}")
                else:
                    aciertos=sum(resp_psico); porc=aciertos/len(todas)*100
                    ac_t=sum(resp_psico[:25]); ac_p=sum(resp_psico[25:50]); ac_i=sum(resp_psico[50:55]); ac_b=sum(resp_psico[55:60])
                    if porc>=90: perfil="ALTAMENTE CONFIABLE - Sin distorsiones"; conf="95% SI contratar"
                    elif porc>=80: perfil="CONFIABLE CON OBSERVACIONES"; conf="85% SI con refuerzo"
                    elif porc>=60: perfil="EN OBSERVACION - Posible distorsión"; conf="65% NO sin evaluación psicólogo"
                    else: perfil="NO CONFIABLE - ALERTA PERSONALIDAD DISTORSIONADA"; conf="30% NO recomiendo contratar"
                    registro={"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":asig.get('cedula',''),"nombre":asig.get('nombre',''),"cargo":asig.get('cargo',''),"sede":asig.get('sede',''),"telefono":asig.get('telefono',''),"modulo":"Test Psicológico Laboral","aciertos":aciertos,"total":len(todas),"porcentaje":round(porc,1),"psicotecnica":f"{ac_t}/25","psicologica":f"{ac_p}/25","imagenes":f"{ac_i}/5","incomodas":f"{ac_b}/5","perfil":perfil,"estado":conf,"alertas":alertas,"interpretacion_imagenes":"; ".join(inter_img[:3]),"interpretacion_incomodas":"; ".join(inter_inc[:3]),"fuente":"Asignación RRHH","agente":"Agente Psicológico","asignado_por":asig.get('asignado_por','RRHH'),"observaciones":perfil}
                    regs=cargar_json(REGISTROS_FILE,[]); regs.append(registro); guardar_json(REGISTROS_FILE,regs)
                    pdf_buf=generar_pdf_psicologico(registro)
                    if alertas: st.markdown('<div class="alert-rojo"><b>🚨 ALERTAS PERSONALIDAD DISTORSIONADA:</b><br>'+ "<br>".join(alertas[:5]) +"</div>",unsafe_allow_html=True)
                    else: st.markdown('<div class="alert-verde"><b>✅ Sin alertas personalidad</b></div>',unsafe_allow_html=True)
                    st.success(f"{porc:.1f}% - {perfil}")
                    st.download_button("🧠 DESCARGAR PDF PSICOLÓGICO CONFIDENCIAL - AQUÍ ESTÁ TU PDF",pdf_buf,file_name=f"Informe_Psicologico_{asig.get('cedula','')}.pdf",mime="application/pdf")

    else:
        st.sidebar.success(f"🔐 {st.session_state.user['nombre']}")
        if st.sidebar.button("🚪 Cerrar sesión"): st.session_state.auth=False; st.session_state.user=None; st.session_state.user_type=None; st.rerun()
        menu=st.sidebar.selectbox("Menú V10.2", ["📊 Dashboard Gerencia + Informe General Mensual", "📝 Asignar Pruebas por Cédula (con quien asignó)", "💎 Talent Pool + PDFs + WhatsApp", "📋 Ver PDFs Generados - Dónde están?"])

        if menu=="📝 Asignar Pruebas por Cédula (con quien asignó)":
            st.markdown('<div class="hero"><h2>📝 Asignar Pruebas por Cédula</h2><p>Ahora guarda QUIÉN de RRHH asignó la prueba</p></div>',unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                cedula_asig=st.text_input("📇 Cédula *"); nombre_asig=st.text_input("👤 Nombre *"); cargo_asig=st.selectbox("💼 Cargo *",CARGOS_DEFAULT)
            with c2:
                sede_asig=st.text_input("📍 Ciudad"); tel_asig=st.text_input("📱 WhatsApp"); modulos_asig=st.multiselect("🧩 Módulos *",["Entrevista General","Test Psicologico Laboral"],default=["Entrevista General","Test Psicologico Laboral"])
            if st.button("✅ ASIGNAR PRUEBAS",type="primary",use_container_width=True):
                if not (cedula_asig and nombre_asig and modulos_asig): st.error("Cédula, nombre y módulos obligatorios")
                else:
                    asignaciones=cargar_json(ASIGNACIONES_FILE,[])
                    nueva={"fecha_asignacion":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":cedula_asig,"nombre":nombre_asig,"cargo":cargo_asig,"sede":sede_asig,"telefono":tel_asig,"modulos":modulos_asig,"asignado_por":st.session_state.user['nombre']+" ("+st.session_state.user['usuario']+")","estado":"PENDIENTE"}
                    asignaciones.append(nueva); guardar_json(ASIGNACIONES_FILE,asignaciones)
                    st.success(f"✅ Asignado a {nombre_asig} por {nueva['asignado_por']}. El candidato ya puede entrar con cédula {cedula_asig}"); st.balloons()
            st.divider(); st.subheader("📚 Tabla Asignaciones - Con Usuario RRHH que asignó")
            asignaciones=cargar_json(ASIGNACIONES_FILE,[])
            if asignaciones:
                df_asig=pd.DataFrame(asignaciones)
                # Asegurar columna asignado_por visible
                cols_orden=["fecha_asignacion","cedula","nombre","cargo","modulos","asignado_por","estado","sede","telefono"]
                cols_exist=[c for c in cols_orden if c in df_asig.columns]
                st.dataframe(df_asig[cols_exist],use_container_width=True)
                st.download_button("📥 Descargar Asignaciones CSV con quien asignó",df_asig.to_csv(index=False).encode(),"asignaciones_con_usuario_RRHH.csv")
            else: st.info("Sin asignaciones")

        elif menu=="📊 Dashboard Gerencia + Informe General Mensual":
            st.markdown('<div class="hero"><h2>📊 Dashboard Gerencia - Informe General Todos los Meses</h2><p>KPIs, gráfico mensual, filtros y PDFs para Gerencia</p></div>',unsafe_allow_html=True)
            regs=cargar_json(REGISTROS_FILE,[])
            if not regs: st.info("Sin registros aún. Asigna pruebas y haz que candidatos presenten.")
            else:
                df=pd.DataFrame(regs)
                df['fecha_dt']=pd.to_datetime(df['fecha'], errors='coerce')
                df['mes']=df['fecha_dt'].dt.to_period('M').astype(str)
                # KPIs
                k1,k2,k3,k4,k5=st.columns(5)
                with k1: st.markdown(f'<div class="kpi-card"><div class="kpi-number">{len(df)}</div><div>Total Evaluaciones</div></div>',unsafe_allow_html=True)
                with k2: st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:#22c55e;">{len(df[df["porcentaje"]>=90])}</div><div>90%+ Altamente Confiable</div></div>',unsafe_allow_html=True)
                with k3: st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:#f59e0b;">{len(df[(df["porcentaje"]>=80)&(df["porcentaje"]<90)])}</div><div>80-89% Confiable c/ Recom.</div></div>',unsafe_allow_html=True)
                with k4: st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:#ef4444;">{len(df[df["porcentaje"]<60])}</div><div>NO Recomendado</div></div>',unsafe_allow_html=True)
                with k5: st.markdown(f'<div class="kpi-card"><div class="kpi-number">{df["porcentaje"].mean():.1f}%</div><div>Promedio</div></div>',unsafe_allow_html=True)

                st.divider()
                c_g1,c_g2=st.columns(2)
                with c_g1:
                    st.subheader("📈 Evaluaciones por Mes")
                    df_mes=df.groupby('mes').size().reset_index(name='total')
                    st.bar_chart(df_mes.set_index('mes'))
                with c_g2:
                    st.subheader("📊 Promedio por Cargo (Top 10)")
                    df_cargo=df.groupby('cargo')['porcentaje'].mean().sort_values(ascending=False).head(10)
                    st.bar_chart(df_cargo)

                st.divider()
                st.subheader("🔍 Filtro por Mes para Informe Gerencia")
                meses=df['mes'].dropna().unique().tolist()
                mes_sel=st.multiselect("Selecciona mes(es) - deja vacío para todos", meses, default=meses)
                df_f=df if not mes_sel else df[df['mes'].isin(mes_sel)]

                st.dataframe(df_f, use_container_width=True, height=350)

                st.divider()
                st.subheader("📄 GENERAR INFORME GENERAL PARA GERENCIA - TODOS LOS MESES")
                col_pdf1,col_pdf2,col_pdf3=st.columns(3)
                with col_pdf1:
                    pdf_gerencia=generar_pdf_gerencia_general(df_f)
                    st.download_button("📄 DESCARGAR PDF INFORME GENERAL GERENCIA - AQUÍ",pdf_gerencia,file_name=f"Informe_General_Gerencia_{datetime.now().strftime('%Y%m%d')}.pdf",mime="application/pdf",type="primary",use_container_width=True)
                with col_pdf2:
                    st.download_button("📥 DESCARGAR CSV GENERAL TODOS LOS MESES",df_f.to_csv(index=False).encode(),f"Informe_General_Gerencia_{datetime.now().strftime('%Y%m%d')}.csv",mime="text/csv",use_container_width=True)
                with col_pdf3:
                    # Resumen ejecutivo texto
                    total=len(df_f); aptos=len(df_f[df_f["porcentaje"]>=70]); porc_apto=aptos/total*100 if total>0 else 0
                    st.markdown(f'<div class="mod-card"><b>Resumen Ejecutivo:</b><br>Total: {total}<br>Aptos: {aptos} ({porc_apto:.1f}%)<br>90%+: {len(df_f[df_f["porcentaje"]>=90])}<br>80-89%: {len(df_f[(df_f["porcentaje"]>=80)&(df_f["porcentaje"]<90)])}</div>',unsafe_allow_html=True)

                st.divider()
                st.subheader("📄 GENERAR PDFs INDIVIDUALES POR CANDIDATO - DÓNDE ESTÁN LOS PDFs QUE PEDISTE")
                st.info("👇 Aquí seleccionas cédula y te salen los 2 botones de PDF que pediste: Técnico para HV y Psicológico Confidencial")
                cand_sel=st.selectbox("Selecciona CÉDULA candidato para descargar sus PDFs", df_f["cedula"].unique() if "cedula" in df_f.columns else [])
                if cand_sel:
                    cand_regs=df_f[df_f["cedula"]==cand_sel]
                    for _,row in cand_regs.iterrows():
                        rd=row.to_dict()
                        st.markdown(f"**{rd.get('nombre','')} | {rd.get('modulo','')} | {rd.get('porcentaje','')}% | Asignó: {rd.get('asignado_por','RRHH')}**")
                        col_a,col_b=st.columns(2)
                        with col_a:
                            if "Entrevista General" in str(rd.get('modulo','')):
                                pdf_t=generar_pdf_tecnico(rd)
                                st.download_button(f"📄 PDF TÉCNICO HV - {rd.get('porcentaje','')}% - Para anexar a HV",pdf_t,file_name=f"PDF_TECNICO_HV_{cand_sel}_{rd.get('cargo','')}.pdf",mime="application/pdf",key=f"tec_{cand_sel}_{row.name}",use_container_width=True)
                        with col_b:
                            if "Psicológico" in str(rd.get('modulo','')):
                                pdf_p=generar_pdf_psicologico(rd)
                                st.download_button(f"🧠 PDF PSICOLÓGICO CONFIDENCIAL - {rd.get('porcentaje','')}% - Con alertas",pdf_p,file_name=f"PDF_PSICOLOGICO_{cand_sel}.pdf",mime="application/pdf",key=f"psi_{cand_sel}_{row.name}",use_container_width=True)
                        porc=rd.get('porcentaje',0)
                        if porc>=90: st.markdown(f'<div class="alert-verde">✅ {porc}% - 90%+ ALTAMENTE CONFIABLE - Sabe de su trabajo - Recomiendo contratar - 95% confiable - Solo reforzar temas menores</div>',unsafe_allow_html=True)
                        elif porc>=80: st.markdown(f'<div class="alert-amarillo">⚠️ {porc}% - 80-89% CONFIABLE CON RECOMENDACIONES - Recomiendo contratar con plan refuerzo 30 días en: {rd.get("temas_bajos","")}</div>',unsafe_allow_html=True)
                        else: st.markdown(f'<div class="alert-rojo">🚨 {porc}% - NO CONFIABLE - No sabe o vacíos graves - No recomiendo contratar</div>',unsafe_allow_html=True)
                        if rd.get('alertas'): st.markdown('<div class="alert-rojo"><b>🚨 ALERTAS PERSONALIDAD DISTORSIONADA:</b><br>'+ "<br>".join(rd.get('alertas',[])[:3]) +"</div>",unsafe_allow_html=True)

        elif menu=="💎 Talent Pool + PDFs + WhatsApp":
            st.header("💎 Talent Pool - Con quien asignó + PDFs")
            talent=cargar_json(TALENT_FILE,[])
            if talent:
                df_t=pd.DataFrame(talent)
                st.dataframe(df_t,use_container_width=True)
                cand=st.selectbox("Cédula para PDFs", df_t["cedula"].unique() if "cedula" in df_t.columns else [])
                if cand:
                    for _,r in df_t[df_t["cedula"]==cand].iterrows():
                        rd=r.to_dict()
                        if "Entrevista General" in str(rd.get('modulo','')):
                            pdf_t=generar_pdf_tecnico(rd)
                            st.download_button(f"📄 PDF Técnico HV {rd.get('nombre','')} - Asignó: {rd.get('asignado_por','')}",pdf_t,file_name=f"Tecnico_{cand}.pdf",mime="application/pdf",key=f"t_{cand}_{r.name}")
                        else:
                            pdf_p=generar_pdf_psicologico(rd)
                            st.download_button(f"🧠 PDF Psicológico {rd.get('nombre','')} - Asignó: {rd.get('asignado_por','')}",pdf_p,file_name=f"Psicologico_{cand}.pdf",mime="application/pdf",key=f"p_{cand}_{r.name}")
            else: st.info("Talent Pool vacío")

        elif menu=="📋 Ver PDFs Generados - Dónde están?":
            st.header("📋 DÓNDE VER Y GENERAR LOS PDFs QUE PEDISTE")
            st.markdown("""
            <div class="mod-card">
            <h3>📍 1. PDF Técnico para anexar a HV (si es seleccionado)</h3>
            <p><b>Dónde:</b> Cuando candidato termina Entrevista General -> botón verde <b>📄 DESCARGAR PDF TÉCNICO PARA ANEXAR A HV</b></p>
            <p><b>También:</b> Tú como RRHH vas a <b>📊 Dashboard Gerencia</b> -> seleccionas cédula -> botón <b>📄 PDF TÉCNICO HV</b></p>
            <p><b>Contenido:</b> Nombre, CC, cargo, %, rango 80-90% con recomendaciones, 90%+ altamente confiable, sabe/no sabe, confiable contratar, temas a reforzar, firma RRHH y Gerencia</p>
            </div>
            <div class="mod-card" style="border-left-color:#7AC143;">
            <h3>📍 2. PDF Psicológico y Psicotécnico Confidencial</h3>
            <p><b>Dónde:</b> Cuando candidato termina Test Psicológico -> botón <b>🧠 DESCARGAR PDF PSICOLÓGICO CONFIDENCIAL</b></p>
            <p><b>También:</b> Dashboard Gerencia -> seleccionas cédula -> botón <b>🧠 PDF PSICOLÓGICO CONFIDENCIAL</b></p>
            <p><b>Contenido:</b> 25 Psicotécnica + 25 Psicológica + 5 Imágenes + 5 Incómodas/Bobas, %, perfil, rango confiabilidad, confidencialidad, alertas personalidad distorsionada, interpretación imágenes, interpretación preguntas bobas/incómodas, recomendación contratar</p>
            </div>
            <div class="mod-card" style="border-left-color:#f59e0b;">
            <h3>📍 3. Informe General Mensual para Gerencia (todos los meses)</h3>
            <p><b>Dónde:</b> <b>📊 Dashboard Gerencia + Informe General Mensual</b> -> abajo hay 2 botones:</p>
            <p>- <b>📄 DESCARGAR PDF INFORME GENERAL GERENCIA</b> (con resumen por mes, top cargos, totales, aptos, promedios)</p>
            <p>- <b>📥 DESCARGAR CSV GENERAL TODOS LOS MESES</b></p>
            </div>
            <div class="mod-card" style="border-left-color:#ef4444;">
            <h3>📍 4. Tabla con usuario que asignó la prueba</h3>
            <p><b>Dónde:</b> <b>📝 Asignar Pruebas por Cédula</b> -> abajo ves tabla con columna <b>asignado_por</b> que dice qué usuario de RRHH asignó (ej: Admin Simple (admin) o RRHH HireReady (rrhh@hireready.ia))</p>
            <p><b>También:</b> En Dashboard y Talent Pool cada registro muestra <b>Asignó:...</b></p>
            </div>
            """, unsafe_allow_html=True)
