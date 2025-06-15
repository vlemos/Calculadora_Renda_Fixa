import streamlit as st
import pandas as pd
import time
import numpy as np

# declara variaveis globais --------------------------------------------------------------------------------------------------------------

Taxa_Prefixada_ano = 0
CDI_ano = 0
Taxa_adicional_CDI = 0
Percentual_CDI_ano = 0
IPCA_estimado = 0
Taxa_real = 0
valor_face=0

# funções ---------------------------------------------------------------------------------------------------------------------------------
def calcula_taxa_efetiva_anual(opcao):
     if opcao == 'Prefixado':
          return Taxa_Prefixada_ano /100
     if opcao == 'DI+Taxa':
          return (CDI_ano + Taxa_adicional_CDI)/100
     if opcao == '%DI':
          return ((CDI_ano/100) * Percentual_CDI_ano)/ 100
     if opcao == 'IPCA+Taxa':
          return (IPCA_estimado + Taxa_real)/100
     

def calcula_dias_uteis(data_compra, data_venda):
     
     data_compra = pd.to_datetime(data_compra)
     data_venda = pd.to_datetime(data_venda)
     feriados_df = pd.read_excel('feriados_nacionais.xls')
     feriados = pd.to_datetime(feriados_df['Data']).dt.date
     feriados_np = np.array(feriados, dtype='datetime64[D]')

     return np.busday_count(data_compra.date(), data_venda.date(), holidays=feriados_np) -1
    

def calcular_renda_fixa(opcao,data_compra,data_venda):
    ''' Calcula a Renda Fixa com base na escola do Usuario'''
    taxa_efetiva_anual = calcula_taxa_efetiva_anual(opcao)
    dias_uteis = calcula_dias_uteis(data_compra,data_venda)

    calculo = valor_face / (1 + taxa_efetiva_anual)**(dias_uteis/252)

    st.write(f'A Opcação escolhida foi: {opcao}, O perido contempla {dias_uteis} dias utéis,  e o valor calculado é R${calculo:.2f}')

# Capturando os dadods --------------------------------------------------------------------------------------------------------------------
st.title("Calculadora de Renda Fixa")

valor_face = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", step=0.01)
data_compra = st.date_input("Data da Compra")
data_venda = st.date_input("Data da Venda")
# Lista de opções
opcoes = ["Selecione", "Prefixado", "DI+Taxa", "%DI", "IPCA+Taxa"]
opcao = st.selectbox("opção", opcoes)

if opcao == 'Prefixado':
    Taxa_Prefixada_ano = st.number_input('Taxa Préfixada (% a.a)', min_value=0.00 , max_value=100.0,step=0.1, format="%.2f")

if opcao == 'DI+Taxa' or opcao ==  '%DI':
    CDI_ano =st.number_input('CDI (% a.a.)', min_value=0.00 , max_value=100.0,step=0.1, format="%.2f")

if opcao == 'DI+Taxa':
    Taxa_adicional_CDI = st.number_input('Taxa adicional sobre CDI (%)', min_value=0.00 , max_value=100.0,step=0.1, format="%.2f")

if opcao == '%DI':   
    Percentual_CDI_ano = st.number_input('Percentual do CDI (%)', min_value=0.00 , max_value=100.0,step=0.1, format="%.2f")
    
if opcao == 'IPCA+Taxa':      
    IPCA_estimado = st.number_input('IPCA estimado (% a.a.)', min_value=0.00 , max_value=100.0,step=0.1, format="%.2f")
    Taxa_real = st.number_input('Taxa real (% a.a.)', min_value=0.00 , max_value=100.0,step=0.1, format="%.2f")


# Botão de envio do formulário 
enviado = st.button("Calcular")


# Faz todas as consistências de tela -------------------------------------------------------------------------------------------
if enviado:
    if valor_face <=0:
        st.warning('Informe um valor Maior que Zero!')
        st.stop()
    if data_compra >= data_venda:
       st.warning('A data da Compra deve ser menor que a data da venda')
       st.stop()  
    if opcao == 'Selecione':
        st.warning('Selecione uma Opção')
        st.stop()
    else:
        if opcao == 'Prefixado' and Taxa_Prefixada_ano == 0.0:
            st.warning('Preencha a Taxa Prefixada ao Ano') 
            st.stop()
        if opcao == 'DI+Taxa' and (CDI_ano == 0 or Taxa_adicional_CDI == 0 ):
              st.warning('Preencha O % CDI ao Ano e Também a Taxa adicional do CDI')
              st.stop()
        if opcao == '%DI' and (CDI_ano == 0 or Percentual_CDI_ano == 0 ):
               st.warning('Preencha O % CDI ao Ano e Também o percentual de retorno do CDI')
               st.stop()       
        if opcao == 'IPCA+Taxa' and (IPCA_estimado == 0 or Taxa_real == 0 ):
               st.warning('Preencha O IPCA Estimado e a Taxa Real')
               st.stop()   
        else:
            with st.spinner('Calculando...'):
                time.sleep(2)
            calcular_renda_fixa(opcao,data_compra,data_venda)