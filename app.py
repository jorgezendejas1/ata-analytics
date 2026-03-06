import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración Estética Premium
st.set_page_config(page_title="ATA - Terminal 3 Insights", layout="wide")

st.title("📊 Terminal 3: Data Analytics Engine")
st.markdown("---")

uploaded_file = st.file_uploader("Arrastra aquí tu archivo (CSV o XLSX)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # 1. CARGA INTELIGENTE: Saltamos las filas decorativas del Excel (usualmente las primeras 4)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            # En Excel, la data real suele empezar en la fila 5 (índice 4)
            df = pd.read_excel(uploaded_file, skiprows=4)

        # 2. LIMPIEZA DE COLUMNAS (Eliminamos espacios y caracteres raros)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Mapeo flexible para encontrar la columna de Q's aunque cambie el acento
        df = df.rename(columns={
            'Q´s Totales': 'Qs_Real', 
            'Q's Totales': 'Qs_Real', 
            'Q´s  Totales': 'Qs_Real',
            'Efectivo si(1)/no(0).2': 'Entrega' # Pandas suele numerar columnas repetidas
        })

        # 3. PROCESAMIENTO ATLAS (ffill para fechas y bloques)
        # Buscamos la columna que debería tener la fecha/horario (usualmente la primera o segunda)
        col_contexto = df.columns[0]
        df['Fecha_Limpia'] = df[col_contexto].where(df[col_contexto].str.contains('/', na=False)).ffill()
        df['Bloque_Limpio'] = df[col_contexto].where(df[col_contexto].str.contains('-', na=False)).ffill()

        # Limpiamos valores numéricos
        df['Qs_Real'] = pd.to_numeric(df['Qs_Real'], errors='coerce').fillna(0)
        df['Entrega'] = pd.to_numeric(df['Entrega'], errors='coerce').fillna(0)

        # Filtramos solo filas con datos reales de PC
        df_final = df[df['PC'].notna()].copy()

        # 4. INTERFAZ DE RESULTADOS
        st.success("Archivo procesado con éxito.")
        
        # KPIs en tarjetas
        kpi1, kpi2, kpi3 = st.columns(3)
        total_qs = df_final['Qs_Real'].sum()
        kpi1.metric("Total Q's Desaprovechadas", f"{total_qs:,.0f}")
        
        # Cálculo de eficiencia
        eficiencia = (df_final['Entrega'].sum() / len(df_final)) * 100 if len(df_final) > 0 else 0
        kpi2.metric("Eficiencia de Entrega", f"{eficiencia:.1f}%")
        kpi3.metric("Puntas Analizadas", len(df_final))

        # Gráfico Estilo Apple
        st.subheader("Fuga de Prospectos por Consultor (Top 10)")
        top_pc = df_final.groupby('PC')['Qs_Real'].sum().reset_index().sort_values('Qs_Real', ascending=False).head(10)
        
        fig = px.bar(top_pc, x='Qs_Real', y='PC', orientation='h',
                     color_discrete_sequence=['#2c3e50'], template='plotly_white')
        
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, font_family="Helvetica")
        st.plotly_chart(fig, use_container_width=True)

        # Ver tabla completa opcional
        if st.checkbox("Mostrar tabla de datos limpia"):
            st.dataframe(df_final)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
        st.info("Asegúrate de que el archivo tenga la estructura estándar de Power 1.")
else:
    st.info("Esperando el archivo para iniciar la auditoría...")
