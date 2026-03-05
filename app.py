import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página Estilo Apple
st.set_page_config(page_title="ATA - Terminal 3 Insights", layout="wide")

st.title("📊 Terminal 3: Data Analytics Engine")
st.markdown("---")

# 1. El Uploader (Aquí es donde se siente como Julius)
uploaded_file = st.file_uploader("Arrastra aquí tu archivo de Mayo (CSV o Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Carga de datos
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    
    # Limpieza Automática de Atlas
    df['Qs_Real'] = pd.to_numeric(df['Q´s Totales'], errors='coerce').fillna(0)
    
    # KPIs en la parte superior (Tarjetas elegantes)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Q's Desaprovechadas", f"{df['Qs_Real'].sum():,.0f}")
    col2.metric("Eficiencia de Entrega", f"{(df['Entrega'].sum()/len(df)*100):.1f}%")
    col3.metric("Puntas Analizadas", len(df))

    # Gráfico de Fuga por PC
    st.subheader("Fuga de Prospectos por Consultor")
    fig = px.bar(df.groupby('PC')['Qs_Real'].sum().reset_index().sort_values('Qs_Real'), 
                 x='Qs_Real', y='PC', orientation='h', 
                 template='plotly_white', color_discrete_sequence=['#2c3e50'])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Esperando el archivo para iniciar la auditoría...")