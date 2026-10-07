import streamlit as st
import pandas as pd
from datetime import datetime
import json, os, re, random
from io import BytesIO

st.set_page_config(page_title="HIREREADY-IA V10 Enterprise", page_icon="🏆", layout="wide")

st.markdown("""
<style>
.stApp{background:#f8fafc;} h1,h2,h3{color:#0B4DA2!important; font-weight:800!important;}
.brand{font-size:36px;font-weight:800;color:#0B4DA2;}.brand span{color:#7AC143;}
.hero{background: linear-gradient(135deg, #0B4DA2 0%, #7AC143 100%); color:white; padding:25px; border-radius:16px; text-align:center; margin-bottom:20px;}
.kpi{background:white; border-radius:16px; padding:18px; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.06); border-top:4px solid #0B4DA2;}
.mod-card{background:white; border-radius:12px; padding:16px; border-left:6px solid #0B4DA2; box-shadow:0 2px 8px rgba(0,0,0,0.05); margin-bottom:10px;}
.alert-card{background:#fef2f2; border:1px solid #fecaca; border-left:6px solid #ef4444; padding:12px; border-radius:8px; margin:8px 0;}
.ok-card{background:#f0fdf4; border:1px solid #bbf7d0; border-left:6px solid #7AC143; padding:12px; border-radius:8px; margin:8px 0;}
[data-testid="stSidebar"]{background:#0B4DA2;} [data-testid="stSidebar"] *{color:white!important;}
.stButton>button{border-radius:10px!important; font-weight:700!important;}
</style>
""", unsafe_allow_html=True)

USUARIOS_FILE="usuarios_admin.json"; REGISTROS_FILE="registros_farmart.json"; CARGOS_FILE="cargos.json"; PREGUNTAS_FILE="preguntas_banco.json"; ASIGNACIONES_FILE="asignaciones.json"; TALENT_FILE="talent_pool.json"

def cargar_json(p, default=None):
    try:
        with open(p,"r", encoding="utf-8") as f: return json.load(f)
    except: return default if default is not None else []
def guardar_json(p,d):
    with open(p,"w", encoding="utf-8") as f: json.dump(d,f,indent=2,ensure_ascii=False)

USUARIOS_CORRECTOS=[
    {"usuario":"admin","clave":"admin123","rol":"Super Admin","nombre":"Admin RRHH","email":"admin@hireready.ia"},
    {"usuario":"admin@hireready.ia","clave":"HireReady2026*","rol":"Super Admin","nombre":"Admin Principal"},
    {"usuario":"rrhh@hireready.ia","clave":"HireReady2026*","rol":"RRHH","nombre":"RRHH Farmart"},
]

def init_users(): guardar_json(USUARIOS_FILE, USUARIOS_CORRECTOS)

CARGOS_DEFAULT=["Personal de Nómina","Tesorería","Auxiliar de bodega de carga","Auxiliar de farmacia","Mensajero de moto","Conductor de carro","Quimico farmaceutico","Regente de farmacia","Auditoria y facturación","Contadores público","Auxiliares contables","Revisores fiscales","Auxiliares de servicios generales","Recursos Humanos","Auxiliares de archivo","Auditores médicos","Operadores logísticos","Ingenieros ambientales","Ingeniero de sistemas","Ingenieros de software","Desarrolladores fullstack","Auxiliares de recursos humanos","Abogados","Alta gerencia","Auxiliares administrativas","Ingenieros especialistas TIC / Ciberseguridad"]

# === BANCO 25 PREGUNTAS POR CARGO ===
def generar_banco():
    banco={}
    banco["Personal de Nómina"]=[
        {"q":"Seguridad social integral compone","op":["Salud, pensión, ARL, caja","Solo salud","Solo ARL"],"r":0, "tema":"Seguridad Social"},
        {"q":"PILA que es","op":["Planilla integrada liquidación aportes","Inventario","Aseo"],"r":0, "tema":"PILA"},
        {"q":"Auxilio transporte cuándo se paga","op":["Hasta 2 SMMLV","Todos","Nunca"],"r":0, "tema":"Auxilio"},
        {"q":"Novedad nómina ejemplo","op":["Incapacidad, vacaciones, horas extra","Solo cargo","Solo aumento"],"r":0, "tema":"Novedades"},
        {"q":"Liquidación prestaciones incluye","op":["Cesantías, intereses, prima, vacaciones","Solo salario","Solo prima"],"r":0, "tema":"Prestaciones"},
        {"q":"Cesantías se consignan","op":["Antes 14 feb","31 dic","Cuando renuncia"],"r":0, "tema":"Cesantías"},
        {"q":"Intereses cesantías %","op":["12% anual","5%","20%"],"r":0, "tema":"Cesantías"},
        {"q":"Prima servicios se paga","op":["Junio y diciembre","Solo diciembre","Mensual"],"r":0, "tema":"Prima"},
        {"q":"Hora extra diurna recargo","op":["25%","75%","100%"],"r":0, "tema":"Horas Extra"},
        {"q":"Hora extra nocturna","op":["75%","25%","0%"],"r":0, "tema":"Horas Extra"},
        {"q":"Dominical festivo","op":["75%","25%","10%"],"r":0, "tema":"Recargos"},
        {"q":"Retención art 383","op":["Tabla progresiva DIAN","Fija 10%","No aplica"],"r":0, "tema":"Retención"},
        {"q":"Incapacidad primeros 2 días","op":["Empleador","EPS","ARL"],"r":0, "tema":"Incapacidades"},
        {"q":"Licencia maternidad","op":["18 semanas","12 semanas","8 semanas"],"r":0, "tema":"Licencias"},
        {"q":"Parafiscales total","op":["9% (4% caja,3% ICBF,2% SENA)","4%","12%"],"r":0, "tema":"Parafiscales"},
        {"q":"Aporte salud","op":["12.5%","4%","8%"],"r":0, "tema":"Aportes"},
        {"q":"Aporte pensión","op":["16%","4%","10%"],"r":0, "tema":"Aportes"},
        {"q":"ARL quien paga","op":["100% empleador","Empleado","50/50"],"r":0, "tema":"ARL"},
        {"q":"Vacaciones año","op":["15 días hábiles","10 días","30 días"],"r":0, "tema":"Vacaciones"},
        {"q":"Contrato fijo máximo","op":["3 años","1 año","Indefinido"],"r":0, "tema":"Contratación"},
        {"q":"Siigo reporte clave nómina","op":["Resumen nómina y provisiones","Inventario","Ventas"],"r":0, "tema":"Siigo"},
        {"q":"World Office nómina","op":["Liquidación y PILA","Facturación","CRM"],"r":0, "tema":"World Office"},
        {"q":"Excel buscar salario función","op":["BUSCARV/XLOOKUP","SUMA","PROMEDIO"],"r":0, "tema":"Excel"},
        {"q":"Nómina electrónica frecuencia","op":["Mensual","Anual","No aplica"],"r":0, "tema":"Nómina Electrónica"},
        {"q":"Falla pago seguridad social","op":["Sanción y no cobertura","Nada","Solo interés"],"r":0, "tema":"Cumplimiento"},
    ]
    for cargo in CARGOS_DEFAULT:
        if cargo not in banco:
            banco[cargo]=[{"q":f"{cargo} P{i+1}: ¿Procedimiento correcto caso {i+1}?","op":[f"Correcto {cargo}", "Incorrecto", "Omitir"],"r":0, "tema":f"Tema {i+1}"} for i in range(25)]
    return banco

BANCO_ENTREVISTA=generar_banco()

# === TEST PSICOLOGÍA V10 CON IMÁGENES + INCÓMODAS + BOBAS ===
TEST_PSICO_V10={
"Psicotecnicas_15":[
    {"q":"Compañero toma medicamento sin fórmula, ¿qué haces?","op":["Reportas por seguridad paciente","Te callas","Lo ayudas a vender"],"r":0, "riesgo":"Baja"},
    {"q":"Jefe pide entregar pedido vencido","op":["Te niegas y reportas, ética primero","Lo entregas","Cambias fecha"],"r":0, "riesgo":"Baja"},
    {"q":"Ves compañero robando medicamento","op":["Reportas con evidencia","Te unes","Te callas"],"r":0, "riesgo":"Baja"},
    {"q":"Te ofrecen coima proveedor","op":["Rechazas y reportas","Aceptas","Negocias más"],"r":0, "riesgo":"Baja"},
    {"q":"Confidencialidad datos paciente Ley 1581","op":["Nunca compartir","Contar amigos","Publicar redes"],"r":0, "riesgo":"Baja"},
    {"q":"Cambio turno queda pendiente crítico","op":["Entregas completo escrito y verbal","Te vas sin decir","Nota confusa"],"r":0, "riesgo":"Media"},
    {"q":"Detectas casi error (near miss)","op":["Reportas como aprendizaje","Ocultas miedo","Culpas sistema"],"r":0, "riesgo":"Media"},
    {"q":"Prioridad en Farmart","op":["Seguridad paciente, calidad, velocidad","Velocidad primero","Fácil primero"],"r":0, "riesgo":"Media"},
    {"q":"Trabajas con quimio citotóxico, ¿qué prima?","op":["Seguridad, EPP, procedimiento","Rapidez","Ahorrar guantes"],"r":0, "riesgo":"Media"},
    {"q":"Entregar sin fórmula para no perder venta","op":["No, exige fórmula","Sí entrega","Depende cliente"],"r":0, "riesgo":"Alta"},
    {"q":"Error propio grave, ¿qué haces?","op":["Admites, corriges, reportas inmediato","Ocultas","Culpas a otro"],"r":0, "riesgo":"Baja"},
    {"q":"Paciente reclama agresivo","op":["Escuchas, empatía, solución","Gritas también","Ignoras"],"r":0, "riesgo":"Media"},
    {"q":"Meta imposible de cumplir","op":["Comunicas a tiempo, propones plan","Mientes que sí cumpliste","No haces nada"],"r":0, "riesgo":"Media"},
    {"q":"Jefe te grita injustamente","op":["Calma, hablar privado, respeto","Gritas más fuerte","Renuncias gritando"],"r":0, "riesgo":"Alta"},
    {"q":"Condición insegura en bodega","op":["Reportas, señalizas, corriges","Ignoras","Solo te quejas"],"r":0, "riesgo":"Media"},
],
"Psicologicas_15":[
    {"q":"Cuando te critican, tú","op":["Escuchas, evalúas, mejoras","Te ofendes y atacas","Ignoras todo"],"r":0, "riesgo":"Media"},
    {"q":"Tomas decisiones bajo presión","op":["Analizas rápido, calma, datos","Impulsivo sin pensar","Paralizas"],"r":0, "riesgo":"Alta"},
    {"q":"Trabajo monótono y repetitivo","op":["Mantienes calidad concentración","Distraes errores","Aburres dejas"],"r":0, "riesgo":"Media"},
    {"q":"Conflicto con compañero","op":["Dialogas acuerdo respeto","Evitas hablas mal","Confrontas agresivo"],"r":0, "riesgo":"Alta"},
    {"q":"Cometes error pequeño","op":["Reconoces corriges rápido","Ocultas hasta que crece","Culpas otro"],"r":0, "riesgo":"Baja"},
    {"q":"Cambio repentino de planes","op":["Adaptas flexibilidad","Frustras bloqueas","Niegas cambio"],"r":0, "riesgo":"Media"},
    {"q":"Presión por tiempo","op":["Organizas priorizas calidad","Estresas baja calidad","Ignoras tiempo"],"r":0, "riesgo":"Media"},
    {"q":"Fracaso en proyecto","op":["Analizas aprendes intentas","Buscas culpables","Abandonas"],"r":0, "riesgo":"Media"},
    {"q":"Honestidad ante todo","op":["Verdad aunque duela con respeto","Mentira si conviene","Ocultas conveniencia"],"r":0, "riesgo":"Alta"},
    {"q":"Tolerancia a la frustración","op":["Alta persistente alternativas","Baja abandonas rápido","Media quejas"],"r":0, "riesgo":"Alta"},
    {"q":"Empatía con paciente","op":["Alta te pones lugar ayudas","Baja indiferente","Solo si amable"],"r":0, "riesgo":"Baja"},
    {"q":"Responsabilidad","op":["Asumes consecuencias actos","Evitas responsabilidad","Solo si conviene"],"r":0, "riesgo":"Baja"},
    {"q":"Integridad","op":["Correcto aunque nadie vea","Solo si te ven","Depende conviene"],"r":0, "riesgo":"Alta"},
    {"q":"Motivación principal","op":["Aprender aportar crecer propósito","Solo salario","Evitar aburrimiento"],"r":0, "riesgo":"Media"},
    {"q":"¿Por qué Farmart?","op":["Propósito salud, ética, crecimiento","Solo plata","No opción"],"r":0, "riesgo":"Baja"},
],
"Imagenes_5":[
    {"q":"🖼️ IMAGEN 1: Ves una imagen de una balanza con un corazón de un lado y dinero del otro. ¿Qué interpretas?","op":["Equilibrio entre propósito y rentabilidad, ética primero","Solo dinero importa","Solo corazón, no importa negocio"],"r":0, "tipo":"Valor Ético"},
    {"q":"🖼️ IMAGEN 2: Un equipo cruzando un puente estrecho con cajas frágiles. ¿Qué ves?","op":["Trabajo en equipo, cuidado, seguridad paciente, apoyo mutuo","Cada uno por su lado","Dejar caer cajas"],"r":0, "tipo":"Trabajo Equipo"},
    {"q":"🖼️ IMAGEN 3: Un reloj derritiéndose con medicamentos al fondo. ¿Qué interpretas?","op":["Tiempo crítico en salud, vencimientos, urgencia pero sin saltar procedimientos","Tiempo no importa","Entregar todo rápido sin verificar"],"r":0, "tipo":"Gestión Tiempo"},
    {"q":"🖼️ IMAGEN 4: Una persona con 2 caras, una sonríe al jefe y otra grita al compañero. ¿Qué ves?","op":["Doble personalidad, falsedad, riesgo para clima laboral","Normal, todos lo hacen","No veo problema"],"r":0, "tipo":"Personalidad - Alerta Distorsión"},
    {"q":"🖼️ IMAGEN 5: Un laberinto con una luz al final y huellas de otros. ¿Qué interpretas?","op":["Perseverancia, aprendizaje de otros, buscar salida con ética","Abandonar laberinto","Romper paredes"],"r":0, "tipo":"Resiliencia"},
],
"Incomodas_5":[
    {"q":"❓ INCÓMODA 1: ¿Has robado alguna vez en un trabajo anterior aunque sea algo pequeño?","op":["No, nunca, ética innegociable","Sí, pero fue poco","Depende si nadie ve"],"r":0, "tipo":"Honestidad Extrema"},
    {"q":"❓ INCÓMODA 2: Si tu jefe te pide mentir a un paciente sobre un medicamento, ¿lo harías para no perder el empleo?","op":["No, nunca, reporto por canal ético, seguridad paciente primero","Sí, necesito empleo","Depende del paciente"],"r":0, "tipo":"Ética vs Empleo"},
    {"q":"❓ INCÓMODA 3: ¿Qué es lo peor que has hecho en un trabajo y no te descubrieron?","op":["Nada grave, siempre he sido transparente, si cometí error lo reporté","Varias cosas pero no digo","He ocultado errores graves"],"r":0, "tipo":"Transparencia"},
    {"q":"❓ INCÓMODA 4: ¿Hablas mal de tus jefes anteriores? ¿Cómo te expresas de ellos?","op":["Habla con respeto, aprendí de ellos, enfoco en aprendizaje","Habla mal, culpa a jefes","Evita responder"],"r":0, "tipo":"Lealtad"},
    {"q":"❓ INCÓMODA 5: Si ves que un compañero va a ser despedido injustamente, ¿te callas para no meterte en problemas?","op":["No, apoyo con evidencias, hablo por canal correcto","Me callo, no es mi problema","Me uno para que lo despidan"],"r":0, "tipo":"Solidaridad"},
],
"Bobas_5":[
    {"q":"🤪 BOBA 1: Si pudieras ser un medicamento, ¿cuál serías y por qué?","op":["Respuesta creativa con propósito de ayudar, ej: analgésico quita dolor, antibiótico cura","Respuesta sin sentido","No sé, no respondo"],"r":0, "tipo":"Creatividad"},
    {"q":"🤪 BOBA 2: ¿Cuántas pelotas de tenis caben en una central de mezclas?","op":["Hace cálculo lógico, estima volumen, muestra pensamiento estructurado","Dice número sin justificar","Se enoja, dice que pregunta es tonta"],"r":0, "tipo":"Pensamiento Lógico"},
    {"q":"🤪 BOBA 3: Si los medicamentos hablaran, ¿qué diría una caja vencida?","op":["Respuesta empática, reconoce riesgo, habla de seguridad y responsabilidad","Respuesta burlona sin ética","No responde"],"r":0, "tipo":"Empatía"},
    {"q":"🤪 BOBA 4: ¿Prefieres ser Batman o Robin en el equipo de Farmart?","op":["Explica rol con humildad, Batman lidera con ejemplo, Robin apoya clave, ambos importantes","Solo Batman, quiero mandar","Solo Robin, no quiero responsabilidad"],"r":0, "tipo":"Rol Equipo"},
    {"q":"🤪 BOBA 5: Si te quedan 3 minutos de vida, ¿qué le dirías a tu jefe?","op":["Mensaje de agradecimiento, aprendizaje, cierre ético","Reclamo o insulto","Nada"],"r":0, "tipo":"Cierre Emocional"},
]
}

if not os.path.exists(CARG
