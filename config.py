import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def create_stylish_kpi(value, sline, wch_colour_box = None, wch_colour_font = None, fontsize = None, valign = None, iconname = None, lnk = None):

    if not wch_colour_box:
        wch_colour_box = (0, 75, 92) 
    if not wch_colour_font:
        wch_colour_font = (255, 255, 255)
    if not fontsize:
        fontsize = 24
    if not valign:
        valign = "left"
    if not iconname:
        iconname = ""
    if not lnk:
        lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
    
    # caso especial de percentual nan%
    if value == 'nan%':
        value = '-'
        
    htmlstr = f"""<p style='background-color: rgb({wch_colour_box[0]}, 
                                                      {wch_colour_box[1]}, 
                                                      {wch_colour_box[2]}, 0.75); 
                                color: rgb({wch_colour_font[0]}, 
                                           {wch_colour_font[1]}, 
                                           {wch_colour_font[2]}, 1); 
                                font-size: {fontsize}px; 
                                border-radius: 7px; 
                                padding-left: 12px; 
                                padding-top: 18px; 
                                padding-bottom: 18px; 
                                line-height:25px;'>
                                <i class='{iconname} fa-xs'></i> {value}
                                </style><BR><span style='font-size: 14px; 
                                margin-top: 0;'>{sline}</style></span></p>"""
    
    return st.markdown(lnk + htmlstr, unsafe_allow_html=True)

def create_data(taxa_juros_anual, num_prestacoes, valor_financiamento, modalidade, valor_extra):

    def _create_data_price(taxa_juros_anual, num_prestacoes, valor_financiamento, valor_extra):
        taxa_juros_mensal = (1 + taxa_juros_anual) ** (1 / 12) - 1
        prestacao_base = valor_financiamento * taxa_juros_mensal / (1 - (1 + taxa_juros_mensal) ** -num_prestacoes)

        prestacoes_base = []
        prestacoes_totais = []
        juros_pago = []
        amortizacoes_base = []
        amortizacoes_totais =[]
        amortizacoes_extra = []
        saldos_devedores = []
        saldo_devedor = valor_financiamento

        for _ in range(num_prestacoes):
            prestacao_total = prestacao_base + valor_extra
            juros_mes = saldo_devedor * taxa_juros_mensal
            amortizacao_base = prestacao_base - juros_mes
            amortizacao_total = prestacao_total - juros_mes

            if saldo_devedor <= amortizacao_base:
                amortizacao_base = saldo_devedor
                amortizacao_total = amortizacao_base
                saldo_devedor -= amortizacao_total
                prestacao_base = juros_mes + amortizacao_base
                prestacao_total = prestacao_base
                valor_extra = 0

            elif saldo_devedor <= amortizacao_total:
                prestacao_total = saldo_devedor + juros_mes
                valor_extra = prestacao_total - prestacao_base
                amortizacao_total = saldo_devedor
                saldo_devedor -= amortizacao_total
            
            else:
                saldo_devedor -= amortizacao_total
                

            # Evita saldo devedor negativo
            if saldo_devedor <= 0:
                saldo_devedor = 0


            prestacoes_base.append(prestacao_base)
            prestacoes_totais.append(prestacao_total)
            juros_pago.append(juros_mes)
            amortizacoes_base.append(amortizacao_base)
            amortizacoes_totais.append(amortizacao_total)
            amortizacoes_extra.append(valor_extra)
            saldos_devedores.append(saldo_devedor)

            # Interrompe o loop se o saldo devedor for zero
            if saldo_devedor <= 0:
                break

        num_prestacoes = len(saldos_devedores)

        df = pd.DataFrame({
            'Parcela': np.arange(1, num_prestacoes + 1),
            'Prestação Base': prestacoes_base,
            'Prestação Total': prestacoes_totais,
            'Juros': juros_pago,
            'Amortização Base': amortizacoes_base,
            'Amortização Extra': amortizacoes_extra,
            'Amortização Total': amortizacoes_totais,
            'Saldo Devedor': saldos_devedores
        })
        
        return df
    
    def _create_data_sac(taxa_juros_anual, num_prestacoes, valor_financiamento, valor_extra):
        # Calcular a taxa de juros mensal
        taxa_juros_mensal = (1 + taxa_juros_anual) ** (1 / 12) - 1

        # Calcular a amortização mensal
        amortizacao_base = valor_financiamento / num_prestacoes

        # Inicializar listas para armazenar os valores
        prestacoes_base = []
        prestacoes_totais = []
        juros_pago = []
        amortizacoes_base = []
        amortizacoes_totais =[]
        saldos_devedores = []
        amortizacoes_extra = []
        saldo_devedor = valor_financiamento

        # Calcular os valores para cada mês
        for _ in range(num_prestacoes):
            juros_mes = saldo_devedor * taxa_juros_mensal
            amortizacao_total = amortizacao_base + valor_extra

            if saldo_devedor <= amortizacao_base:
                amortizacao_base = saldo_devedor
                amortizacao_total = amortizacao_base
                saldo_devedor -= amortizacao_total
                prestacao_base = juros_mes + amortizacao_base
                prestacao_total = prestacao_base
                valor_extra = 0

            elif saldo_devedor <= amortizacao_total:
                prestacao_total = saldo_devedor + juros_mes
                valor_extra = prestacao_total - prestacao_base
                saldo_devedor -= amortizacao_total
            else:
                juros_mes = saldo_devedor * taxa_juros_mensal
                amortizacao_total = amortizacao_base + valor_extra
                prestacao_base = amortizacao_base + juros_mes
                prestacao_total = amortizacao_total + juros_mes
                saldo_devedor -= amortizacao_total

            saldos_devedores.append(saldo_devedor)  # Garantir que não fique negativo
            prestacoes_base.append(prestacao_base)
            prestacoes_totais.append(prestacao_total)
            juros_pago.append(juros_mes)
            amortizacoes_base.append(amortizacao_base)
            amortizacoes_extra.append(valor_extra)
            amortizacoes_totais.append(amortizacao_total)

            # Interrompe o loop se o saldo devedor for zero
            if saldo_devedor <= 0:
                break

        num_prestacoes = len(saldos_devedores)
        # Criar DataFrame
        df = pd.DataFrame({
            'Parcela': np.arange(1, num_prestacoes + 1),
            'Prestação Base': prestacoes_base,
            'Prestação Total': prestacoes_totais,
            'Juros': juros_pago,
            'Amortização Base': amortizacoes_base,
            'Amortização Extra': amortizacoes_extra,
            'Amortização Total': amortizacoes_totais,
            'Saldo Devedor': saldos_devedores
        })

        return df
    
    def _create_data_sac_const_parcela(taxa_juros_anual, num_prestacoes, valor_financiamento, valor_extra):
        valor_extra_extra = valor_extra

        # Calcular a taxa de juros mensal
        taxa_juros_mensal = (1 + taxa_juros_anual) ** (1 / 12) - 1

        # Calcular a amortização mensal
        amortizacao_base = valor_financiamento / num_prestacoes

        # Inicializar listas para armazenar os valores
        prestacoes_base = []
        prestacoes_totais = []
        juros_pago = []
        amortizacoes_base = []
        amortizacoes_totais =[]
        saldos_devedores = []
        amortizacoes_extra = []
        saldo_devedor = valor_financiamento

        # Calcular os valores para o primeiro mês
        juros_mes = saldo_devedor * taxa_juros_mensal
        prestacao_constante = amortizacao_base + juros_mes

        # Calcular os valores para cada mês
        for _ in range(num_prestacoes):
            juros_mes = saldo_devedor * taxa_juros_mensal
            prestacao_base = amortizacao_base + juros_mes
            amortizacao_total = prestacao_constante - juros_mes
            valor_extra = amortizacao_total - amortizacao_base + valor_extra_extra

            if saldo_devedor <= amortizacao_base:
                amortizacao_base = saldo_devedor
                amortizacao_total = amortizacao_base
                saldo_devedor -= amortizacao_total
                prestacao_base = juros_mes + amortizacao_base
                prestacao_total = prestacao_base
                valor_extra = 0

            elif saldo_devedor <= amortizacao_total:
                prestacao_total = saldo_devedor + juros_mes
                valor_extra = prestacao_total - prestacao_base
                amortizacao_total = amortizacao_base + valor_extra
                saldo_devedor -= amortizacao_total
            else:
                juros_mes = saldo_devedor * taxa_juros_mensal
                amortizacao_total = amortizacao_base + valor_extra
                prestacao_base = amortizacao_base + juros_mes
                prestacao_total = prestacao_constante + valor_extra_extra
                saldo_devedor -= amortizacao_total

            saldos_devedores.append(max(saldo_devedor, 0))  # Garantir que não fique negativo
            prestacoes_base.append(prestacao_base)
            prestacoes_totais.append(prestacao_total)
            juros_pago.append(juros_mes)
            amortizacoes_base.append(amortizacao_base)
            amortizacoes_extra.append(valor_extra)
            amortizacoes_totais.append(amortizacao_total)

            # Interrompe o loop se o saldo devedor for zero
            if saldo_devedor <= 0:
                break

        num_prestacoes = len(saldos_devedores)
        # Criar DataFrame
        df = pd.DataFrame({
            'Parcela': np.arange(1, num_prestacoes + 1),
            'Prestação Base': prestacoes_base,
            'Prestação Total': prestacoes_totais,
            'Juros': juros_pago,
            'Amortização Base': amortizacoes_base,
            'Amortização Extra': amortizacoes_extra,
            'Amortização Total': amortizacoes_totais,
            'Saldo Devedor': saldos_devedores
        })

        return df

    if modalidade == 'SAC':
        return _create_data_sac(taxa_juros_anual, num_prestacoes, valor_financiamento, valor_extra)
    if modalidade == 'Price':
        return _create_data_price(taxa_juros_anual, num_prestacoes, valor_financiamento, valor_extra)
    if modalidade == 'SAC (parcela constante)':
        return _create_data_sac_const_parcela(taxa_juros_anual, num_prestacoes, valor_financiamento, valor_extra)

def create_chart(df):
    # Criar gráfico com Plotly
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['Parcela'], y=df['Saldo Devedor'], mode='lines', name='Saldo Devedor', line=dict(color='#0098ff')))

    # fig.add_trace(go.Scatter(x=df['Parcela'], y=df['Amortização Base'], mode='lines', name='Amortização Base', line=dict(color='yellow')))

    # fig.add_trace(go.Scatter(x=df['Parcela'], y=df['Amortização Extra'], mode='lines', name='Amortização Extra', line=dict(color='grey')))

    fig.add_trace(go.Scatter(x=df['Parcela'], y=df['Amortização Total'], mode='lines', name='Amortização Total', line=dict(color='pink')))

    fig.add_trace(go.Scatter(x=df['Parcela'], y=df['Juros'], mode='lines', name='Juros', line=dict(color='green')))

    # fig.add_trace(go.Scatter(x=df['Parcela'], y=df['Prestação Base'], mode='lines', name='Prestação Base', line=dict(color='red')))

    fig.add_trace(go.Scatter(x=df['Parcela'], y=df['Prestação Total'], mode='lines', name='Prestação Total', line=dict(color='orange')))

    fig.update_layout(
        # title='Saldo Devedor e Valores das Prestações ao longo das 360 Prestações',
        xaxis_title='Parcela',
        yaxis_title='Valor (R$)',
        yaxis=dict(title='Saldo Devedor (R$)', side='left', overlaying='y2'),
        yaxis2=dict(title='Prestação (R$)', side='right'),
        legend=dict(
            orientation='h',
            x=0.5,
            xanchor='center',
            y=-0.2,
            yanchor='top'
        )
    )
    fig.update_layout(legend_itemdoubleclick=False)
    return fig