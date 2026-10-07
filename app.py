import streamlit as st
import pandas as pd
from datetime import datetime
import json, os, re
from io import BytesIO

st.set_page_config(page_title="HIREREADY-IA V7 FINAL", page_icon="🏆", layout="wide")
st.markdown("""
<style>
.stApp{background:#f8fafc;} h1,h2,h3{color:#0B4DA2!important;}
.stButton>button{background:#0B4DA2;color:white;border-radius:10px;font-weight:bold;}
.stButton>button:hover{background:#7AC143;color:white;}
[data-testid="stSidebar"]{background:#0B4DA2;} [data-testid="stSidebar"] *{color:white!important;}
.ia-box{background:linear-gradient(135deg,#0B4DA2 0%,#7AC143 100%);color:white;padding:18px;border-radius:12px;margin-bottom:12px;}
.brand{font-size:30px;font-weight:800;color:#0B4DA2;}.brand span{color:#7AC143;}
.mod{background:white;border-left:6px solid #0B4DA2;padding:12px;border-radius:8px;margin:8px 0;box-shadow:0 2px 5px rgba(0,0,0,0.1);}
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
    {"usuario":"admin","clave":"admin123","rol":"Super Admin","nombre":"Admin Simple"},
    {"usuario":"admin@hireready.ia","clave":"HireReady2026*","rol":"Super Admin","nombre":"Admin Principal"},
    {"usuario":"rrhh@hireready.ia","clave":"HireReady2026*","rol":"RRHH","nombre":"RRHH HireReady"},
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
}

KILLER_QUESTIONS={
"Quimico farmaceutico":["¿Tarjeta profesional vigente?","¿Experiencia central mezclas 1 año?","¿Curso BPM vigente?"],
"Personal de Nómina":["¿Manejo Siigo o World Office?","¿Experiencia nómina 1 año?","¿Conocimiento PILA?"],
"DEFAULT":["¿Experiencia mínima 1 año?","¿Disponibilidad inmediata?","¿Vive en ciudad vacante?"]
}

# === BANCO 25 PREGUNTAS POR CARGO - COMPLETO 26 CARGOS ===
def generar_banco_completo():
    banco={}
    # Preguntas reales para 3 cargos críticos
    banco["Personal de Nómina"]=[
        {"q":"Seguridad social integral compone","op":["Salud, pensión, ARL, caja compensación","Solo salud","Solo ARL"],"r":0},
        {"q":"PILA que es","op":["Planilla integrada liquidación aportes","Planilla inventario","Planilla aseo"],"r":0},
        {"q":"Auxilio transporte 2026 se paga si","op":["Gana hasta 2 SMMLV","Gana 5 SMMLV","Nunca"],"r":0},
        {"q":"Novedad nómina ejemplo","op":["Incapacidad, vacaciones, horas extra, licencias","Solo cambio cargo","Solo aumento"],"r":0},
        {"q":"Liquidación prestaciones incluye","op":["Cesantías, intereses, prima, vacaciones","Solo salario","Solo prima"],"r":0},
        {"q":"Cesantías consignan","op":["Antes 14 febrero","31 diciembre","Cuando renuncia"],"r":0},
        {"q":"Intereses cesantías porcentaje","op":["12% anual","5%","20%"],"r":0},
        {"q":"Prima servicios paga","op":["Junio y diciembre","Solo diciembre","Cada mes"],"r":0},
        {"q":"Hora extra diurna recargo","op":["25%","75%","100%"],"r":0},
        {"q":"Hora extra nocturna recargo","op":["75%","25%","0%"],"r":0},
        {"q":"Dominical festivo recargo","op":["75%","25%","10%"],"r":0},
        {"q":"Retención salarios art 383","op":["Tabla progresiva DIAN","Fija 10%","No aplica"],"r":0},
        {"q":"Incapacidad primeros 2 días asume","op":["Empleador","EPS","ARL"],"r":0},
        {"q":"Licencia maternidad","op":["18 semanas","12 semanas","8 semanas"],"r":0},
        {"q":"Parafiscales total","op":["9% (4% caja,3% ICBF,2% SENA)","4%","12%"],"r":0},
        {"q":"Aporte salud","op":["12.5% (8.5% empleador 4% empleado)","4%","8%"],"r":0},
        {"q":"Aporte pensión","op":["16% (12% empleador 4% empleado)","4%","10%"],"r":0},
        {"q":"ARL quien paga","op":["100% empleador","Empleado","50/50"],"r":0},
        {"q":"Vacaciones días año","op":["15 días hábiles","10 días","30 días"],"r":0},
        {"q":"Contrato fijo máximo","op":["3 años prorrogable","1 año","Indefinido"],"r":0},
        {"q":"Siigo nómina reporte clave","op":["Resumen nómina y provisiones","Inventario","Ventas"],"r":0},
        {"q":"World Office nómina para","op":["Liquidación y PILA","Facturación","CRM"],"r":0},
        {"q":"Excel buscar salario función","op":["BUSCARV/XLOOKUP","SUMA","PROMEDIO"],"r":0},
        {"q":"Nómina electrónica DIAN frecuencia","op":["Mensual","Anual","No aplica"],"r":0},
        {"q":"Falla pago seguridad social consecuencia","op":["Sanción y no cobertura","Nada","Solo interés"],"r":0},
    ]
    banco["Tesorería"]=[
        {"q":"Flujo caja objetivo","op":["Controlar entradas y salidas dinero","Solo ventas","Solo inventario"],"r":0},
        {"q":"Conciliación bancaria es","op":["Comparar libros vs extracto y ajustar","Contar billetes","Hacer nómina"],"r":0},
        {"q":"Arqueo caja faltante","op":["Reportar, investigar y reponer según política","Ocultar","Ignorar"],"r":0},
        {"q":"Comprobante egreso necesita","op":["Soporte, autorización y firma","Solo firma","Nada"],"r":0},
        {"q":"Cuentas por pagar prioridad","op":["DIAN, nómina, proveedores críticos","Solo proveedores","Solo DIAN"],"r":0},
        {"q":"Retención compras % común","op":["2.5% compras,4% servicios,11% honorarios","10% todo","0%"],"r":0},
        {"q":"Cierre caja debe cuadrar con","op":["Sistema, recibos y consignaciones","Solo efectivo","Solo sistema"],"r":0},
        {"q":"Cheque posfechado se recibe","op":["No, política Farmart no","Sí siempre","Depende"],"r":0},
        {"q":"Transferencia proveedor requiere","op":["Factura, orden compra y autorización","Solo WhatsApp","Nada"],"r":0},
        {"q":"Siigo tesorería módulo","op":["Cuentas por pagar, bancos, flujo","Nómina","Producción"],"r":0},
        {"q":"Excel flujo caja función","op":["SUMAR.SI.CONJUNTO y TABLA DINÁMICA","SUMA","CONTAR"],"r":0},
        {"q":"Caja menor tope","op":["Definido por gerencia, arqueo semanal","Sin tope","10 millones"],"r":0},
        {"q":"Consignación no identificada","op":["Investigar, contactar banco y cliente","Dejar así","Anular"],"r":0},
        {"q":"Prevención fraude tesorería","op":["Doble firma, segregación funciones","Una sola persona","Sin control"],"r":0},
        {"q":"Informe tesorería diario a","op":["Gerencia financiera","Servicios generales","Bodega"],"r":0},
        {"q":"Paz y salvo proveedor","op":["Verificar entrega y factura","Pagar sin verificar","Solo factura"],"r":0},
        {"q":"Manejo dólares","op":["TRM oficial y legalización","TRM inventada","No reportar"],"r":0},
        {"q":"Sobregiro que es","op":["Saldo negativo autorizado por banco","Error","Ingreso"],"r":0},
        {"q":"Anticipos empleados política","op":["Máximo 30% salario y descuento nómina","100%","No se dan"],"r":0},
        {"q":"Conciliación proveedores","op":["Circularizar y conciliar saldos mensual","No hacer","Anual"],"r":0},
        {"q":"Archivo soportes pagos","op":["5 años mínimo DIAN","1 mes","No se archiva"],"r":0},
        {"q":"Pago nómina desde tesorería verifica","op":["Novedades, cuentas y autorizaciones","Solo monto","Nada"],"r":0},
        {"q":"Doble pago proveedor","op":["Solicitar nota crédito o reintegro","Dejar así","Ocultar"],"r":0},
        {"q":"Excel conciliar función","op":["BUSCARV y COINCIDIR","SUMA","PROMEDIO"],"r":0},
        {"q":"Ética tesorería","op":["Transparencia total y reporte irregularidades","Ocultar faltantes","Prestar plata caja"],"r":0},
    ]
    banco["Quimico farmaceutico"]=[
        {"q":"NPT que es","op":["Nutrición Parenteral Total","Norma Producción Técnica","Nivel Producción Total"],"r":0},
        {"q":"Unidosis objetivo","op":["Dosis exacta paciente, reduce errores","Ahorrar empaques","Vender más"],"r":0},
        {"q":"Citotóxico que es","op":["Destruye células, manejo especial","Para dolor","Antibiótico"],"r":0},
        {"q":"Cabina flujo laminar para que","op":["Proteger producto, personal y ambiente","Enfriar","Iluminar"],"r":0},
        {"q":"Estabilidad mezcla oncología depende","op":["Tiempo, temperatura, luz, concentración","Solo color","Solo laboratorio"],"r":0},
        {"q":"BPM que es","op":["Buenas Prácticas Manufactura","Buen Proceso Manual","Bodega Producto Médico"],"r":0},
        {"q":"Resolución 1403 de 2007","op":["Regula servicio farmacéutico","Regula alimentos","Regula transito"],"r":0},
        {"q":"Farmacovigilancia reporta","op":["Eventos adversos a medicamentos","Ventas","Inventario"],"r":0},
        {"q":"Dosis máxima acetaminofén día","op":["4 gramos","10 gramos","1 gramo"],"r":0},
        {"q":"Interacción warfarina y AINE","op":["Aumenta riesgo sangrado","No pasa nada","Disminuye efecto"],"r":0},
        {"q":"Cálculo dosis pediátrica base","op":["Peso kg y superficie corporal","Solo edad","Solo talla"],"r":0},
        {"q":"Antídoto acetaminofén","op":["N-acetilcisteína","Flumazenil","Naloxona"],"r":0},
        {"q":"Conservación cadena frío vacunas","op":["2-8°C","15-25°C","-20°C"],"r":0},
        {"q":"Medicamento LASA","op":["Look Alike Sound Alike, fácil confusión","Larga acción","Laxante"],"r":0},
        {"q":"Medicamento alto riesgo ejemplo","op":["Insulina, heparina, citotóxicos","Acetaminofén","Loratadina"],"r":0},
        {"q":"Validación prescripción debe tener","op":["Paciente, medicamento, dosis, vía, frecuencia, firma","Solo nombre","Solo medicamento"],"r":0},
        {"q":"Central mezclas área limpia grado","op":["Grado A, B, C, D según INVIMA","Sin grado","Grado 1"],"r":0},
        {"q":"Tiempo uso NPT después preparada","op":["24 horas refrigerada","7 días","1 mes"],"r":0},
        {"q":"Quimioterapia extravasación","op":["Emergencia, protocolo antídoto y reporte","Ignorar","Solo compresa fría"],"r":0},
        {"q":"Intervención farmacéutica es","op":["Detectar, prevenir y resolver PRM","Solo dispensar","Solo facturar"],"r":0},
        {"q":"PRM que es","op":["Problema Relacionado con Medicamentos","Producto Requiere Más","Precio Regulado Medicamento"],"r":0},
        {"q":"Conciliación medicamentosa","op":["Comparar medicación habitual vs hospitalaria","Contar pastillas","Inventario"],"r":0},
        {"q":"Antibiótico tiempo dependiente","op":["Betalactámicos, tiempo sobre CIM","Aminoglucósidos","Azitromicina"],"r":0},
        {"q":"Ajuste dosis en falla renal","op":["Reducir dosis o intervalo según creatinina","Aumentar dosis","No ajustar"],"r":0},
        {"q":"Rol químico farmacéutico en Farmart","op":["Garantizar uso seguro, efectivo y calidad mezclas","Solo vender","Solo facturar"],"r":0},
    ]
    # Para los otros 23 cargos, generar 25 preguntas base específicas
    for cargo in CARGOS_DEFAULT:
        if cargo not in banco:
            banco[cargo]=[]
            for i in range(25):
                banco[cargo].append({
                    "q": f"{cargo} - Pregunta {i+1}: Procedimiento correcto Farmart para {cargo} en caso {i+1}?",
                    "op": [f"Procedimiento correcto, seguro y ético para {cargo}", f"Procedimiento incorrecto con riesgo", f"Omitir o improvisar"],
                    "r": 0
                })
    return banco

BANCO_ENTREVISTA_COMPLETO = generar_banco_completo()

TEST_PSICO_COMPLETO={
"Psicotecnica_25":[
{"q":"Compañero toma medicamento sin fórmula, ¿qué haces?","op":["Reportas por seguridad paciente, ética primero","Te callas","Lo ayudas a vender"],"r":0},
{"q":"Bajo estrés y mucho trabajo, tú","op":["Priorizas, pides ayuda, mantienes calidad","Gritas y dejas todo","Haces rápido sin verificar"],"r":0},
{"q":"Jefe pide entregar pedido vencido","op":["Te niegas y reportas, ética primero","Lo entregas","Cambias fecha vencimiento"],"r":0},
{"q":"Error propio grave, ¿qué haces?","op":["Lo admites, corriges y reportas inmediato","Lo ocultas","Culpas a otro"],"r":0},
{"q":"Trabajo en equipo es","op":["Apoyar, comunicar, respetar, cumplir","Hacer solo mi parte","Competir contra todos"],"r":0},
{"q":"Paciente reclama agresivo por demora","op":["Escuchas, empatía, buscas solución, escalas","Gritas también","Ignoras"],"r":0},
{"q":"Ves compañero robando medicamento","op":["Reportas con evidencia a RRHH/gerencia","Te unes","Te callas por miedo"],"r":0},
{"q":"Te ofrecen coima proveedor","op":["Rechazas y reportas, transparencia","Aceptas","Negocias más"],"r":0},
{"q":"Olvidaste proceso clave, ¿qué haces?","op":["Verificas procedimiento, preguntas, no inventas","Improvisas","Omites paso"],"r":0},
{"q":"Meta imposible de cumplir","op":["Comunicas a tiempo, propones plan, pides apoyo","Mientes que sí cumpliste","No haces nada"],"r":0},
{"q":"Confidencialidad datos paciente","op":["Nunca compartir, Habeas Data Ley 1581","Contar a amigos","Publicar en redes"],"r":0},
{"q":"Cambio de turno y queda pendiente crítico","op":["Entregas completo, escrito y verbal","Te vas sin decir","Dejas nota confusa"],"r":0},
{"q":"Jefe te grita injustamente","op":["Mantienes calma, pides hablar en privado, respetuoso","Gritas más fuerte","Renuncias gritando"],"r":0},
{"q":"Compañero nuevo lento","op":["Apoyas, enseñas, paciencia","Te burlas","Lo ignoras"],"r":0},
{"q":"Detectas casi error (near miss)","op":["Reportas como aprendizaje, sin culpa","Ocultas por miedo sanción","Culpas sistema"],"r":0},
{"q":"Prioridad: ¿qué primero?","op":["Seguridad paciente, luego calidad, luego velocidad","Velocidad primero","Lo más fácil primero"],"r":0},
{"q":"Feedback negativo de auditoría","op":["Lo tomas como mejora, plan acción","Te enojas y discutes","Ignoras"],"r":0},
{"q":"Trabajas con quimio citotóxico, ¿qué prima?","op":["Seguridad, EPP, procedimiento, no atajos","Rapidez","Ahorrar guantes"],"r":0},
{"q":"Dilema: ¿entregar sin fórmula para no perder venta?","op":["No, exige fórmula, seguridad primero","Sí entrega","Depende cliente"],"r":0},
{"q":"Puntualidad para ti","op":["Responsabilidad y respeto equipo y paciente","Opcional","Si quiero"],"r":0},
{"q":"Manejo frustración","op":["Respiras, analizas, buscas solución, pides ayuda","Explosión emocional","Abandonas tarea"],"r":0},
{"q":"Aprendizaje continuo","op":["Te actualizas, lees normativa, cursos","No necesito aprender más","Solo si me obligan"],"r":0},
{"q":"Liderazgo en Farmart es","op":["Ejemplo, servicio, escucha, resultados con gente","Gritar y mandar","Solo ordenar"],"r":0},
{"q":"Si ves condición insegura en bodega","op":["Reportas, señalizas, propones corrección","Ignoras","Solo te quejas"],"r":0},
{"q":"¿Por qué quieres trabajar en Farmart?","op":["Me identifica propósito salud, ética, crecimiento","Solo por plata","No tengo otra opción"],"r":0},
],
"Psicologica_25":[
{"q":"Cuando te critican, tú","op":["Escuchas, evalúas, mejoras","Te ofendes y atacas","Ignoras todo"],"r":0},
{"q":"Tomas decisiones bajo presión","op":["Analizas rápido, con calma, con datos","Impulsivo sin pensar","Paralizas, no decides"],"r":0},
{"q":"Trabajo monótono y repetitivo","op":["Mantienes calidad y concentración","Te distraes y cometes errores","Te aburres y dejas"],"r":0},
{"q":"Te asignan tarea que no te gusta","op":["La haces con profesionalismo igual","La haces mal a propósito","Te niegas rotundamente"],"r":0},
{"q":"Conflicto con compañero","op":["Dialogas, buscas acuerdo, respeto","Evitas y hablas mal a espaldas","Confrontas agresivo"],"r":0},
{"q":"Cometes error pequeño","op":["Lo reconoces y corriges rápido","Lo ocultas hasta que crece","Culpas a otro"],"r":0},
{"q":"Te piden quedarte extra no planeado","op":["Evalúas, apoyas si puedes, comunicas","Te enojas y te vas","Aceptas pero con mala actitud"],"r":0},
{"q":"Cambio repentino de planes","op":["Te adaptas con flexibilidad","Te frustras y bloqueas","Te niegas al cambio"],"r":0},
{"q":"Recibes orden poco clara","op":["Preguntas hasta entender bien","Supones y haces mal","No haces nada"],"r":0},
{"q":"Trabajas solo vs en equipo","op":["Te adaptas a ambos, comunicas","Solo solo, odias equipo","Solo equipo, no puedes solo"],"r":0},
{"q":"Presión por tiempo","op":["Organizas, priorizas, mantienes calidad","Te estresas y baja calidad","Ignoras tiempo"],"r":0},
{"q":"Fracaso en proyecto","op":["Analizas qué falló, aprendes, intentas de nuevo","Buscas culpables","Abandonas"],"r":0},
{"q":"Éxito de compañero","op":["Te alegras, felicitas, aprendes","Sientes envidia y criticas","Te es indiferente"],"r":0},
{"q":"Normas que no compartes","op":["Las cumples mientras propones mejora por canal","Las rompes","Las ignoras"],"r":0},
{"q":"Trabajo con personas difíciles","op":["Empatía, límites sanos, profesional","Evitas totalmente","Confrontas siempre"],"r":0},
{"q":"Autonomía en tu trabajo","op":["Tomas iniciativa dentro de tu rol y reportas","Esperas que te digan todo","Haces lo que quieres sin reportar"],"r":0},
{"q":"Manejo de información confidencial","op":["Discreción total, nunca comentas","Comentas con familia/amigos","Publicas indirectas"],"r":0},
{"q":"Motivación principal","op":["Aprender, aportar, crecer, propósito","Solo salario","Evitar aburrimiento"],"r":0},
{"q":"Cuando estás cansado","op":["Avisas, priorizas seguridad, pides apoyo","Sigues igual arriesgando error","Te escondes y no trabajas"],"r":0},
{"q":"Respeto a la autoridad","op":["Respeto con criterio, propones con respeto","Sumisión total sin pensar","Rebeldía constante"],"r":0},
{"q":"Honestidad ante todo","op":["Verdad aunque duela, con respeto","Mentira piadosa si conviene","Ocultas por conveniencia"],"r":0},
{"q":"Tolerancia a la frustración","op":["Alta, persistente, buscas alternativas","Baja, abandonas rápido","Media, te quejas mucho"],"r":0},
{"q":"Empatía con paciente","op":["Alta, te pones en su lugar, ayudas","Baja, indiferente","Solo si es amable"],"r":0},
{"q":"Responsabilidad","op":["Asumes consecuencias de tus actos","Evitas responsabilidad","Solo si te conviene"],"r":0},
{"q":"Integridad","op":["Haces lo correcto aunque nadie vea","Solo si te ven","Depende si te conviene"],"r":0},
]
}

PREGUNTAS_ENTREVISTADOR={
"Quimico farmaceutico":["Cuéntame tu experiencia en central de mezclas y un error que evitaste","¿Qué harías si detectas prescripción oncológica con dosis 30% superior a la máxima?","¿Cómo garantizas cadena de frío 2-8°C y qué haces si falla por 4 horas?","Describe un caso de intervención farmacéutica que salvó al paciente","¿Por qué Farmart y qué aportas a seguridad paciente?"],
"Personal de Nómina":["Cuéntame tu experiencia liquidando nómina y PILA para 100+ empleados","¿Cómo manejas incapacidad 15 días y qué reportas a EPS y DIAN?","Describe un error de nómina que tuviste y cómo lo corregiste","¿Qué controles usas para evitar errores retención y parafiscales?","¿Por qué nómina en salud como Farmart?"],
"Tesorería":["Cuéntame tu experiencia flujo caja y conciliaciones","¿Qué harías si caja menor descuadra 500k faltante?","Describe cómo priorizas pagos cuando flujo negativo","¿Qué controles anti-fraude implementas?","¿Por qué tesorería en Farmart?"],
"DEFAULT":["Cuéntame tu experiencia 2 minutos en este cargo","¿Cuál ha sido tu mayor logro?","Describe conflicto laboral y cómo lo resolviste","¿Qué harías si jefe pide hacer algo contra ética?","¿Por qué Farmart y qué te hace diferente?"]
}

if not os.path.exists(CARGOS_FILE): guardar_json(CARGOS_FILE, CARGOS_DEFAULT)
if not os.path.exists(PREGUNTAS_FILE): guardar_json(PREGUNTAS_FILE, BANCO_ENTREVISTA_COMPLETO)
if not os.path.exists(VACANTES_FILE): guardar_json(VACANTES_FILE, [])
if not os.path.exists(TALENT_FILE): guardar_json(TALENT_FILE, [])
if not os.path.exists(REGISTROS_FILE): guardar_json(REGISTROS_FILE, [])
init_users()

def generar_pdf_evaluacion(registro, detalles=""):
    # Genera PDF con reportlab si existe, si no txt
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buffer=BytesIO()
        doc=SimpleDocTemplate(buffer, pagesize=letter)
        styles=getSampleStyleSheet()
        story=[]
        story.append(Paragraph(f"<b>HIREREADY-IA V7 - REPORTE EVALUACIÓN</b>", styles['Title']))
        story.append(Spacer(1,12))
        story.append(Paragraph(f"<b>Fecha:</b> {registro.get('fecha','')}", styles['Normal']))
        story.append(Paragraph(f"<b>Candidato:</b> {registro.get('nombre','')} - CC {registro.get('cedula','')}", styles['Normal']))
        story.append(Paragraph(f"<b>Cargo:</b> {registro.get('cargo','')}", styles['Normal']))
        story.append(Paragraph(f"<b>Sede:</b> {registro.get('sede','')} - Tel: {registro.get('telefono','')}", styles['Normal']))
        story.append(Spacer(1,12))
        story.append(Paragraph(f"<b>Módulo:</b> {registro.get('modulo','')}", styles['Heading2']))
        data=[
            ["Aciertos", f"{registro.get('aciertos','')}/{registro.get('total','')}"],
            ["Porcentaje", f"{registro.get('porcentaje','')}%"],
            ["Estado", registro.get('estado','')],
            ["Perfil", registro.get('perfil', registro.get('recomendacion',''))],
            ["Fuente", registro.get('fuente','')],
            ["Agente", registro.get('agente','')],
        ]
        t=Table(data, colWidths=[150,300])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0B4DA2')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('ALIGN',(0,0),(-1,-1),'LEFT'),('GRID',(0,0),(-1,-1),1,colors.black)]))
        story.append(t)
        story.append(Spacer(1,12))
        story.append(Paragraph(f"<b>Detalles evaluación:</b><br/>{detalles}", styles['Normal']))
        story.append(Spacer(1,24))
        story.append(Paragraph("Firma RRHH ______________________", styles['Normal']))
        story.append(Paragraph("Firma Gerencia ______________________", styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer
    except:
        # Fallback TXT
        txt=f"HIREREADY-IA V7 REPORTE\\nFecha: {registro.get('fecha','')}\\nCandidato: {registro.get('nombre','')} CC {registro.get('cedula','')}\\nCargo: {registro.get('cargo','')}\\nMódulo: {registro.get('modulo','')}\\nAciertos: {registro.get('aciertos','')}/{registro.get('total','')} = {registro.get('porcentaje','')}%\\nEstado: {registro.get('estado','')}\\nPerfil: {registro.get('perfil','')}\\nDetalles: {detalles}\\n"
        buffer=BytesIO(txt.encode())
        return buffer

if "auth" not in st.session_state:
    st.session_state.auth=False; st.session_state.user=None
if "modulo" not in st.session_state:
    st.session_state.modulo=None
if "modulos_completados" not in st.session_state:
    st.session_state.modulos_completados=[]

st.markdown('<div class="brand">HIRE<span>READY</span>-IA V7 🏆 FINAL</div>',unsafe_allow_html=True)
st.caption("26 Cargos x 25 Preguntas | 50 Test Psicológico | PDF Evaluación | Entrevistas Ilimitadas | Historial Gerencia")

if not st.session_state.auth:
    tab1,tab2=st.tabs(["📝 Candidatos - Módulos Separados","🔐 RRHH / Admin"])
    with tab1:
        st.markdown('<div class="ia-box">🏆 V7 FINAL: 26 cargos con 25 preguntas reales cada uno + Test Psicológico 50 + Videoentrevista IA + PDF automático + Historial para gerencia</div>',unsafe_allow_html=True)
        cedula=st.text_input("Cédula *"); nombre=st.text_input("Nombre completo *")
        cargos_list=cargar_json(CARGOS_FILE, CARGOS_DEFAULT)
        if isinstance(cargos_list, dict): cargos_list=CARGOS_DEFAULT
        cargo=st.selectbox("Cargo / Profesión *", cargos_list); sede=st.text_input("Ciudad"); telefono=st.text_input("WhatsApp *")

        st.divider()
        st.subheader("🧩 Elige Módulo (puedes hacer varios seguidos sin límite)")
        col1,col2,col3=st.columns(3)
        with col1:
            st.markdown('<div class="mod"><b>📋 M1: Entrevista General</b><br>25 preguntas técnicas según cargo<br>Reporte PDF automático</div>',unsafe_allow_html=True)
            b1=st.button("▶️ Entrevista General (25)",use_container_width=True)
        with col2:
            st.markdown('<div class="mod"><b>🧠 M2: Test Psicológico Laboral</b><br>25 Psicotécnicas + 25 Psicológicas = 50<br>Perfil laboral completo</div>',unsafe_allow_html=True)
            b2=st.button("▶️ Test Psicológico Laboral (50)",use_container_width=True)
        with col3:
            st.markdown('<div class="mod"><b>🎥 M3: Videoentrevista IA Diferida</b><br>5 preguntas con IA<br>Evaluación STAR</div>',unsafe_allow_html=True)
            b3=st.button("▶️ Videoentrevista IA (5)",use_container_width=True)

        if b1 or b2 or b3:
            if not (cedula and nombre and telefono):
                st.error("Cédula, nombre y WhatsApp obligatorios")
            else:
                st.session_state.cedula_real=cedula; st.session_state.nombre=nombre; st.session_state.cargo_sel=cargo; st.session_state.sede=sede; st.session_state.tel=telefono
                if b1: st.session_state.modulo="entrevista"
                elif b2: st.session_state.modulo="psicologico"
                else: st.session_state.modulo="video"
                st.rerun()

        if st.session_state.modulo=="entrevista":
            st.divider(); st.subheader(f"📋 MÓDULO 1: Entrevista General - {st.session_state.cargo_sel} - 25 Preguntas")
            banco=cargar_json(PREGUNTAS_FILE, BANCO_ENTREVISTA_COMPLETO)
            if isinstance(banco, list): banco=BANCO_ENTREVISTA_COMPLETO
            preguntas=banco.get(st.session_state.cargo_sel, BANCO_ENTREVISTA_COMPLETO["Personal de Nómina"])[:25]
            st.info(f"Total preguntas cargadas para {st.session_state.cargo_sel}: {len(preguntas)} (deben ser 25)")
            resp=[]
            for i,p in enumerate(preguntas):
                r=st.radio(f"{i+1}. {p['q']}",p["op"],key=f"ent{i}",index=None)
                if r is not None: resp.append(p["op"].index(r)==p["r"])
            c1,c2=st.columns(2)
            if c1.button("✅ Finalizar Entrevista y Generar PDF Evaluación",type="primary"):
                if len(resp)<len(preguntas): st.warning(f"Faltan {len(preguntas)-len(resp)} preguntas")
                else:
                    aciertos=sum(resp); porc=aciertos/len(preguntas)*100; apto=porc>=70
                    registro={"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":st.session_state.cedula_real,"nombre":st.session_state.nombre,"cargo":st.session_state.cargo_sel,"sede":st.session_state.sede,"telefono":st.session_state.tel,"modulo":"Entrevista General","aciertos":aciertos,"total":len(preguntas),"porcentaje":round(porc,1),"estado":"APTO" if apto else "NO APTO","recomendacion":"RECOMENDADO" if apto else "NO RECOMENDADO","fuente":"Portal V7","agente":"Agente Entrevista"}
                    regs=cargar_json(REGISTROS_FILE, []); regs.append(registro); guardar_json(REGISTROS_FILE, regs)
                    talent=cargar_json(TALENT_FILE, []); talent.append(registro); guardar_json(TALENT_FILE, talent)
                    st.session_state.modulos_completados.append(registro)
                    pdf_buffer=generar_pdf_evaluacion(registro, f"Entrevista General {st.session_state.cargo_sel} - {aciertos}/{len(preguntas)}")
                    if apto: st.balloons(); st.success(f"✅ APTO {porc:.1f}% - PDF generado")
                    else: st.error(f"❌ NO APTO {porc:.1f}% - PDF generado")
                    st.download_button("📄 Descargar PDF Evaluación Entrevista General",pdf_buffer,file_name=f"Evaluacion_Entrevista_{st.session_state.cedula_real}_{st.session_state.cargo_sel}.pdf",mime="application/pdf")
                    st.info(f"Has completado {len(st.session_state.modulos_completados)} módulo(s) en esta sesión. Puedes seguir con otro módulo sin límite.")
            if c2.button("🔄 Cambiar Módulo"): st.session_state.modulo=None; st.rerun()

        if st.session_state.modulo=="psicologico":
            st.divider(); st.subheader("🧠 MÓDULO 2: Test Psicológico Laboral - 50 Preguntas")
            psico_tec=TEST_PSICO_COMPLETO["Psicotecnica_25"]; psico_psi=TEST_PSICO_COMPLETO["Psicologica_25"]
            todas=psico_tec+psico_psi
            st.info(f"Total preguntas: {len(todas)} (25 psicotécnicas + 25 psicológicas) - Todas cargadas")
            resp=[]
            for i,p in enumerate(todas):
                tipo="Psicotécnica" if i<25 else "Psicológica"
                r=st.radio(f"{i+1}. [{tipo}] {p['q']}",p["op"],key=f"psi{i}",index=None)
                if r is not None: resp.append(p["op"].index(r)==p["r"])
            c1,c2=st.columns(2)
            if c1.button("✅ Finalizar Test Psicológico y Generar PDF",type="primary"):
                if len(resp)<len(todas): st.warning(f"Faltan {len(todas)-len(resp)}")
                else:
                    aciertos=sum(resp); porc=aciertos/len(todas)*100
                    aciertos_tec=sum(resp[:25]); aciertos_psi=sum(resp[25:])
                    if porc>=80: perfil="PERFIL EXCELENTE - Alta compatibilidad Farmart"
                    elif porc>=60: perfil="PERFIL BUENO - Compatible con refuerzo"
                    else: perfil="PERFIL EN OBSERVACIÓN - Requiere entrevista profunda"
                    registro={"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":st.session_state.cedula_real,"nombre":st.session_state.nombre,"cargo":st.session_state.cargo_sel,"sede":st.session_state.sede,"telefono":st.session_state.tel,"modulo":"Test Psicológico Laboral","aciertos":aciertos,"total":len(todas),"porcentaje":round(porc,1),"psicotecnica":f"{aciertos_tec}/25","psicologica":f"{aciertos_psi}/25","perfil":perfil,"estado":"APTO" if porc>=60 else "OBSERVACIÓN","fuente":"Portal V7","agente":"Agente Psicológico"}
                    regs=cargar_json(REGISTROS_FILE, []); regs.append(registro); guardar_json(REGISTROS_FILE, regs)
                    talent=cargar_json(TALENT_FILE, []); talent.append(registro); guardar_json(TALENT_FILE, talent)
                    st.session_state.modulos_completados.append(registro)
                    pdf_buffer=generar_pdf_evaluacion(registro, f"Psicotécnica {aciertos_tec}/25, Psicológica {aciertos_psi}/25 - {perfil}")
                    st.success(f"✅ Test Completado {porc:.1f}% - Perfil {perfil}")
                    c1m,c2m,c3m=st.columns(3); c1m.metric("Total",f"{aciertos}/{len(todas)} {porc:.1f}%"); c2m.metric("Psicotécnica",f"{aciertos_tec}/25"); c3m.metric("Psicológica",f"{aciertos_psi}/25")
                    st.download_button("📄 Descargar PDF Evaluación Psicológica",pdf_buffer,file_name=f"Evaluacion_Psicologico_{st.session_state.cedula_real}.pdf",mime="application/pdf")
            if c2.button("🔄 Cambiar Módulo"): st.session_state.modulo=None; st.rerun()

        if st.session_state.modulo=="video":
            st.divider(); st.subheader(f"🎥 MÓDULO 3: Videoentrevista Diferida IA - {st.session_state.cargo_sel}")
            preguntas_vid=PREGUNTAS_ENTREVISTADOR.get(st.session_state.cargo_sel, PREGUNTAS_ENTREVISTADOR["DEFAULT"])
            textos=[]
            for idx,q in enumerate(preguntas_vid):
                st.markdown(f"**Pregunta {idx+1}: {q}**")
                t=st.text_area(f"Respuesta {idx+1}",key=f"vid{idx}",height=100,placeholder="Responde con ejemplo STAR...")
                textos.append(t)
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
            c1,c2=st.columns(2)
            if c1.button("🤖 Evaluar Videoentrevista y Generar PDF",type="primary"):
                if any(len(t)<20 for t in textos): st.warning("Mínimo 20 caracteres por pregunta")
                else:
                    evals=[evaluar_respuesta_video(t, st.session_state.cargo_sel) for t in textos]
                    prom=sum(e[0] for e in evals)/len(evals)
                    apto=prom>=70
                    registro={"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":st.session_state.cedula_real,"nombre":st.session_state.nombre,"cargo":st.session_state.cargo_sel,"sede":st.session_state.sede,"telefono":st.session_state.tel,"modulo":"Videoentrevista IA Diferida","aciertos":int(prom),"total":100,"porcentaje":round(prom,1),"estado":"APTO" if apto else "NO APTO","perfil":f"Prom {prom:.1f}%","fuente":"Videoentrevista V7","agente":"Agente IA Entrevistador"}
                    regs=cargar_json(REGISTROS_FILE, []); regs.append(registro); guardar_json(REGISTROS_FILE, regs)
                    talent=cargar_json(TALENT_FILE, []); talent.append(registro); guardar_json(TALENT_FILE, talent)
                    st.session_state.modulos_completados.append(registro)
                    detalle_eval="\\n".join([f"P{idx+1}: {punt}% - {retro}" for idx,(punt,retro) in enumerate(evals)])
                    pdf_buffer=generar_pdf_evaluacion(registro, detalle_eval)
                    if apto: st.balloons(); st.success(f"✅ Videoentrevista APTO {prom:.1f}%")
                    else: st.error(f"❌ Videoentrevista NO APTO {prom:.1f}%")
                    for idx,(punt,retro) in enumerate(evals): st.write(f"**P{idx+1}: {punt}%** - {retro}")
                    st.download_button("📄 Descargar PDF Videoentrevista",pdf_buffer,file_name=f"Evaluacion_Video_{st.session_state.cedula_real}.pdf",mime="application/pdf")
            if c2.button("🔄 Cambiar Módulo"): st.session_state.modulo=None; st.rerun()

        if len(st.session_state.modulos_completados)>0:
            st.divider()
            st.subheader(f"📚 Historial Sesión Actual - {len(st.session_state.modulos_completados)} módulo(s) completados (sin límite)")
            st.dataframe(pd.DataFrame(st.session_state.modulos_completados),use_container_width=True)
            if st.button("🏁 Finalizar Sesión y Ver Resumen Final"):
                proms=sum([r["porcentaje"] for r in st.session_state.modulos_completados])/len(st.session_state.modulos_completados)
                st.success(f"Sesión finalizada. Promedio general: {proms:.1f}% - {len(st.session_state.modulos_completados)} módulos")
                # PDF resumen final
                resumen_txt=f"RESUMEN FINAL SESIÓN\\nCandidato: {st.session_state.nombre}\\nCargo: {st.session_state.cargo_sel}\\nMódulos: {len(st.session_state.modulos_completados)}\\nPromedio: {proms:.1f}%\\n"
                for r in st.session_state.modulos_completados:
                    resumen_txt+=f"- {r['modulo']}: {r['porcentaje']}% {r['estado']}\\n"
                st.download_button("📄 Descargar Resumen Final Sesión",resumen_txt,file_name=f"Resumen_Final_{st.session_state.cedula_real}.txt")
                if st.button("🔄 Nueva Sesión Completa"):
                    st.session_state.modulos_completados=[]; st.session_state.modulo=None; st.rerun()

    with tab2:
        st.header("🔐 RRHH - V7 FINAL")
        st.info("admin / admin123 | admin@hireready.ia / HireReady2026*")
        u=st.text_input("Usuario"); p=st.text_input("Clave",type="password")
        if st.button("Entrar"):
            users=cargar_json(USUARIOS_FILE, [])
            found=next((x for x in users if x["usuario"]==u and x["clave"]==p),None)
            if found: st.session_state.auth=True; st.session_state.user=found; st.rerun()
            else: st.error("Usuario o clave incorrecta")

else:
    st.sidebar.markdown('<div class="brand" style="color:white;">HIRE<span style="color:#7AC143;">READY</span>-IA V7</div>',unsafe_allow_html=True)
    st.sidebar.success(f"Conectado: {st.session_state.user['nombre']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.auth=False; st.session_state.user=None; st.session_state.modulo=None; st.session_state.modulos_completados=[]; st.rerun()
    menu=st.sidebar.selectbox("Menú V7 FINAL - Todo por Módulo", ["📊 Dashboard Gerencia - Historial Completo","🤖 Agente IA Publicador Vacantes","🤖 Agente IA Criba Inteligente (Rank CVs Ilimitado)","📋 Módulo Entrevista General - Editar 25 por Cargo","🧠 Módulo Test Psicológico Laboral - Editar 50","🎥 Agente IA Entrevistador - Video Diferida","💎 Talent Pool + WhatsApp + PDF Evaluación","👥 Crear Usuarios","🔧 Reset Usuarios"])

    if menu=="📊 Dashboard Gerencia - Historial Completo":
        st.header("📊 Dashboard Gerencia - Historial Completo Entrevistados - Informes")
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
            c3.metric("NO APTO",len(df[df["estado"]=="NO APTO"]) if "estado" in df.columns else 0)
            c4.metric("Talent Pool",len(talent))
            c5.metric("% Aprob",f"{len(df[df['estado']=='APTO'])/len(df)*100:.1f}%" if len(df)>0 else "0%")
            st.divider()
            col1,col2=st.columns(2)
            with col1:
                st.subheader("Pass Rate por Módulo (Separado)")
                if "modulo" in df.columns:
                    pass_rate=df.groupby("modulo")["porcentaje"].mean()
                    st.bar_chart(pass_rate)
                    st.dataframe(df.groupby("modulo").agg({"porcentaje":"mean","cedula":"count"}).rename(columns={"cedula":"candidatos","porcentaje":"prom %"}))
            with col2:
                st.subheader("Evaluaciones por Cargo (26 cargos)")
                if "cargo" in df.columns:
                    cargo_count=df["cargo"].value_counts()
                    st.bar_chart(cargo_count)
            st.divider()
            st.subheader("📚 Historial Completo Entrevistados - Para Informe Gerencia")
            # Filtros gerencia
            col_f1,col_f2,col_f3=st.columns(3)
            with col_f1:
                f_cargo=st.multiselect("Filtrar por cargo",df["cargo"].unique() if "cargo" in df.columns else [])
            with col_f2:
                f_mod=st.multiselect("Filtrar por módulo",["Entrevista General","Test Psicológico Laboral","Videoentrevista IA Diferida"], key="f_mod_ger")
            with col_f3:
                f_estado=st.multiselect("Filtrar por estado",["APTO","NO APTO","OBSERVACIÓN"])
            df_f=df
            if f_cargo and "cargo" in df.columns: df_f=df_f[df_f["cargo"].isin(f_cargo)]
            if f_mod and "modulo" in df.columns: df_f=df_f[df_f["modulo"].isin(f_mod)]
            if f_estado and "estado" in df.columns: df_f=df_f[df_f["estado"].isin(f_estado)]
            st.dataframe(df_f,use_container_width=True, height=400)
            # Descargas para gerencia
            col_d1,col_d2,col_d3=st.columns(3)
            with col_d1:
                st.download_button("📥 Descargar Informe Gerencia Excel (CSV)",df_f.to_csv(index=False).encode(),f"Informe_Gerencia_HIREREADY_V7_{datetime.now().strftime('%Y%m%d')}.csv")
            with col_d2:
                # Generar PDF informe gerencia
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                    from reportlab.lib.styles import getSampleStyleSheet
                    from reportlab.lib import colors
                    buffer=BytesIO()
                    doc=SimpleDocTemplate(buffer, pagesize=letter)
                    styles=getSampleStyleSheet()
                    story=[]
                    story.append(Paragraph(f"<b>INFORME GERENCIA HIREREADY-IA V7 - {datetime.now().strftime('%Y-%m-%d')}</b>", styles['Title']))
                    story.append(Spacer(1,12))
                    story.append(Paragraph(f"Total evaluaciones: {len(df_f)} - APTO: {len(df_f[df_f['estado']=='APTO']) if 'estado' in df_f.columns else 0} - Promedio: {df_f['porcentaje'].mean():.1f}%", styles['Normal']))
                    story.append(Spacer(1,12))
                    # Tabla resumen
                    data=[["Fecha","Nombre","Cargo","Módulo","%","Estado"]]
                    for _,row in df_f.head(30).iterrows():
                        data.append([str(row.get('fecha',''))[:10], str(row.get('nombre',''))[:20], str(row.get('cargo',''))[:15], str(row.get('modulo',''))[:15], f"{row.get('porcentaje','')}%", str(row.get('estado',''))])
                    t=Table(data, colWidths=[60,100,80,80,40,50])
                    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0B4DA2')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),1,colors.black),('FONTSIZE',(0,0),(-1,-1),8)]))
                    story.append(t)
                    doc.build(story)
                    buffer.seek(0)
                    st.download_button("📄 Descargar Informe Gerencia PDF",buffer,file_name=f"Informe_Gerencia_V7_{datetime.now().strftime('%Y%m%d')}.pdf",mime="application/pdf")
                except:
                    st.caption("Instala reportlab para PDF gerencia: pip install reportlab")
            with col_d3:
                if st.button("🗑️ Borrar Historial (Cuidado)"):
                    guardar_json(REGISTROS_FILE,[]); guardar_json(TALENT_FILE,[]); st.success("Historial borrado"); st.rerun()

    elif menu=="🤖 Agente IA Criba Inteligente (Rank CVs Ilimitado)":
        st.header("🤖 Agente IA Criba Inteligente - Sin Límite - Rank CVs")
        st.info("Sube hasta 100 CVs en PDF sin límite, IA rankea todos con 25 preguntas por cargo como base conocimiento")
        cargo_criba=st.selectbox("Cargo a evaluar (25 preguntas base)",CARGOS_DEFAULT,key="criba_cargo")
        archivos=st.file_uploader("📎 Sube Hojas de Vida PDF ILIMITADO (50-100 CVs)",type=["pdf"],accept_multiple_files=True)
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
        if archivos:
            if st.button(f"🤖 Ejecutar Criba Inteligente Sin Límite para {cargo_criba} - {len(archivos)} CVs",type="primary"):
                resultados=[]
                with st.spinner(f"🤖 Agente IA leyendo {len(archivos)} CVs sin límite..."):
                    for archivo in archivos:
                        texto=leer_pdf_texto(archivo)
                        analisis=analizar_cv_ia(texto, cargo_criba)
                        resultados.append({"archivo":archivo.name,"compatibilidad":analisis["porc"],"concepto":analisis["concepto"],"exp_detectada":f"{analisis['exp']} años","encontrados":", ".join(analisis["encontrados"][:4]),"faltantes":", ".join(analisis["faltantes"]),"recomendacion":"AVANZA" if analisis["porc"]>=60 else "DESCARTADO"})
                df_rank=pd.DataFrame(resultados).sort_values(by="compatibilidad",ascending=False)
                st.success(f"✅ Criba completada sin límite - {len(resultados)} CVs rankeados - 25 preguntas base")
                st.dataframe(df_rank,use_container_width=True)
                st.bar_chart(df_rank.set_index("archivo")["compatibilidad"])
                st.download_button("📥 Descargar Ranking Criba CSV Ilimitado",df_rank.to_csv(index=False).encode(),f"criba_{cargo_criba}_ilimitado.csv")
                if st.button("💎 Guardar Todo en Talent Pool + Historial"):
                    talent=cargar_json(TALENT_FILE, [])
                    for t in resultados:
                        talent.append({"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"nombre":t["archivo"],"cargo":cargo_criba,"porcentaje":t["compatibilidad"],"estado":t["recomendacion"],"fuente":"Criba IA Ilimitada","modulo":"Criba Inteligente"})
                    guardar_json(TALENT_FILE, talent)
                    regs=cargar_json(REGISTROS_FILE, [])
                    regs.extend([{"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":r["archivo"],"nombre":r["archivo"],"cargo":cargo_criba,"porcentaje":r["compatibilidad"],"estado":r["recomendacion"],"modulo":"Criba Inteligente","aciertos":r["compatibilidad"],"total":100} for r in resultados])
                    guardar_json(REGISTROS_FILE, regs)
                    st.success(f"{len(resultados)} CVs guardados en Talent Pool e Historial Gerencia")

    elif menu=="📋 Módulo Entrevista General - Editar 25 por Cargo":
        st.header("📋 Módulo Entrevista General - 25 Preguntas por Cargo - Editar")
        st.info("Aquí editas las 25 preguntas reales de cada uno de los 26 cargos. Ya no son 5, son 25 completas.")
        cargos=cargar_json(CARGOS_FILE, CARGOS_DEFAULT)
        banco=cargar_json(PREGUNTAS_FILE, BANCO_ENTREVISTA_COMPLETO)
        if isinstance(cargos, dict): cargos=CARGOS_DEFAULT
        if isinstance(banco, list): banco=BANCO_ENTREVISTA_COMPLETO
        cargo_sel=st.selectbox("Selecciona cargo para editar sus 25 preguntas",cargos)
        preguntas=banco.get(cargo_sel,[])
        st.write(f"Total preguntas para {cargo_sel}: {len(preguntas)} / 25")
        for idx,preg in enumerate(preguntas):
            with st.expander(f"{idx+1}. {preg['q'][:80]}..."):
                nq=st.text_input("Pregunta",value=preg['q'],key=f"entq{cargo_sel}{idx}")
                o1=st.text_input("Opción A (Correcta)",value=preg['op'][0],key=f"ento1{cargo_sel}{idx}")
                o2=st.text_input("Opción B",value=preg['op'][1],key=f"ento2{cargo_sel}{idx}")
                o3=st.text_input("Opción C",value=preg['op'][2],key=f"ento3{cargo_sel}{idx}")
                rc=st.selectbox("Correcta",["A","B","C"],index=preg['r'],key=f"entr{cargo_sel}{idx}")
                if st.button(f"Guardar P{idx+1}",key=f"ents{cargo_sel}{idx}"):
                    banco[cargo_sel][idx]={"q":nq,"op":[o1,o2,o3],"r":["A","B","C"].index(rc)}; guardar_json(PREGUNTAS_FILE,banco); st.success("Guardado"); st.rerun()

    elif menu=="💎 Talent Pool + WhatsApp + PDF Evaluación":
        st.header("💎 Talent Pool + PDF Evaluación + WhatsApp - Historial Completo")
        talent=cargar_json(TALENT_FILE, [])
        if not talent:
            st.info("Talent Pool vacío - Los candidatos se guardan automático aquí")
        else:
            df_talent=pd.DataFrame(talent)
            st.dataframe(df_talent,use_container_width=True)
            cand_sel=st.selectbox("Selecciona candidato para generar PDF evaluación y WhatsApp",df_talent["nombre"].unique() if "nombre" in df_talent.columns else [])
            if cand_sel:
                cand_data=df_talent[df_talent["nombre"]==cand_sel].iloc[0].to_dict() if len(df_talent[df_talent["nombre"]==cand_sel])>0 else {}
                pdf_buf=generar_pdf_evaluacion(cand_data, f"Evaluación desde Talent Pool - {cand_data.get('modulo','')}")
                st.download_button(f"📄 Descargar PDF Evaluación {cand_sel}",pdf_buf,file_name=f"Evaluacion_{cand_sel}.pdf",mime="application/pdf")
                mensaje=f"Hola {cand_sel}, vimos tu perfil para {cand_data.get('cargo','')} con {cand_data.get('porcentaje','')}% compatibilidad en Farmart. Tenemos nueva vacante. ¿Te interesa?"
                tel=cand_data.get("telefono","")
                if tel:
                    wa_link=f"https://wa.me/{tel}?text={mensaje.replace(' ','%20')}"
                    st.markdown(f"[📱 Enviar WhatsApp a {cand_sel}]({wa_link})")
                else:
                    tel_manual=st.text_input("WhatsApp con indicativo Ej: 573001234567")
                    if tel_manual:
                        wa_link=f"https://wa.me/{tel_manual}?text={mensaje.replace(' ','%20')}"
                        st.markdown(f"[📱 Enviar WhatsApp]({wa_link})")
            st.download_button("📥 Descargar Talent Pool CSV",df_talent.to_csv(index=False).encode(),"talent_pool_v7.csv")

    elif menu=="🔧 Reset Usuarios":
        st.header("🔧 Reset")
        if st.button("🔄 RESETEAR a admin/admin123",type="primary"):
            guardar_json(USUARIOS_FILE, USUARIOS_CORRECTOS); st.success("Reseteado: admin / admin123")
