import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import re

st.set_page_config(page_title="HIREREADY-IA", page_icon="🤖", layout="wide")

st.markdown("""
<style>
   .stApp { background-color: #f8fafc; }
    h1, h2, h3 { color: #0B4DA2!important; }
   .stButton>button { background-color: #0B4DA2; color: white; border-radius: 10px; font-weight: bold; }
   .stButton>button:hover { background-color: #7AC143; color: white; }
    [data-testid="stSidebar"] { background-color: #0B4DA2; }
    [data-testid="stSidebar"] * { color: white!important; }
   .ia-box { background: linear-gradient(135deg, #0B4DA2 0%, #7AC143 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
   .brand { font-size: 32px; font-weight: 800; color: #0B4DA2; }
   .brand span { color: #7AC143; }
</style>
""", unsafe_allow_html=True)

USUARIOS_FILE = "usuarios_admin.json"
REGISTROS_FILE = "registros_farmart.json"
CARGOS_FILE = "cargos.json"
PREGUNTAS_FILE = "preguntas_banco.json"
CONFIG_FILE = "config_excel.json"

if not os.path.exists(USUARIOS_FILE):
    with open(USUARIOS_FILE, "w") as f:
        json.dump([{"usuario":"admin@hireready.ia","clave":"HireReady2026*","rol":"Super Admin","nombre":"Admin Principal"}, {"usuario":"admin@farmart.system","clave":"Farmart2026*","rol":"Super Admin","nombre":"Admin Farmart"}], f)
if not os.path.exists(REGISTROS_FILE):
    with open(REGISTROS_FILE, "w") as f:
        json.dump([], f)

CARGOS_DEFAULT = [
    "Personal de Nómina","Tesorería",
    "Auxiliar de bodega de carga","Auxiliar de farmacia","Mensajero de moto","Conductor de carro",
    "Quimico farmaceutico","Regente de farmacia","Auditoria y facturación","Contadores público",
    "Auxiliares contables","Revisores fiscales","Auxiliares de servicios generales","Recursos Humanos",
    "Auxiliares de archivo","Auditores médicos","Operadores logísticos","Ingenieros ambientales",
    "Ingeniero de sistemas","Ingenieros de software","Desarrolladores fullstack","Auxiliares de recursos humanos",
    "Abogados","Alta gerencia","Auxiliares administrativas","Ingenieros especialistas TIC / Ciberseguridad"
]

BANCO_DEFAULT = {
    "Personal de Nómina": [
        {"q":"¿Qué compone la seguridad social integral?","op":["Salud, pensión y ARL","Solo salud","Solo pensión"],"r":0},
        {"q":"¿Qué es una novedad de nómina?","op":["Incapacidad, vacaciones, horas extra","Solo cambio de cargo","Solo aumento"],"r":0},
        {"q":"¿Qué es PILA?","op":["Planilla para pago seguridad social","Planilla de inventario","Planilla de aseo"],"r":0},
        {"q":"Auxilio de transporte ¿cuándo se paga?","op":["Si gana hasta 2 SMMLV","A todos","Nunca"],"r":0},
    ],
    "Tesorería": [
        {"q":"¿Qué es flujo de caja?","op":["Entrada y salida de dinero","Solo entradas","Solo inventario"],"r":0},
        {"q":"¿Qué es conciliación bancaria?","op":["Comparar libros con extracto bancario","Contar caja menor","Hacer nómina"],"r":0},
        {"q":"¿Qué es arqueo de caja?","op":["Verificación física del efectivo vs sistema","Inventario medicamentos","Revisión tutelas"],"r":0},
    ],
    "Auxiliar de bodega de carga": [
        {"q":"¿Qué significa FEFO?","op":["First Expire First Out","First Entry First Out","Fast Expire"],"r":0},
        {"q":"¿Temperatura cadena de frio?","op":["2-8°C","15-25°C","-20°C"],"r":0},
        {"q":"Medicamento vencido ¿qué hace?","op":["Separa, identifica y reporta","Lo devuelve al estante","Lo bota a basura común"],"r":0},
    ],
    "Quimico farmaceutico": [
        {"q":"Central de mezclas: ¿Qué es NPT?","op":["Nutrición Parenteral Total","Norma de Preparación Técnica","Nivel Total"],"r":0},
        {"q":"Unidosis: ¿Objetivo?","op":["Dosis exacta por paciente, reduce errores","Ahorrar empaques","Vender más"],"r":0},
        {"q":"Oncológico: ¿Qué es citotóxico?","op":["Medicamento que destruye células, manejo especial","Para dolor","Antibiótico"],"r":0},
    ],
    "Abogados": [
        {"q":"Tutela: ¿Término para fallar?","op":["10 días","30 días","6 meses"],"r":0},
        {"q":"CASO oncológico vital ¿qué argumenta?","op":["Derecho a vida, salud y mínimo vital","Solo trabajo","Solo petición"],"r":0},
    ]
}

EXCEL_DEFAULT = [
    {"q":"Excel: ¿Fórmula para sumar?","op":["=SUMA(A1:A10)","SUMAR A1","=ADD()"],"r":0},
    {"q":"¿Qué hace BUSCARV?","op":["Busca dato en tabla","Borra valores","Crea gráfico"],"r":0},
    {"q":"Tabla dinámica sirve para:","op":["Resumir grandes datos rápido","Escribir cartas","Navegar internet"],"r":0},
]
PSICO_DEFAULT = [
    {"q":"Si compañero toma medicamento sin fórmula, ¿qué haces?","op":["Reportas por seguridad del paciente","Te callas","Lo ayudas a vender"],"r":0},
    {"q":"Bajo estrés, tú:","op":["Priorizas, pides ayuda, mantienes calidad","Gritas y dejas todo","Haces rápido sin verificar"],"r":0},
    {"q":"Jefe pide entregar vencido, ¿qué haces?","op":["Te niegas y reportas, ética primero","Lo entregas","Cambias fecha"],"r":0},
]

KEYWORDS_POR_CARGO = {
    "Personal de Nómina": ["nomina","pila","seguridad social","retencion","prestaciones","cesantias","liquidacion","parafiscales","excel","siigo"],
    "Tesorería": ["tesoreria","flujo de caja","conciliacion","bancos","egreso","arqueo","cuentas por pagar","excel"],
    "Quimico farmaceutico": ["quimico farmaceutico","central de mezclas","unidosis","oncologico","citotoxico","NPT","asepsia","BPM","INVIMA"],
    "Auxiliar de farmacia": ["dispensacion","farmacia","invima","medicamentos","lote","vencimiento"],
    "Abogados": ["tutela","derecho de peticion","contratacion estatal","ley 80","laboral"],
    "Ingeniero de sistemas": ["sistemas","python","base de datos","ciberseguridad","redes","soporte"],
    "Contadores público": ["contador","contabilidad","dian","facturacion electronica","iva"],
}

if not os.path.exists(CARGOS_FILE):
    with open(CARGOS_FILE,"w") as f:
        json.dump(CARGOS_DEFAULT,f, indent=2)
if not os.path.exists(PREGUNTAS_FILE):
    full = {}
    for c in CARGOS_DEFAULT:
        full[c] = BANCO_DEFAULT.get(c, BANCO_DEFAULT.get("Auxiliar de bodega de carga", [])[:2])
    with open(PREGUNTAS_FILE,"w") as f:
        json.dump(full,f, indent=2, ensure_ascii=False)
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE,"w") as f:
        json.dump({"sin_excel": ["Mensajero de moto","Conductor de carro","Auxiliares de servicios generales","Auxiliar de bodega de carga"],"excel": EXCEL_DEFAULT,"psico": PSICO_DEFAULT, "requiere_hv": False}, f, indent=2, ensure_ascii=False)

def cargar_json(path):
    with open(path,"r") as f:
        return json.load(f)
def guardar_json(path,data):
    with open(path,"w") as f:
        json.dump(data,f, indent=2, ensure_ascii=False)

def get_preguntas_cargo(cargo):
    banco = cargar_json(PREGUNTAS_FILE)
    config = cargar_json(CONFIG_FILE)
    base = banco.get(cargo, [])
    if cargo not in config.get("sin_excel",[]):
        base = base + config.get("excel",[])
    base = base + config.get("psico",[])
    return base, len(banco.get(cargo,[])), len(config.get("excel",[])), len(config.get("psico",[]))

def analizar_hv_ia(texto_hv, cargo):
    texto = texto_hv.lower()
    keywords = KEYWORDS_POR_CARGO.get(cargo, [])
    if not keywords:
        keywords = ["experiencia","excel","trabajo en equipo"]
    encontrados = [k for k in keywords if k.lower() in texto]
    porcentaje = int((len(encontrados)/len(keywords)*100) if keywords else 50)
    porcentaje = min(95, max(15, porcentaje))
    anios = re.findall(r"(\d+)\s*a\w*\s*de experiencia|experiencia\s*(\d+)", texto)
    exp = "No especificada"
    if anios:
        try:
            exp = f"{anios[0][0] or anios[0][1]} años aprox"
        except:
            exp = "Detectada experiencia"
    fortalezas = ", ".join(encontrados[:5]) if encontrados else "Perfil general"
    faltantes = [k for k in keywords if k.lower() not in texto][:3]
    if porcentaje >= 80:
        concepto = "PERFIL ALTAMENTE COMPATIBLE"
        rec = "AVANZA A ENTREVISTA"
    elif porcentaje >= 50:
        concepto = "PERFIL MEDIANAMENTE COMPATIBLE"
        rec = "ENTREVISTA CON VALIDACION - Reforzar: " + ", ".join(faltantes)
    else:
        concepto = "PERFIL BAJO"
        rec = "NO RECOMENDADO o periodo prueba - Faltan: " + ", ".join(faltantes)
    preguntas_ia = [
        f"Cuéntame tu experiencia en {keywords[0] if keywords else cargo}",
        f"¿Qué harías en un caso de {faltantes[0] if faltantes else 'emergencia'}?",
        "¿Por qué cambiaste de empleo?",
        "¿Manejas Excel avanzado?"
    ]
    return {"porcentaje": porcentaje,"concepto": concepto,"exp": exp,"fortalezas": fortalezas,"faltantes": ", ".join(faltantes) if faltantes else "Ninguno crítico","rec": rec,"preguntas_ia": preguntas_ia,"encontrados": encontrados}

def leer_pdf(file):
    texto = ""
    try:
        import fitz
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            texto += page.get_text()
    except:
        try:
            import PyPDF2
            file.seek(0)
            reader = PyPDF2.PdfReader(file)
            for p in reader.pages:
                texto += p.extract_text() or ""
        except:
            try:
                file.seek(0)
                texto = file.read().decode(errors="ignore")
            except:
                texto = ""
    return texto[:15000]

if "auth" not in st.session_state:
    st.session_state.auth=False
    st.session_state.user=None

st.markdown('<div class="brand">HIRE<span>READY</span>-IA 🤖</div>', unsafe_allow_html=True)
st.caption("Plataforma inteligente de evaluación - V4.1 con HV opcional")

if not st.session_state.auth:
    tab1, tab2 = st.tabs(["📝 Prueba Aspirante", "🔐 RRHH / Admin"])
    with tab1:
        config = cargar_json(CONFIG_FILE)
        requiere_hv = config.get("requiere_hv", False)
        if requiere_hv:
            st.markdown('<div class="ia-box">🤖 Sube tu hoja de vida en PDF - OBLIGATORIO por configuración de RRHH</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ia-box">🤖 HIREREADY-IA - Sube tu HV (opcional) y la IA la analiza. Si no quieres, pasa directo a la prueba.</div>', unsafe_allow_html=True)
        cedula = st.text_input("Cédula *")
        nombre = st.text_input("Nombre completo *")
        cargos_list = cargar_json(CARGOS_FILE)
        cargo = st.selectbox("Cargo al que aspira *", cargos_list)
        sede = st.text_input("Ciudad / Sede")
        label_hv = "📎 HOJA DE VIDA PDF - OBLIGATORIA" if requiere_hv else "📎 HOJA DE VIDA PDF - OPCIONAL (Recomendada para análisis IA)"
        archivo_hv = st.file_uploader(label_hv, type=["pdf"])
        if not requiere_hv:
            st.caption("ℹ️ Si no subes HV, puedes ir directo a la prueba técnica.")
        if "inicio_test" not in st.session_state:
            st.session_state.inicio_test=False
            st.session_state.analisis_ia=None
        col1, col2 = st.columns(2)
        with col1:
            btn_analizar = st.button("1️⃣ Analizar HV con IA", type="primary", use_container_width=True)
        with col2:
            btn_saltar = st.button("⏭️ Saltar HV e ir a Prueba", use_container_width=True)
        if btn_analizar:
            if requiere_hv and not archivo_hv:
                st.error("Hoja de vida obligatoria según RRHH. Súbela.")
            elif archivo_hv:
                if not (cedula and nombre):
                    st.error("Cédula y nombre obligatorios")
                else:
                    with st.spinner("🤖 IA analizando..."):
                        texto_hv = leer_pdf(archivo_hv)
                        if len(texto_hv) < 30:
                            st.error("PDF no legible, usa PDF con texto seleccionable")
                        else:
                            analisis = analizar_hv_ia(texto_hv, cargo)
                            st.session_state.analisis_ia = analisis
                            st.session_state.cedula_real=cedula
                            st.session_state.nombre=nombre
                            st.session_state.cargo_sel=cargo
                            st.session_state.sede=sede
                            st.success("✅ IA completado")
                            st.rerun()
            else:
                if not (cedula and nombre):
                    st.error("Cédula y nombre obligatorios")
                else:
                    st.session_state.analisis_ia = {"porcentaje":0,"concepto":"Sin HV","fortalezas":"No aplica","faltantes":"No aplica","rec":"Solo prueba técnica","exp":"No aplica","preguntas_ia":[],"encontrados":[]}
                    st.session_state.cedula_real=cedula
                    st.session_state.nombre=nombre
                    st.session_state.cargo_sel=cargo
                    st.session_state.sede=sede
                    st.session_state.inicio_test=True
                    st.rerun()
        if btn_saltar:
            if not (cedula and nombre):
                st.error("Cédula y nombre obligatorios")
            else:
                if requiere_hv:
                    st.error("No puedes saltar, RRHH configuró HV como OBLIGATORIA")
                else:
                    st.session_state.analisis_ia = {"porcentaje":0,"concepto":"Sin HV - Opcional","fortalezas":"No aplica","faltantes":"No aplica","rec":"Sin análisis HV, solo prueba técnica","exp":"No aplica","preguntas_ia":[],"encontrados":[]}
                    st.session_state.cedula_real=cedula
                    st.session_state.nombre=nombre
                    st.session_state.cargo_sel=cargo
                    st.session_state.sede=sede
                    st.session_state.inicio_test=True
                    st.rerun()
        if st.session_state.get("analisis_ia") and st.session_state.analisis_ia["porcentaje"]>0:
            a = st.session_state.analisis_ia
            st.divider()
            st.subheader("🤖 Resultado IA Hoja de Vida")
            c1,c2,c3=st.columns(3)
            c1.metric("Compatibilidad IA", f"{a['porcentaje']}%")
            c2.metric("Concepto", a["concepto"][:22])
            c3.metric("Experiencia", a["exp"])
            st.write(f"**Fortalezas:** {a['fortalezas']}")
            st.write(f"**Brechas:** {a['faltantes']}")
            st.info(f"**IA:** {a['rec']}")
            if not st.session_state.inicio_test:
                if st.button("Continuar a Prueba Técnica"):
                    st.session_state.inicio_test=True
                    st.rerun()
        if st.session_state.inicio_test:
            preguntas, n_tec, n_exc, n_psi = get_preguntas_cargo(st.session_state.cargo_sel)
            st.divider()
            st.subheader(f"Evaluación: {st.session_state.cargo_sel}")
            st.info(f"Total: {len(preguntas)} preguntas | Técnicas: {n_tec} | Excel: {n_exc if st.session_state.cargo_sel not in cargar_json(CONFIG_FILE).get('sin_excel',[]) else 0} | Psico: {n_psi} | 90% para APTO")
            respuestas=[]
            for i,p in enumerate(preguntas):
                r = st.radio(f"{i+1}. {p['q']}", p["op"], key=f"pq{i}", index=None)
                if r is not None:
                    respuestas.append(p["op"].index(r)==p["r"])
            if st.button("FINALIZAR Y GENERAR REPORTE HIREREADY-IA", type="primary"):
                if len(respuestas) < len(preguntas):
                    st.warning(f"Faltan {len(preguntas)-len(respuestas)}")
                else:
                    aciertos=sum(respuestas)
                    porc=aciertos/len(preguntas)*100
                    apto=porc>=90
                    aciertos_psico=sum(respuestas[-n_psi:])
                    a = st.session_state.get("analisis_ia", {"porcentaje":0,"concepto":"Sin HV","fortalezas":"N/A","faltantes":"N/A","rec":"Solo prueba","exp":"N/A","preguntas_ia":[]})
                    final = int((a["porcentaje"]*0.4 + porc*0.6)) if a["porcentaje"]>0 else int(porc)
                    if aciertos_psico>=3 and apto and final>=70:
                        rec="ALTA RECOMENDACIÓN - Contratar"; rec_porc=95
                    elif final>=60 and porc>=70:
                        rec="RECOMENDADO CON PERIODO PRUEBA"; rec_porc=75
                    else:
                        rec="NO RECOMENDADO"; rec_porc=35
                    registro={
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cedula": st.session_state.cedula_real,
                        "nombre": st.session_state.nombre,
                        "cargo": st.session_state.cargo_sel,
                        "sede": st.session_state.sede,
                        "aciertos": aciertos,
                        "total": len(preguntas),
                        "porcentaje": round(porc,1),
                        "psicotecnica": f"{aciertos_psico}/{n_psi}",
                        "ia_compatibilidad": a["porcentaje"],
                        "puntaje_final": final,
                        "estado": "APTO" if apto else "NO APTO",
                        "recomendacion": rec,
                        "porc_recomendacion": rec_porc,
                        "fortalezas_ia": a["fortalezas"],
                        "faltantes_ia": a["faltantes"]
                    }
                    regs=cargar_json(REGISTROS_FILE)
                    regs.append(registro)
                    guardar_json(REGISTROS_FILE,regs)
                    st.divider()
                    if apto and final>=60:
                        st.balloons()
                        st.success(f"## ✅ {registro['estado']} - Prueba {porc:.1f}% | IA {a['porcentaje']}% | FINAL {final}%")
                    else:
                        st.error(f"## ❌ {registro['estado']} - Prueba {porc:.1f}% | IA {a['porcentaje']}% | FINAL {final}%")
                    reporte = f"HIREREADY-IA REPORTE\\nFecha: {registro['fecha']}\\nNombre: {registro['nombre']}\\nCedula: {registro['cedula']}\\nCargo: {registro['cargo']}\\nIA Compat: {a['porcentaje']}% - {a['concepto']}\\nPrueba: {aciertos}/{len(preguntas)}={porc:.1f}%\\nFinal: {final}%\\nEstado: {registro['estado']}\\nRec: {rec} {rec_porc}%\\n"
                    st.download_button("📄 Descargar Reporte HIREREADY-IA", reporte, file_name=f"Reporte_HIREREADY_{st.session_state.cedula_real}.txt")
                    if st.button("Nueva evaluación"):
                        for k in ["inicio_test","cedula","nombre","cargo_sel","sede","analisis_ia","cedula_real"]:
                            st.session_state.pop(k,None)
                        st.rerun()
    with tab2:
        st.header("Acceso RRHH - HIREREADY-IA")
        u=st.text_input("Usuario RRHH")
        p=st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            users=cargar_json(USUARIOS_FILE)
            found=next((x for x in users if x["usuario"]==u and x["clave"]==p),None)
            if found:
                st.session_state.auth=True
                st.session_state.user=found
                st.rerun()
            else:
                st.error("Usuario o clave incorrecta")
else:
    st.sidebar.markdown('<div class="brand" style="color:white;">HIRE<span style="color:#7AC143;">READY</span>-IA</div>', unsafe_allow_html=True)
    st.sidebar.success(f"Conectado: {st.session_state.user['nombre']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.auth=False
        st.session_state.user=None
        st.rerun()
    menu = st.sidebar.selectbox("Menú", ["Dashboard Resultados", "Crear Cargos", "Gestionar Preguntas por Cargo", "Gestionar Excel y Psicotécnica", "Crear Usuarios RRHH", "Config IA / HV"])
    if menu=="Dashboard Resultados":
        st.header("📊 Dashboard HIREREADY-IA")
        regs=cargar_json(REGISTROS_FILE)
        if not regs:
            st.info("Sin registros")
        else:
            df=pd.DataFrame(regs)
            c1,c2,c3,c4,c5=st.columns(5)
            c1.metric("Total", len(df))
            c2.metric("APTO", len(df[df["estado"]=="APTO"]))
            c3.metric("NO APTO", len(df[df["estado"]=="NO APTO"]))
            c4.metric("% Aprob", f"{len(df[df['estado']=='APTO'])/len(df)*100:.1f}%")
            c5.metric("Prom Final IA", f"{df['puntaje_final'].mean():.1f}%" if 'puntaje_final' in df else "N/A")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Descargar CSV", df.to_csv(index=False).encode(), "hireready_ia.csv")
            if st.button("🗑️ Borrar registros"):
                guardar_json(REGISTROS_FILE, [])
                st.success("Borrados"); st.rerun()
    elif menu=="Crear Cargos":
        st.header("🏷️ Crear / Eliminar Cargos")
        cargos=cargar_json(CARGOS_FILE)
        st.write(cargos)
        nuevo=st.text_input("Nuevo cargo")
        if st.button("Crear cargo"):
            if nuevo and nuevo not in cargos:
                cargos.append(nuevo)
                guardar_json(CARGOS_FILE,cargos)
                banco=cargar_json(PREGUNTAS_FILE)
                banco[nuevo]=[]
                guardar_json(PREGUNTAS_FILE,banco)
                st.success("Creado"); st.rerun()
        eliminar=st.selectbox("Eliminar cargo", cargos)
        if st.button("Eliminar"):
            cargos=[c for c in cargos if c!=eliminar]
            guardar_json(CARGOS_FILE,cargos)
            banco=cargar_json(PREGUNTAS_FILE)
            banco.pop(eliminar,None)
            guardar_json(PREGUNTAS_FILE,banco)
            st.success("Eliminado"); st.rerun()
    elif menu=="Gestionar Preguntas por Cargo":
        st.header("📚 Preguntas por Cargo")
        cargos=cargar_json(CARGOS_FILE)
        banco=cargar_json(PREGUNTAS_FILE)
        cargo_sel=st.selectbox("Cargo", cargos)
        preguntas_actuales=banco.get(cargo_sel,[])
        st.subheader(f"{cargo_sel}: {len(preguntas_actuales)} preguntas")
        for idx, preg in enumerate(preguntas_actuales):
            with st.expander(f"{idx+1}. {preg['q'][:60]}..."):
                nuevo_q=st.text_input("Pregunta", value=preg['q'], key=f"qedit_{cargo_sel}_{idx}")
                op1=st.text_input("Op A", value=preg['op'][0], key=f"op1_{cargo_sel}_{idx}")
                op2=st.text_input("Op B", value=preg['op'][1], key=f"op2_{cargo_sel}_{idx}")
                op3=st.text_input("Op C", value=preg['op'][2], key=f"op3_{cargo_sel}_{idx}")
                correcta=st.selectbox("Correcta", ["A","B","C"], index=preg['r'], key=f"r_{cargo_sel}_{idx}")
                if st.button(f"Guardar P{idx+1}", key=f"save_{cargo_sel}_{idx}"):
                    banco[cargo_sel][idx]={"q":nuevo_q,"op":[op1,op2,op3],"r":["A","B","C"].index(correcta)}
                    guardar_json(PREGUNTAS_FILE,banco)
                    st.success("Guardado"); st.rerun()
                if st.button(f"Eliminar", key=f"del_{cargo_sel}_{idx}"):
                    banco[cargo_sel].pop(idx)
                    guardar_json(PREGUNTAS_FILE,banco)
                    st.success("Eliminada"); st.rerun()
        st.divider()
        with st.form(f"form_{cargo_sel}"):
            nq=st.text_area("Nueva pregunta")
            nop1=st.text_input("Opción A")
            nop2=st.text_input("Opción B")
            nop3=st.text_input("Opción C")
            ncorrecta=st.selectbox("Correcta", ["A","B","C"])
            if st.form_submit_button("Agregar"):
                if nq and nop1 and nop2:
                    banco[cargo_sel].append({"q":nq,"op":[nop1,nop2,nop3],"r":["A","B","C"].index(ncorrecta)})
                    guardar_json(PREGUNTAS_FILE,banco)
                    st.success("Agregada"); st.rerun()
    elif menu=="Gestionar Excel y Psicotécnica":
        st.header("🧠 Excel y Psicotécnica")
        config=cargar_json(CONFIG_FILE)
        tab1, tab2 = st.tabs(["Excel","Psico"])
        with tab1:
            for idx, preg in enumerate(config.get("excel",[])):
                with st.expander(f"Excel {idx+1}"):
                    nq=st.text_input("Pregunta", value=preg['q'], key=f"exq_{idx}")
                    o1=st.text_input("A", value=preg['op'][0], key=f"exo1_{idx}")
                    o2=st.text_input("B", value=preg['op'][1], key=f"exo2_{idx}")
                    o3=st.text_input("C", value=preg['op'][2], key=f"exo3_{idx}")
                    rc=st.selectbox("Correcta", ["A","B","C"], index=preg['r'], key=f"exr_{idx}")
                    if st.button(f"Guardar Excel {idx+1}", key=f"exsave_{idx}"):
                        config["excel"][idx]={"q":nq,"op":[o1,o2,o3],"r":["A","B","C"].index(rc)}
                        guardar_json(CONFIG_FILE,config)
                        st.success("Guardado"); st.rerun()
        with tab2:
            for idx, preg in enumerate(config.get("psico",[])):
                with st.expander(f"Psico {idx+1}"):
                    nq=st.text_input("Pregunta", value=preg['q'], key=f"psiq_{idx}")
                    o1=st.text_input("A", value=preg['op'][0], key=f"psio1_{idx}")
                    o2=st.text_input("B", value=preg['op'][1], key=f"psio2_{idx}")
                    o3=st.text_input("C", value=preg['op'][2], key=f"psio3_{idx}")
                    rc=st.selectbox("Correcta", ["A","B","C"], index=preg['r'], key=f"psir_{idx}")
                    if st.button(f"Guardar Psico {idx+1}", key=f"psisave_{idx}"):
                        config["psico"][idx]={"q":nq,"op":[o1,o2,o3],"r":["A","B","C"].index(rc)}
                        guardar_json(CONFIG_FILE,config)
                        st.success("Guardado"); st.rerun()
    elif menu=="Crear Usuarios RRHH":
        st.header("👥 Usuarios RRHH")
        users=cargar_json(USUARIOS_FILE)
        st.dataframe(pd.DataFrame(users))
        nu=st.text_input("Email usuario")
        nn=st.text_input("Nombre")
        nc=st.text_input("Clave", type="password")
        nr=st.selectbox("Rol", ["RRHH","Coordinador RRHH","Gerencia RRHH"])
        if st.button("Crear usuario"):
            if nu and nc and nn:
                users.append({"usuario":nu,"clave":nc,"rol":nr,"nombre":nn})
                guardar_json(USUARIOS_FILE,users)
                st.success("Creado"); st.rerun()
    elif menu=="Config IA / HV":
        st.header("🤖 Configuración HIREREADY-IA")
        config=cargar_json(CONFIG_FILE)
        st.subheader("📎 Hoja de Vida - ¿Obligatoria u Opcional?")
        requiere = st.checkbox("Hacer HOJA DE VIDA obligatoria para todos los aspirantes", value=config.get("requiere_hv", False))
        st.caption("Si está desactivado, el aspirante puede saltarse la HV y hacer solo la prueba. Si está activado, no puede continuar sin subir PDF.")
        if st.button("💾 Guardar configuración HV"):
            config["requiere_hv"] = requiere
            guardar_json(CONFIG_FILE, config)
            st.success(f"✅ Guardado: HV ahora es {'OBLIGATORIA' if requiere else 'OPCIONAL'}")
            st.rerun()
        st.divider()
        st.subheader("🧠 Keywords IA por cargo (para análisis)")
        st.json(KEYWORDS_POR_CARGO)
