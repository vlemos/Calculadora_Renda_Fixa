import streamlit as st
import pandas as pd
import time
import numpy as np

DIAS_UTEIS_ANO = 252

def calcula_taxa_efetiva_anual(
    opcao: str,
    taxa_prefixada_ano: float = 0,
    cdi_ano: float = 0,
    taxa_adicional_cdi: float = 0,
    percentual_cdi_ano: float = 0,
    ipca_estimado: float = 0,
    taxa_real: float = 0
) -> float:
    if opcao == 'Prefixado':
        return taxa_prefixada_ano / 100
    if opcao == 'DI+Taxa':
        return (cdi_ano + taxa_adicional_cdi) / 100
    if opcao == '%DI':
        return ((cdi_ano / 100) * percentual_cdi_ano) / 100
    if opcao == 'IPCA+Taxa':
        return (ipca_estimado + taxa_real) / 100
    return 0

def calcula_dias_uteis(data_compra, data_venda, caminho_feriados='feriados_nacionais.xls') -> int:
    data_compra = pd.to_datetime(data_compra)
    data_venda = pd.to_datetime(data_venda)
    try:
        feriados_df = pd.read_excel(caminho_feriados)
        feriados = pd.to_datetime(feriados_df['Data']).dt.date
        feriados_np = np.array(feriados, dtype='datetime64[D]')
    except Exception as e:
        st.error(f'Erro ao ler feriados: {e}')
        feriados_np = None
    return np.busday_count(data_compra.date(), data_venda.date(), holidays=feriados_np) - 1

def validar_inputs(valor_face, data_compra, data_venda, opcao, taxas) -> bool:
    if valor_face <= 0:
        st.warning('Informe um valor Maior que Zero!')
        return False
    if data_compra >= data_venda:
        st.warning('A data da Compra deve ser menor que a data da venda')
        return False
    if opcao == 'Selecione':
        st.warning('Selecione uma Opção')
        return False
    if opcao == 'Prefixado' and taxas['taxa_prefixada_ano'] == 0.0:
        st.warning('Preencha a Taxa Prefixada ao Ano')
        return False
    if opcao == 'DI+Taxa' and (taxas['cdi_ano'] == 0 or taxas['taxa_adicional_cdi'] == 0):
        st.warning('Preencha O % CDI ao Ano e Também a Taxa adicional do CDI')
        return False
    if opcao == '%DI' and (taxas['cdi_ano'] == 0 or taxas['percentual_cdi_ano'] == 0):
        st.warning('Preencha O % CDI ao Ano e Também o percentual de retorno do CDI')
        return False
    if opcao == 'IPCA+Taxa' and (taxas['ipca_estimado'] == 0 or taxas['taxa_real'] == 0):
        st.warning('Preencha O IPCA Estimado e a Taxa Real')
        return False
    return True

def calcular_renda_fixa(valor_face, opcao, data_compra, data_venda, taxas):
    taxa_efetiva_anual = calcula_taxa_efetiva_anual(opcao, **taxas)
    dias_uteis = calcula_dias_uteis(data_compra, data_venda)
    calculo = valor_face / (1 + taxa_efetiva_anual) ** (dias_uteis / DIAS_UTEIS_ANO)
    st.write(f'A Opção escolhida foi: {opcao}, O período contempla {dias_uteis} dias úteis, e o valor calculado é R${calculo:.2f}')

# Interface Streamlit
st.title("Calculadora de Renda Fixa")
valor_face = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", step=0.01)
data_compra = st.date_input("Data da Compra")
data_venda = st.date_input("Data da Venda")
opcoes = ["Selecione", "Prefixado", "DI+Taxa", "%DI", "IPCA+Taxa"]
opcao = st.selectbox("Opção", opcoes)

taxas = {
    'taxa_prefixada_ano': 0,
    'cdi_ano': 0,
    'taxa_adicional_cdi': 0,
    'percentual_cdi_ano': 0,
    'ipca_estimado': 0,
    'taxa_real': 0
}

if opcao == 'Prefixado':
    taxas['taxa_prefixada_ano'] = st.number_input('Taxa Préfixada (% a.a)', min_value=0.00, max_value=100.0, step=0.1, format="%.2f")
if opcao in ['DI+Taxa', '%DI']:
    taxas['cdi_ano'] = st.number_input('CDI (% a.a.)', min_value=0.00, max_value=100.0, step=0.1, format="%.2f")
if opcao == 'DI+Taxa':
    taxas['taxa_adicional_cdi'] = st.number_input('Taxa adicional sobre CDI (%)', min_value=0.00, max_value=100.0, step=0.1, format="%.2f")
if opcao == '%DI':
    taxas['percentual_cdi_ano'] = st.number_input('Percentual do CDI (%)', min_value=0.00, max_value=100.0, step=0.1, format="%.2f")
if opcao == 'IPCA+Taxa':
    taxas['ipca_estimado'] = st.number_input('IPCA estimado (% a.a.)', min_value=0.00, max_value=100.0, step=0.1, format="%.2f")
    taxas['taxa_real'] = st.number_input('Taxa real (% a.a.)', min_value=0.00, max_value=100.0, step=0.1, format="%.2f")

if st.button("Calcular"):
    if validar_inputs(valor_face, data_compra, data_venda, opcao, taxas):
        with st.spinner('Calculando...'):
            time.sleep(2)
        calcular_renda_fixa(valor_face, opcao, data_compra, data_venda, taxas)