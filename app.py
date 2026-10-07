import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import re

st.set_page_config(page_title="FARMART V4 IA", page_icon="💊", layout="wide")

st.markdown("""
<style>
   .stApp { background-color: #f8fafc; }
    h1, h2, h3 { color: #0B4DA2!important; }
   .stButton>button { background-color: #0B4DA2; color: white; border-radius: 8px; font-weight: bold; }
   .stButton>button:hover { background-color: #7AC143; color: white; }
    [data-testid="stSidebar"] { background-color: #0B4DA2; }
    [data-testid="stSidebar"] * { color: white!important; }
   .ia-box { background: linear-gradient(135deg, #0B4DA2 0%, #7AC143 100%); color: white; padding: 20px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

USUARIOS_FILE = "usuarios_admin.json"
REGISTROS_FILE = "registros_farmart.json"
CARGOS_FILE = "cargos.json"
PREGUNTAS_FILE = "preguntas_banco.json"
CONFIG_FILE = "config_excel.json"

if not os.path.exists(USUARIOS_FILE):
    with open(USUARIOS_FILE, "w") as f:
        json.dump([{"usuario":"admin@farmart.system","clave":"Farmart2026*","rol":"Super Admin","nombre":"Admin Principal"}], f)
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
        {"q":"Cabina flujo laminar ¿para qué?","op":["Proteger producto, personal y ambiente","Solo enfriar","Solo iluminar"],"r":0},
    ],
    "Abogados": [
        {"q":"Tutela: ¿Término para fallar?","op":["10 días","30 días","6 meses"],"r":0},
        {"q":"CASO oncológico vital ¿qué argumenta?","op":["Derecho a vida, salud y mínimo vital","Solo trabajo","Solo petición"],"r":0},
        {"q":"Ley 80 principio clave?","op":["Transparencia, economía, responsabilidad","Rapidez","Menor precio"],"r":0},
    ]
}

EXCEL_DEFAULT = [
    {"q":"Excel: ¿Fórmula para sumar?","op":["=SUMA(A1:A10)","SUMAR A1","=ADD()"],"r":0},
    {"q":"¿Qué hace BUSCARV?","op":["Busca dato en tabla","Borra valores","Crea gráfico"],"r":0},
    {"q":"Tabla dinámica sirve para:","op":["Resumir grandes datos rápido","Escribir cartas","Navegar internet"],"r":0},
]
PSICO_DEFAULT = [
    {"q":"Si compañero toma medicamento sin fórmula, ¿qué haces?","op":["Reportas por seguridad del paciente","Te callas","Lo ayudas a vender"],"r":0},
    {"q":"Bajo estrés, tú:","op":["Priorizas, pides ayuda, mantienes calidad","Gritas y dejas todo","Haces todo rápido sin verificar"],"r":0},
    {"q":"Jefe pide entregar vencido, ¿qué haces?","op":["Te niegas y reportas, ética primero","Lo entregas","Cambias fecha"],"r":0},
    {"q":"¿Cómo manejas error propio?","op":["Lo admites, corriges y reportas","Lo ocultas","Culpas a otro"],"r":0},
]

KEYWORDS_POR_CARGO = {
    "Personal de Nómina": ["nomina","pila","seguridad social","retencion","prestaciones","cesantias","liquidacion","parafiscales","excel","siigo","world office"],
    "Tesorería": ["tesoreria","flujo de caja","conciliacion","bancos","egreso","arqueo","cuentas por pagar","excel","siigo"],
    "Quimico farmaceutico": ["quimico farmaceutico","central de mezclas","unidosis","oncologico","citotoxico","NPT","asepsia","BPM","INVIMA","flujo laminar"],
    "Auxiliar de farmacia": ["dispensacion","farmacia","invima","medicamentos","lote","vencimiento","formula"],
    "Abogados": ["tutela","derecho de peticion","contratacion estatal","ley 80","laboral","penal","civil","comercial"],
    "Ingeniero de sistemas": ["sistemas","python","base de datos","ciberseguridad","redes","soporte","tic"],
    "Contadores público": ["contador","contabilidad","dian","facturacion electronica","retencion","iva","estados financieros"],
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
        json.dump({"sin_excel": ["Mensajero de moto","Conductor de carro","Auxiliares de servicios generales","Auxiliar de bodega de carga"],"excel": EXCEL_DEFAULT,"psico": PSICO_DEFAULT}, f, indent=2, ensure_ascii=False)

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
    if cargo not in config["sin_excel"]:
        base = base + config["excel"]
    base = base + config["psico"]
    return base, len(banco.get(cargo,[])), len(config["excel"]), len(config["psico"])

def analizar_hv_ia(texto_hv, cargo):
    texto = texto_hv.lower()
    keywords = KEYWORDS_POR_CARGO.get(cargo, KEYWORDS_POR_CARGO.get("Auxiliar de farmacia", []))
    encontrados = [k for k in keywords if k.lower() in texto]
    porcentaje = int((len(encontrados)/len(keywords)*100) if keywords else 50)
    porcentaje = min(95, max(15, porcentaje))
    anios = re.findall(r"(\d+)\s*a\w*\s*de experiencia|experiencia\s*(\d+)", texto)
    exp = "No especificada"
    if anios:
        try:
            exp = f"{anios[0][0] or anios[0][1]} años aprox detectados"
        except:
            exp = "Detectada experiencia"
    fortalezas = ", ".join(encontrados[:5]) if encontrados else "Perfil general, requiere validar"
    faltantes = [k for k in keywords if k.lower() not in texto][:3]
    if porcentaje >= 80:
        concepto = "PERFIL ALTAMENTE COMPATIBLE"
        rec = "AVANZA A ENTREVISTA - Cumple palabras clave del cargo"
    elif porcentaje >= 50:
        concepto = "PERFIL MEDIANAMENTE COMPATIBLE"
        rec = "ENTREVISTA CON VALIDACION - Reforzar en: " + ", ".join(faltantes)
    else:
        concepto = "PERFIL BAJO - REQUIERE CAPACITACION"
        rec = "NO RECOMENDADO o con periodo de prueba - Faltan: " + ", ".join(faltantes)
    preguntas_ia = [
        f"Cuéntame tu experiencia en {keywords[0] if keywords else cargo}",
        f"¿Qué harías en un caso de {faltantes[0] if faltantes else 'emergencia'} en Farmart?",
        "¿Por qué duraste poco en tu último empleo? (si aplica)",
        "¿Manejas Excel avanzado y qué funciones?"
    ]
    return {
        "porcentaje": porcentaje,
        "concepto": concepto,
        "exp": exp,
        "fortalezas": fortalezas,
        "faltantes": ", ".join(faltantes) if faltantes else "Ninguno crítico",
        "rec": rec,
        "preguntas_ia": preguntas_ia,
        "encontrados": encontrados
    }

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
            reader = PyPDF2.PdfReader(file)
            for p in reader.pages:
                texto += p.extract_text() or ""
        except:
            texto = file.read().decode(errors="ignore") if hasattr(file, "read") else ""
    return texto[:15000]

if "auth" not in st.session_state:
    st.session_state.auth=False
    st.session_state.user=None

st.title("💊 FARMART V4 - Sistema con IA + Hoja de Vida")
st.caption("Cargos editables + Preguntas editables + Análisis de HV con IA")

if not st.session_state.auth:
    tab1, tab2 = st.tabs(["📝 Prueba Empleado + Subir HV", "🔐 RRHH / Admin"])
    with tab1:
        st.markdown('<div class="ia-box">🤖 NUEVO: Sube tu hoja de vida en PDF y la IA la analiza automáticamente para el cargo</div>', unsafe_allow_html=True)
        cedula = st.text_input("Cédula *")
        nombre = st.text_input("Nombre completo *")
        cargos_list = cargar_json(CARGOS_FILE)
        cargo = st.selectbox("Cargo al que aspira *", cargos_list)
        sede = st.text_input("Ciudad / Sede")
        archivo_hv = st.file_uploader("📎 ANEXAR HOJA DE VIDA (PDF) - Obligatorio para análisis IA", type=["pdf"])
        if "inicio_test" not in st.session_state:
            st.session_state.inicio_test=False
            st.session_state.analisis_ia=None
        if st.button("1️⃣ Analizar Hoja de Vida con IA", type="primary"):
            if not archivo_hv:
                st.error("Primero sube tu hoja de vida en PDF")
            elif cedula and nombre:
                with st.spinner("🤖 IA analizando hoja de vida..."):
                    texto_hv = leer_pdf(archivo_hv)
                    if len(texto_hv) < 30:
                        st.error("No pude leer el PDF, intenta con otro PDF con texto seleccionable")
                    else:
                        analisis = analizar_hv_ia(texto_hv, cargo)
                        st.session_state.analisis_ia = analisis
                        st.session_state.texto_hv = texto_hv[:2000]
                        st.session_state.cedula=cargo and cedula
                        st.session_state.nombre=nombre
                        st.session_state.cargo_sel=cargo
                        st.session_state.sede=sede
                        st.session_state.cedula_real=cedula
                        st.success("✅ Análisis IA completado")
                        st.rerun()
            else:
                st.error("Cédula y nombre obligatorios")
        if st.session_state.get("analisis_ia"):
            a = st.session_state.analisis_ia
            st.divider()
            st.subheader("🤖 Resultado Análisis IA de Hoja de Vida")
            c1,c2,c3=st.columns(3)
            c1.metric("Compatibilidad IA", f"{a['porcentaje']}%")
            c2.metric("Concepto", a["concepto"][:20])
            c3.metric("Experiencia", a["exp"])
            st.write(f"**Fortalezas detectadas:** {a['fortalezas']}")
            st.write(f"**Faltantes / Brechas:** {a['faltantes']}")
            st.info(f"**Recomendación IA:** {a['rec']}")
            st.write("**Preguntas sugeridas por IA para entrevista presencial:**")
            for i, pq in enumerate(a["preguntas_ia"],1):
                st.write(f"{i}. {pq}")
            if st.button("2️⃣ Continuar a Prueba Técnica (20 preguntas)"):
                st.session_state.inicio_test=True
                st.rerun()
        if st.session_state.inicio_test:
            preguntas, n_tec, n_exc, n_psi = get_preguntas_cargo(st.session_state.cargo_sel)
            st.divider()
            st.subheader(f"Evaluación Técnica: {st.session_state.cargo_sel}")
            st.info(f"Total: {len(preguntas)} preguntas | Técnicas: {n_tec} | Excel: {n_exc if st.session_state.cargo_sel not in cargar_json(CONFIG_FILE)['sin_excel'] else 0} | Psicotécnica: {n_psi} | Mínimo 90% para APTO")
            respuestas=[]
            for i,p in enumerate(preguntas):
                r = st.radio(f"{i+1}. {p['q']}", p["op"], key=f"pq{i}", index=None)
                if r is not None:
                    respuestas.append(p["op"].index(r)==p["r"])
            if st.button("FINALIZAR TODO Y GENERAR REPORTE FINAL CON IA", type="primary"):
                if len(respuestas) < len(preguntas):
                    st.warning(f"Faltan {len(preguntas)-len(respuestas)} por responder")
                else:
                    aciertos=sum(respuestas)
                    porc=aciertos/len(preguntas)*100
                    apto=porc>=90
                    aciertos_psico=sum(respuestas[-n_psi:])
                    a = st.session_state.get("analisis_ia", {"porcentaje":0,"concepto":"Sin HV","fortalezas":"N/A","faltantes":"N/A","rec":"Sin análisis HV","exp":"N/A","preguntas_ia":[]})
                    final = int((a["porcentaje"]*0.4 + porc*0.6))
                    if aciertos_psico>=7 and apto and final>=80:
                        rec="ALTA RECOMENDACIÓN - Contratar"
                        rec_porc=95
                    elif final>=60 and porc>=70:
                        rec="RECOMENDADO CON PERIODO PRUEBA Y CAPACITACION"
                        rec_porc=75
                    else:
                        rec="NO RECOMENDADO"
                        rec_porc=35
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
                    if apto and final>=70:
                        st.balloons()
                        st.success(f"## ✅ {registro['estado']} - Prueba {porc:.1f}% | IA {a['porcentaje']}% | FINAL {final}%")
                    else:
                        st.error(f"## ❌ {registro['estado']} - Prueba {porc:.1f}% | IA {a['porcentaje']}% | FINAL {final}%")
                    reporte = f"""FARMART - REPORTE INTEGRAL CON IA
Fecha: {registro['fecha']}
Nombre: {registro['nombre']}
Cédula: {registro['cedula']}
Cargo: {registro['cargo']}
--- ANALISIS IA HV ---
Compatibilidad IA: {a['porcentaje']}%
Concepto IA: {a['concepto']}
Experiencia: {a['exp']}
Fortalezas: {a['fortalezas']}
Brechas: {a['faltantes']}
--- PRUEBA TECNICA ---
Aciertos: {aciertos}/{len(preguntas)} = {porc:.1f}%
Estado: {registro['estado']}
--- FINAL ---
Puntaje Final (40% HV + 60% Prueba): {final}%
Recomendación: {rec} - {rec_porc}%
"""
                    st.download_button("📄 Descargar Reporte Final IA + Prueba", reporte, file_name=f"Reporte_IA_{st.session_state.cedula_real}.txt")
                    if st.button("Nueva evaluación"):
                        for k in ["inicio_test","cedula","nombre","cargo_sel","sede","analisis_ia","texto_hv","cedula_real"]:
                            st.session_state.pop(k,None)
                        st.rerun()
    with tab2:
        st.header("Acceso RRHH")
        u=st.text_input("Usuario RRHH")
        p=st.text_input("Contraseña", type="password")
        if st.button("Entrar como Admin"):
            users=cargar_json(USUARIOS_FILE)
            found=next((x for x in users if x["usuario"]==u and x["clave"]==p),None)
            if found:
                st.session_state.auth=True
                st.session_state.user=found
                st.rerun()
            else:
                st.error("Usuario o clave incorrecta")
else:
    st.sidebar.success(f"Conectado: {st.session_state.user['nombre']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.auth=False
        st.session_state.user=None
        st.rerun()
    menu = st.sidebar.selectbox("Menú Admin", ["Dashboard Resultados", "Crear Cargos", "Gestionar Preguntas por Cargo", "Gestionar Excel y Psicotécnica", "Crear Usuarios RRHH", "Config IA"])
    if menu=="Dashboard Resultados":
        st.header("📊 Dashboard con IA")
        regs=cargar_json(REGISTROS_FILE)
        if not regs:
            st.info("Sin registros aún")
        else:
            df=pd.DataFrame(regs)
            c1,c2,c3,c4,c5=st.columns(5)
            c1.metric("Total", len(df))
            c2.metric("APTO", len(df[df["estado"]=="APTO"]))
            c3.metric("NO APTO", len(df[df["estado"]=="NO APTO"]))
            c4.metric("% Aprob", f"{len(df[df['estado']=='APTO'])/len(df)*100:.1f}%")
            c5.metric("Prom Final IA", f"{df['puntaje_final'].mean():.1f}%" if 'puntaje_final' in df else "N/A")
            f_cargo=st.multiselect("Filtrar cargo", cargar_json(CARGOS_FILE))
            if f_cargo:
                df=df[df["cargo"].isin(f_cargo)]
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Descargar CSV Completo IA", df.to_csv(index=False).encode(), "farmart_v4_ia.csv")
            if st.button("🗑️ Borrar todos los registros"):
                guardar_json(REGISTROS_FILE, [])
                st.success("Borrados"); st.rerun()
    elif menu=="Crear Cargos":
        st.header("🏷️ Crear / Eliminar Cargos")
        cargos=cargar_json(CARGOS_FILE)
        st.write("Cargos actuales:", cargos)
        st.divider()
        nuevo=st.text_input("Nuevo cargo")
        if st.button("Crear cargo"):
            if nuevo and nuevo not in cargos:
                cargos.append(nuevo)
                guardar_json(CARGOS_FILE,cargos)
                banco=cargar_json(PREGUNTAS_FILE)
                banco[nuevo]=[]
                guardar_json(PREGUNTAS_FILE,banco)
                st.success(f"Cargo {nuevo} creado"); st.rerun()
            else:
                st.error("Ya existe o vacío")
        eliminar=st.selectbox("Eliminar cargo", cargos)
        if st.button("Eliminar cargo seleccionado"):
            cargos=[c for c in cargos if c!=eliminar]
            guardar_json(CARGOS_FILE,cargos)
            banco=cargar_json(PREGUNTAS_FILE)
            banco.pop(eliminar,None)
            guardar_json(PREGUNTAS_FILE,banco)
            st.success("Eliminado"); st.rerun()
    elif menu=="Gestionar Preguntas por Cargo":
        st.header("📚 Gestionar Preguntas por Cargo")
        cargos=cargar_json(CARGOS_FILE)
        banco=cargar_json(PREGUNTAS_FILE)
        cargo_sel=st.selectbox("Selecciona cargo", cargos)
        preguntas_actuales=banco.get(cargo_sel,[])
        st.subheader(f"Preguntas de {cargo_sel}: {len(preguntas_actuales)}")
        for idx, preg in enumerate(preguntas_actuales):
            with st.expander(f"{idx+1}. {preg['q'][:60]}..."):
                nuevo_q=st.text_input("Pregunta", value=preg['q'], key=f"qedit_{cargo_sel}_{idx}")
                op1=st.text_input("Op A", value=preg['op'][0], key=f"op1_{cargo_sel}_{idx}")
                op2=st.text_input("Op B", value=preg['op'][1], key=f"op2_{cargo_sel}_{idx}")
                op3=st.text_input("Op C", value=preg['op'][2], key=f"op3_{cargo_sel}_{idx}")
                correcta=st.selectbox("Correcta", ["A","B","C"], index=preg['r'], key=f"r_{cargo_sel}_{idx}")
                col1,col2=st.columns(2)
                if col1.button(f"Guardar P{idx+1}", key=f"save_{cargo_sel}_{idx}"):
                    banco[cargo_sel][idx]={"q":nuevo_q,"op":[op1,op2,op3],"r":["A","B","C"].index(correcta)}
                    guardar_json(PREGUNTAS_FILE,banco)
                    st.success("Guardado"); st.rerun()
                if col2.button(f"Eliminar", key=f"del_{cargo_sel}_{idx}"):
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
            if st.form_submit_button("Agregar pregunta"):
                if nq and nop1 and nop2:
                    banco[cargo_sel].append({"q":nq,"op":[nop1,nop2,nop3],"r":["A","B","C"].index(ncorrecta)})
                    guardar_json(PREGUNTAS_FILE,banco)
                    st.success("Agregada"); st.rerun()
    elif menu=="Gestionar Excel y Psicotécnica":
        st.header("🧠 Excel y Psicotécnica")
        config=cargar_json(CONFIG_FILE)
        tab_excel, tab_psico = st.tabs(["Excel", "Psicotécnica"])
        with tab_excel:
            for idx, preg in enumerate(config["excel"]):
                with st.expander(f"Excel {idx+1}. {preg['q'][:50]}"):
                    nq=st.text_input("Pregunta", value=preg['q'], key=f"exq_{idx}")
                    o1=st.text_input("Op A", value=preg['op'][0], key=f"exo1_{idx}")
                    o2=st.text_input("Op B", value=preg['op'][1], key=f"exo2_{idx}")
                    o3=st.text_input("Op C", value=preg['op'][2], key=f"exo3_{idx}")
                    rc=st.selectbox("Correcta", ["A","B","C"], index=preg['r'], key=f"exr_{idx}")
                    if st.button(f"Guardar Excel {idx+1}", key=f"exsave_{idx}"):
                        config["excel"][idx]={"q":nq,"op":[o1,o2,o3],"r":["A","B","C"].index(rc)}
                        guardar_json(CONFIG_FILE,config)
                        st.success("Guardado"); st.rerun()
        with tab_psico:
            for idx, preg in enumerate(config["psico"]):
                with st.expander(f"Psico {idx+1}. {preg['q'][:50]}"):
                    nq=st.text_input("Pregunta", value=preg['q'], key=f"psiq_{idx}")
                    o1=st.text_input("Op A", value=preg['op'][0], key=f"psio1_{idx}")
                    o2=st.text_input("Op B", value=preg['op'][1], key=f"psio2_{idx}")
                    o3=st.text_input("Op C", value=preg['op'][2], key=f"psio3_{idx}")
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
                st.success(f"Usuario {nu} creado"); st.rerun()
    elif menu=="Config IA":
        st.header("🤖 Configuración IA")
        st.info("IA Local actual: Analiza palabras clave por cargo. Keywords editables:")
        st.json(KEYWORDS_POR_CARGO)
        st.write("Para IA avanzada con ChatGPT, agrega tu API KEY en Secrets de Streamlit como OPENAI_API_KEY")
