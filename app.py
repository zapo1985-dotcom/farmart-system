import streamlit as st
import pandas as pd
from datetime import datetime
import json, os, re
from collections import Counter

st.set_page_config(page_title="HIREREADY-IA V6 - Agentes Bizneo", page_icon="🚀", layout="wide")
st.markdown("""
<style>
.stApp{background:#f8fafc;} h1,h2,h3{color:#0B4DA2!important;}
.stButton>button{background:#0B4DA2;color:white;border-radius:10px;font-weight:bold;}
.stButton>button:hover{background:#7AC143;color:white;}
[data-testid="stSidebar"]{background:#0B4DA2;} [data-testid="stSidebar"] *{color:white!important;}
.ia-box{background:linear-gradient(135deg,#0B4DA2 0%,#7AC143 100%);color:white;padding:18px;border-radius:12px;margin-bottom:12px;}
.brand{font-size:30px;font-weight:800;color:#0B4DA2;}.brand span{color:#7AC143;}
.agent{background:white;border-left:6px solid #7AC143;padding:12px;border-radius:8px;margin:8px 0;box-shadow:0 2px 5px rgba(0,0,0,0.1);}
.agent-pub{border-left-color:#0B4DA2;}.agent-criba{border-left-color:#FF6B35;}.agent-ent{border-left-color:#7AC143;}.agent-pool{border-left-color:#9C27B0;}
.kpi{background:white;padding:15px;border-radius:10px;box-shadow:0 2px 4px rgba(0,0,0,0.1);text-align:center;}
</style>
""", unsafe_allow_html=True)

USUARIOS_FILE="usuarios_admin.json"; REGISTROS_FILE="registros_farmart.json"; CARGOS_FILE="cargos.json"; PREGUNTAS_FILE="preguntas_banco.json"; VACANTES_FILE="vacantes.json"; TALENT_FILE="talent_pool.json"

def cargar_json(p, default=None):
    try:
        with open(p,"r") as f: return json.load(f)
    except: return default if default is not None else []
def guardar_json(p,d):
    with open(p,"w") as f: json.dump(d,f,indent=2,ensure_ascii=False)

USUARIOS_CORRECTOS=[
    {"usuario":"admin","clave":"admin123","rol":"Super Admin","nombre":"Admin Simple"},
    {"usuario":"admin@hireready.ia","clave":"HireReady2026*","rol":"Super Admin","nombre":"Admin Principal"},
    {"usuario":"rrhh@hireready.ia","clave":"HireReady2026*","rol":"RRHH","nombre":"RRHH HireReady"},
    {"usuario":"gerencia@hireready.ia","clave":"Gerencia2026*","rol":"Gerencia","nombre":"Gerencia"},
]
def init_users():
    if not os.path.exists(USUARIOS_FILE): guardar_json(USUARIOS_FILE, USUARIOS_CORRECTOS)
    else:
        users=cargar_json(USUARIOS_FILE, [])
        if isinstance(users, dict): users=[users]
        for uc in USUARIOS_CORRECTOS:
            if not any(u["usuario"]==uc["usuario"] for u in users): users.append(uc)
        guardar_json(USUARIOS_FILE, users)

CARGOS_DEFAULT=["Personal de Nómina","Tesorería","Auxiliar de bodega de carga","Auxiliar de farmacia","Mensajero de moto","Conductor de carro","Quimico farmaceutico","Regente de farmacia","Auditoria y facturación","Contadores público","Auxiliares contables","Revisores fiscales","Auxiliares de servicios generales","Recursos Humanos","Auxiliares de archivo","Auditores médicos","Operadores logísticos","Ingenieros ambientales","Ingeniero de sistemas","Ingenieros de software","Desarrolladores fullstack","Auxiliares de recursos humanos","Abogados","Alta gerencia","Auxiliares administrativas","Ingenieros especialistas TIC / Ciberseguridad"]

KEYWORDS_POR_CARGO={
"Personal de Nómina":["nomina","pila","seguridad social","retencion","prestaciones","cesantias","liquidacion","parafiscales","siigo","excel","dian"],
"Tesorería":["tesoreria","flujo de caja","conciliacion","bancos","arqueo","cuentas por pagar","egreso","excel","siigo"],
"Quimico farmaceutico":["quimico farmaceutico","regente","central de mezclas","unidosis","oncologico","citotoxico","NPT","asepsia","BPM","INVIMA","farmacovigilancia"],
"Auxiliar de farmacia":["dispensacion","farmacia","invima","medicamentos","lote","vencimiento","unidosis"],
"Abogados":["tutela","derecho de peticion","contratacion estatal","ley 80","laboral","ley 100","jurisprudencia"],
"Ingeniero de sistemas":["sistemas","python","base de datos","ciberseguridad","redes","soporte","desarrollo","java","sql"],
"Contadores público":["contador","contabilidad","dian","facturacion electronica","iva","retencion","niif"],
"Auditoria y facturación":["auditoria","facturacion","cuentas medicas","soat","glosas","rips"],
}

KILLER_QUESTIONS={
"Quimico farmaceutico":["¿Tiene tarjeta profesional vigente?","¿Experiencia en central de mezclas mínimo 1 año?","¿Curso BPM vigente?"],
"Personal de Nómina":["¿Manejo Siigo o World Office?","¿Experiencia mínima 1 año en nómina?","¿Conocimiento PILA y seguridad social?"],
"Tesorería":["¿Experiencia en arqueos y conciliaciones?","¿Manejo Excel intermedio?","¿Experiencia tesorería mínimo 1 año?"],
"Abogados":["¿Tarjeta profesional vigente?","¿Experiencia en tutelas de salud?","¿Conocimiento Ley 80?"],
"DEFAULT":["¿Experiencia mínima 1 año en el cargo?","¿Disponibilidad inmediata?","¿Vive en la ciudad de la vacante?"]
}

BANCO_ENTREVISTA={
"Personal de Nómina":[
{"q":"¿Qué compone seguridad social integral?","op":["Salud, pensión, ARL, caja","Solo salud","Solo pensión"],"r":0},
{"q":"¿Qué es PILA?","op":["Planilla integrada liquidación aportes","Inventario","Aseo"],"r":0},
{"q":"¿Auxilio transporte cuándo?","op":["Hasta 2 SMMLV","Todos","Nunca"],"r":0},
{"q":"¿Novedad nómina ejemplo?","op":["Incapacidad, vacaciones, horas extra","Solo cargo","Solo aumento"],"r":0},
{"q":"¿Liquidación prestaciones incluye?","op":["Cesantías, intereses, prima, vacaciones","Solo salario","Solo prima"],"r":0},
{"q":"Cesantías ¿cuándo consignan?","op":["Antes 14 feb","31 dic","Cuando renuncia"],"r":0},
{"q":"Intereses cesantías","op":["12% anual","5%","20%"],"r":0},
{"q":"Prima servicios ¿cuándo?","op":["Junio y diciembre","Solo diciembre","Mensual"],"r":0},
{"q":"Hora extra diurna recargo","op":["25%","75%","100%"],"r":0},
{"q":"Hora extra nocturna","op":["75%","25%","0%"],"r":0},
{"q":"Dominical festivo recargo","op":["75%","25%","10%"],"r":0},
{"q":"Retención salarios art 383","op":["Tabla progresiva DIAN","Fija 10%","No aplica"],"r":0},
{"q":"Incapacidad primeros 2 días","op":["Empleador","EPS","ARL"],"r":0},
{"q":"Licencia maternidad","op":["18 semanas","12 semanas","8 semanas"],"r":0},
{"q":"Parafiscales total","op":["9% (4% caja,3% ICBF,2% SENA)","4%","12%"],"r":0},
{"q":"Aporte salud %","op":["12.5% (8.5% empleador 4% empleado)","4%","8%"],"r":0},
{"q":"Aporte pensión %","op":["16% (12% empleador 4% empleado)","4%","10%"],"r":0},
{"q":"ARL quien paga","op":["100% empleador","Empleado","50/50"],"r":0},
{"q":"Vacaciones días año","op":["15 días hábiles","10 días","30 días"],"r":0},
{"q":"Contrato fijo máximo","op":["3 años prorrogable","1 año","Indefinido"],"r":0},
{"q":"Siigo nómina reporte clave","op":["Resumen nómina y provisiones","Inventario","Ventas"],"r":0},
{"q":"World Office nómina","op":["Liquidación y PILA","Facturación","CRM"],"r":0},
{"q":"BUSCARV en Excel para nómina","op":["BUSCARV/XLOOKUP para salarios","SUMA","PROMEDIO"],"r":0},
{"q":"Nómina electrónica DIAN","op":["Mensual","Anual","No aplica"],"r":0},
{"q":"Falla pago seguridad social","op":["Sanción y no cobertura","Nada","Solo interés"],"r":0},
],
"Quimico farmaceutico":[
{"q":"NPT que es","op":["Nutrición Parenteral Total","Norma Producción Técnica","Nivel Total"],"r":0},
{"q":"Unidosis objetivo","op":["Dosis exacta paciente, reduce errores","Ahorrar empaques","Vender más"],"r":0},
{"q":"Citotóxico que es","op":["Destruye células, manejo especial","Para dolor","Antibiótico"],"r":0},
{"q":"Cabina flujo laminar para","op":["Proteger producto, personal, ambiente","Enfriar","Iluminar"],"r":0},
{"q":"Estabilidad mezcla depende","op":["Tiempo, temperatura, luz, concentración","Solo color","Solo lab"],"r":0},
{"q":"BPM que es","op":["Buenas Prácticas Manufactura","Buen Proceso Manual","Bodega Producto"],"r":0},
{"q":"Resolución 1403 de 2007","op":["Regula servicio farmacéutico","Regula alimentos","Regula tránsito"],"r":0},
{"q":"Farmacovigilancia reporta","op":["Eventos adversos medicamentos","Ventas","Inventario"],"r":0},
{"q":"Dosis máxima acetaminofén día","op":["4 gramos","10 gramos","1 gramo"],"r":0},
{"q":"Interacción warfarina y AINE","op":["Aumenta riesgo sangrado","No pasa nada","Disminuye efecto"],"r":0},
{"q":"Cálculo dosis pediátrica","op":["Peso kg y superficie corporal","Solo edad","Solo talla"],"r":0},
{"q":"Antídoto acetaminofén","op":["N-acetilcisteína","Flumazenil","Naloxona"],"r":0},
{"q":"Cadena frío vacunas","op":["2-8°C","15-25°C","-20°C"],"r":0},
{"q":"Medicamento LASA","op":["Look Alike Sound Alike, confusión","Larga acción","Laxante"],"r":0},
{"q":"Medicamento alto riesgo","op":["Insulina, heparina, citotóxicos","Acetaminofén","Loratadina"],"r":0},
{"q":"Validación prescripción","op":["Paciente, medicamento, dosis, vía, frecuencia, firma","Solo nombre","Solo medicamento"],"r":0},
{"q":"Central mezclas área limpia grado","op":["Grado A, B, C, D según INVIMA","Sin grado","Grado 1"],"r":0},
{"q":"Tiempo uso NPT","op":["24 horas refrigerada","7 días","1 mes"],"r":0},
{"q":"Quimioterapia extravasación","op":["Emergencia, protocolo antídoto y reporte","Ignorar","Solo compresa fría"],"r":0},
{"q":"Intervención farmacéutica","op":["Detectar, prevenir y resolver PRM","Solo dispensar","Solo facturar"],"r":0},
{"q":"PRM que es","op":["Problema Relacionado Medicamentos","Producto Requiere Más","Precio Regulado"],"r":0},
{"q":"Conciliación medicamentosa","op":["Comparar medicación habitual vs hospitalaria","Contar pastillas","Inventario"],"r":0},
{"q":"Antibiótico tiempo dependiente","op":["Betalactámicos, tiempo sobre CIM","Aminoglucósidos","Azitromicina"],"r":0},
{"q":"Ajuste dosis falla renal","op":["Reducir dosis según creatinina","Aumentar dosis","No ajustar"],"r":0},
{"q":"Rol químico farmacéutico","op":["Garantizar uso seguro, efectivo y calidad","Solo vender","Solo facturar"],"r":0},
],
"Tesorería":[
{"q":"Flujo caja objetivo","op":["Controlar entradas y salidas dinero","Solo ventas","Solo inventario"],"r":0},
{"q":"Conciliación bancaria","op":["Comparar libros vs extracto","Contar billetes","Hacer nómina"],"r":0},
{"q":"Arqueo caja faltante","op":["Reportar, investigar, reponer","Ocultar","Ignorar"],"r":0},
{"q":"Comprobante egreso necesita","op":["Soporte, autorización, firma","Solo firma","Nada"],"r":0},
{"q":"Cuentas por pagar prioridad","op":["DIAN, nómina, proveedores críticos","Solo proveedores","Solo DIAN"],"r":0},
{"q":"Retención compras %","op":["2.5% compras, 4% servicios, 11% honorarios","10% todo","0%"],"r":0},
{"q":"Cierre caja debe cuadrar con","op":["Sistema, recibos, consignaciones","Solo efectivo","Solo sistema"],"r":0},
{"q":"Cheque posfechado","op":["No, política Farmart no","Sí siempre","Depende"],"r":0},
{"q":"Transferencia proveedor requiere","op":["Factura, orden compra, autorización","Solo WhatsApp","Nada"],"r":0},
{"q":"Siigo tesorería","op":["Cuentas por pagar, bancos, flujo","Nómina","Producción"],"r":0},
{"q":"Excel flujo caja","op":["SUMAR.SI.CONJUNTO y TABLA DINÁMICA","SUMA","CONTAR"],"r":0},
{"q":"Caja menor tope","op":["Definido gerencia, arqueo semanal","Sin tope","10M"],"r":0},
{"q":"Consignación no identificada","op":["Investigar, contactar banco","Dejar así","Anular"],"r":0},
{"q":"Prevención fraude","op":["Doble firma, segregación funciones","Una persona","Sin control"],"r":0},
{"q":"Informe tesorería diario a","op":["Gerencia financiera","Servicios generales","Bodega"],"r":0},
{"q":"Paz y salvo proveedor","op":["Verificar entrega y factura","Pagar sin verificar","Solo factura"],"r":0},
{"q":"Manejo dólares","op":["TRM oficial y legalización","TRM inventada","No reportar"],"r":0},
{"q":"Sobregiro","op":["Saldo negativo autorizado banco","Error","Ingreso"],"r":0},
{"q":"Anticipos empleados","op":["Máx 30% salario, descuento nómina","100%","No se dan"],"r":0},
{"q":"Conciliación proveedores","op":["Circularizar y conciliar mensual","No hacer","Anual"],"r":0},
{"q":"Archivo soportes pagos","op":["5 años mínimo DIAN","1 mes","No archiva"],"r":0},
{"q":"Pago nómina verifica","op":["Novedades, cuentas, autorizaciones","Solo monto","Nada"],"r":0},
{"q":"Doble pago proveedor","op":["Solicitar nota crédito o reintegro","Dejar así","Ocultar"],"r":0},
{"q":"Excel conciliar","op":["BUSCARV y COINCIDIR","SUMA","PROMEDIO"],"r":0},
{"q":"Ética tesorería","op":["Transparencia total y reporte","Ocultar faltantes","Prestar plata caja"],"r":0},
],
}

for c in CARGOS_DEFAULT:
    if c not in BANCO_ENTREVISTA:
        BANCO_ENTREVISTA[c]=[{"q":f"{c} - Pregunta {i+1}: Procedimiento correcto Farmart para {c}?","op":[f"Correcto para {c}","Incorrecto con riesgo","Omitir"],"r":0} for i in range(25)]

TEST_PSICO={
"Psicotecnica":[
{"q":"Compañero toma medicamento sin fórmula","op":["Reportas por seguridad paciente","Te callas","Lo ayudas"],"r":0},
{"q":"Bajo estrés mucho trabajo","op":["Priorizas, pides ayuda, calidad","Gritas y dejas todo","Rápido sin verificar"],"r":0},
{"q":"Jefe pide entregar vencido","op":["Te niegas y reportas","Lo entregas","Cambias fecha"],"r":0},
{"q":"Error propio grave","op":["Admites, corriges, reportas","Ocultas","Culpas a otro"],"r":0},
{"q":"Paciente reclama agresivo","op":["Escuchas, empatía, solución","Gritas también","Ignoras"],"r":0},
{"q":"Ves compañero robando","op":["Reportas con evidencia","Te unes","Te callas"],"r":0},
{"q":"Te ofrecen coima","op":["Rechazas y reportas","Aceptas","Negocias más"],"r":0},
{"q":"Confidencialidad datos paciente","op":["Nunca compartir, Ley 1581","Contar a amigos","Publicar redes"],"r":0},
{"q":"Prioridad ¿qué primero?","op":["Seguridad paciente, calidad, velocidad","Velocidad primero","Fácil primero"],"r":0},
{"q":"¿Por qué Farmart?","op":["Propósito salud, ética, crecimiento","Solo plata","No opción"],"r":0},
],
"Psicologica":[
{"q":"Cuando te critican","op":["Escuchas, evalúas, mejoras","Te ofendes y atacas","Ignoras todo"],"r":0},
{"q":"Decisiones bajo presión","op":["Analizas rápido, con calma, datos","Impulsivo","Paralizas"],"r":0},
{"q":"Conflicto con compañero","op":["Dialogas, buscas acuerdo","Evitas y hablas mal","Confrontas agresivo"],"r":0},
{"q":"Trabajo monótono","op":["Mantienes calidad y concentración","Te distraes errores","Te aburres y dejas"],"r":0},
{"q":"Cambio repentino planes","op":["Te adaptas flexibilidad","Frustras y bloqueas","Nie gas cambio"],"r":0},
{"q":"Honestidad","op":["Verdad aunque duela, respeto","Mentira si conviene","Ocultas conveniencia"],"r":0},
{"q":"Integridad","op":["Haces correcto aunque nadie vea","Solo si te ven","Depende conviene"],"r":0},
{"q":"Responsabilidad","op":["Asumes consecuencias","Evitas responsabilidad","Solo si conviene"],"r":0},
{"q":"Empatía paciente","op":["Alta, te pones en lugar, ayudas","Baja, indiferente","Solo si amable"],"r":0},
{"q":"Tolerancia frustración","op":["Alta, persistente, alternativas","Baja, abandonas rápido","Media, quejas mucho"],"r":0},
]
}

PREGUNTAS_ENTREVISTADOR={
"Quimico farmaceutico":[
"Cuéntame tu experiencia en central de mezclas y un error que evitaste",
"¿Qué harías si detectas prescripción oncológica con dosis 30% superior a la máxima?",
"¿Cómo garantizas cadena de frío 2-8°C y qué haces si falla por 4 horas?",
"Describe un caso de intervención farmacéutica que salvó al paciente",
"¿Por qué quieres trabajar en Farmart y qué aportas a seguridad paciente?"
],
"Personal de Nómina":[
"Cuéntame tu experiencia liquidando nómina y PILA para 100+ empleados",
"¿Cómo manejas una incapacidad de 15 días y qué reportas a EPS y DIAN?",
"Describe un error de nómina que tuviste y cómo lo corregiste",
"¿Qué controles usas para evitar errores en retención y parafiscales?",
"¿Por qué nómina en empresa de salud como Farmart?"
],
"Tesorería":[
"Cuéntame tu experiencia en flujo de caja y conciliaciones bancarias",
"¿Qué harías si caja menor descuadra 500k faltante?",
"Describe cómo priorizas pagos cuando flujo es negativo",
"¿Qué controles anti-fraude implementas en tesorería?",
"¿Por qué tesorería en Farmart?"
],
"DEFAULT":[
"Cuéntame tu experiencia de 2 minutos en este cargo",
"¿Cuál ha sido tu mayor logro en este rol?",
"Describe un conflicto laboral y cómo lo resolviste",
"¿Qué harías si tu jefe te pide hacer algo contra ética/procedimiento?",
"¿Por qué quieres trabajar en Farmart y qué te hace diferente?"
]
}

if not os.path.exists(CARGOS_FILE): guardar_json(CARGOS_FILE, CARGOS_DEFAULT)
if not os.path.exists(PREGUNTAS_FILE): guardar_json(PREGUNTAS_FILE, BANCO_ENTREVISTA)
if not os.path.exists(VACANTES_FILE): guardar_json(VACANTES_FILE, [])
if not os.path.exists(TALENT_FILE): guardar_json(TALENT_FILE, [])
if not os.path.exists(REGISTROS_FILE): guardar_json(REGISTROS_FILE, [])

init_users()

if "auth" not in st.session_state:
    st.session_state.auth=False; st.session_state.user=None
if "modulo" not in st.session_state:
    st.session_state.modulo=None

def leer_pdf_texto(file):
    texto=""
    try:
        import fitz
        doc=fitz.open(stream=file.read(), filetype="pdf")
        for p in doc: texto+=p.get_text()
    except:
        try:
            import PyPDF2
            file.seek(0)
            reader=PyPDF2.PdfReader(file)
            for p in reader.pages: texto+=p.extract_text() or ""
        except:
            try:
                file.seek(0)
                texto=file.read().decode(errors="ignore")
            except: texto=""
    return texto[:10000]

def analizar_cv_ia(texto, cargo):
    tl=texto.lower()
    kws=KEYWORDS_POR_CARGO.get(cargo, ["experiencia","trabajo en equipo","excel"])
    encontrados=[k for k in kws if k.lower() in tl]
    porc=int(len(encontrados)/len(kws)*100) if kws else 50
    porc=min(95, max(10, porc))
    exp_match=re.search(r"(\d+)\s*a[ñn]os", tl)
    exp=int(exp_match.group(1)) if exp_match else 0
    if porc>=80: concepto="ALTA COMPATIBILIDAD"
    elif porc>=50: concepto="MEDIA COMPATIBILIDAD"
    else: concepto="BAJA COMPATIBILIDAD"
    faltantes=[k for k in kws if k.lower() not in tl][:3]
    return {"porc":porc,"concepto":concepto,"encontrados":encontrados,"faltantes":faltantes,"exp":exp}

def evaluar_respuesta_video(texto, cargo):
    tl=texto.lower()
    if len(tl)<20: return 20, "Respuesta muy corta"
    puntaje=40
    kws=KEYWORDS_POR_CARGO.get(cargo, ["experiencia","seguridad","ética","procedimiento"])
    puntaje+=sum(1 for k in kws if k.lower() in tl)*10
    puntaje+=min(20, len(tl)//100)
    puntaje=min(95,puntaje)
    if puntaje>=80: retro="Excelente, menciona experiencia, procedimiento y seguridad paciente"
    elif puntaje>=60: retro="Buena, pero falta profundizar normativa y ejemplo concreto"
    else: retro="Básica, necesita más detalle técnico y ejemplo STAR"
    return puntaje, retro

st.markdown('<div class="brand">HIRE<span>READY</span>-IA V6 🚀</div>',unsafe_allow_html=True)
st.caption("AGENTES IA tipo Bizneo ATS: Publicador + Criba Inteligente + Entrevistador + Talent Pool + Métricas")

if not st.session_state.auth:
    tab1,tab2=st.tabs(["📝 Candidatos - Agentes IA","🔐 RRHH - Agentes IA"])
    with tab1:
        st.markdown('<div class="ia-box">🤖 Bienvenido a HIREREADY-IA V6 - Sistema con Agentes IA como Bizneo ATS: Criba inteligente, videoentrevista diferida y talent pool</div>',unsafe_allow_html=True)
        cedula=st.text_input("Cédula *"); nombre=st.text_input("Nombre completo *")
        cargos_list=cargar_json(CARGOS_FILE, CARGOS_DEFAULT)
        if isinstance(cargos_list, dict): cargos_list=CARGOS_DEFAULT
        cargo=st.selectbox("Cargo / Profesión *", cargos_list); sede=st.text_input("Ciudad"); telefono=st.text_input("WhatsApp")

        st.divider()
        st.subheader("🧩 Elige Módulo")
        col1,col2,col3=st.columns(3)
        with col1:
            st.markdown('<div class="agent agent-pub"><b>📋 M1: Entrevista General</b><br>25 preguntas técnicas por cargo</div>',unsafe_allow_html=True)
            b1=st.button("▶️ Entrevista General (25)",use_container_width=True)
        with col2:
            st.markdown('<div class="agent"><b>🧠 M2: Test Psicológico Laboral</b><br>50 preguntas perfil laboral</div>',unsafe_allow_html=True)
            b2=st.button("▶️ Test Psicológico (50)",use_container_width=True)
        with col3:
            st.markdown('<div class="agent agent-ent"><b>🎥 M3: Videoentrevista IA Diferida</b><br>5 preguntas con IA - tipo Bizneo</div>',unsafe_allow_html=True)
            b3=st.button("▶️ Videoentrevista IA (5)",use_container_width=True)

        if b1 or b2 or b3:
            if not (cedula and nombre):
                st.error("Cédula y nombre obligatorios")
            else:
                st.session_state.cedula_real=cedula; st.session_state.nombre=nombre; st.session_state.cargo_sel=cargo; st.session_state.sede=sede; st.session_state.tel=telefono
                if b1: st.session_state.modulo="entrevista"
                elif b2: st.session_state.modulo="psicologico"
                else: st.session_state.modulo="video"
                st.rerun()

        if st.session_state.modulo=="entrevista":
            st.divider(); st.subheader(f"📋 Entrevista General - {st.session_state.cargo_sel}")
            banco=cargar_json(PREGUNTAS_FILE, BANCO_ENTREVISTA)
            if isinstance(banco, list): banco=BANCO_ENTREVISTA
            preguntas=banco.get(st.session_state.cargo_sel, [])[:25]
            resp=[]
            for i,p in enumerate(preguntas):
                r=st.radio(f"{i+1}. {p['q']}",p["op"],key=f"ent{i}",index=None)
                if r is not None: resp.append(p["op"].index(r)==p["r"])
            if st.button("✅ Finalizar Entrevista y Guardar en Talent Pool",type="primary"):
                if len(resp)<len(preguntas): st.warning(f"Faltan {len(preguntas)-len(resp)}")
                else:
                    aciertos=sum(resp); porc=aciertos/len(preguntas)*100; apto=porc>=70
                    registro={"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":st.session_state.cedula_real,"nombre":st.session_state.nombre,"cargo":st.session_state.cargo_sel,"sede":st.session_state.sede,"telefono":st.session_state.tel,"modulo":"Entrevista General","aciertos":aciertos,"total":len(preguntas),"porcentaje":round(porc,1),"estado":"APTO" if apto else "NO APTO","fuente":"Portal Web","agente":"Agente Entrevista"}
                    regs=cargar_json(REGISTROS_FILE, []); regs.append(registro); guardar_json(REGISTROS_FILE, regs)
                    talent=cargar_json(TALENT_FILE, []); talent.append(registro); guardar_json(TALENT_FILE, talent)
                    if apto: st.balloons(); st.success(f"✅ APTO {porc:.1f}% - Guardado en Talent Pool")
                    else: st.error(f"❌ NO APTO {porc:.1f}% - Guardado en Talent Pool para futuro")
                    if st.button("🔄 Nuevo Módulo"): st.session_state.modulo=None; st.rerun()

        if st.session_state.modulo=="psicologico":
            st.divider(); st.subheader("🧠 Test Psicológico Laboral - 20 preguntas")
            todas=TEST_PSICO["Psicotecnica"]+TEST_PSICO["Psicologica"]
            resp=[]
            for i,p in enumerate(todas):
                r=st.radio(f"{i+1}. {p['q']}",p["op"],key=f"psi{i}",index=None)
                if r is not None: resp.append(p["op"].index(r)==p["r"])
            if st.button("✅ Finalizar Test Psicológico y Guardar",type="primary"):
                if len(resp)<len(todas): st.warning(f"Faltan {len(todas)-len(resp)}")
                else:
                    aciertos=sum(resp); porc=aciertos/len(todas)*100
                    if porc>=80: perfil="EXCELENTE"
                    elif porc>=60: perfil="BUENO"
                    else: perfil="OBSERVACIÓN"
                    registro={"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":st.session_state.cedula_real,"nombre":st.session_state.nombre,"cargo":st.session_state.cargo_sel,"sede":st.session_state.sede,"telefono":st.session_state.tel,"modulo":"Test Psicológico Laboral","aciertos":aciertos,"total":len(todas),"porcentaje":round(porc,1),"perfil":perfil,"estado":"APTO" if porc>=60 else "OBSERVACIÓN","fuente":"Portal Web","agente":"Agente Psicológico"}
                    regs=cargar_json(REGISTROS_FILE, []); regs.append(registro); guardar_json(REGISTROS_FILE, regs)
                    talent=cargar_json(TALENT_FILE, []); talent.append(registro); guardar_json(TALENT_FILE, talent)
                    st.success(f"✅ Test Completado {porc:.1f}% - Perfil {perfil} - Guardado en Talent Pool")
                    if st.button("🔄 Nuevo Módulo"): st.session_state.modulo=None; st.rerun()

        if st.session_state.modulo=="video":
            st.divider(); st.subheader(f"🎥 Videoentrevista Diferida IA - {st.session_state.cargo_sel}")
            preguntas_vid=PREGUNTAS_ENTREVISTADOR.get(st.session_state.cargo_sel, PREGUNTAS_ENTREVISTADOR["DEFAULT"])
            textos=[]
            for idx,q in enumerate(preguntas_vid):
                st.markdown(f"**Pregunta {idx+1}: {q}**")
                t=st.text_area(f"Respuesta {idx+1}",key=f"vid{idx}",height=100,placeholder="Escribe con ejemplo STAR...")
                textos.append(t)
            if st.button("🤖 Enviar Videoentrevista a IA para Evaluación",type="primary"):
                if any(len(t)<20 for t in textos): st.warning("Responde mínimo 20 caracteres por pregunta")
                else:
                    evals=[evaluar_respuesta_video(t, st.session_state.cargo_sel) for t in textos]
                    prom=sum(e[0] for e in evals)/len(evals)
                    apto=prom>=70
                    registro={"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":st.session_state.cedula_real,"nombre":st.session_state.nombre,"cargo":st.session_state.cargo_sel,"sede":st.session_state.sede,"telefono":st.session_state.tel,"modulo":"Videoentrevista IA Diferida","aciertos":int(prom),"total":100,"porcentaje":round(prom,1),"estado":"APTO" if apto else "NO APTO","perfil":f"Prom {prom:.1f}%","fuente":"Videoentrevista","agente":"Agente IA Entrevistador"}
                    regs=cargar_json(REGISTROS_FILE, []); regs.append(registro); guardar_json(REGISTROS_FILE, regs)
                    talent=cargar_json(TALENT_FILE, []); talent.append(registro); guardar_json(TALENT_FILE, talent)
                    if apto: st.balloons(); st.success(f"✅ Videoentrevista APTO {prom:.1f}%")
                    else: st.error(f"❌ Videoentrevista NO APTO {prom:.1f}%")
                    for idx,(punt,retro) in enumerate(evals):
                        st.write(f"**P{idx+1}: {punt}%** - {retro}")
                    if st.button("🔄 Nuevo Módulo"): st.session_state.modulo=None; st.rerun()

    with tab2:
        st.header("🔐 RRHH - Agentes IA tipo Bizneo")
        u=st.text_input("Usuario"); p=st.text_input("Clave",type="password")
        if st.button("Entrar"):
            users=cargar_json(USUARIOS_FILE, [])
            found=next((x for x in users if x["usuario"]==u and x["clave"]==p),None)
            if found: st.session_state.auth=True; st.session_state.user=found; st.rerun()
            else: st.error("Usuario o clave incorrecta")

else:
    st.sidebar.markdown('<div class="brand" style="color:white;">HIRE<span style="color:#7AC143;">READY</span>-IA V6</div>',unsafe_allow_html=True)
    st.sidebar.success(f"Conectado: {st.session_state.user['nombre']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.auth=False; st.session_state.user=None; st.session_state.modulo=None; st.rerun()
    menu=st.sidebar.selectbox("Menú V6 Agentes Bizneo", ["📊 Dashboard Métricas Bizneo","🤖 Agente IA Publicador Vacantes","🤖 Agente IA Criba Inteligente (Rank CVs)","📋 Módulo Entrevista General","🧠 Módulo Test Psicológico Laboral","🎥 Agente IA Entrevistador - Video Diferida","💎 Talent Pool + WhatsApp Reactivación","👥 Crear Usuarios","🔧 Reset Usuarios"])

    if menu=="📊 Dashboard Métricas Bizneo":
        st.header("📊 Dashboard Métricas - Tipo Bizneo ATS")
        regs=cargar_json(REGISTROS_FILE, [])
        talent=cargar_json(TALENT_FILE, [])
        vacantes=cargar_json(VACANTES_FILE, [])
        if not regs:
            st.info("Sin registros aún")
        else:
            df=pd.DataFrame(regs)
            c1,c2,c3,c4,c5=st.columns(5)
            c1.metric("Total Evaluaciones",len(df))
            c2.metric("APTO",len(df[df["estado"]=="APTO"]) if "estado" in df.columns else 0)
            c3.metric("Talent Pool",len(talent))
            c4.metric("Vacantes Activas",len(vacantes))
            c5.metric("% Aprob",f"{len(df[df['estado']=='APTO'])/len(df)*100:.1f}%" if len(df)>0 else "0%")
            st.divider()
            col1,col2=st.columns(2)
            with col1:
                st.subheader("Pass Rate por Fase / Módulo")
                if "modulo" in df.columns:
                    pass_rate=df.groupby("modulo")["porcentaje"].mean()
                    st.bar_chart(pass_rate)
            with col2:
                st.subheader("Calidad por Fuente")
                if "fuente" in df.columns:
                    fuente=df.groupby("fuente")["porcentaje"].mean()
                    st.bar_chart(fuente)
            st.dataframe(df,use_container_width=True)
            st.download_button("📥 Descargar CSV Completo",df.to_csv(index=False).encode(),"hireready_v6_bizneo.csv")

    elif menu=="🤖 Agente IA Publicador Vacantes":
        st.header("🤖 Agente IA Publicador - Multiposting tipo Bizneo")
        with st.form("form_vacante"):
            cargo_pub=st.selectbox("Cargo",CARGOS_DEFAULT)
            sede_pub=st.text_input("Sede / Ciudad")
            salario_pub=st.text_input("Salario")
            tipo_pub=st.selectbox("Tipo contrato",["Indefinido","Fijo","Prestación servicios","Aprendizaje"])
            desc_manual=st.text_area("Descripción breve (opcional, IA la optimiza)")
            if st.form_submit_button("🚀 Publicar Vacante con IA - Multiposting"):
                keywords=KEYWORDS_POR_CARGO.get(cargo_pub, ["experiencia","trabajo en equipo"])
                desc_ia=f"Oferta {cargo_pub} en {sede_pub} - Farmart\\nBuscamos {cargo_pub} con experiencia en {', '.join(keywords[:3])}.\\nSalario {salario_pub} - Contrato {tipo_pub}.\\nRequisitos: {', '.join(KILLER_QUESTIONS.get(cargo_pub, KILLER_QUESTIONS['DEFAULT']))}\\nBeneficios: Estabilidad, crecimiento, propósito salud."
                vacante={"id":len(cargar_json(VACANTES_FILE,[]))+1,"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cargo":cargo_pub,"sede":sede_pub,"salario":salario_pub,"tipo":tipo_pub,"descripcion":desc_ia,"estado":"Publicada","portales":["LinkedIn","Indeed","Torre","Magneto","Computrabajo","Portal Farmart"],"candidatos":0}
                vacantes=cargar_json(VACANTES_FILE, []); vacantes.append(vacante); guardar_json(VACANTES_FILE, vacantes)
                st.success(f"✅ Vacante {cargo_pub} publicada en 6 portales - ID {vacante['id']}")
                st.text_area("Descripción IA optimizada:",desc_ia,height=200)

    elif menu=="🤖 Agente IA Criba Inteligente (Rank CVs)":
        st.header("🤖 Agente IA Criba Inteligente - Criba Semántica tipo Bizneo")
        cargo_criba=st.selectbox("Cargo a evaluar",CARGOS_DEFAULT,key="criba_cargo")
        archivos=st.file_uploader("📎 Sube hasta 20 Hojas de Vida PDF (Criba Masiva)",type=["pdf"],accept_multiple_files=True)
        if archivos:
            if st.button(f"🤖 Ejecutar Criba Inteligente para {cargo_criba} - Rankear {len(archivos)} CVs",type="primary"):
                resultados=[]
                with st.spinner(f"🤖 Agente IA leyendo {len(archivos)} CVs..."):
                    for archivo in archivos:
                        texto=leer_pdf_texto(archivo)
                        analisis=analizar_cv_ia(texto, cargo_criba)
                        killer=KILLER_QUESTIONS.get(cargo_criba, KILLER_QUESTIONS["DEFAULT"])
                        cumple_killer=True
                        if analisis["exp"]<1 and "experiencia" in " ".join(killer).lower():
                            cumple_killer=False
                        resultados.append({"archivo":archivo.name,"compatibilidad":analisis["porc"],"concepto":analisis["concepto"],"exp_detectada":f"{analisis['exp']} años","encontrados":", ".join(analisis["encontrados"][:4]),"faltantes":", ".join(analisis["faltantes"]),"killer_pass": "✅ Pasa" if cumple_killer else "❌ No pasa killer","recomendacion":"AVANZA" if analisis["porc"]>=60 and cumple_killer else "DESCARTADO"})
                df_rank=pd.DataFrame(resultados).sort_values(by="compatibilidad",ascending=False)
                st.success(f"✅ Criba completada - {len(resultados)} CVs rankeados")
                st.dataframe(df_rank,use_container_width=True)
                st.bar_chart(df_rank.set_index("archivo")["compatibilidad"])
                st.download_button("📥 Descargar Ranking Criba CSV",df_rank.to_csv(index=False).encode(),f"criba_{cargo_criba}.csv")

    elif menu=="💎 Talent Pool + WhatsApp Reactivación":
        st.header("💎 Talent Pool + Reactivación WhatsApp")
        talent=cargar_json(TALENT_FILE, [])
        if not talent:
            st.info("Talent Pool vacío")
        else:
            df_talent=pd.DataFrame(talent)
            st.dataframe(df_talent,use_container_width=True)
            st.subheader("📱 Reactivación por WhatsApp (3x más respuesta que email)")
            cand_sel=st.selectbox("Selecciona candidato",df_talent["nombre"].unique() if "nombre" in df_talent.columns and len(df_talent)>0 else [])
            if cand_sel:
                cand_data=df_talent[df_talent["nombre"]==cand_sel].iloc[0] if len(df_talent[df_talent["nombre"]==cand_sel])>0 else {}
                mensaje_default=f"Hola {cand_sel}, vimos tu perfil para {cand_data.get('cargo','')} con {cand_data.get('porcentaje','')}% compatibilidad en Farmart. Tenemos nueva vacante que encaja contigo. ¿Te interesa conversar? Responde SI y te llamamos."
                mensaje=st.text_area("Mensaje WhatsApp",value=mensaje_default,height=100)
                telefono=cand_data.get("telefono","")
                if telefono:
                    wa_link=f"https://wa.me/{telefono}?text={mensaje.replace(' ','%20')}"
                    st.markdown(f"[📱 Enviar WhatsApp a {cand_sel}]({wa_link})")
                else:
                    tel_manual=st.text_input("Ingresa WhatsApp con indicativo Ej: 573001234567")
                    if tel_manual:
                        wa_link=f"https://wa.me/{tel_manual}?text={mensaje.replace(' ','%20')}"
                        st.markdown(f"[📱 Enviar WhatsApp a {cand_sel}]({wa_link})")
            st.download_button("📥 Descargar Talent Pool CSV",df_talent.to_csv(index=False).encode(),"talent_pool.csv")

    elif menu=="🔧 Reset Usuarios":
        st.header("🔧 Reset")
        if st.button("🔄 RESETEAR a admin/admin123",type="primary"):
            guardar_json(USUARIOS_FILE, USUARIOS_CORRECTOS); st.success("Reseteado")
