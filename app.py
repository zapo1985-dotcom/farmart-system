import streamlit as st
import pandas as pd
from datetime import datetime
import json, os, re, random
from io import BytesIO

st.set_page_config(page_title="HIREREADY-IA V10 FINAL", page_icon="💎", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
.stApp{background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%); font-family:'Inter',sans-serif;}
h1,h2,h3{color:#0B4DA2!important; font-weight:800!important;}
.brand{font-size:36px;font-weight:800;color:#0B4DA2;}.brand span{color:#7AC143;}
.hero{background: linear-gradient(135deg, #0B4DA2 0%, #1e40af 50%, #7AC143 100%); color:white; padding:25px; border-radius:20px; text-align:center; box-shadow:0 10px 30px rgba(11,77,162,0.3); margin-bottom:20px;}
.hero h2{color:white!important; margin:0;}
.mod-card{background:white; border-radius:16px; padding:20px; box-shadow:0 4px 12px rgba(0,0,0,0.06); border-left:6px solid #0B4DA2; margin-bottom:15px;}
.kpi-card{background:white; border-radius:16px; padding:18px; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.06);}
.kpi-number{font-size:28px; font-weight:800; color:#0B4DA2;}
.alert-rojo{background:#fee2e2; border-left:6px solid #ef4444; padding:15px; border-radius:10px; margin:10px 0;}
.alert-verde{background:#dcfce7; border-left:6px solid #22c55e; padding:15px; border-radius:10px; margin:10px 0;}
.alert-amarillo{background:#fef3c7; border-left:6px solid #f59e0b; padding:15px; border-radius:10px; margin:10px 0;}
.stButton>button{border-radius:12px!important; font-weight:700!important;}
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
    {"usuario": "admin@hireready.ia", "clave": "HireReady2026*", "rol": "Super Admin", "nombre": "Admin Principal"},
    {"usuario": "rrhh@hireready.ia", "clave": "HireReady2026*", "rol": "RRHH", "nombre": "RRHH HireReady"},
]

def init_all():
    if not os.path.exists(USUARIOS_FILE):
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

CARGOS_DEFAULT = [
    "Personal de Nómina","Tesorería","Auxiliar de bodega de carga","Auxiliar de farmacia",
    "Mensajero de moto","Conductor de carro","Quimico farmaceutico","Regente de farmacia",
    "Auditoria y facturación","Contadores público","Auxiliares contables","Revisores fiscales",
    "Auxiliares de servicios generales","Recursos Humanos","Auxiliares de archivo","Auditores médicos",
    "Operadores logísticos","Ingenieros ambientales","Ingeniero de sistemas","Ingenieros de software",
    "Desarrolladores fullstack","Auxiliares de recursos humanos","Abogados","Alta gerencia",
    "Auxiliares administrativas","Ingenieros especialistas TIC / Ciberseguridad"
]

def gen_preguntas(cargo, n=25):
    base = []
    for i in range(n):
        base.append({
            "q": f"{cargo} - P{i+1}: Procedimiento correcto Farmart para {cargo} caso {i+1}?",
            "op": [f"Procedimiento correcto, seguro y ético para {cargo}", "Procedimiento incorrecto con riesgo", "Omitir o improvisar"],
            "r": 0,
            "tema": f"Tema {i+1} {cargo}"
        })
    return base

BANCO_ENTREVISTA = {}
for c in CARGOS_DEFAULT:
    BANCO_ENTREVISTA[c] = gen_preguntas(c, 25)

BANCO_ENTREVISTA["Personal de Nómina"] = [
    {"q": "Seguridad social integral compone", "op": ["Salud, pensión, ARL, caja compensación", "Solo salud", "Solo ARL"], "r": 0, "tema": "Seguridad social"},
    {"q": "PILA que es", "op": ["Planilla integrada liquidación aportes", "Planilla inventario", "Planilla aseo"], "r": 0, "tema": "PILA"},
    {"q": "Auxilio transporte 2026 se paga si gana hasta", "op": ["2 SMMLV", "5 SMMLV", "Nunca"], "r": 0, "tema": "Auxilio transporte"},
    {"q": "Novedad nómina ejemplo", "op": ["Incapacidad, vacaciones, horas extra", "Solo cambio cargo", "Solo aumento"], "r": 0, "tema": "Novedades"},
    {"q": "Liquidación prestaciones incluye", "op": ["Cesantías, intereses, prima, vacaciones", "Solo salario", "Solo prima"], "r": 0, "tema": "Prestaciones"},
    {"q": "Cesantías consignan antes", "op": ["14 febrero", "31 diciembre", "Cuando renuncia"], "r": 0, "tema": "Cesantías"},
    {"q": "Intereses cesantías porcentaje", "op": ["12% anual", "5%", "20%"], "r": 0, "tema": "Intereses"},
    {"q": "Prima servicios paga", "op": ["Junio y diciembre", "Solo diciembre", "Cada mes"], "r": 0, "tema": "Prima"},
    {"q": "Hora extra diurna recargo", "op": ["25%", "75%", "100%"], "r": 0, "tema": "Horas extra"},
    {"q": "Hora extra nocturna recargo", "op": ["75%", "25%", "0%"], "r": 0, "tema": "Horas extra nocturna"},
    {"q": "Dominical festivo recargo", "op": ["75%", "25%", "10%"], "r": 0, "tema": "Dominical"},
    {"q": "Retención salarios art 383", "op": ["Tabla progresiva DIAN", "Fija 10%", "No aplica"], "r": 0, "tema": "Retención"},
    {"q": "Incapacidad primeros 2 días asume", "op": ["Empleador", "EPS", "ARL"], "r": 0, "tema": "Incapacidad"},
    {"q": "Licencia maternidad", "op": ["18 semanas", "12 semanas", "8 semanas"], "r": 0, "tema": "Licencia maternidad"},
    {"q": "Parafiscales total", "op": ["9% (4% caja,3% ICBF,2% SENA)", "4%", "12%"], "r": 0, "tema": "Parafiscales"},
    {"q": "Aporte salud", "op": ["12.5% (8.5% empleador 4% empleado)", "4%", "8%"], "r": 0, "tema": "Salud"},
    {"q": "Aporte pensión", "op": ["16% (12% empleador 4% empleado)", "4%", "10%"], "r": 0, "tema": "Pensión"},
    {"q": "ARL quien paga", "op": ["100% empleador", "Empleado", "50/50"], "r": 0, "tema": "ARL"},
    {"q": "Vacaciones días año", "op": ["15 días hábiles", "10 días", "30 días"], "r": 0, "tema": "Vacaciones"},
    {"q": "Contrato fijo máximo", "op": ["3 años prorrogable", "1 año", "Indefinido"], "r": 0, "tema": "Contratos"},
    {"q": "Siigo nómina reporte clave", "op": ["Resumen nómina y provisiones", "Inventario", "Ventas"], "r": 0, "tema": "Siigo"},
    {"q": "World Office nómina para", "op": ["Liquidación y PILA", "Facturación", "CRM"], "r": 0, "tema": "World Office"},
    {"q": "Excel buscar salario función", "op": ["BUSCARV/XLOOKUP", "SUMA", "PROMEDIO"], "r": 0, "tema": "Excel"},
    {"q": "Nómina electrónica DIAN frecuencia", "op": ["Mensual", "Anual", "No aplica"], "r": 0, "tema": "Nómina electrónica"},
    {"q": "Falla pago seguridad social consecuencia", "op": ["Sanción y no cobertura", "Nada", "Solo interés"], "r": 0, "tema": "Sanciones"},
]

BANCO_ENTREVISTA["Quimico farmaceutico"] = [
    {"q": "NPT que es", "op": ["Nutrición Parenteral Total", "Norma Producción Técnica", "Nivel Producción Total"], "r": 0, "tema": "NPT"},
    {"q": "Unidosis objetivo", "op": ["Dosis exacta paciente, reduce errores", "Ahorrar empaques", "Vender más"], "r": 0, "tema": "Unidosis"},
    {"q": "Citotóxico que es", "op": ["Destruye células, manejo especial", "Para dolor", "Antibiótico"], "r": 0, "tema": "Citotóxicos"},
    {"q": "Cabina flujo laminar para que", "op": ["Proteger producto, personal y ambiente", "Enfriar", "Iluminar"], "r": 0, "tema": "Cabina"},
    {"q": "Estabilidad mezcla oncología depende", "op": ["Tiempo, temperatura, luz, concentración", "Solo color", "Solo laboratorio"], "r": 0, "tema": "Estabilidad"},
    {"q": "BPM que es", "op": ["Buenas Prácticas Manufactura", "Buen Proceso Manual", "Bodega Producto Médico"], "r": 0, "tema": "BPM"},
    {"q": "Resolución 1403 de 2007", "op": ["Regula servicio farmacéutico", "Regula alimentos", "Regula transito"], "r": 0, "tema": "Res 1403"},
    {"q": "Farmacovigilancia reporta", "op": ["Eventos adversos a medicamentos", "Ventas", "Inventario"], "r": 0, "tema": "Farmacovigilancia"},
    {"q": "Dosis máxima acetaminofén día", "op": ["4 gramos", "10 gramos", "1 gramo"], "r": 0, "tema": "Dosis"},
    {"q": "Interacción warfarina y AINE", "op": ["Aumenta riesgo sangrado", "No pasa nada", "Disminuye efecto"], "r": 0, "tema": "Interacciones"},
    {"q": "Cálculo dosis pediátrica base", "op": ["Peso kg y superficie corporal", "Solo edad", "Solo talla"], "r": 0, "tema": "Pediatría"},
    {"q": "Antídoto acetaminofén", "op": ["N-acetilcisteína", "Flumazenil", "Naloxona"], "r": 0, "tema": "Antídotos"},
    {"q": "Conservación cadena frío vacunas", "op": ["2-8°C", "15-25°C", "-20°C"], "r": 0, "tema": "Cadena frío"},
    {"q": "Medicamento LASA", "op": ["Look Alike Sound Alike, fácil confusión", "Larga acción", "Laxante"], "r": 0, "tema": "LASA"},
    {"q": "Medicamento alto riesgo ejemplo", "op": ["Insulina, heparina, citotóxicos", "Acetaminofén", "Loratadina"], "r": 0, "tema": "Alto riesgo"},
    {"q": "Validación prescripción debe tener", "op": ["Paciente, medicamento, dosis, vía, frecuencia, firma", "Solo nombre", "Solo medicamento"], "r": 0, "tema": "Validación"},
    {"q": "Central mezclas área limpia grado", "op": ["Grado A, B, C, D según INVIMA", "Sin grado", "Grado 1"], "r": 0, "tema": "Áreas limpias"},
    {"q": "Tiempo uso NPT después preparada", "op": ["24 horas refrigerada", "7 días", "1 mes"], "r": 0, "tema": "NPT tiempo"},
    {"q": "Quimioterapia extravasación", "op": ["Emergencia, protocolo antídoto y reporte", "Ignorar", "Solo compresa fría"], "r": 0, "tema": "Extravasación"},
    {"q": "Intervención farmacéutica es", "op": ["Detectar, prevenir y resolver PRM", "Solo dispensar", "Solo facturar"], "r": 0, "tema": "Intervención"},
    {"q": "PRM que es", "op": ["Problema Relacionado con Medicamentos", "Producto Requiere Más", "Precio Regulado Medicamento"], "r": 0, "tema": "PRM"},
    {"q": "Conciliación medicamentosa", "op": ["Comparar medicación habitual vs hospitalaria", "Contar pastillas", "Inventario"], "r": 0, "tema": "Conciliación"},
    {"q": "Antibiótico tiempo dependiente", "op": ["Betalactámicos, tiempo sobre CIM", "Aminoglucósidos", "Azitromicina"], "r": 0, "tema": "Antibiótico"},
    {"q": "Ajuste dosis en falla renal", "op": ["Reducir dosis o intervalo según creatinina", "Aumentar dosis", "No ajustar"], "r": 0, "tema": "Falla renal"},
    {"q": "Rol químico farmacéutico en Farmart", "op": ["Garantizar uso seguro, efectivo y calidad mezclas", "Solo vender", "Solo facturar"], "r": 0, "tema": "Rol QF"},
]

TEST_PSICO = {
    "Psicotecnica_25": [
        {"q": "Compañero toma medicamento sin fórmula, que haces?", "op": ["Reportas por seguridad paciente", "Te callas", "Lo ayudas a vender"], "r": 0, "alerta": "BAJA ETICA si no es A"},
        {"q": "Bajo estrés y mucho trabajo, tú", "op": ["Priorizas, pides ayuda, mantienes calidad", "Gritas y dejas todo", "Haces rápido sin verificar"], "r": 0, "alerta": "RIESGO SEGURIDAD si no es A"},
        {"q": "Jefe pide entregar pedido vencido", "op": ["Te niegas y reportas, ética primero", "Lo entregas", "Cambias fecha vencimiento"], "r": 0, "alerta": "FALTA ETICA GRAVE si no es A"},
        {"q": "Error propio grave, que haces?", "op": ["Lo admites, corriges y reportas inmediato", "Lo ocultas", "Culpas a otro"], "r": 0, "alerta": "DESHONESTIDAD si no es A"},
        {"q": "Ves compañero robando medicamento", "op": ["Reportas con evidencia a RRHH/gerencia", "Te unes", "Te callas por miedo"], "r": 0, "alerta": "COMPLICIDAD si no es A"},
        {"q": "Te ofrecen coima proveedor", "op": ["Rechazas y reportas, transparencia", "Aceptas", "Negocias más"], "r": 0, "alerta": "CORRUPCIÓN si no es A"},
        {"q": "Confidencialidad datos paciente", "op": ["Nunca compartir, Habeas Data Ley 1581", "Contar a amigos", "Publicar en redes"], "r": 0, "alerta": "VIOLA HABEAS DATA si no es A"},
        {"q": "Prioridad: que primero?", "op": ["Seguridad paciente, luego calidad, luego velocidad", "Velocidad primero", "Lo más fácil primero"], "r": 0, "alerta": "NO ENTIENDE PRIORIDAD si no es A"},
        {"q": "Trabajas con quimio citotóxico, que prima?", "op": ["Seguridad, EPP, procedimiento, no atajos", "Rapidez", "Ahorrar guantes"], "r": 0, "alerta": "RIESGO QUIMICO si no es A"},
        {"q": "Dilema: entregar sin fórmula para no perder venta?", "op": ["No, exige fórmula, seguridad primero", "Sí entrega", "Depende cliente"], "r": 0, "alerta": "RIESGO LEGAL si no es A"},
        {"q": "Manejo frustración", "op": ["Respiras, analizas, buscas solución, pides ayuda", "Explosión emocional", "Abandonas tarea"], "r": 0, "alerta": "BAJA TOLERANCIA si no es A"},
        {"q": "Si ves condición insegura en bodega", "op": ["Reportas, señalizas, propones corrección", "Ignoras", "Solo te quejas"], "r": 0, "alerta": "INDIFERENCIA RIESGO si no es A"},
        {"q": "Paciente reclama agresivo por demora", "op": ["Escuchas, empatía, buscas solución, escalas", "Gritas también", "Ignoras"], "r": 0, "alerta": "MAL SERVICIO si no es A"},
        {"q": "Olvidaste proceso clave, que haces?", "op": ["Verificas procedimiento, preguntas, no inventas", "Improvisas", "Omites paso"], "r": 0, "alerta": "IMPROVISACIÓN PELIGROSA si no es A"},
        {"q": "Meta imposible de cumplir", "op": ["Comunicas a tiempo, propones plan, pides apoyo", "Mientes que sí cumpliste", "No haces nada"], "r": 0, "alerta": "MENTIRA si no es A"},
        {"q": "Cambio de turno y queda pendiente crítico", "op": ["Entregas completo, escrito y verbal", "Te vas sin decir", "Dejas nota confusa"], "r": 0, "alerta": "IRRESPONSABLE si no es A"},
        {"q": "Jefe te grita injustamente", "op": ["Mantienes calma, pides hablar en privado, respetuoso", "Gritas más fuerte", "Renuncias gritando"], "r": 0, "alerta": "REACTIVO si no es A"},
        {"q": "Compañero nuevo lento", "op": ["Apoyas, enseñas, paciencia", "Te burlas", "Lo ignoras"], "r": 0, "alerta": "MAL EQUIPO si no es A"},
        {"q": "Detectas casi error (near miss)", "op": ["Reportas como aprendizaje, sin culpa", "Ocultas por miedo sanción", "Culpas sistema"], "r": 0, "alerta": "CULTURA CULPA si no es A"},
        {"q": "Feedback negativo de auditoría", "op": ["Lo tomas como mejora, plan acción", "Te enojas y discutes", "Ignoras"], "r": 0, "alerta": "NO ACEPTA FEEDBACK si no es A"},
        {"q": "Puntualidad para ti", "op": ["Responsabilidad y respeto equipo y paciente", "Opcional", "Si quiero"], "r": 0, "alerta": "IMPUNTUAL si no es A"},
        {"q": "Aprendizaje continuo", "op": ["Te actualizas, lees normativa, cursos", "No necesito aprender más", "Solo si me obligan"], "r": 0, "alerta": "ESTANCADO si no es A"},
        {"q": "Liderazgo en Farmart es", "op": ["Ejemplo, servicio, escucha, resultados con gente", "Gritar y mandar", "Solo ordenar"], "r": 0, "alerta": "LIDERAZGO AUTORITARIO si no es A"},
        {"q": "Por qué quieres trabajar en Farmart?", "op": ["Me identifica propósito salud, ética, crecimiento", "Solo por plata", "No tengo otra opción"], "r": 0, "alerta": "SOLO DINERO si no es A"},
        {"q": "Trabajo en equipo es", "op": ["Apoyar, comunicar, respetar, cumplir", "Hacer solo mi parte", "Competir contra todos"], "r": 0, "alerta": "INDIVIDUALISTA si no es A"},
    ],
    "Psicologica_25": [
        {"q": "Cuando te critican, tú", "op": ["Escuchas, evalúas, mejoras", "Te ofendes y atacas", "Ignoras todo"], "r": 0, "alerta": "SUSCEPTIBLE si no es A"},
        {"q": "Tomas decisiones bajo presión", "op": ["Analizas rápido, con calma, con datos", "Impulsivo sin pensar", "Paralizas, no decides"], "r": 0, "alerta": "IMPULSIVO/PARALIZADO si no es A"},
        {"q": "Trabajo monótono y repetitivo", "op": ["Mantienes calidad y concentración", "Te distraes y cometes errores", "Te aburres y dejas"], "r": 0, "alerta": "BAJA CONCENTRACIÓN si no es A"},
        {"q": "Conflicto con compañero", "op": ["Dialogas, buscas acuerdo, respeto", "Evitas y hablas mal a espaldas", "Confrontas agresivo"], "r": 0, "alerta": "PASIVO-AGRESIVO o AGRESIVO si no es A"},
        {"q": "Cometes error pequeño", "op": ["Lo reconoces y corriges rápido", "Lo ocultas hasta que crece", "Culpas a otro"], "r": 0, "alerta": "OCULTA ERRORES si no es A"},
        {"q": "Cambio repentino de planes", "op": ["Te adaptas con flexibilidad", "Te frustras y bloqueas", "Te niegas al cambio"], "r": 0, "alerta": "RÍGIDO si no es A"},
        {"q": "Recibes orden poco clara", "op": ["Preguntas hasta entender bien", "Supones y haces mal", "No haces nada"], "r": 0, "alerta": "SUPONE si no es A"},
        {"q": "Presión por tiempo", "op": ["Organizas, priorizas, mantienes calidad", "Te estresas y baja calidad", "Ignoras tiempo"], "r": 0, "alerta": "SE DESBORDA si no es A"},
        {"q": "Fracaso en proyecto", "op": ["Analizas qué falló, aprendes, intentas de nuevo", "Buscas culpables", "Abandonas"], "r": 0, "alerta": "CULPA EXTERNA si no es A"},
        {"q": "Normas que no compartes", "op": ["Las cumples mientras propones mejora por canal", "Las rompes", "Las ignoras"], "r": 0, "alerta": "REBELDE si no es A"},
        {"q": "Manejo de información confidencial", "op": ["Discreción total, nunca comentas", "Comentas con familia/amigos", "Publicas indirectas"], "r": 0, "alerta": "INDISCRETO si no es A"},
        {"q": "Motivación principal", "op": ["Aprender, aportar, crecer, propósito", "Solo salario", "Evitar aburrimiento"], "r": 0, "alerta": "BAJA MOTIVACIÓN INTRÍNSECA si no es A"},
        {"q": "Cuando estás cansado", "op": ["Avisas, priorizas seguridad, pides apoyo", "Sigues igual arriesgando error", "Te escondes y no trabajas"], "r": 0, "alerta": "RIESGO FATIGA si no es A"},
        {"q": "Honestidad ante todo", "op": ["Verdad aunque duela, con respeto", "Mentira piadosa si conviene", "Ocultas por conveniencia"], "r": 0, "alerta": "MENTIROSO si no es A"},
        {"q": "Tolerancia a la frustración", "op": ["Alta, persistente, buscas alternativas", "Baja, abandonas rápido", "Media, te quejas mucho"], "r": 0, "alerta": "BAJA TOLERANCIA si no es A"},
        {"q": "Empatía con paciente", "op": ["Alta, te pones en su lugar, ayudas", "Baja, indiferente", "Solo si es amable"], "r": 0, "alerta": "BAJA EMPATÍA si no es A"},
        {"q": "Responsabilidad", "op": ["Asumes consecuencias de tus actos", "Evitas responsabilidad", "Solo si te conviene"], "r": 0, "alerta": "EVADE RESPONSABILIDAD si no es A"},
        {"q": "Integridad", "op": ["Haces lo correcto aunque nadie vea", "Solo si te ven", "Depende si te conviene"], "r": 0, "alerta": "INTEGRIDAD SITUACIONAL si no es A"},
        {"q": "Te piden quedarte extra no planeado", "op": ["Evalúas, apoyas si puedes, comunicas", "Te enojas y te vas", "Aceptas pero con mala actitud"], "r": 0, "alerta": "MALA ACTITUD si no es A"},
        {"q": "Trabajas solo vs en equipo", "op": ["Te adaptas a ambos, comunicas", "Solo solo, odias equipo", "Solo equipo, no puedes solo"], "r": 0, "alerta": "NO COLABORA si no es A"},
        {"q": "Éxito de compañero", "op": ["Te alegras, felicitas, aprendes", "Sientes envidia y criticas", "Te es indiferente"], "r": 0, "alerta": "ENVIDIA si no es A"},
        {"q": "Trabajo con personas difíciles", "op": ["Empatía, límites sanos, profesional", "Evitas totalmente", "Confrontas siempre"], "r": 0, "alerta": "EVITA CONFLICTO o AGRESIVO si no es A"},
        {"q": "Autonomía en tu trabajo", "op": ["Tomas iniciativa dentro de tu rol y reportas", "Esperas que te digan todo", "Haces lo que quieres sin reportar"], "r": 0, "alerta": "DEPENDIENTE o REBELDE si no es A"},
        {"q": "Respeto a la autoridad", "op": ["Respeto con criterio, propones con respeto", "Sumisión total sin pensar", "Rebeldía constante"], "r": 0, "alerta": "SUMISO o REBELDE si no es A"},
        {"q": "PREGUNTA INCOMODA: Has robado en un trabajo anterior?", "op": ["Nunca, valoro honestidad", "Prefiero no responder", "Todos lo han hecho alguna vez"], "r": 0, "alerta": "EVASIVO / POSIBLE ROBO si no es A"},
    ],
    "Imagenes_5": [
        {"q": "IMAGEN 1: Ves una mancha negra con bordes irregulares. Que interpretas? (Test proyectivo)", "op": ["Veo una oportunidad para analizar con calma", "Veo algo feo y me asusta", "No veo nada"], "r": 0, "interpreta": "A= Pensamiento analítico, B= Ansiedad, C= Bloqueo"},
        {"q": "IMAGEN 2: Dos personas discutiendo frente a ti. Que haces?", "op": ["Intervengo con calma y busco mediar", "Me alejo para no meterme en problemas", "Tomo partido por el que me cae mejor"], "r": 0, "interpreta": "A= Mediador, B= Evasivo, C= Parcializado"},
        {"q": "IMAGEN 3: Un reloj marcando las 11:55 PM y mucho trabajo pendiente", "op": ["Priorizo lo crítico y comunico avance", "Me estreso y me paralizo", "Dejo todo para mañana"], "r": 0, "interpreta": "A= Gestión presión, B= Ansiedad, C= Procrastinación"},
        {"q": "IMAGEN 4: Una caja cerrada con etiqueta CONFIDENCIAL", "op": ["No la abro, respeto confidencialidad", "La abro por curiosidad", "La abro si nadie me ve"], "r": 0, "interpreta": "A= Alta confidencialidad, B y C= Baja confidencialidad"},
        {"q": "IMAGEN 5: Un paciente llorando en farmacia", "op": ["Me acerco con empatía y ofrezco ayuda", "Lo ignoro, no es mi problema", "Le digo que se calme y se vaya"], "r": 0, "interpreta": "A= Alta empatía, B y C= Baja empatía"},
    ],
    "Incomodas_Bobas_5": [
        {"q": "PREGUNTA BOBA: Si pudieras ser un medicamento, cual serías y por qué?", "op": ["Sería un antibiótico, porque ayudo a curar con precisión", "Sería una droga recreativa", "No sé, cualquiera"], "r": 0, "interpreta": "A= Propósito, B= Riesgo, C= Falta creatividad"},
        {"q": "PREGUNTA INCOMODA: Tu último jefe era malo?", "op": ["Tuve aprendizajes, prefiero hablar de lo que aportó", "Sí, era pésimo", "No comento de jefes anteriores"], "r": 0, "interpreta": "A= Profesional, B= Quejumbroso, C= Evasivo"},
        {"q": "PREGUNTA BOBA: Cuántos ladrillos se necesitan para hacer un hospital?", "op": ["Depende del diseño, pero lo importante es planear con seguridad y calidad", "No sé, muchos", "Esa pregunta es estúpida"], "r": 0, "interpreta": "A= Pensamiento lógico, B= Simplista, C= Reactivo"},
        {"q": "PREGUNTA INCOMODA: Has mentido en una entrevista?", "op": ["No, prefiero ser honesto aunque pierda la oportunidad", "Todos mienten un poco", "Prefiero no responder"], "r": 0, "interpreta": "A= Honesto, B= Normaliza mentira, C= Evasivo"},
        {"q": "PREGUNTA INCOMODA: Que harías si ves a tu jefe haciendo algo ilegal?", "op": ["Reportaría por canal ético, con evidencia, pensando en paciente y empresa", "Me callaría por miedo", "Me uniría si me conviene"], "r": 0, "interpreta": "A= Ético, B= Miedo, C= Corrupto"},
    ]
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
        story.append(Paragraph("<b>HIREREADY-IA V10 - INFORME TECNICO PARA HV</b>", styles['Title']))
        story.append(Spacer(1, 12))
        porc = registro.get('porcentaje', 0)
        if porc >= 90:
            rango = "90-100% ALTAMENTE CONFIABLE - ALTAMENTE RECOMENDADO"
            recomend = "Listo para contratar. Sabe de su trabajo. Confiabilidad ALTA. Reforzar solo temas menores."
            confi = "95% Confiable"
        elif porc >= 80:
            rango = "80-89% CONFIABLE CON RECOMENDACIONES"
            recomend = "Recomendado con plan de refuerzo 30 días en: " + registro.get('temas_bajos', 'temas específicos') + ". Supervisión quincenal."
            confi = "85% Confiable"
        elif porc >= 60:
            rango = "60-79% EN OBSERVACION - CONFIABILIDAD MEDIA"
            recomend = "No recomendado para cargo crítico sin 60 días refuerzo intensivo y re-evaluación."
            confi = "65% Confiable"
        else:
            rango = "0-59% NO RECOMENDADO - NO CONFIABLE"
            recomend = "No sabe de su trabajo o graves vacíos. No contratar para Farmart."
            confi = "30% No confiable"

        story.append(Paragraph(f"<b>Fecha:</b> {registro.get('fecha','')}<br/><b>Candidato:</b> {registro.get('nombre','')} CC {registro.get('cedula','')}<br/><b>Cargo:</b> {registro.get('cargo','')}<br/><b>Sede:</b> {registro.get('sede','')} Tel: {registro.get('telefono','')}", styles['Normal']))
        story.append(Spacer(1, 12))
        data = [
            ["Concepto", "Resultado"],
            ["Módulo", registro.get('modulo','')],
            ["Aciertos", f"{registro.get('aciertos','')}/{registro.get('total','')}"],
            ["Porcentaje", f"{porc}%"],
            ["Rango Confiabilidad", rango],
            ["Nivel Confianza Contratación", confi],
            ["Estado", registro.get('estado','')],
            ["Sabe de su trabajo?", "SI" if porc>=80 else "PARCIAL" if porc>=60 else "NO"],
            ["Recomendación Contratación", recomend],
        ]
        t = Table(data, colWidths=[160, 340])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B4DA2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>Temas a reforzar:</b> {registro.get('temas_bajos','Ninguno crítico')}<br/><b>Observaciones:</b> {registro.get('observaciones','')}", styles['Normal']))
        story.append(Spacer(1, 24))
        story.append(Paragraph("Firma RRHH ___________________ Gerencia ___________________", styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        txt = f"INFORME TECNICO {registro.get('nombre','')} {registro.get('porcentaje','')}%"
        return BytesIO(txt.encode())

def generar_pdf_psicologico(registro):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph("<b>HIREREADY-IA V10 - INFORME PSICOLOGICO Y PSICOTECNICO CONFIDENCIAL</b>", styles['Title']))
        story.append(Spacer(1, 12))
        porc = registro.get('porcentaje', 0)
        story.append(Paragraph(f"<b>Candidato:</b> {registro.get('nombre','')} CC {registro.get('cedula','')}<br/><b>Fecha:</b> {registro.get('fecha','')}<br/><b>Porcentaje:</b> {porc}%<br/><b>Psicotécnica:</b> {registro.get('psicotecnica','')}<br/><b>Psicológica:</b> {registro.get('psicologica','')}<br/><b>Imágenes:</b> {registro.get('imagenes','')}<br/><b>Incómodas/Bobas:</b> {registro.get('incomodas','')}", styles['Normal']))
        story.append(Spacer(1, 12))
        # Alertas personalidad
        alertas = registro.get('alertas', [])
        if alertas:
            story.append(Paragraph("<b>🚨 ALERTAS PERSONALIDAD DISTORSIONADA:</b>", styles['Heading2']))
            for al in alertas:
                story.append(Paragraph(f"- {al}", styles['Normal']))
            story.append(Spacer(1, 12))
        # Rango confiabilidad
        if porc >= 90:
            rango_psico = "PERFIL ALTAMENTE CONFIABLE - Sin distorsiones, alta ética, listo para cargo crítico"
        elif porc >= 80:
            rango_psico = "PERFIL CONFIABLE CON OBSERVACIONES MENORES - Requiere seguimiento"
        elif porc >= 60:
            rango_psico = "PERFIL EN OBSERVACION - Posibles distorsiones, requiere entrevista profunda con psicólogo"
        else:
            rango_psico = "PERFIL NO CONFIABLE - ALERTA PERSONALIDAD DISTORSIONADA - No contratar sin evaluación clínica"

        data = [
            ["Rango Psicológico", rango_psico],
            ["Recomendación", registro.get('perfil','')],
            ["Confidencialidad", "ALTA" if porc>=80 else "MEDIA" if porc>=60 else "BAJA - RIESGO"],
            ["Confiable contratar?", "SI - ALTAMENTE CONFIABLE" if porc>=90 else "SI con refuerzo" if porc>=80 else "NO sin terapia/evaluación"],
        ]
        t = Table(data, colWidths=[150, 350])
        t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7AC143')), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        story.append(t)
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>Interpretación imágenes:</b> {registro.get('interpretacion_imagenes','')}<br/><b>Interpretación incómodas/bobas:</b> {registro.get('interpretacion_incomodas','')}", styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        txt = f"INFORME PSICOLOGICO {registro.get('nombre','')} {registro.get('porcentaje','')}% Alertas: {registro.get('alertas','')}"
        return BytesIO(txt.encode())

# SESSION
if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None
    st.session_state.user_type = None
if "modulo" not in st.session_state:
    st.session_state.modulo = None
if "asignacion_actual" not in st.session_state:
    st.session_state.asignacion_actual = None

# LOGIN
if not st.session_state.auth:
    st.markdown('<div class="hero"><h2>💎 HIREREADY-IA V10 FINAL - FARMART</h2><p>26 Cargos x 25 Preguntas | PDF HV + PDF Psicológico | Imágenes + Incómodas + Alertas</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="mod-card" style="border-left-color:#7AC143;"><h3>👤 SOY CANDIDATO - Ingreso por CÉDULA</h3><p>El administrador te asigna pruebas según cargo. Solo ingresas cédula y presentas.</p></div>', unsafe_allow_html=True)
        cedula_login = st.text_input("📇 CÉDULA para iniciar prueba *", placeholder="Ej: 1234567890")
        if st.button("🚀 INGRESAR A MIS PRUEBAS ASIGNADAS", use_container_width=True, type="primary"):
            asignaciones = cargar_json(ASIGNACIONES_FILE, [])
            mi_asig = [a for a in asignaciones if a.get('cedula') == cedula_login and a.get('estado')!= 'COMPLETADO']
            if not mi_asig:
                # Buscar si ya tiene registro previo
                regs = cargar_json(REGISTROS_FILE, [])
                tiene = [r for r in regs if r.get('cedula') == cedula_login]
                if tiene:
                    st.warning(f"Ya presentaste pruebas con esa cédula. Si RRHH te re-asignó, contacta a RRHH para reactivar. Historial: {len(tiene)} pruebas")
                else:
                    st.error("❌ No tienes pruebas asignadas aún. El administrador de RRHH debe asignarte pruebas primero por tu cargo. Contacta a RRHH.")
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
        st.info("Demo candidato: Si eres admin, primero asigna pruebas en panel RRHH > Asignar Pruebas por Cédula")

    with col2:
        st.markdown('<div class="mod-card" style="border-left-color:#0B4DA2;"><h3>🔐 SOY RRHH / ADMIN</h3><p>Asignas pruebas por cédula y cargo, ves informes PDF técnico y psicológico con rangos confiabilidad.</p></div>', unsafe_allow_html=True)
        u = st.text_input("Usuario", placeholder="admin")
        p = st.text_input("Clave", type="password", placeholder="admin123")
        if st.button("🔐 INGRESAR PANEL RRHH", use_container_width=True):
            users = cargar_json(USUARIOS_FILE, [])
            found = next((x for x in users if x["usuario"] == u and x["clave"] == p), None)
            if found:
                st.session_state.auth = True
                st.session_state.user = found
                st.session_state.user_type = "admin"
                st.rerun()
            else:
                st.error("Usuario o clave incorrecta. Prueba: admin / admin123")

else:
    # CANDIDATO LOGUEADO
    if st.session_state.user_type == "candidate":
        asig = st.session_state.asignacion_actual
        st.markdown(f'<div class="hero"><h2>👤 Bienvenido {asig.get("nombre","")} | CC {asig.get("cedula","")} | Cargo: {asig.get("cargo","")}</h2><p>Pruebas asignadas: {", ".join(asig.get("modulos", []))}</p></div>', unsafe_allow_html=True)
        if st.button("🚪 Salir"):
            st.session_state.auth = False
            st.session_state.user_type = None
            st.session_state.asignacion_actual = None
            st.rerun()

        modulos_asignados = asig.get('modulos', ["Entrevista General"])

        if "Entrevista General" in modulos_asignados:
            st.divider()
            st.subheader(f"📋 MÓDULO: Entrevista General - {asig.get('cargo','')} - 25 Preguntas")
            banco = cargar_json(PREGUNTAS_FILE, BANCO_ENTREVISTA)
            preguntas = banco.get(asig.get('cargo',''), [])[:25]
            resp = []
            temas_fallos = []
            for i, pr in enumerate(preguntas):
                r = st.radio(f"{i+1}. {pr['q']}", pr["op"], key=f"ent{i}", index=None)
                if r is not None:
                    es_ok = pr["op"].index(r) == pr["r"]
                    resp.append(es_ok)
                    if not es_ok:
                        temas_fallos.append(pr.get('tema', f"Tema {i+1}"))
            if st.button("✅ Finalizar Entrevista General y Generar PDF Técnico para HV", type="primary"):
                if len(resp) < len(preguntas):
                    st.warning(f"Faltan {len(preguntas)-len(resp)} preguntas")
                else:
                    aciertos = sum(resp)
                    porc = aciertos / len(preguntas) * 100
                    apto = porc >= 70
                    if porc >= 90:
                        estado = "ALTA CONFIABILIDAD - ALTAMENTE RECOMENDADO"
                        obs = "Sabe de su trabajo. Confiable contratar. Reforzar temas menores."
                    elif porc >= 80:
                        estado = "CONFIABLE CON RECOMENDACIONES - RECOMENDADO CON RESERVA"
                        obs = f"Reforzar: {', '.join(temas_fallos[:3])} en 30 días"
                    elif porc >= 60:
                        estado = "EN OBSERVACION - CONFIABILIDAD MEDIA"
                        obs = "Requiere 60 días refuerzo intensivo"
                    else:
                        estado = "NO RECOMENDADO - NO SABE / NO CONFIABLE"
                        obs = "No sabe de su trabajo, no contratar"

                    registro = {
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cedula": asig.get('cedula',''),
                        "nombre": asig.get('nombre',''),
                        "cargo": asig.get('cargo',''),
                        "sede": asig.get('sede',''),
                        "telefono": asig.get('telefono',''),
                        "modulo": "Entrevista General",
                        "aciertos": aciertos,
                        "total": len(preguntas),
                        "porcentaje": round(porc, 1),
                        "estado": estado,
                        "temas_bajos": ", ".join(temas_fallos[:5]) if temas_fallos else "Ninguno crítico",
                        "observaciones": obs,
                        "fuente": "Asignación RRHH",
                        "agente": "Agente Entrevista"
                    }
                    regs = cargar_json(REGISTROS_FILE, [])
                    regs.append(registro)
                    guardar_json(REGISTROS_FILE, regs)
                    talent = cargar_json(TALENT_FILE, [])
                    talent.append(registro)
                    guardar_json(TALENT_FILE, talent)
                    # Marcar asignación como en proceso
                    asignaciones = cargar_json(ASIGNACIONES_FILE, [])
                    for a in asignaciones:
                        if a.get('cedula') == asig.get('cedula') and "Entrevista General" in a.get('modulos', []):
                            a['estado'] = 'EN PROCESO'
                    guardar_json(ASIGNACIONES_FILE, asignaciones)

                    pdf_buf = generar_pdf_tecnico(registro)
                    if apto:
                        st.balloons()
                        st.success(f"✅ {porc:.1f}% - {estado}")
                    else:
                        st.error(f"❌ {porc:.1f}% - {estado}")
                    st.download_button("📄 Descargar PDF Informe Técnico para anexar a HV", pdf_buf, file_name=f"Informe_Tecnico_{asig.get('cedula','')}_{asig.get('cargo','')}.pdf", mime="application/pdf")

        if "Test Psicologico Laboral" in modulos_asignados or "Test Psicológico Laboral" in modulos_asignados:
            st.divider()
            st.subheader("🧠 MÓDULO: Test Psicológico Laboral - 60 Preguntas - Con Imágenes + Incómodas/Bobas")
            todas_psico = TEST_PSICO["Psicotecnica_25"] + TEST_PSICO["Psicologica_25"] + TEST_PSICO["Imagenes_5"] + TEST_PSICO["Incomodas_Bobas_5"]
            st.info(f"Total: 25 Psicotécnicas + 25 Psicológicas + 5 Imágenes + 5 Incómodas/Bobas = {len(todas_psico)} preguntas")
            resp_psico = []
            alertas = []
            interpret_imagenes = []
            interpret_incomodas = []
            for i, pr in enumerate(todas_psico):
                tipo = "Psicotécnica" if i < 25 else "Psicológica" if i < 50 else "Imagen" if i < 55 else "Incómoda/Boba"
                r = st.radio(f"{i+1}. [{tipo}] {pr['q']}", pr["op"], key=f"psi_v10_{i}", index=None)
                if r is not None:
                    es_ok = pr["op"].index(r) == pr["r"]
                    resp_psico.append(es_ok)
                    if not es_ok and "alerta" in pr:
                        alertas.append(f"{pr['q'][:50]}... -> {pr['alerta']}")
                    if tipo == "Imagen" and "interpreta" in pr:
                        interpret_imagenes.append(f"P{i+1}: {pr['interpreta']} - Resp: {r[:30]}")
                    if tipo == "Incómoda/Boba" and "interpreta" in pr:
                        interpret_incomodas.append(f"P{i+1}: {pr['interpreta']} - Resp: {r[:30]}")

            if st.button("✅ Finalizar Test Psicológico y Generar PDF Psicológico Confidencial", type="primary"):
                if len(resp_psico) < len(todas_psico):
                    st.warning(f"Faltan {len(todas_psico)-len(resp_psico)} preguntas")
                else:
                    aciertos = sum(resp_psico)
                    porc = aciertos / len(todas_psico) * 100
                    aciertos_tec = sum(resp_psico[:25])
                    aciertos_psi = sum(resp_psico[25:50])
                    aciertos_img = sum(resp_psico[50:55])
                    aciertos_inc = sum(resp_psico[55:60])

                    if porc >= 90:
                        perfil = "ALTAMENTE CONFIABLE - Sin distorsiones, alta ética"
                        conf = "95% Confiable - Recomiendo contratar"
                    elif porc >= 80:
                        perfil = "CONFIABLE CON OBSERVACIONES - Requiere seguimiento"
                        conf = "85% Confiable - Recomiendo contratar con refuerzo 30 días"
                    elif porc >= 60:
                        perfil = "EN OBSERVACION - Posible distorsión personalidad"
                        conf = "65% Confiable - No contratar sin evaluación psicológica profunda"
                    else:
                        perfil = "NO CONFIABLE - ALERTA PERSONALIDAD DISTORSIONADA"
                        conf = "30% No confiable - No recomiendo contratar"

                    registro = {
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cedula": asig.get('cedula',''),
                        "nombre": asig.get('nombre',''),
                        "cargo": asig.get('cargo',''),
                        "sede": asig.get('sede',''),
                        "telefono": asig.get('telefono',''),
                        "modulo": "Test Psicológico Laboral",
                        "aciertos": aciertos,
                        "total": len(todas_psico),
                        "porcentaje": round(porc, 1),
                        "psicotecnica": f"{aciertos_tec}/25",
                        "psicologica": f"{aciertos_psi}/25",
                        "imagenes": f"{aciertos_img}/5",
                        "incomodas": f"{aciertos_inc}/5",
                        "perfil": perfil,
                        "estado": conf,
                        "alertas": alertas,
                        "interpretacion_imagenes": "; ".join(interpret_imagenes),
                        "interpretacion_incomodas": "; ".join(interpret_incomodas),
                        "fuente": "Asignación RRHH",
                        "agente": "Agente Psicológico"
                    }
                    regs = cargar_json(REGISTROS_FILE, [])
                    regs.append(registro)
                    guardar_json(REGISTROS_FILE, regs)
                    talent = cargar_json(TALENT_FILE, [])
                    talent.append(registro)
                    guardar_json(TALENT_FILE, talent)

                    pdf_buf = generar_pdf_psicologico(registro)
                    if porc >= 80:
                        st.success(f"✅ {porc:.1f}% - {perfil}")
                    else:
                        st.error(f"❌ {porc:.1f}% - {perfil}")

                    if alertas:
                        st.markdown('<div class="alert-rojo"><b>🚨 ALERTAS PERSONALIDAD DISTORSIONADA DETECTADAS:</b><br>' + "<br>".join(alertas[:5]) + "</div>", unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="alert-verde"><b>✅ Sin alertas personalidad distorsionada</b></div>', unsafe_allow_html=True)

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Total", f"{aciertos}/{len(todas_psico)} {porc:.1f}%")
                    c2.metric("Psicotécnica", f"{aciertos_tec}/25")
                    c3.metric("Imágenes", f"{aciertos_img}/5")
                    c4.metric("Incómodas/Bobas", f"{aciertos_inc}/5")

                    st.download_button("📄 Descargar PDF Informe Psicológico Confidencial", pdf_buf, file_name=f"Informe_Psicologico_{asig.get('cedula','')}.pdf", mime="application/pdf")

    # ADMIN
    else:
        st.sidebar.markdown('<div style="color:white; font-weight:800; font-size:22px;">💎 HIRE<span style="color:#7AC143;">READY</span> V10</div>', unsafe_allow_html=True)
        st.sidebar.success(f"🔐 {st.session_state.user['nombre']}")
        if st.sidebar.button("🚪 Cerrar sesión"):
            st.session_state.auth = False
            st.session_state.user = None
            st.session_state.user_type = None
            st.session_state.asignacion_actual = None
            st.rerun()

        menu = st.sidebar.selectbox("Menú V10 FINAL", ["📊 Dashboard Gerencia + Informes PDF", "📝 Asignar Pruebas por Cédula (Admin asigna)", "🤖 Criba Inteligente Ilimitada", "📋 Editar 25 Preguntas por Cargo", "💎 Talent Pool + PDFs + WhatsApp", "🔧 Reset Usuarios"])

        if menu == "📝 Asignar Pruebas por Cédula (Admin asigna)":
            st.markdown('<div class="hero"><h2>📝 Asignar Pruebas por Cédula - Admin Dirige</h2><p>El candidato solo ingresa cédula y presenta. Tú decides cargo y módulos.</p></div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                cedula_asig = st.text_input("📇 Cédula candidato *", placeholder="Ej: 1234567890")
                nombre_asig = st.text_input("👤 Nombre completo *", placeholder="Ej: Juan Pérez")
                cargo_asig = st.selectbox("💼 Cargo / Profesión *", CARGOS_DEFAULT)
            with col2:
                sede_asig = st.text_input("📍 Ciudad", placeholder="Ej: Cali")
                tel_asig = st.text_input("📱 WhatsApp", placeholder="Ej: 573001234567")
                modulos_asig = st.multiselect("🧩 Módulos a asignar *", ["Entrevista General", "Test Psicologico Laboral"], default=["Entrevista General", "Test Psicologico Laboral"])

            if st.button("✅ ASIGNAR PRUEBAS A CANDIDATO POR CÉDULA", type="primary", use_container_width=True):
                if not (cedula_asig and nombre_asig and modulos_asig):
                    st.error("Cédula, nombre y módulos obligatorios")
                else:
                    asignaciones = cargar_json(ASIGNACIONES_FILE, [])
                    nueva = {
                        "fecha_asignacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cedula": cedula_asig,
                        "nombre": nombre_asig,
                        "cargo": cargo_asig,
                        "sede": sede_asig,
                        "telefono": tel_asig,
                        "modulos": modulos_asig,
                        "asignado_por": st.session_state.user['nombre'],
                        "estado": "PENDIENTE"
                    }
                    asignaciones.append(nueva)
                    guardar_json(ASIGNACIONES_FILE, asignaciones)
                    st.success(f"✅ Pruebas asignadas a {nombre_asig} CC {cedula_asig} para {cargo_asig} - Módulos: {', '.join(modulos_asig)}. El candidato ya puede ingresar solo con cédula.")
                    st.balloons()

            st.divider()
            st.subheader("📚 Asignaciones Activas")
            asignaciones = cargar_json(ASIGNACIONES_FILE, [])
            if asignaciones:
                df_asig = pd.DataFrame(asignaciones)
                st.dataframe(df_asig, use_container_width=True)
                st.download_button("📥 Descargar Asignaciones CSV", df_asig.to_csv(index=False).encode(), "asignaciones_v10.csv")
                if st.button("🗑️ Limpiar Asignaciones Completadas"):
                    pendientes = [a for a in asignaciones if a.get('estado')!= 'COMPLETADO']
                    guardar_json(ASIGNACIONES_FILE, pendientes)
                    st.success("Limpiadas")
                    st.rerun()
            else:
                st.info("Sin asignaciones aún. Asigna la primera arriba.")

        elif menu == "📊 Dashboard Gerencia + Informes PDF":
            st.markdown('<div class="hero"><h2>📊 Dashboard Gerencia - Informes PDF Técnico + Psicológico</h2></div>', unsafe_allow_html=True)
            regs = cargar_json(REGISTROS_FILE, [])
            if not regs:
                st.info("Sin registros aún")
            else:
                df = pd.DataFrame(regs)
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-number">{len(df)}</div><div>Total Evaluaciones</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:#22c55e;">{len(df[df["porcentaje"]>=90]) if "porcentaje" in df.columns else 0}</div><div>90%+ Altamente Confiable</div></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:#f59e0b;">{len(df[(df["porcentaje"]>=80) & (df["porcentaje"]<90)]) if "porcentaje" in df.columns else 0}</div><div>80-89% Recomendado</div></div>', unsafe_allow_html=True)
                with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-number" style="color:#ef4444;">{len(df[df["porcentaje"]<60]) if "porcentaje" in df.columns else 0}</div><div><60% No Recomendado</div></div>', unsafe_allow_html=True)
                with c5: st.markdown(f'<div class="kpi-card"><div class="kpi-number">{df["porcentaje"].mean():.1f}%</div><div>Promedio</div></div>', unsafe_allow_html=True)

                st.divider()
                # Filtros
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    f_cargo = st.multiselect("Filtrar cargo", df["cargo"].unique() if "cargo" in df.columns else [])
                with col_f2:
                    f_mod = st.multiselect("Filtrar módulo", ["Entrevista General", "Test Psicológico Laboral"])
                with col_f3:
                    f_estado = st.multiselect("Filtrar confiabilidad", ["ALTAMENTE CONFIABLE", "CONFIABLE", "OBSERVACION", "NO CONFIABLE"])

                df_f = df
                if f_cargo and "cargo" in df.columns:
                    df_f = df_f[df_f["cargo"].isin(f_cargo)]
                if f_mod and "modulo" in df.columns:
                    df_f = df_f[df_f["modulo"].isin(f_mod)]

                st.dataframe(df_f, use_container_width=True, height=400)

                st.subheader("📄 Generar PDFs para HV")
                cand_sel = st.selectbox("Selecciona candidato para generar PDFs", df_f["cedula"].unique() if "cedula" in df_f.columns else [])
                if cand_sel:
                    cand_regs = df_f[df_f["cedula"] == cand_sel]
                    if len(cand_regs) > 0:
                        for _, row in cand_regs.iterrows():
                            reg_dict = row.to_dict()
                            col_pdf1, col_pdf2 = st.columns(2)
                            with col_pdf1:
                                if "Entrevista General" in str(reg_dict.get('modulo','')):
                                    pdf_tec = generar_pdf_tecnico(reg_dict)
                                    st.download_button(f"📄 PDF Técnico HV - {reg_dict.get('modulo','')} - {reg_dict.get('porcentaje','')}%", pdf_tec, file_name=f"Informe_Tecnico_{cand_sel}_{reg_dict.get('modulo','')}.pdf", mime="application/pdf", key=f"tec_{cand_sel}_{row.name}")
                            with col_pdf2:
                                if "Psicológico" in str(reg_dict.get('modulo','')):
                                    pdf_psi = generar_pdf_psicologico(reg_dict)
                                    st.download_button(f"🧠 PDF Psicológico Confidencial - {reg_dict.get('porcentaje','')}%", pdf_psi, file_name=f"Informe_Psicologico_{cand_sel}.pdf", mime="application/pdf", key=f"psi_{cand_sel}_{row.name}")

                            # Mostrar rango confiabilidad
                            porc = reg_dict.get('porcentaje', 0)
                            if porc >= 90:
                                st.markdown(f'<div class="alert-verde"><b>✅ {porc}% - 90%+ ALTAMENTE CONFIABLE - SÍ sabe de su trabajo - Recomiendo contratar sin restricciones - Confiabilidad 95% - Solo reforzar temas menores</b></div>', unsafe_allow_html=True)
                            elif porc >= 80:
                                st.markdown(f'<div class="alert-amarillo"><b>⚠️ {porc}% - 80-89% CONFIABLE CON RECOMENDACIONES - Sabe parcialmente - Recomiendo contratar con plan refuerzo 30 días: {reg_dict.get("temas_bajos","")}</b></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="alert-rojo"><b>🚨 {porc}% - NO CONFIABLE - No sabe o vacíos graves - No recomiendo contratar - Requiere refuerzo total</b></div>', unsafe_allow_html=True)

                            if reg_dict.get('alertas'):
                                st.markdown('<div class="alert-rojo"><b>🚨 ALERTAS PERSONALIDAD DISTORSIONADA:</b><br>' + "<br>".join(reg_dict.get('alertas', [])[:3]) + "</div>", unsafe_allow_html=True)

                st.download_button("📥 Descargar Informe Gerencia CSV", df_f.to_csv(index=False).encode(), f"Informe_Gerencia_V10_{datetime.now().strftime('%Y%m%d')}.csv")

        elif menu == "💎 Talent Pool + PDFs + WhatsApp":
            st.header("💎 Talent Pool + PDFs")
            talent = cargar_json(TALENT_FILE, [])
            if talent:
                df_talent = pd.DataFrame(talent)
                st.dataframe(df_talent, use_container_width=True)
                cand = st.selectbox("Candidato", df_talent["cedula"].unique() if "cedula" in df_talent.columns else [])
                if cand:
                    regs_cand = df_talent[df_talent["cedula"] == cand]
                    for _, r in regs_cand.iterrows():
                        rd = r.to_dict()
                        if "Entrevista General" in str(rd.get('modulo','')):
                            pdf_t = generar_pdf_tecnico(rd)
                            st.download_button(f"📄 PDF Técnico {rd.get('nombre','')} {rd.get('porcentaje','')}%", pdf_t, file_name=f"Tecnico_{cand}.pdf", mime="application/pdf", key=f"t_talent_{cand}_{r.name}")
                        else:
                            pdf_p = generar_pdf_psicologico(rd)
                            st.download_button(f"🧠 PDF Psicológico {rd.get('nombre','')} {rd.get('porcentaje','')}%", pdf_p, file_name=f"Psicologico_{cand}.pdf", mime="application/pdf", key=f"p_talent_{cand}_{r.name}")
            else:
                st.info("Talent Pool vacío")

        elif menu == "🔧 Reset Usuarios":
            st.header("🔧 Reset")
            if st.button("🔄 RESETEAR a admin/admin123", type="primary"):
                guardar_json(USUARIOS_FILE, USUARIOS_CORRECTOS)
                st.success("Reseteado: admin / admin123 | admin@hireready.ia / HireReady2026*")
                st.json(USUARIOS_CORRECTOS)
