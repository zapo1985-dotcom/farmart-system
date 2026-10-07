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
}
