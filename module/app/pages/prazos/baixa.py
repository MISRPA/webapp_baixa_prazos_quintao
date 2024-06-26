import streamlit as st
import io
import pandas as pd
import os

from module.app.utils.components import gerar_markdown_download_excel
from module.core.utils import retry_on_failure
from module.manager import engine_espelho, engine_producao_escrita
from module.models import text
from module.robot.utils import (
    update_status_TbStatusRobo,
    select_TbStatusRobo,
    update_erros_legado,
    update_importacao_TbStatusRobo,
    select_robo_top_running,
)


USUARIOS_PERMITIDOS = [
    'leticia.quintao',
]

COLUNAS_OBRIGATORIAS = [
    "IdProc",
    "DtCompromisso",
    "Data_cad_prazo",
    "CodPublicacao",
]

texto_colunas = "\n".join(list('- '+ i for i in COLUNAS_OBRIGATORIAS))

robo = 'webapp_baixa_prazos'


PRODUCAO = False
if not PRODUCAO:
    print('////////////// AMBIENTE DE DESENVOLVIMENTO ///////////')
    print('BAIXA DE PRAZOS')
    print('////////////// AMBIENTE DE DESENVOLVIMENTO ///////////')
    engine = engine_espelho
    tabela = 'mis.rpa.teste_webapp_baixa_prazos_quintao'
else:
    engine = engine_producao_escrita
    tabela = f'TOTAL_FC.dbo.TbPrazos'


def botao_start_baixa():
    if st.form_submit_button("Set running", help='Clique aqui para setar importacao running'):
        update_importacao_TbStatusRobo(status='running', robo=robo)
        st.experimental_rerun()

def botao_stop_baixa():
    if st.form_submit_button("Set paused", help='Clique aqui para setar importacao paused'):
        update_importacao_TbStatusRobo(status='paused', robo=robo)
        st.experimental_rerun()

def baixa_prazos(df: pd.DataFrame):
    
    
    
    try:
        with engine.begin() as con:
            for index, row in df.iterrows():
                con.execute(text(f'''
    INSERT INTO {tabela} (
        IDPROC,
        DTCOMPROMISSO,
        CODTIPOPRAZO,
        PEREMPTORIO,
        CODADVOGADO,
        USERCAD,
        DATACAD,
        STATUS,
        CODPUBLICACAO) 
    VALUES (
        :IDPROC,
        :DTCOMPROMISSO,
        1775,
        'SIM',
        '228',
        'ROBO.WEBAPP.LETICIA',
        :DATA_CAD_PRAZO,
        'B',
        :CODPUBLICACAO
    )
    '''), [{
        'IDPROC': int(row['IdProc']),
        'DTCOMPROMISSO': pd.to_datetime(row['DtCompromisso']),
        'DATA_CAD_PRAZO': pd.to_datetime(row['Data_cad_prazo']),
        'CODPUBLICACAO': int(row['CodPublicacao']),
    }])
    except Exception as e:
        raise e
    
    finally:
        con.close()


def pagina_baixa_prazos(user_data):
    
    df = select_TbStatusRobo(robo=robo)
    
    status_robo = df['STATUS'][0]
    importacao = df['IMPORTACAO'][0]
    
    st.header("Baixa de Prazos")
    st.warning(f"""
A base deve conter as seguintes colunas:

{texto_colunas}


Baixe a planilha modelo abaixo.

            """, icon="🚨")

    st.markdown(
        gerar_markdown_download_excel(
            dicio_excel={'BASE': pd.DataFrame(columns=COLUNAS_OBRIGATORIAS)},
            name='modelo_insert_prazos_baixados.xlsx',
            texto_botao='Planilha Modelo',
            btn_class='css-lte5cn ef3psqc11'
            ),
        unsafe_allow_html=True
    )
    
    if user_data['role'] == 'admin':
        expander_table = st.expander('Controle do Status da Importação')

        with expander_table:
            with st.form("controle_baixa_form"):
                wcol1, wcol2 = st.columns(2)
                
                with wcol1:
                    botao_start_baixa()
                
                with wcol2:
                    botao_stop_baixa()
    
    if importacao == 'paused':
        uploaded_file = st.file_uploader(
            "Por favor, faça o upload do arquivo Excel:",
            type=['xlsx'],
            help='Arrate ou clique para selecionar o arquivo Excel'
            )
        if uploaded_file is not None:
            filename, extension  = os.path.splitext(uploaded_file.name)
            
            with st.spinner(f'Carregando {filename}'):
                df = pd.read_excel(uploaded_file)
                
            if df.empty:
                st.error(f'A base não pode estar vazia!')
                
            else:
                colunas_faltantes = []
                for col in COLUNAS_OBRIGATORIAS:
                    if col not in df.columns.tolist():
                        colunas_faltantes.append(col)

                if colunas_faltantes:
                    st.error(f'Coluna(s) {colunas_faltantes} não encontrada(s)!')
                    
                else:
                    for col in df.columns.tolist():
                        if not df[df[col].isnull()].empty:
                            st.error(f'Coluna {col} contém valores nulos, verifique a base inserida!')
                            break
                        
                    else:
                        df = df[COLUNAS_OBRIGATORIAS].copy()
                        
                        with st.expander(filename):
                            st.dataframe(df)
                        
                        st.warning(f'''
    Ao clicar em Importar, aguarde até que a baixa seja finalizada!
                    ''', icon='🚨')
                        
                        btn_import = st.empty()
                        
                        if btn_import.button('Baixar Prazos', key='import_button'):
                            with st.spinner('Realizando baixa dos prazos, aguarde...'):
                                try:
                                    btn_import.empty()
                                    
                                    # update_importacao_TbStatusRobo(status='running', robo=robo)
                                    
                                    baixa_prazos(df)
                                    st.success('Baixa de Prazos concluída com sucesso!')
                                    
                                except Exception as e:
                                    st.error(f'Erro:\n {e}')
                                    
                                finally:
                                    update_importacao_TbStatusRobo(status='paused', robo=robo)
    else:
        st.warning(f'''
Baixa de prazos em andamento, aguarde...
                ''', icon='🚨')