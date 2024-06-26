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
from module.app.utils.components import gerar_botao_download_imagem

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

# Sua função para adicionar texto à imagem
def adicionar_texto(imagem, texto, posicao, fonte, cor=(255, 255, 255)):
    desenho = ImageDraw.Draw(imagem)
    desenho.text(posicao, texto, fill=cor, font=fonte)

def pagina_gerador_assinaturas_unitario(name):
    st.header("Gerador de Assinatura Unitário FC")
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
        
        imagem_gerada = False
        
        if select_filial:
            col1, col2, col3 = st.columns(3)
            with col1:
                input_nome = st.text_input('Nome Completo*: ')
            with col2:
                input_cargo = st.text_input("Cargo*: ")
            with col3:
                input_celular = st.text_input("Celular: ")
            
            with st.container():
                col1, col2, _ = st.columns([2, 1, 1])
                
                with col1:
                    if input_nome.strip() and input_cargo.strip():
                        if st.button("Gerar assinatura"):
                            with st.spinner("Gerando assinatura..."):
                                fonte14px, fonte12px, fonte8px = inicializar_fontes()

                                if fonte14px and fonte12px and fonte8px:
                                    posicaoNome = (200, 20)
                                    posicaoTelefone = (200, 45)
                                    posicaoEndereco = (200, 70)
                                    posicaoSite = (300, 108)
                                
                                if not os.path.exists('output'):
                                    os.makedirs('output')

                                nome_completo = input_nome.title()
                                cargo = input_cargo
                                nome_cargo = f"{nome_completo} | {cargo}"
                                # Telefone e Endereço
                                telefone, endereco = DADOS_FILIAIS.get(select_filial, ["", ""])
                                celular = input_celular
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
                                # output_path = os.path.join(Directory.OUTPUT.value, f"{input_nome}.png")
                                # imagem.save(output_path)                        
                                imagem_gerada = True
                                
                        
                    else:
                        st.warning("Por favor, preencha os campos necessários.")
                
                with col2:
                    if imagem_gerada:
                        st.markdown(
                            gerar_botao_download_imagem(
                                imagem=imagem,
                                texto_botao='Baixar Assinatura',
                            ),
                            unsafe_allow_html=True
                        )
                        
                if imagem_gerada:
                    st.image(imagem, caption=f"Assinatura de {input_nome}")