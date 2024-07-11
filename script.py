import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from config import *

st.markdown('## Simulador de financiamentos')

valor_financiamento = int(st.number_input('Valor do financiamento (milhares)', value=200)) * 1000
num_prestacoes = int(st.number_input('Quantidade de parcelas', value=360))
modalidade = st.selectbox('Modalidade', ['SAC', 'Price', 'SAC (parcela constante)'])
taxa_juros_anual = st.number_input('Taxa de juros (TR) a. a.', format= "%.2f", step=1., value=10.0)/100
valor_extra = int(st.number_input('Amortização extra', value=0))

col11, col12, col13 = st.columns(3)

with col12:
    simular = st.button('Simular', use_container_width=True)


if simular:
    df = create_data(taxa_juros_anual, num_prestacoes, valor_financiamento, modalidade, valor_extra)
    juros_total = df['Juros'].sum()
    qtde_parcelas = len(df)

    total = juros_total + valor_financiamento
    tab1, tab2 = st.tabs(['Gráfico', 'Detalhes'])

    with tab1:
        with st.container():
            st.plotly_chart(create_chart(df), use_container_width=True, theme=None)

    with tab2:
        st.dataframe(df, use_container_width=True, height=450)

    
    time.sleep(0.2)
    col21, col22, col23 = st.columns(3)
    with col21:
        create_stylish_kpi(f"R$ {juros_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 'Juros', (17, 78, 120))
    with col22:
        create_stylish_kpi(qtde_parcelas, 'Quantidade de prestações', (17, 78, 120))
    with col23:
        create_stylish_kpi(f"{juros_total*100/(juros_total+valor_financiamento):,.2f}%".replace(",", "X").replace(".", ",").replace("X", "."), "Percentual de juros", (17, 78, 120))