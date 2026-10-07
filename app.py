import streamlit as st
import pandas as pd
from datetime import datetime
import random

st.set_page_config(page_title="FARMART SYSTEM", layout="wide")
st.title("FARMART SYSTEM - HR Testing 90% APTO")

if 'base' not in st.session_state:
    st.session_state.base = []
if 'paso' not in st.session_state:
    st.session_state.paso = "login"

# SIDEBAR ADMIN
with st.sidebar:
    st.header("Admin Farmart")
    user = st.text_input("Usuario")
    pwd = st.text_input("Clave", type="password")
    es_admin = (user == "admin@farmart.system" and pwd == "Farmart2026*")
    if es_admin:
        st.success("Admin OK")
        st.session_state.paso = "admin"

# DASHBOARD ADMIN
if st.session_state.paso == "admin" and es_admin:
    st.subheader("Lista Candidatos 90%+ APTO")
    df = pd.DataFrame(st.session_state.base)
    c1,c2 = st.columns(2)
    c1.metric("Total", len(df))
    if not df.empty:
        aptos = df[df['final'] >= 90]
        c2.metric("90%+ APTO", len(aptos))
        filtro = st.checkbox("Solo mostrar 90%+ APTO", value=True)
        tabla = aptos if filtro else df
        st.dataframe(tabla, use_container_width=True)
        st.download_button("Descargar Excel", tabla.to_csv(index=False), "FARMART_90.csv")
    else:
        st.info("Base vacia")
    if st.button("Salir"):
        st.session_state.paso = "login"
        st.rerun()

# CANDIDATO
else:
    st.header("Registro por Cedula")
    col1,col2,col3 = st.columns(3)
    cedula = col1.text_input("CEDULA")
    nombre = col2.text_input("Nombre")
    cargo = col3.selectbox("Cargo", ["Bodega","Mensajero","Servicios Generales","Tesoreria","Calidad","Juridica","Archivo","Auditoria Formulas","Oncologia","DBA","Fullstack","TI"])

    if st.button("Iniciar Prueba"):
        if cedula and nombre:
            st.session_state.ced = {"cedula":cedula,"nombre":nombre,"cargo":cargo,"pts":0,"idx":0}
            st.session_state.paso = "prueba"
            st.rerun()
        else:
            st.error("Llene cedula y nombre")

    if st.session_state.paso == "prueba" and 'ced' in st.session_state:
        preguntas = [
            {"q":"PEPS significa?","o":["Primeras Entrar Primeras Salir","Producto Expira Pronto Sale"],"a":0},
            {"q":"Nevera 2-8C fuera de rango?","o":["Reporto a Calidad y cuarentena","Lo despacho igual"],"a":0},
            {"q":"BUSCARV no encuentra?","o":["Espacios extra","Excel danado"],"a":0},
            {"q":"Suma ventas Cali enero?","o":["SUMAR.SI.CONJUNTO","SUMA"],"a":0},
            {"q":"Formula Losartan 50mg pero paciente 70a dosis 25mg?","o":["Valido con medico","Despacho 90"],"a":0},
        ]
        idx = st.session_state.ced["idx"]
        if idx < len(preguntas):
            p = preguntas[idx]
            st.write(f"Pregunta {idx+1}/{len(preguntas)}: {p['q']}")
            r = st.radio("Seleccione", p['o'], index=None, key=idx)
            if st.button("Siguiente"):
                if r is None:
                    st.error("Seleccione opcion")
                else:
                    if r == p['o'][p['a']]:
                        st.session_state.ced["pts"] += 1
                    st.session_state.ced["idx"] += 1
                    st.rerun()
        else:
            final = int(st.session_state.ced["pts"]/len(preguntas)*100)
            estado = "90%+ APTO" if final >= 90 else "REFUERZO"
            st.success(f"Resultado {final}% - {estado}")
            st.session_state.base.append({
                "cedula": st.session_state.ced["cedula"],
                "nombre": st.session_state.ced["nombre"],
                "cargo": st.session_state.ced["cargo"],
                "final": final,
                "estado": estado,
                "fecha": datetime.now().strftime("%d/%m/%Y")
            })
            if st.button("Finalizar"):
                st.session_state.paso = "login"
                st.rerun()
