import streamlit as st
import pandas as pd
from datetime import datetime
import json, os, re

st.set_page_config(page_title="HIREREADY-IA V5.1", page_icon="🤖", layout="wide")
st.markdown("""
<style>
.stApp {background:#f8fafc;} h1,h2,h3{color:#0B4DA2!important;}
.stButton>button{background:#0B4DA2;color:white;border-radius:10px;font-weight:bold;}
.stButton>button:hover{background:#7AC143;color:white;}
[data-testid="stSidebar"]{background:#0B4DA2;}
[data-testid="stSidebar"] *{color:white!important;}
.ia-box{background:linear-gradient(135deg,#0B4DA2 0%,#7AC143 100%);color:white;padding:18px;border-radius:12px;margin-bottom:12px;}
.brand{font-size:32px;font-weight:800;color:#0B4DA2;}.brand span{color:#7AC143;}
.step{background:#0B4DA2;color:white;padding:8px 14px;border-radius:20px;font-weight:bold;display:inline-block;margin:4px;}
</style>
""", unsafe_allow_html=True)

USUARIOS_FILE="usuarios_admin.json"; REGISTROS_FILE="registros_farmart.json"; CARGOS_FILE="cargos.json"; PREGUNTAS_FILE="preguntas_banco.json"; CONFIG_FILE="config_excel.json"

def cargar_json(p):
    with open(p,"r") as f: return json.load(f)
def guardar_json(p,d):
    with open(p,"w") as f: json.dump(d,f,indent=2,ensure_ascii=False)

USUARIOS_CORRECTOS = [
    {"usuario":"admin","clave":"admin123","rol":"Super Admin","nombre":"Admin Simple"},
    {"usuario":"admin@hireready.ia","clave":"HireReady2026*","rol":"Super Admin","nombre":"Admin Principal"},
    {"usuario":"rrhh@hireready.ia","clave":"HireReady2026*","rol":"RRHH","nombre":"RRHH HireReady"},
    {"usuario":"admin@farmart.system","clave":"Farmart2026*","rol":"Super Admin","nombre":"Admin Farmart"},
    {"usuario":"gerencia@hireready.ia","clave":"Gerencia2026*","rol":"Gerencia RRHH","nombre":"Gerencia"}
]

def inicializar_usuarios():
    if not os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE,"w") as f:
            json.dump(USUARIOS_CORRECTOS,f,indent=2)
    else:
        try:
            users = cargar_json(USUARIOS_FILE)
            for uc in USUARIOS_CORRECTOS:
                if not any(u["usuario"]==uc["usuario"] for u in users):
                    users.append(uc)
            guardar_json(USUARIOS_FILE,users)
        except:
            with open(USUARIOS_FILE,"w") as f:
                json.dump(USUARIOS_CORRECTOS,f,indent=2)

if not os.path.exists(REGISTROS_FILE):
    with open(REGISTROS_FILE,"w") as f: json.dump([],f)

CARGOS_DEFAULT=["Personal de Nómina","Tesorería","Auxiliar de bodega de carga","Auxiliar de farmacia","Mensajero de moto","Conductor de carro","Quimico farmaceutico","Regente de farmacia","Auditoria y facturación","Contadores público","Auxiliares contables","Revisores fiscales","Auxiliares de servicios generales","Recursos Humanos","Auxiliares de archivo","Auditores médicos","Operadores logísticos","Ingenieros ambientales","Ingeniero de sistemas","Ingenieros de software","Desarrolladores fullstack","Auxiliares de recursos humanos","Abogados","Alta gerencia","Auxiliares administrativas","Ingenieros especialistas TIC / Ciberseguridad"]

BANCO_TECNICO_25={
"Personal de Nómina":[
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
],
"Tesorería":[
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
],
"Quimico farmaceutico":[
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
],
"Abogados":[
{"q":"Tutela término fallo primera instancia","op":["10 días","30 días","6 meses"],"r":0},
{"q":"Tutela medicamento vital argumento","op":["Vida, salud, mínimo vital, medida provisional","Solo trabajo","Solo petición"],"r":0},
{"q":"Ley 80 principio clave","op":["Transparencia, economía, responsabilidad","Rapidez","Menor precio"],"r":0},
{"q":"Derecho petición término general","op":["15 días hábiles","1 año","3 días"],"r":0},
{"q":"Contratación EPS Farmart tipo","op":["Prestación servicios salud","Compraventa","Arrendamiento"],"r":0},
{"q":"Cláusula penal en contrato","op":["Estimación anticipada perjuicios","Multa DIAN","Impuesto"],"r":0},
{"q":"Despido sin justa causa consecuencia","op":["Indemnización art 64 CST","Nada","Solo carta"],"r":0},
{"q":"Contrato prestación servicios vs laboral diferencia","op":["Subordinación, horario, prestación personal","Solo salario","No hay diferencia"],"r":0},
{"q":"Acción popular protege","op":["Derechos colectivos","Derecho individual","Solo empresas"],"r":0},
{"q":"Habeas data ley","op":["1581 de 2012","100 de 1993","80 de 1993"],"r":0},
{"q":"SARLAFT que es","op":["Prevención lavado activos y financiación terrorismo","Salud","Seguridad industrial"],"r":0},
{"q":"Responsabilidad farmacéutica por error dispensación","op":["Civil, penal y administrativa","Solo administrativa","Ninguna"],"r":0},
{"q":"INVIMA sanción por mala práctica central mezclas","op":["Cierre temporal, multa, suspensión","Felicitación","Nada"],"r":0},
{"q":"Conciliación extrajudicial requisito","op":["Procedibilidad en laboral y civil","Opcional siempre","Prohibida"],"r":0},
{"q":"Término prescripción laboral","op":["3 años","1 año","10 años"],"r":0},
{"q":"Tutela contra EPS por no entrega oncológico juez puede","op":["Ordenar entrega 48h y medida provisional","Negar siempre","Solo multar usuario"],"r":0},
{"q":"Contrato estatal Farmart con hospital público ley aplica","op":["Ley 80 y 1150","Solo código comercio","Solo CST"],"r":0},
{"q":"Cláusula confidencialidad en central mezclas","op":["Proteger fórmulas y datos pacientes","No necesaria","Opcional"],"r":0},
{"q":"Due diligence en compra droguería","op":["Revisar licencias INVIMA, sanciones, laboral, tributario","Solo precio","Solo inventario"],"r":0},
{"q":"Petición, queja, reclamo Farmart responde","op":["15 días hábiles con trazabilidad","1 año","No responde"],"r":0},
{"q":"Comité ética farmacéutica debe","op":["Evaluar casos críticos y eventos adversos","Solo fiestas","Solo nómina"],"r":0},
{"q":"Ley 100 de 1993","op":["Crea sistema seguridad social integral","Regula tránsito","Regula ambiente"],"r":0},
{"q":"Responsabilidad por medicamento vencido dispensado","op":["Grave, puede ser homicidio culposo si causa muerte","Leve","No hay responsabilidad"],"r":0},
{"q":"Contrato suministro medicamentos cláusula clave","op":["Calidad, cadena frío, entrega oportuna, sanciones","Solo precio","Solo cantidad"],"r":0},
{"q":"Ética abogado Farmart","op":["Defender vida y salud, transparencia, no corrupción","Ocultar errores","Cobrar coima"],"r":0},
],
}

for c in CARGOS_DEFAULT:
    if c not in BANCO_TECNICO_25:
        BANCO_TECNICO_25[c]=[{"q":f"{c} - Técnica {i+1}: Procedimiento correcto según Farmart?","op":[f"Procedimiento correcto para {c}","Incorrecto con riesgo","Omitir"],"r":0} for i in range(25)]

EXCEL_REAL_25=[{"q":"Excel: ¿SUMA rango A1:A100?","op":["=SUMA(A1:A100)","=ADD A1:A100","SUMAR(A1:A100)"],"r":0},{"q":"BUSCARV sirve para","op":["Buscar valor en tabla y traer dato","Borrar","Crear gráfico"],"r":0},{"q":"XLOOKUP ventaja","op":["Busca a izquierda y derecha, más rápido","Solo suma","No existe"],"r":0},{"q":"Tabla dinámica sirve para","op":["Resumir miles datos en segundos","Escribir cartas","Navegar internet"],"r":0},{"q":"SUMAR.SI.CONJUNTO","op":["Suma con múltiples criterios","Suma todo","Cuenta"],"r":0},{"q":"CONTAR.SI","op":["Cuenta celdas que cumplen criterio","Suma","Promedia"],"r":0},{"q":"Fijar celda $A$1","op":["Referencia absoluta","Relativa","Mixta"],"r":0},{"q":"Función SI","op":["=SI(A1>10,\"Aprobado\",\"Reprobado\")","=SI SUMA","=SI BUSCAR"],"r":0},{"q":"Formato condicional","op":["Colorear automáticamente según valor","Borrar","Imprimir"],"r":0},{"q":"Validación datos","op":["Evitar errores, lista desplegable","Borrar datos","Sumar"],"r":0},{"q":"Texto en columnas","op":["Separar nombre y apellido en dos columnas","Unir texto","Borrar"],"r":0},{"q":"Quitar duplicados","op":["Datos > Quitar duplicados","Inicio > Borrar","Fórmulas > Duplicados"],"r":0},{"q":"HOY() retorna","op":["Fecha actual","Hora","Texto"],"r":0},{"q":"DIAS.LAB","op":["Días hábiles entre fechas","Días calendario","Meses"],"r":0},{"q":"Gráfico dinámico","op":["Gráfico que cambia con filtro tabla dinámica","Gráfico estático","Imagen"],"r":0},{"q":"Segmentador","op":["Filtro visual rápido","Borrar tabla","Suma"],"r":0},{"q":"Power Query","op":["Limpiar y transformar datos masivos","Escribir Word","Navegar"],"r":0},{"q":"CONCATENAR o &","op":["Unir texto de varias celdas","Sumar números","Dividir"],"r":0},{"q":"Buscar objetivo","op":["Encontrar valor necesario para llegar a meta","Buscar texto","Eliminar"],"r":0},{"q":"Solver","op":["Optimizar, hallar mejor escenario con restricciones","Borrar","Imprimir"],"r":0},{"q":"Ctrl+T","op":["Crear tabla estructurada","Cerrar libro","Guardar"],"r":0},{"q":"Ctrl+Shift+L","op":["Activar filtros","Poner negrita","Subrayar"],"r":0},{"q":"PROMEDIO.SI.CONJUNTO","op":["Promedio con varios criterios","Suma","Cuenta"],"r":0},{"q":"#N/A en BUSCARV","op":["Valor no encontrado","Error suma","División cero"],"r":0},{"q":"Proteger hoja","op":["Revisar > Proteger hoja con clave","Inicio > Proteger","No se puede"],"r":0},]
PSICO_25=[{"q":"Compañero toma medicamento sin fórmula, ¿qué haces?","op":["Reportas por seguridad paciente, ética primero","Te callas","Lo ayudas a vender"],"r":0},{"q":"Bajo estrés y mucho trabajo, tú","op":["Priorizas, pides ayuda, mantienes calidad","Gritas y dejas todo","Haces rápido sin verificar"],"r":0},{"q":"Jefe pide entregar pedido vencido","op":["Te niegas y reportas, ética primero","Lo entregas","Cambias fecha vencimiento"],"r":0},{"q":"Error propio grave, ¿qué haces?","op":["Lo admites, corriges y reportas inmediato","Lo ocultas","Culpas a otro"],"r":0},{"q":"Trabajo en equipo es","op":["Apoyar, comunicar, respetar, cumplir","Hacer solo mi parte","Competir contra todos"],"r":0},{"q":"Paciente reclama agresivo por demora","op":["Escuchas, empatía, buscas solución, escalas","Gritas también","Ignoras"],"r":0},{"q":"Ves compañero robando medicamento","op":["Reportas con evidencia a RRHH/gerencia","Te unes","Te callas por miedo"],"r":0},{"q":"Te ofrecen coima proveedor","op":["Rechazas y reportas, transparencia","Aceptas","Negocias más"],"r":0},{"q":"Olvidaste proceso clave, ¿qué haces?","op":["Verificas procedimiento, preguntas, no inventas","Improvisas","Omites paso"],"r":0},{"q":"Meta imposible de cumplir","op":["Comunicas a tiempo, propones plan, pides apoyo","Mientes que sí cumpliste","No haces nada"],"r":0},{"q":"Confidencialidad datos paciente","op":["Nunca compartir, Habeas Data Ley 1581","Contar a amigos","Publicar en redes"],"r":0},{"q":"Cambio de turno y queda pendiente crítico","op":["Entregas completo, escrito y verbal","Te vas sin decir","Dejas nota confusa"],"r":0},{"q":"Jefe te grita injustamente","op":["Mantienes calma, pides hablar en privado, respetuoso","Gritas más fuerte","Renuncias gritando"],"r":0},{"q":"Compañero nuevo lento","op":["Apoyas, enseñas, paciencia","Te burlas","Lo ignoras"],"r":0},{"q":"Detectas casi error (near miss)","op":["Reportas como aprendizaje, sin culpa","Ocultas por miedo sanción","Culpas sistema"],"r":0},{"q":"Prioridad: ¿qué primero?","op":["Seguridad paciente, luego calidad, luego velocidad","Velocidad primero","Lo más fácil primero"],"r":0},{"q":"Feedback negativo de auditoría","op":["Lo tomas como mejora, plan acción","Te enojas y discutes","Ignoras"],"r":0},{"q":"Trabajas con quimio citotóxico, ¿qué prima?","op":["Seguridad, EPP, procedimiento, no atajos","Rapidez","Ahorrar guantes"],"r":0},{"q":"Dilema: ¿entregar sin fórmula para no perder venta?","op":["No, exige fórmula, seguridad primero","Sí entrega","Depende cliente"],"r":0},{"q":"Puntualidad para ti","op":["Responsabilidad y respeto equipo y paciente","Opcional","Si quiero"],"r":0},{"q":"Manejo frustración","op":["Respiras, analizas, buscas solución, pides ayuda","Explosión emocional","Abandonas tarea"],"r":0},{"q":"Aprendizaje continuo","op":["Te actualizas, lees normativa, cursos","No necesito aprender más","Solo si me obligan"],"r":0},{"q":"Liderazgo en Farmart es","op":["Ejemplo, servicio, escucha, resultados con gente","Gritar y mandar","Solo ordenar"],"r":0},{"q":"Si ves condición insegura en bodega","op":["Reportas, señalizas, propones corrección","Ignoras","Solo te quejas"],"r":0},{"q":"¿Por qué quieres trabajar en Farmart?","op":["Me identifica propósito salud, ética, crecimiento","Solo por plata","No tengo otra opción"],"r":0},]
CASOS_POR_CARGO={"Personal de Nómina":["Caso 1: Empleado gana 3M, incapacitado 10 días por EPS, 5h extra nocturnas. Liquida nómina, PILA y soportes.","Caso 2: Error pago seguridad social mes anterior no pagaste ARL de 20 empleados. Plan corrección.","Caso 3: Empleado pide liquidación renuncia 6 meses, salario 2.5M, no tomó vacaciones."],"Tesorería":["Caso 1: Arqueo caja menor descuadre 700k faltante, ¿procedimiento?","Caso 2: Flujo caja negativo 50M próxima semana, ¿qué priorizas?","Caso 3: Proveedor exige anticipo 50% sin factura, ¿cómo manejas?"],"Quimico farmaceutico":["Caso 1: Prescripción oncológica dosis 30% sobre máxima, médico insiste, ¿qué haces?","Caso 2: Falla cadena frío 2-8°C por 5h, vacunas 40M, ¿decisión?","Caso 3: Error unidosis detectado a tiempo, paciente equivocado, ¿causa raíz?"],"Abogados":["Caso 1: Tutela por no entrega medicamento vital, juez pide informe 48h.","Caso 2: Contrato EPS vence en 15 días, sin nuevo contrato, ¿riesgos?","Caso 3: Demanda laboral despido sin justa causa 50M."],"DEFAULT":["Caso 1: Falla crítica en tu área que afecta paciente, ¿qué haces 2 horas?","Caso 2: Conflicto compañero no sigue procedimiento seguro.","Caso 3: Propuesta mejora para tu cargo con indicadores."]}

def get_casos(cargo): return CASOS_POR_CARGO.get(cargo, CASOS_POR_CARGO["DEFAULT"])
def evaluar_caso_ia(texto,cargo):
    tl=texto.lower()
    if len(tl)<40: return 20, "Muy corta, desarrolla procedimiento, normativa, ética."
    puntaje=50
    kws={"Personal de Nómina":["pila","seguridad social","liquidación","soporte","dian"],"Tesorería":["arqueo","conciliación","soporte","autorización","flujo"],"Quimico farmaceutico":["invima","bpm","seguridad paciente","farmacovigilancia"],"Abogados":["tutela","jurisprudencia","prueba","normativa"]}
    kw=kws.get(cargo,["normativa","procedimiento","ética","reporte","evidencia"])
    puntaje+=sum(1 for k in kw if k in tl)*8
    puntaje+=min(15,len(tl)//200)
    puntaje=min(95,puntaje)
    retro="Excelente: menciona normativa y procedimiento." if puntaje>=80 else "Bueno pero falta normativa específica." if puntaje>=60 else "Básico, falta estructura: Análisis, Normativa, Acción, Prevención, Reporte."
    return puntaje, retro

if not os.path.exists(CARGOS_FILE):
    with open(CARGOS_FILE,"w") as f: json.dump(CARGOS_DEFAULT,f,indent=2)
if not os.path.exists(PREGUNTAS_FILE):
    with open(PREGUNTAS_FILE,"w") as f: json.dump(BANCO_TECNICO_25,f,indent=2,ensure_ascii=False)
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE,"w") as f: json.dump({"sin_excel":[],"excel":EXCEL_REAL_25,"psico":PSICO_25,"requiere_hv":False},f,indent=2,ensure_ascii=False)

inicializar_usuarios()

if "auth" not in st.session_state:
    st.session_state.auth=False; st.session_state.user=None
if "etapa" not in st.session_state:
    st.session_state.etapa=0
if "respuestas_tecnicas" not in st.session_state:
    st.session_state.respuestas_tecnicas=[]
if "respuestas_excel" not in st.session_state:
    st.session_state.respuestas_excel=[]
if "respuestas_psico" not in st.session_state:
    st.session_state.respuestas_psico=[]
if "casos_texto" not in st.session_state:
    st.session_state.casos_texto=["","",""]
if "analisis_ia_hv" not in st.session_state:
    st.session_state.analisis_ia_hv=None

st.markdown('<div class="brand">HIRE<span>READY</span>-IA V5.1 🤖</div>',unsafe_allow_html=True)
st.caption("CORREGIDO - 4 Pruebas: 25 Técnicas + 25 Excel Real + 25 Psicotécnica + 3 Casos con IA")

if not st.session_state.auth:
    tab1,tab2=st.tabs(["📝 Aspirante - 4 Pruebas","🔐 RRHH / Admin"])
    with tab1:
        cfg=cargar_json(CONFIG_FILE) if os.path.exists(CONFIG_FILE) else {"requiere_hv":False}
        requiere_hv=cfg.get("requiere_hv",False)
        cedula=st.text_input("Cédula *"); nombre=st.text_input("Nombre completo *")
        cargos_list=cargar_json(CARGOS_FILE) if os.path.exists(CARGOS_FILE) else CARGOS_DEFAULT
        cargo=st.selectbox("Cargo *",cargos_list); sede=st.text_input("Ciudad / Sede")
        archivo_hv=st.file_uploader("📎 Hoja de Vida PDF - "+("OBLIGATORIA" if requiere_hv else "OPCIONAL"),type=["pdf"])
        if st.session_state.etapa==0:
            c1,c2=st.columns(2)
            if c1.button("▶️ Iniciar Pruebas",type="primary",use_container_width=True):
                if not (cedula and nombre):
                    st.error("Cédula y nombre obligatorios")
                elif requiere_hv and not archivo_hv:
                    st.error("HV obligatoria por RRHH")
                else:
                    st.session_state.cedula_real=cedula; st.session_state.nombre=nombre; st.session_state.cargo_sel=cargo; st.session_state.sede=sede
                    st.session_state.analisis_ia_hv={"compat":60 if archivo_hv else 0,"txt":"HV" if archivo_hv else "Sin HV"}
                    st.session_state.etapa=1; st.rerun()
            if c2.button("⏭️ Saltar HV (si opcional)",use_container_width=True):
                if requiere_hv:
                    st.error("No puedes saltar, HV obligatoria")
                else:
                    if not (cedula and nombre):
                        st.error("Cédula y nombre obligatorios")
                    else:
                        st.session_state.cedula_real=cedula; st.session_state.nombre=nombre; st.session_state.cargo_sel=cargo; st.session_state.sede=sede
                        st.session_state.analisis_ia_hv={"compat":0,"txt":"Sin HV opcional"}
                        st.session_state.etapa=1; st.rerun()
        if st.session_state.etapa>=1:
            st.divider(); st.markdown('<span class="step">ETAPA 1/4 - TÉCNICA 25 PREGUNTAS</span>',unsafe_allow_html=True)
            banco=cargar_json(PREGUNTAS_FILE) if os.path.exists(PREGUNTAS_FILE) else BANCO_TECNICO_25
            preguntas=banco.get(st.session_state.get("cargo_sel",cargos_list[0]),[])[:25]
            if st.session_state.etapa==1:
                resp=[]
                for i,p in enumerate(preguntas):
                    r=st.radio(f"{i+1}. {p['q']}",p["op"],key=f"t{i}",index=None)
                    if r is not None:
                        resp.append(p["op"].index(r)==p["r"])
                if st.button("✅ Finalizar Técnica e ir a Excel Real",type="primary"):
                    if len(resp)<len(preguntas):
                        st.warning(f"Faltan {len(preguntas)-len(resp)}")
                    else:
                        st.session_state.respuestas_tecnicas=resp; st.session_state.etapa=2; st.rerun()
            else:
                st.success(f"Técnica: {sum(st.session_state.respuestas_tecnicas)}/{len(preguntas)} = {sum(st.session_state.respuestas_tecnicas)/len(preguntas)*100:.1f}%")
        if st.session_state.etapa>=2:
            st.divider(); st.markdown('<span class="step">ETAPA 2/4 - EXCEL REAL 25</span>',unsafe_allow_html=True)
            cfg=cargar_json(CONFIG_FILE); excel_preg=cfg.get("excel",EXCEL_REAL_25)[:25]
            if st.session_state.etapa==2:
                resp=[]
                for i,p in enumerate(excel_preg):
                    r=st.radio(f"{i+1}. {p['q']}",p["op"],key=f"e{i}",index=None)
                    if r is not None:
                        resp.append(p["op"].index(r)==p["r"])
                if st.button("✅ Finalizar Excel e ir a Psicotécnica",type="primary"):
                    if len(resp)<len(excel_preg):
                        st.warning(f"Faltan {len(excel_preg)-len(resp)}")
                    else:
                        st.session_state.respuestas_excel=resp; st.session_state.etapa=3; st.rerun()
            else:
                st.success(f"Excel: {sum(st.session_state.respuestas_excel)}/{len(excel_preg)} = {sum(st.session_state.respuestas_excel)/len(excel_preg)*100:.1f}%")
        if st.session_state.etapa>=3:
            st.divider(); st.markdown('<span class="step">ETAPA 3/4 - PSICOTÉCNICA 25</span>',unsafe_allow_html=True)
            cfg=cargar_json(CONFIG_FILE); psico_preg=cfg.get("psico",PSICO_25)[:25]
            if st.session_state.etapa==3:
                resp=[]
                for i,p in enumerate(psico_preg):
                    r=st.radio(f"{i+1}. {p['q']}",p["op"],key=f"p{i}",index=None)
                    if r is not None:
                        resp.append(p["op"].index(r)==p["r"])
                if st.button("✅ Finalizar Psicotécnica e ir a Casos IA",type="primary"):
                    if len(resp)<len(psico_preg):
                        st.warning(f"Faltan {len(psico_preg)-len(resp)}")
                    else:
                        st.session_state.respuestas_psico=resp; st.session_state.etapa=4; st.rerun()
            else:
                st.success(f"Psicotécnica: {sum(st.session_state.respuestas_psico)}/{len(psico_preg)} = {sum(st.session_state.respuestas_psico)/len(psico_preg)*100:.1f}%")
        if st.session_state.etapa>=4:
            st.divider(); st.markdown('<span class="step">ETAPA 4/4 - CASOS CON IA</span>',unsafe_allow_html=True)
            casos=get_casos(st.session_state.get("cargo_sel","DEFAULT"))
            textos=[]
            for idx,caso in enumerate(casos):
                st.subheader(f"Caso {idx+1}"); st.write(caso)
                t=st.text_area(f"Desarrollo caso {idx+1}",value=st.session_state.casos_texto[idx] if idx < len(st.session_state.casos_texto) else "",key=f"caso{idx}",height=150)
                textos.append(t)
            st.session_state.casos_texto=textos
            if st.button("🤖 EVALUAR CASOS CON IA Y GENERAR REPORTE FINAL",type="primary"):
                if any(len(t)<30 for t in textos):
                    st.warning("Mínimo 30 caracteres por caso")
                else:
                    tec=sum(st.session_state.respuestas_tecnicas)/len(st.session_state.respuestas_tecnicas)*100
                    exc=sum(st.session_state.respuestas_excel)/len(st.session_state.respuestas_excel)*100
                    psi=sum(st.session_state.respuestas_psico)/len(st.session_state.respuestas_psico)*100
                    casos_eval=[evaluar_caso_ia(t, st.session_state.cargo_sel) for t in textos]
                    prom_casos=sum([c[0] for c in casos_eval])/len(casos_eval)
                    final = tec*0.4 + exc*0.2 + psi*0.2 + prom_casos*0.2
                    apto = final>=75 and tec>=70
                    rec = "ALTA RECOMENDACIÓN - CONTRATAR" if final>=85 else "RECOMENDADO CON PERIODO PRUEBA" if final>=70 else "NO RECOMENDADO"
                    registro={"fecha":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"cedula":st.session_state.cedula_real,"nombre":st.session_state.nombre,"cargo":st.session_state.cargo_sel,"sede":st.session_state.sede,"tecnica":round(tec,1),"excel":round(exc,1),"psico":round(psi,1),"casos_prom":round(prom_casos,1),"final":round(final,1),"estado":"APTO" if apto else "NO APTO","recomendacion":rec}
                    regs=cargar_json(REGISTROS_FILE) if os.path.exists(REGISTROS_FILE) else []; regs.append(registro); guardar_json(REGISTROS_FILE,regs)
                    st.divider()
                    if apto: st.balloons(); st.success(f"## ✅ {registro['estado']} - FINAL {final:.1f}%")
                    else: st.error(f"## ❌ {registro['estado']} - FINAL {final:.1f}%")
                    c1,c2,c3,c4=st.columns(4); c1.metric("Técnica",f"{tec:.1f}%"); c2.metric("Excel",f"{exc:.1f}%"); c3.metric("Psico",f"{psi:.1f}%"); c4.metric("Casos IA",f"{prom_casos:.1f}%")
                    for idx,(punt,retro) in enumerate(casos_eval): st.write(f"**Caso {idx+1}: {punt}%** - {retro}")
                    reporte=f"HIREREADY-IA V5.1 REPORTE\\nNombre: {registro['nombre']}\\nCargo: {registro['cargo']}\\nTecnica: {tec:.1f}% Excel: {exc:.1f}% Psico: {psi:.1f}% Casos: {prom_casos:.1f}% Final: {final:.1f}% Estado: {registro['estado']} Rec: {rec}\\n"
                    st.download_button("📄 Descargar Reporte V5.1",reporte,file_name=f"HIREREADY_V51_{st.session_state.cedula_real}.txt")
                    if st.button("🔄 Nueva evaluación"):
                        for k in ["etapa","respuestas_tecnicas","respuestas_excel","respuestas_psico","casos_texto","analisis_ia_hv","cedula_real","nombre","cargo_sel","sede"]: st.session_state.pop(k,None)
                        st.session_state.etapa=0; st.rerun()
    with tab2:
        st.header("Acceso RRHH - HIREREADY-IA V5.1")
        st.info("Usuarios: admin / admin123 | admin@hireready.ia / HireReady2026* | rrhh@hireready.ia / HireReady2026*")
        u=st.text_input("Usuario"); p=st.text_input("Clave",type="password")
        if st.button("Entrar"):
            users=cargar_json(USUARIOS_FILE) if os.path.exists(USUARIOS_FILE) else USUARIOS_CORRECTOS
            found=next((x for x in users if x["usuario"]==u and x["clave"]==p),None)
            if found:
                st.session_state.auth=True; st.session_state.user=found; st.rerun()
            else:
                st.error(f"Usuario o clave incorrecta. Usuarios disponibles: {[u['usuario'] for u in users]}")
else:
    st.sidebar.markdown('<div class="brand" style="color:white;">HIRE<span style="color:#7AC143;">READY</span>-IA V5.1</div>',unsafe_allow_html=True)
    st.sidebar.success(f"Conectado: {st.session_state.user['nombre']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.auth=False; st.session_state.user=None; st.rerun()
    menu=st.sidebar.selectbox("Menú V5.1", ["Dashboard V5","Crear Cargos","Gestionar Preguntas Técnicas 25","Gestionar Excel Real 25","Gestionar Psicotécnica 25","Gestionar Casos IA","Crear Usuarios RRHH","Config IA / HV","Reset Usuarios"])
    if menu=="Dashboard V5":
        st.header("📊 Dashboard V5.1 - 4 Pruebas")
        regs=cargar_json(REGISTROS_FILE) if os.path.exists(REGISTROS_FILE) else []
        if not regs: st.info("Sin registros")
        else:
            df=pd.DataFrame(regs)
            c1,c2,c3,c4,c5=st.columns(5); c1.metric("Total",len(df)); c2.metric("APTO",len(df[df["estado"]=="APTO"])); c3.metric("NO APTO",len(df[df["estado"]=="NO APTO"])); c4.metric("% Aprob",f"{len(df[df['estado']=='APTO'])/len(df)*100:.1f}%" if len(df)>0 else "0%"); c5.metric("Prom Final",f"{df['final'].mean():.1f}%" if 'final' in df else "N/A")
            st.dataframe(df,use_container_width=True)
            st.download_button("📥 Descargar CSV V5.1",df.to_csv(index=False).encode(),"hireready_v51.csv")
            if st.button("🗑️ Borrar todo"): guardar_json(REGISTROS_FILE,[]); st.success("Borrado"); st.rerun()
    elif menu=="Reset Usuarios":
        st.header("🔧 Reset Usuarios - SOLUCIÓN LOGIN")
        st.warning("Si no puedes entrar, haz clic aquí para resetear todos los usuarios a los valores por defecto")
        if st.button("🔄 RESETEAR USUARIOS AHORA",type="primary"):
            guardar_json(USUARIOS_FILE, USUARIOS_CORRECTOS)
            st.success("✅ Usuarios reseteados! Ahora puedes entrar con: admin / admin123")
            st.json(USUARIOS_CORRECTOS)
    elif menu=="Crear Cargos":
        st.header("🏷️ Cargos"); cargos=cargar_json(CARGOS_FILE); st.write(cargos)
        nuevo=st.text_input("Nuevo cargo")
        if st.button("Crear"):
            if nuevo and nuevo not in cargos:
                cargos.append(nuevo); guardar_json(CARGOS_FILE,cargos)
                banco=cargar_json(PREGUNTAS_FILE); banco[nuevo]=[{"q":f"{nuevo} - Técnica {i+1}","op":["Correcta","Incorrecta B","Incorrecta C"],"r":0} for i in range(25)]
                guardar_json(PREGUNTAS_FILE,banco); st.success("Creado"); st.rerun()
        elim=st.selectbox("Eliminar",cargos)
        if st.button("Eliminar cargo"):
            cargos=[c for c in cargos if c!=elim]; guardar_json(CARGOS_FILE,cargos); banco=cargar_json(PREGUNTAS_FILE); banco.pop(elim,None); guardar_json(PREGUNTAS_FILE,banco); st.success("Eliminado"); st.rerun()
    elif menu=="Gestionar Preguntas Técnicas 25":
        st.header("📚 Técnicas 25 por cargo"); cargos=cargar_json(CARGOS_FILE); banco=cargar_json(PREGUNTAS_FILE); cargo_sel=st.selectbox("Cargo",cargos); preguntas=banco.get(cargo_sel,[]); st.write(f"Total: {len(preguntas)}")
        for idx,preg in enumerate(preguntas):
            with st.expander(f"{idx+1}. {preg['q'][:70]}..."):
                nq=st.text_input("Pregunta",value=preg['q'],key=f"qt{cargo_sel}{idx}"); o1=st.text_input("A",value=preg['op'][0],key=f"qa{cargo_sel}{idx}"); o2=st.text_input("B",value=preg['op'][1],key=f"qb{cargo_sel}{idx}"); o3=st.text_input("C",value=preg['op'][2],key=f"qc{cargo_sel}{idx}"); rc=st.selectbox("Correcta",["A","B","C"],index=preg['r'],key=f"qr{cargo_sel}{idx}")
                if st.button(f"Guardar {idx+1}",key=f"qs{cargo_sel}{idx}"): banco[cargo_sel][idx]={"q":nq,"op":[o1,o2,o3],"r":["A","B","C"].index(rc)}; guardar_json(PREGUNTAS_FILE,banco); st.success("Guardado"); st.rerun()
    elif menu=="Gestionar Excel Real 25":
        st.header("📊 Excel Real 25"); cfg=cargar_json(CONFIG_FILE); excel=cfg.get("excel",[]); st.write(f"Total: {len(excel)}")
        for idx,preg in enumerate(excel):
            with st.expander(f"Excel {idx+1}. {preg['q'][:60]}"):
                nq=st.text_input("Pregunta",value=preg['q'],key=f"exq{idx}"); o1=st.text_input("A",value=preg['op'][0],key=f"exo1{idx}"); o2=st.text_input("B",value=preg['op'][1],key=f"exo2{idx}"); o3=st.text_input("C",value=preg['op'][2],key=f"exo3{idx}"); rc=st.selectbox("Correcta",["A","B","C"],index=preg['r'],key=f"exr{idx}")
                if st.button(f"Guardar Excel {idx+1}",key=f"exs{idx}"): cfg["excel"][idx]={"q":nq,"op":[o1,o2,o3],"r":["A","B","C"].index(rc)}; guardar_json(CONFIG_FILE,cfg); st.success("Guardado"); st.rerun()
    elif menu=="Gestionar Psicotécnica 25":
        st.header("🧠 Psicotécnica 25"); cfg=cargar_json(CONFIG_FILE); psico=cfg.get("psico",[]); st.write(f"Total: {len(psico)}")
        for idx,preg in enumerate(psico):
            with st.expander(f"Psico {idx+1}. {preg['q'][:60]}"):
                nq=st.text_input("Pregunta",value=preg['q'],key=f"psq{idx}"); o1=st.text_input("A",value=preg['op'][0],key=f"pso1{idx}"); o2=st.text_input("B",value=preg['op'][1],key=f"pso2{idx}"); o3=st.text_input("C",value=preg['op'][2],key=f"pso3{idx}"); rc=st.selectbox("Correcta",["A","B","C"],index=preg['r'],key=f"psr{idx}")
                if st.button(f"Guardar Psico {idx+1}",key=f"pss{idx}"): cfg["psico"][idx]={"q":nq,"op":[o1,o2,o3],"r":["A","B","C"].index(rc)}; guardar_json(CONFIG_FILE,cfg); st.success("Guardado"); st.rerun()
    elif menu=="Crear Usuarios RRHH":
        st.header("👥 Usuarios"); users=cargar_json(USUARIOS_FILE); st.dataframe(pd.DataFrame(users))
        nu=st.text_input("Email"); nn=st.text_input("Nombre"); nc=st.text_input("Clave",type="password"); nr=st.selectbox("Rol",["RRHH","Coordinador RRHH","Gerencia RRHH"])
        if st.button("Crear usuario"): users.append({"usuario":nu,"clave":nc,"rol":nr,"nombre":nn}); guardar_json(USUARIOS_FILE,users); st.success("Creado"); st.rerun()
    elif menu=="Config IA / HV":
        st.header("🤖 Config V5.1"); cfg=cargar_json(CONFIG_FILE); requiere=cfg.get("requiere_hv",False); nuevo_req=st.checkbox("HV obligatoria",value=requiere)
        if st.button("Guardar HV"): cfg["requiere_hv"]=nuevo_req; guardar_json(CONFIG_FILE,cfg); st.success(f"HV {'OBLIGATORIA' if nuevo_req else 'OPCIONAL'}"); st.rerun()
