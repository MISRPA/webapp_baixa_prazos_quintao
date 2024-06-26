import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

from module.manager import engine_espelho
from module.models import text
from module.core.utils import retry_on_failure, logger
from module.core.enviar_email import SendMail
from module.core.templates import TemplateRender
from module.directory import Directory, WORK_DIR

from .querys import QUERY_ASSINATURA


DADOS_FILIAIS = {
    "BH - MATRIZ": ["(31) 3298-5600", "Rua Bernardo Guimarães, 1998 \nLourdes, Belo Horizonte/MG | 30140-087"],
    "BH - SANTOS DUMONT": ["(31) 3298-5600", "Av. Santos Dumont, 330 \nCentro, Belo Horizonte/MG | 30111-040"],
    "BRASÍLIA": ["(61) 3574-2267 | (61) 3574-3370", "SRTVS Quadra 701 Bloco K, Salas 510 a 512 \nAsa Sul, Brasília/DF, 70340-908"],
    "CURITIBA": ["(41) 3501-2099 | (41) 3501-2055", "Rua Heitor Stockler de França, 396, Sala 1607 \nCentro Cívico, Curitiba/PR - 80030-030"],
    "FLORIANÓPOLIS": ["(48) 3204-67476 | (48) 3204-6477", "Rua Emílio Blum, 131, Sala 103, Bloco B \nCentro, Florianópolis/SC - 88020-010"],
    "FORTALEZA": ["(85) 2180-7307", "Rua Monsenhor Bruno, 1153, Sala 105, \nAldeota, Fortaleza/CE - 60115-191"],
    "PORTO ALEGRE": ["(51) 3519-3509", "Avenida Praia de Belas, 1212, Sala 1421, \nPraia de Belas, Porto Alegre/RS - 90110-000"],
    "RECIFE": ["(81) 3040-0852 | (81) 3037-0851", "Avenida Governador Agamenon Magalhães, 4775, Salas 505/506 \nIlha do Leite, Recife/PE - 50070-160"],
    "RIO DE JANEIRO": ["(21) 2531-1166", "Rua da Assembléia, 35 - 11° Andar \nCentro, Rio de Janeiro/RJ - 20011-001"],
    "SALVADOR": ["(71) 3500-5040 | (71) 3500-5041", "Avenida Tancredo Neves, 2.539, Sala 1313, Torre Nova York \nCaminho das Árvores, Salvador/BA - 41820-021"],
    "SP - SÃO PAULO": ["(11) 3054-5430", "Avenida Paulista, 1274 - Cj.31 - 12° andar \nBela Vista/SP - 01310-100"],
    "SP - SANTO ANDRÉ": ["(11) 3614-4900", "Rua Siqueira Campos, 842 \nCentro - Santo André/SP - 09020-240"],
    "TERESINA": ["(86) 3303-8975", "Rua Mato Grosso, nº 720, Sala 205, Torre Empresarial 01 \nPorenquanto, Teresina/PI - 64000-710"],
    "VITÓRIA": ["(27) 3222-2525", "Avenida Jerônimo Monteiro, 1000 - Salas: 508, 510 e 512 \nCentro, Vitória/ES - 29010-935"]
}

EXEMPLO_CARGOS_PROTHEUS = os.path.join('__notebook__', 'cargos_existentes_protheus.xlsx')

# inicializar as fontes
def inicializar_fontes():
    fonte14px_path = os.path.join('module', 'app', 'fonts', 'Roboto-Bold.ttf')
    fonte12px_path = os.path.join('module', 'app', 'fonts', 'Roboto-Bold.ttf')
    fonte8px_path = os.path.join('module', 'app', 'fonts', 'Roboto-Medium.ttf')

    if os.path.exists(fonte14px_path) and os.path.exists(fonte12px_path) and os.path.exists(fonte8px_path):
        fonte14px = ImageFont.truetype(fonte14px_path, size=14, encoding="unic")
        fonte12px = ImageFont.truetype(fonte12px_path, size=12, encoding="unic")
        fonte8px = ImageFont.truetype(fonte8px_path, size=10, encoding="unic")
        return fonte14px, fonte12px, fonte8px
    else:
        st.error("Arquivo de fonte ausente. Verifique os caminhos das fontes no código.")
        return None, None, None

#envio de email
def enviar_email(nome, row, output_path):
    mail = SendMail()
    
    mail.assunto = f'Assinatura de email atualizada - {nome}'
    mail.destinatarios = [
        row['USUARIOS']+'@ferreiraechagas.com.br',
    ]
    mail.copia = [
        'douglas.medina@ferreiraechagas.com.br'
    ]
    
    #TODO: Arrumar template do email
    template_render = TemplateRender(Directory.EMAIL_TEMPLATES.value)
    message = template_render.render_template(
        "feedback.html",
        url_site_header='https://ferreiraechagas.com.br/',
        url_logo_header='https://ferreiraechagas.com.br/wp-content/uploads/2019/07/logo-fc-branca2.png',
        url_site_footer='https://ferreiraechagas.com.br/',
        url_logo_footer='https://ferreiraechagas.com.br/wp-content/uploads/2019/07/logo-fc-branca2.png',
        data_email=datetime.now().strftime('%d/%m/%Y às %H:%M:%S'),
        textos=[
            f'Olá, {nome}.',
            'Segue em anexo sua assinatura de email atualizada.'
        ]
    )

    # Verificar se o arquivo da imagem existe antes de anexar
    if os.path.exists(output_path):
        mail.enviar_email(
            message,
            arquivos={f'{nome}.png': output_path,
                      'Assinatura_Gmail.pdf': os.path.join(WORK_DIR, 'app', 'guide_assinaturas', 'Assinatura_Gmail.pdf'),
                      'Assinatura_Zimbra.pdf': os.path.join(WORK_DIR, 'app', 'guide_assinaturas', 'Assinatura_Zimbra.pdf')
                      }
        )
        print(f'Envio de email para {nome} -- \033[92m OK \033[0m')
        logger.info(f'Envio de email para {nome} -- \033[92m OK \033[0m')
        
        os.remove(output_path)
        print(f'Arquivo {output_path} excluído -- \033[92m OK \033[0m')
        
    else:
        print(f"O arquivo da imagem para '{output_path}' não foi encontrado.")
        logger.info(f"O arquivo da imagem para '{output_path}' não foi encontrado.")

# Sua função para adicionar texto à imagem
def adicionar_texto(imagem, texto, posicao, fonte, cor=(255, 255, 255)):
    desenho = ImageDraw.Draw(imagem)
    desenho.text(posicao, texto, fill=cor, font=fonte)

# Função para buscar dados do usuário no banco de dados usando apenas o nome
@retry_on_failure(5, 30)
def df_usuarios_db():
    with engine_espelho.begin() as con:
        df = pd.read_sql(text(QUERY_ASSINATURA), con)
    
    df.drop_duplicates('USUARIOS', inplace=True)
    df['USUARIOS'] = df['USUARIOS'].str.lower()
    print('Consulta realizada -- \033[92m OK \033[0m')
    return df

def pagina_gerador_assinaturas(name):
    st.header("Gerador de Assinaturas FC")
    with st.expander(':information_source: Informações sobre a aplicação'):
        st.info(f'''
Bem vindo(a), {name}! \n\n 
Esta aplicação facilita a criação e envio de assinaturas de email em lote para os usuários. \n\n 
Para que funcione corretamente, é necessário selecionar a filial desejada e inserir um arquivo excel com uma coluna que **contenha o nome exatamente igual a:
"Usuarios" e outra coluna com o nome "Cargo"**. \n\n
:warning: :orange[**O conteúdo da coluna "Usuarios" deverá ser preenchida com o login de usuário com "." ex: seu.usuario.**] :warning: \n
:warning: :orange[**O campo CARGO pode ser preenchido da maneira que será apresentada na assinatura, porém, abaixo haverá um guia com os alguns dos cargos disponíveis no Protheus e no padrão das assinaturas.**] :warning: \n
Após o upload, você deve clicar no botão "Gerar assinaturas" para começar o processo. \n\n
:warning: :orange[**Ao clicar no botão, será iniciado o processo de criação e será enviado automaticamente a assinatura ao email do usuário que está cadastrado no MAX.**] :warning: \n
:warning: :orange[**Esta operação pode demorar um pouco, de acordo com a quantidade de usuários.**] :warning: \n
Ao completar o processo, será apresentada uma mensagem de sucesso.
                    ''', 
                    icon="ℹ️"
                )
        st.table(pd.read_excel(EXEMPLO_CARGOS_PROTHEUS))
            
    with st.container():
        select_filial = st.selectbox("Selecione a filial:", DADOS_FILIAIS.keys())
        
        if select_filial: 
            uploaded_file = st.file_uploader("Escolha um arquivo", type=['xlsx'])

            if uploaded_file is not None:
                print('Arquivo anexado -- \033[92m OK \033[0m')
                df_input = pd.read_excel(uploaded_file)
                df_input.columns = df_input.columns.str.upper()
                
                st.markdown('Primeiras linhas da tabela inserida')
                st.table(df_input.head(2))

                if 'USUARIOS' in df_input.columns.tolist() and 'CARGO' in df_input.columns.tolist():
                    if st.button("Gerar assinaturas"):
                        with st.spinner('Gerando assinaturas...'):
                            fonte14px, fonte12px, fonte8px = inicializar_fontes()

                            if fonte14px and fonte12px and fonte8px:
                                posicaoNome = (200, 20)
                                posicaoTelefone = (200, 45)
                                posicaoEndereco = (200, 70)
                                posicaoSite = (300, 108)
                            
                                if not os.path.exists('output'):
                                    os.makedirs('output')

                                df_input['USUARIOS'] = df_input['USUARIOS'].str.lower().str.strip()
                                df_usuarios = df_usuarios_db()
                                df_merge = pd.merge(df_input, df_usuarios, 'left', 'USUARIOS')
                                df_merge = df_merge[~df_merge['IDUSUARIO'].isnull()].copy()

                                for index, row in df_merge.iterrows():
                                    nome = row['USUARIOS']

                                    # Extrair informações do usuário
                                    nome_completo = row['NOME'].title()
                                    cargo = row['CARGO'].title()
                                    nome_cargo = f"{nome_completo} | {cargo}"
                                    # Telefone e Endereço
                                    telefone, endereco = DADOS_FILIAIS.get(select_filial, ["", ""])
                                    celular = None
                                    telefone_celular = f"{telefone} | {celular}" if celular else telefone
                                    site = "www.ferreiraechagas.com.br"


                                    # Criar a imagem com base nos dados do banco de dados
                                    imagem_path = os.path.join('module', 'app', 'images', 'assinatura_atualizada.png')
                                    imagem = Image.open(imagem_path)
                                    adicionar_texto(imagem, nome_cargo, posicaoNome, fonte14px)
                                    adicionar_texto(imagem, telefone_celular, posicaoTelefone, fonte12px)
                                    adicionar_texto(imagem, endereco, posicaoEndereco, fonte12px)
                                    adicionar_texto(imagem, site, posicaoSite, fonte8px)

                                    # Salvar e exibir a imagem
                                    output_path = f"output/{nome}.png"
                                    imagem.save(output_path)
                                    logger.info('Assinatura gerada -- \033[92m OK \033[0m')

                                    enviar_email(nome, row, output_path)
                                    logger.info("-----------------------------------------------------")
                            st.success("Assinaturas enviadas para o email dos colaboradores.")
                            
                elif not 'USUARIOS' in df_input.columns.tolist():
                    logger.warning('Arquivo sem coluna USUARIOS')
                    st.error('Não foi encontrada a coluna "Usuarios" no arquivo inserido. \n\n Gentileza verificar e inserir novamente.')
                    st.button("Gerar assinaturas", disabled=True)
                
                elif not 'CARGO' in df_input.columns.tolist():
                    logger.warning('Arquivo sem coluna CARGO')
                    st.error('Não foi encontrada a coluna "Cargo" no arquivo inserido. \n\n Gentileza verificar e inserir novamente.')
                    st.button("Gerar assinaturas", disabled=True)