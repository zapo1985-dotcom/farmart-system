import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

st.set_page_config(page_title="FARMART SYSTEM", page_icon="💊", layout="wide")

# --- BASE DE DATOS SIMPLE ---
DB_FILE = "registros.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f)

def cargar_datos():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def guardar_datos(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- PREGUNTAS (Ejemplo 20, luego pones las 100) ---
PREGUNTAS = [
    {"q": "¿Que es BPM?", "op": ["Buenas Practicas de Manufactura","Buen Proceso Manual","Base de Producto Medico"], "r": 0},
    {"q": "¿Temperatura de cadena de frio?", "op": ["2-8°C","10-15°C","-20°C"], "r": 0},
    {"q": "¿Que es FEFO?", "op": ["First Expire First Out","First Entry First Out","Fast Expire Fast Out"], "r": 0},
    {"q": "¿Que hacer si encuentras medicamento vencido?", "op": ["Separar y reportar","Devolver a estante","Vender rapido"], "r": 0},
    {"q": "¿Que es un Lote?", "op": ["Conjunto de productos misma fabricacion","Numero de estante","Codigo de cliente"], "r": 0},
    # Agrega aqui hasta 100 preguntas
]

# --- INTERFAZ ---
st.title("💊 FARMART - Sistema de Evaluación")
st.markdown("**Droguerías - Evaluación 90% APTO**")

menu = st.sidebar.selectbox("Menu", ["Prueba Empleado", "Admin"])

if menu == "Prueba Empleado":
    st.header("Registro del Empleado")
    col1, col2 = st.columns(2)
    with col1:
        cedula = st.text_input("CÉDULA *")
        nombre = st.text_input("Nombre completo *")
    with col2:
        cargo = st.selectbox("Cargo", ["Bodega","Mensajero","Calidad","Auditoria","DBA","Auxiliar"])
        sede = st.text_input("Sede")

    if cedula and nombre:
        st.divider()
        st.header(f"Evaluación - {len(PREGUNTAS)} Preguntas")
        respuestas = []
        for i, p in enumerate(PREGUNTAS):
            resp = st.radio(f"{i+1}. {p['q']}", p["op"], key=f"q{i}", index=None)
            if resp is not None:
                respuestas.append(p["op"].index(resp) == p["r"])
        
        if st.button("FINALIZAR PRUEBA", type="primary"):
            if len(respuestas) < len(PREGUNTAS):
                st.warning(f"Responde todas. Llevas {len(respuestas)}/{len(PREGUNTAS)}")
            else:
                aciertos = sum(respuestas)
                porcentaje = (aciertos / len(PREGUNTAS)) * 100
                apto = porcentaje >= 90
                
                registro = {
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "cedula": cedula,
                    "nombre": nombre,
                    "cargo": cargo,
                    "sede": sede,
                    "aciertos": aciertos,
                    "total": len(PREGUNTAS),
                    "porcentaje": round(porcentaje,1),
                    "estado": "APTO" if apto else "NO APTO"
                }
                datos = cargar_datos()
                datos.append(registro)
                guardar_datos(datos)
                
                if apto:
                    st.balloons()
                    st.success(f"### ✅ APTO - {porcentaje:.1f}% ({aciertos}/{len(PREGUNTAS)})")
                else:
                    st.error(f"### ❌ NO APTO - {porcentaje:.1f}% ({aciertos}/{len(PREGUNTAS)}) - Se requiere 90%")
                st.json(registro)

else: # ADMIN
    st.header("🔐 Panel Admin")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    
    if user == "admin@farmart.system" and pwd == "Farmart2026*":
        st.success("Admin autenticado")
        datos = cargar_datos()
        if not datos:
            st.info("Sin registros aún")
        else:
            df = pd.DataFrame(datos)
            c1,c2,c3 = st.columns(3)
            c1.metric("Total evaluados", len(df))
            c2.metric("APTO (≥90%)", len(df[df["estado"]=="APTO"]))
            c3.metric("% Aprobación", f"{len(df[df['estado']=='APTO'])/len(df)*100:.1f}%" if len(df)>0 else "0%")
            
            st.dataframe(df, use_container_width=True)
            
            # Descargar Excel
            st.download_button("📥 Descargar Excel", df.to_csv(index=False).encode(), "farmart_resultados.csv", "text/csv")
            
            if st.button("🗑️ Borrar todos los registros"):
                guardar_datos([])
                st.rerun()
    elif user or pwd:
        st.error("Usuario o clave incorrecta")
