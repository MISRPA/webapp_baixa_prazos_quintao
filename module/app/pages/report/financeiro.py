import streamlit as st
import io
import pandas as pd

from module.core.utils import retry_on_failure, logger
from module.manager import engine_espelho
from module.models import text

from .querys import QUERY_FINANCEIRO, QUERY_FINANCEIRO_BNB

# ------------------------------------------------------------------- #
# TODO: criar uma opção e uma query para o BNB (todos os clientes) 
# e manter a possibilidade de consultar apenas um cliente.
# ------------------------------------------------------------------- #
def gerar_relatorio_financeiro(consulta_clientes):
    st.header("Relatórios MIS")
    st.write("Os dados das pesquisas estão padronizados, alterando apenas o cliente.")

    df_cliente = consulta_clientes()

    cliente = st.selectbox(
        label='Selecione um cliente:',
        placeholder='Select...',
        options=df_cliente['NomeInterno'],
    )
    logger.info(f'cliente selecionado: {cliente}')
    
    if not cliente:
        st.button("Gerar Relatório", disabled=True)
        
    if 'BANCO DO NORDESTE' in cliente:
        if st.button(f"Gerar Relatório"):
            arquivo_excel = f"relatorio_banco_do_nordeste.xlsx"

            with st.spinner('Gerando relatório, aguarde...'):
                cliente_consulta_fin = df_cliente[df_cliente['NomeInterno'] == cliente]['IdCliente'].astype(str)
                consulta_result = pd.read_sql(text(QUERY_FINANCEIRO_BNB),con=engine_espelho)

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    consulta_result.fillna('NULL').to_excel(writer, index=False, sheet_name='BASE')
                buffer.seek(0)

            st.success(f"Relatório gerado com sucesso!")
            logger.info(f"Relatório gerado com sucesso!")

            # Add a separate button for downloading the report
            bytes_data = buffer.read()
            if st.download_button(
                label="Download Relatório", 
                data=bytes_data, 
                file_name=arquivo_excel
            ):
                print("Arquivo baixado.")
                logger.info("Arquivo baixado.")
            print(f"Consulta BNB finalizada.")
            logger.info(f"Consulta BNB finalizada.")
        
    else:
        if st.button(f"Gerar Relatório"):
            arquivo_excel = f"relatorio_{cliente}.xlsx"

            with st.spinner('Gerando relatório, aguarde...'):
                cliente_consulta_fin = df_cliente[df_cliente['NomeInterno'] == cliente]['IdCliente'].astype(str)
                consulta_result = pd.read_sql(
                        text(QUERY_FINANCEIRO.format(id_cliente=cliente_consulta_fin.iloc[0])),
                        con=engine_espelho
                    )

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    consulta_result.fillna('NULL').to_excel(writer, index=False, sheet_name='BASE')
                buffer.seek(0)

            st.success(f"Relatório gerado com sucesso!")
            logger.info(f"Relatório gerado com sucesso!")

            # Add a separate button for downloading the report
            bytes_data = buffer.read()
            if st.download_button(
                label="Download Relatório", 
                data=bytes_data, 
                file_name=arquivo_excel
            ):
                print("Arquivo baixado.")
                logger.info("Arquivo baixado.")
            print(f"Consulta {cliente} finalizada.")
            logger.info(f"Consulta {cliente} finalizada.")