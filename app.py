import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

st.set_page_config(page_title="FARMART SYSTEM V3.1", page_icon="💊", layout="wide")

st.markdown("""
<style>
   .stApp { background-color: #f8fafc; }
    h1, h2, h3 { color: #0B4DA2!important; }
   .stButton>button { background-color: #0B4DA2; color: white; border-radius: 8px; font-weight: bold; }
   .stButton>button:hover { background-color: #7AC143; color: white; }
    [data-testid="stSidebar"] { background-color: #0B4DA2; }
    [data-testid="stSidebar"] * { color: white!important; }
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
        {"q":"¿Qué es una novedad de nómina?","op":["Incapacidad, vacaciones, horas extra que afectan pago","Solo cambio de cargo","Solo aumento"],"r":0},
        {"q":"¿Qué es retención en la fuente por salarios?","op":["Descuento por impuestos según tabla DIAN","Descuento por préstamo","Descuento por ARL"],"r":0},
        {"q":"Auxilio de transporte ¿cuándo se paga?","op":["Si gana hasta 2 SMMLV","A todos sin importar salario","Nunca se paga"],"r":0},
        {"q":"¿Qué es PILA?","op":["Planilla para pago seguridad social","Planilla de inventario","Planilla de aseo"],"r":0},
        {"q":"¿Qué es liquidación de prestaciones?","op":["Cesantías, intereses, prima, vacaciones al finalizar contrato","Solo salario","Solo prima"],"r":0},
    ],
    "Tesorería": [
        {"q":"¿Qué es flujo de caja?","op":["Entrada y salida de dinero en un periodo","Solo entradas","Solo inventario"],"r":0},
        {"q":"¿Qué es conciliación bancaria?","op":["Comparar libros contables con extracto bancario","Contar caja menor","Hacer nómina"],"r":0},
        {"q":"¿Qué es comprobante de egreso?","op":["Documento que soporta salida de dinero","Documento de entrada","Factura de venta"],"r":0},
        {"q":"Cuentas por pagar son:","op":["Obligaciones con proveedores","Dinero que nos deben","Caja menor"],"r":0},
        {"q":"¿Qué es cierre de caja diario?","op":["Cuadre de ingresos y egresos del día","Cerrar la puerta","Apagar computador"],"r":0},
        {"q":"¿Qué es arqueo de caja?","op":["Verificación física del efectivo vs sistema","Inventario de medicamentos","Revisión de tutelas"],"r":0},
    ],
    "Auxiliar de bodega de carga": [
        {"q":"¿Qué significa FEFO?","op":["First Expire First Out","First Entry First Out","Fast Expire"],"r":0},
        {"q":"¿Temperatura cadena de frio?","op":["2-8°C","15-25°C","-20°C"],"r":0},
        {"q":"¿Qué es un Lote?","op":["Conjunto con misma fabricación","Número de estante","Código cliente"],"r":0},
        {"q":"Medicamento vencido ¿qué hace?","op":["Separa, identifica y reporta","Lo devuelve al estante","Lo bota a la basura común"],"r":0},
        {"q":"¿Qué es BPM?","op":["Buenas Prácticas de Almacenamiento","Buen Proceso Manual","Bodega de Producto Médico"],"r":0},
    ],
    "Quimico farmaceutico": [
        {"q":"Central de mezclas: ¿Qué es NPT?","op":["Nutrición Parenteral Total","Norma de Preparación Técnica","Nivel de Producción Total"],"r":0},
        {"q":"Unidosis: ¿Objetivo principal?","op":["Dosis exacta por paciente, reduce errores","Ahorrar empaques","Vender más"],"r":0},
        {"q":"Oncológico: ¿Qué es citotóxico?","op":["Medicamento que destruye células, manejo especial","Medicamento para dolor","Antibiótico"],"r":0},
        {"q":"Cabina de flujo laminar en oncología ¿para qué?","op":["Proteger producto, personal y ambiente","Solo enfriar","Solo iluminar"],"r":0},
        {"q":"Estabilidad de mezcla oncológica depende de:","op":["Tiempo, temperatura, luz, concentración","Solo color","Solo laboratorio fabricante"],"r":0},
    ],
    "Abogados": [
        {"q":"Tutela: ¿Término para fallar primera instancia?","op":["10 días","30 días","6 meses"],"r":0},
        {"q":"CASO: Usuario tutela por no entrega de oncológico vital. ¿Qué argumenta?","op":["Derecho a vida, salud y mínimo vital, medida provisional","Solo derecho al trabajo","Solo derecho a petición"],"r":0},
        {"q":"Contratación estatal: Ley 80 ¿principio clave?","op":["Transparencia, economía, responsabilidad","Rapidez","Solo menor precio"],"r":0},
        {"q":"Derecho de petición ¿término general?","op":["15 días hábiles","1 año","3 días"],"r":0},
    ]
}EXCEL_DEFAULT = [
    {"q":"Excel: ¿Fórmula para sumar?","op":["=SUMA(A1:A10)","SUMAR A1","=ADD()"],"r":0},
    {"q":"¿Qué hace BUSCARV?","op":["Busca un dato en tabla","Borra valores","Crea gráfico"],"r":0},
    {"q":"Tabla dinámica sirve para:","op":["Resumir grandes datos rápido","Escribir cartas","Navegar internet"],"r":0},
    {"q":"¿Cómo filtrar en Excel?","op":["Datos > Filtro","Borrar columnas","Pegar especial"],"r":0},
]

PSICO_DEFAULT = [
    {"q":"Si un compañero toma medicamento sin fórmula, ¿qué haces?","op":["Reportas por seguridad del paciente","Te callas","Lo ayudas a vender"],"r":0},
    {"q":"Bajo estrés y mucho trabajo, tú:","op":["Priorizas, pides ayuda, mantienes calidad","Gritas y dejas todo","Haces todo rápido sin verificar"],"r":0},
    {"q":"Un jefe te pide entregar pedido vencido, ¿qué haces?","op":["Te niegas y reportas, ética primero","Lo entregas","Lo cambias de fecha"],"r":0},
    {"q":"¿Cómo manejas un error propio?","op":["Lo admites, corriges y reportas","Lo ocultas","Culpas a otro"],"r":0},
    {"q":"Trabajo en equipo es:","op":["Apoyar, comunicar y respetar","Hacer solo mi parte","Competir contra todos"],"r":0},
]

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
        json.dump({
            "sin_excel": ["Mensajero de moto","Conductor de carro","Auxiliares de servicios generales","Auxiliar de bodega de carga"],
            "excel": EXCEL_DEFAULT,
            "psico": PSICO_DEFAULT
        }, f, indent=2, ensure_ascii=False)

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

if "auth" not in st.session_state:
    st.session_state.auth=False
    st.session_state.user=None

st.title("FARMART - Sistema Integral V3.1")
st.caption("Con Nómina y Tesorería + Gestión total de cargos y preguntas")

if not st.session_state.auth:
    tab1, tab2 = st.tabs(["📝 Prueba Empleado", "🔐 Ingreso RRHH / Admin"])
    with tab1:
        st.header("Registro Aspirante")
        cedula = st.text_input("Cédula *")
        nombre = st.text_input("Nombre completo *")
        cargos_list = cargar_json(CARGOS_FILE)
        cargo = st.selectbox("Cargo al que aspira *", cargos_list)
        sede = st.text_input("Ciudad / Sede")
        if "inicio_test" not in st.session_state:
            st.session_state.inicio_test=False
        if st.button("Iniciar Evaluación", type="primary"):
            if cedula and nombre:
                st.session_state.cedula=cedula
                st.session_state.nombre=nombre
                st.session_state.cargo_sel=cargo
                st.session_state.sede=sede
                st.session_state.inicio_test=True
                st.rerun()
            else:
                st.error("Cédula y nombre obligatorios")
        if st.session_state.inicio_test:
            preguntas, n_tec, n_exc, n_psi = get_preguntas_cargo(st.session_state.cargo_sel)
            st.divider()
            st.subheader(f"Evaluación: {st.session_state.cargo_sel}")
            st.info(f"Total: {len(preguntas)} preguntas | Técnicas: {n_tec} | Excel: {n_exc if st.session_state.cargo_sel not in cargar_json(CONFIG_FILE)['sin_excel'] else 0} | Psicotécnica: {n_psi} | Mínimo 90% para APTO")
            respuestas=[]
            for i,p in enumerate(preguntas):
                r = st.radio(f"{i+1}. {p['q']}", p["op"], key=f"pq{i}", index=None)
                if r is not None:
                    respuestas.append(p["op"].index(r)==p["r"])
            if st.button("FINALIZAR Y GENERAR REPORTE", type="primary"):
                if len(respuestas) < len(preguntas):
                    st.warning(f"Faltan {len(preguntas)-len(respuestas)} por responder")
                else:
                    aciertos=sum(respuestas)
                    porc=aciertos/len(preguntas)*100
                    apto=porc>=90
                    aciertos_psico=sum(respuestas[-n_psi:])
                    if aciertos_psico>=7 and apto:
                        rec="ALTA RECOMENDACIÓN - Perfil ético y técnico excelente"
                        rec_porc=95
                    elif aciertos_psico>=5 and porc>=80:
                        rec="RECOMENDADO CON SEGUIMIENTO - Reforzar capacitación"
                        rec_porc=80
                    else:
                        rec="NO RECOMENDADO - Riesgo en seguridad / ética"
                        rec_porc=40
                    registro={
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cedula": st.session_state.cedula,
                        "nombre": st.session_state.nombre,
                        "cargo": st.session_state.cargo_sel,
                        "sede": st.session_state.sede,
                        "aciertos": aciertos,
                        "total": len(preguntas),
                        "porcentaje": round(porc,1),
                        "psicotecnica": f"{aciertos_psico}/{n_psi}",
                        "estado": "APTO" if apto else "NO APTO",
                        "recomendacion": rec,
                        "porc_recomendacion": rec_porc
                    }
                    regs=cargar_json(REGISTROS_FILE)
                    regs.append(registro)
                    guardar_json(REGISTROS_FILE,regs)
                    st.divider()
                    if apto:
                        st.balloons()
                        st.success(f"## ✅ {registro['estado']} - {porc:.1f}%")
                    else:
                        st.error(f"## ❌ {registro['estado']} - {porc:.1f}% (Requiere 90%)")
                    st.write(f"**Psicotécnica:** {aciertos_psico}/{n_psi}")
                    st.write(f"**RRHH:** {rec} - {rec_porc}%")
                    reporte = f"FARMART REPORTE\\nFecha: {registro['fecha']}\\nNombre: {registro['nombre']}\\nCédula: {registro['cedula']}\\nCargo: {registro['cargo']}\\nAciertos: {aciertos}/{len(preguntas)} = {porc:.1f}%\\nEstado: {registro['estado']}\\nPsico: {aciertos_psico}/{n_psi}\\nRecomendación: {rec} {rec_porc}%\\n"
                    st.download_button("📄 Descargar Reporte TXT", reporte, file_name=f"Reporte_{st.session_state.cedula}.txt")
                    if st.button("Nueva evaluación"):
                        for k in ["inicio_test","cedula","nombre","cargo_sel","sede"]:
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
    menu = st.sidebar.selectbox("Menú Admin", ["Dashboard Resultados", "Crear Cargos", "Gestionar Preguntas por Cargo", "Gestionar Excel y Psicotécnica", "Crear Usuarios RRHH"])
    if menu=="Dashboard Resultados":
        st.header("📊 Dashboard")
        regs=cargar_json(REGISTROS_FILE)
        if not regs:
            st.info("Sin registros aún")
        else:
            df=pd.DataFrame(regs)
            c1,c2,c3,c4=st.columns(4)
            c1.metric("Total", len(df))
            c2.metric("APTO", len(df[df["estado"]=="APTO"]))
            c3.metric("NO APTO", len(df[df["estado"]=="NO APTO"]))
            c4.metric("% Aprob", f"{len(df[df['estado']=='APTO'])/len(df)*100:.1f}%")
            f_cargo=st.multiselect("Filtrar cargo", cargar_json(CARGOS_FILE))
            if f_cargo:
                df=df[df["cargo"].isin(f_cargo)]
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Descargar CSV", df.to_csv(index=False).encode(), "farmart.csv")
            if st.button("🗑️ Borrar todos los registros"):
                guardar_json(REGISTROS_FILE, [])
                st.success("Borrados"); st.rerun()
    elif menu=="Crear Cargos":
        st.header("🏷️ Crear / Eliminar Cargos")
        cargos=cargar_json(CARGOS_FILE)
        st.write("Cargos actuales:", cargos)
        st.divider()
        nuevo=st.text_input("Nuevo cargo (ej: Auxiliar de inventario)")
        if st.button("Crear cargo"):
            if nuevo and nuevo not in cargos:
                cargos.append(nuevo)
                guardar_json(CARGOS_FILE,cargos)
                banco=cargar_json(PREGUNTAS_FILE)
                banco[nuevo]=[]
                guardar_json(PREGUNTAS_FILE,banco)
                st.success(f"Cargo {nuevo} creado")
                st.rerun()
            else:
                st.error("Ya existe o vacío")
        st.divider()
        eliminar=st.selectbox("Eliminar cargo", cargos)
        if st.button("Eliminar cargo seleccionado"):
            cargos=[c for c in cargos if c!=eliminar]
            guardar_json(CARGOS_FILE,cargos)
            banco=cargar_json(PREGUNTAS_FILE)
            banco.pop(eliminar,None)
            guardar_json(PREGUNTAS_FILE,banco)
            st.success("Eliminado"); st.rerun()
        st.divider()
        st.subheader("Configurar cargos SIN Excel")
        config=cargar_json(CONFIG_FILE)
        st.write("Actual sin Excel:", config["sin_excel"])
        sin_excel_new=st.multiselect("Selecciona cargos que NO llevan Excel", cargos, default=config["sin_excel"])
        if st.button("Guardar config Excel"):
            config["sin_excel"]=sin_excel_new
            guardar_json(CONFIG_FILE,config)
            st.success("Configuración guardada")
    elif menu=="Gestionar Preguntas por Cargo":
        st.header("📚 Gestionar Preguntas por Cargo")
        cargos=cargar_json(CARGOS_FILE)
        banco=cargar_json(PREGUNTAS_FILE)
        cargo_sel=st.selectbox("Selecciona cargo para editar", cargos)
        preguntas_actuales=banco.get(cargo_sel,[])
        st.subheader(f"Preguntas actuales de {cargo_sel}: {len(preguntas_actuales)}")
        for idx, preg in enumerate(preguntas_actuales):
            with st.expander(f"{idx+1}. {preg['q'][:60]}..."):
                nuevo_q=st.text_input(f"Pregunta {idx+1}", value=preg['q'], key=f"qedit_{cargo_sel}_{idx}")
                op1=st.text_input(f"Opción A", value=preg['op'][0] if len(preg['op'])>0 else "", key=f"op1_{cargo_sel}_{idx}")
                op2=st.text_input(f"Opción B", value=preg['op'][1] if len(preg['op'])>1 else "", key=f"op2_{cargo_sel}_{idx}")
                op3=st.text_input(f"Opción C", value=preg['op'][2] if len(preg['op'])>2 else "", key=f"op3_{cargo_sel}_{idx}")
                correcta=st.selectbox(f"Respuesta correcta", ["A","B","C"], index=preg['r'], key=f"r_{cargo_sel}_{idx}")
                col1,col2=st.columns(2)
                if col1.button(f"Guardar cambios P{idx+1}", key=f"save_{cargo_sel}_{idx}"):
                    banco[cargo_sel][idx]={"q":nuevo_q,"op":[op1,op2,op3],"r":["A","B","C"].index(correcta)}
                    guardar_json(PREGUNTAS_FILE,banco)
                    st.success("Guardado"); st.rerun()
                if col2.button(f"🗑️ Eliminar esta pregunta", key=f"del_{cargo_sel}_{idx}"):
                    banco[cargo_sel].pop(idx)
                    guardar_json(PREGUNTAS_FILE,banco)
                    st.success("Eliminada"); st.rerun()
        st.divider()
        st.subheader(f"➕ Agregar nueva pregunta a {cargo_sel}")
        with st.form(f"form_{cargo_sel}"):
            nq=st.text_area("Nueva pregunta")
            nop1=st.text_input("Opción A (Correcta ideal)")
            nop2=st.text_input("Opción B")
            nop3=st.text_input("Opción C")
            ncorrecta=st.selectbox("¿Cuál es la correcta?", ["A","B","C"])
            submitted=st.form_submit_button("Agregar pregunta")
            if submitted:
                if nq and nop1 and nop2:
                    nueva={"q":nq,"op":[nop1,nop2,nop3],"r":["A","B","C"].index(ncorrecta)}
                    banco[cargo_sel].append(nueva)
                    guardar_json(PREGUNTAS_FILE,banco)
                    st.success(f"Pregunta agregada a {cargo_sel}. Ahora tiene {len(banco[cargo_sel])} preguntas")
                    st.rerun()
                else:
                    st.error("Completa pregunta y al menos 2 opciones")
    elif menu=="Gestionar Excel y Psicotécnica":
        st.header("🧠 Gestionar Preguntas Excel y Psicotécnica")
        config=cargar_json(CONFIG_FILE)
        tab_excel, tab_psico = st.tabs(["Excel", "Psicotécnica"])
        with tab_excel:
            st.subheader(f"Preguntas Excel: {len(config['excel'])}")
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
                    if st.button(f"Eliminar Excel {idx+1}", key=f"exdel_{idx}"):
                        config["excel"].pop(idx)
                        guardar_json(CONFIG_FILE,config)
                        st.success("Eliminado"); st.rerun()
            st.divider()
            st.subheader("Agregar nueva pregunta Excel")
            with st.form("new_excel"):
                q=st.text_area("Pregunta Excel")
                a=st.text_input("Opción A")
                b=st.text_input("Opción B")
                c=st.text_input("Opción C")
                rc=st.selectbox("Correcta", ["A","B","C"])
                if st.form_submit_button("Agregar Excel"):
                    config["excel"].append({"q":q,"op":[a,b,c],"r":["A","B","C"].index(rc)})
                    guardar_json(CONFIG_FILE,config)
                    st.success("Agregada"); st.rerun()
        with tab_psico:
            st.subheader(f"Preguntas Psicotécnicas: {len(config['psico'])}")
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
                    if st.button(f"Eliminar Psico {idx+1}", key=f"psidel_{idx}"):
                        config["psico"].pop(idx)
                        guardar_json(CONFIG_FILE,config)
                        st.success("Eliminado"); st.rerun()
            st.divider()
            st.subheader("Agregar nueva pregunta Psicotécnica")
            with st.form("new_psico"):
                q=st.text_area("Pregunta Psicotécnica")
                a=st.text_input("Opción A")
                b=st.text_input("Opción B")
                c=st.text_input("Opción C")
                rc=st.selectbox("Correcta", ["A","B","C"])
                if st.form_submit_button("Agregar Psicotécnica"):
                    config["psico"].append({"q":q,"op":[a,b,c],"r":["A","B","C"].index(rc)})
                    guardar_json(CONFIG_FILE,config)
                    st.success("Agregada"); st.rerun()
    elif menu=="Crear Usuarios RRHH":
        st.header("👥 Usuarios RRHH")
        users=cargar_json(USUARIOS_FILE)
        st.dataframe(pd.DataFrame(users))
        st.divider()
        st.subheader("Nuevo usuario")
        nu=st.text_input("Email usuario")
        nn=st.text_input("Nombre")
        nc=st.text_input("Clave", type="password")
        nr=st.selectbox("Rol", ["RRHH","Coordinador RRHH","Gerencia RRHH","Auditor"])
        if st.button("Crear usuario"):
            if nu and nc and nn:
                users.append({"usuario":nu,"clave":nc,"rol":nr,"nombre":nn})
                guardar_json(USUARIOS_FILE,users)
                st.success(f"Usuario {nu} creado")
                st.rerun()
            else:
                st.error("Llena todos")
        del_u=st.selectbox("Eliminar usuario", [u["usuario"] for u in users if u["usuario"]!="admin@farmart.system"])
        if st.button("Eliminar seleccionado"):
            users=[u for u in users if u["usuario"]!=del_u]
            guardar_json(USUARIOS_FILE,users)
            st.success("Eliminado"); st.rerun()
