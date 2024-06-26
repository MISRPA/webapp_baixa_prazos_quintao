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
    
]

COLUNAS_OBRIGATORIAS = [
    "ID_Proc",
    "Data_Prazo",
    "Cod_Tipo_prazo",
    "Peremptorio(sim/Não)",
    "Cod_advogado_prazo",
    "User_cad_prazo",
    "Data_cad_prazo",
    "Status",
]

COLUMNS_MAP = {
    'ID_Proc': 'IDPROC',
    'Data_Prazo': 'DTCOMPROMISSO',
    'Cod_Tipo_prazo': 'CODTIPOPRAZO',
    'Peremptorio(sim/Não)': 'PEREMPTORIO',
    'Cod_advogado_prazo': 'CODADVOGADO',
    'User_cad_prazo': 'USERCAD',
    'Data_cad_prazo': 'DATACAD',
    'Status': 'STATUS',
}

texto_colunas = "\n".join(list('- '+ i for i in COLUNAS_OBRIGATORIAS))

robo = 'webapp_importa_prazos'


PRODUCAO = False
if not PRODUCAO:
    print('////////////// AMBIENTE DE DESENVOLVIMENTO ///////////')
    print('IMPORTACAO DE PRAZOS')
    print('////////////// AMBIENTE DE DESENVOLVIMENTO ///////////')
    engine = engine_espelho
    tabela = 'teste_tbprazos'
    schema = 'rpa'
else:
    #TODO: Mudar para base de producao
    engine = engine_producao_escrita
    tabela = 'TbPrazos'
    schema = 'dbo'


def botao_start_importacao():
    if st.form_submit_button("Set running", help='Clique aqui para setar importacao running'):
        update_importacao_TbStatusRobo(status='running', robo=robo)
        st.experimental_rerun()

def botao_stop_importacao():
    if st.form_submit_button("Set paused", help='Clique aqui para setar importacao paused'):
        update_importacao_TbStatusRobo(status='paused', robo=robo)
        st.experimental_rerun()

def importar_prazos(df: pd.DataFrame):
    df.rename(columns=COLUMNS_MAP, inplace=True)
    
    df.to_sql(
        tabela,
        engine,
        schema,
        'append', #[WARNING] Tomar cuidado, se setar replace irá apagar os dados da tabela de prazos
        False
    )


def pagina_importacao_prazos(user_data):
    
    df = select_TbStatusRobo(robo=robo)
    
    status_robo = df['STATUS'][0]
    importacao = df['IMPORTACAO'][0]
    
    
    st.header("Importação de Prazos")
    st.warning(f"""
A base deve conter as seguintes colunas:

{texto_colunas}

Baixe a planilha modelo abaixo.

            """, icon="🚨")

    st.markdown(
        gerar_markdown_download_excel(
            dicio_excel={'BASE': pd.DataFrame(columns=COLUNAS_OBRIGATORIAS)},
            name='importacao_prazos.xlsx',
            texto_botao='Planilha Modelo'
            ),
        unsafe_allow_html=True
    )
    
    if user_data['role'] == 'admin':
        expander_table = st.expander('Controle do Status da Importação')

        with expander_table:
            with st.form("controle_importacao_form"):
                wcol1, wcol2 = st.columns(2)
                
                with wcol1:
                    botao_start_importacao()
                
                with wcol2:
                    botao_stop_importacao()
    
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
    Ao clicar em Importar, aguarde até que a importação seja finalizada!
                    ''', icon='🚨')
                        
                        btn_import = st.empty()
                        
                        if btn_import.button('Importar Prazos', key='import_button'):
                            with st.spinner('Realizando importação, aguarde...'):
                                try:
                                    btn_import.empty()
                                    
                                    update_importacao_TbStatusRobo(status='running', robo=robo)
                                    
                                    importar_prazos(df)
                                    st.success('Importação concluída com sucesso!')
                                    
                                except Exception as e:
                                    st.error(f'Erro:\n {e}')
                                    
                                finally:
                                    update_importacao_TbStatusRobo(status='paused', robo=robo)
    else:
        st.warning(f'''
Importação em andamento, aguarde...
                ''', icon='🚨')