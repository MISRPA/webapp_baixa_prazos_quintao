import streamlit as st
import io
import base64
from PIL import Image

from module.core.excel import Excel

def gerar_markdown_download_excel(
    dicio_excel: dict,
    name: str='relatorio.xlsx',
    texto_botao: str='Baixar Relatório',
    btn_style='border-radius: 5px; padding: 5px; margin-bottom: 15px',
    btn_class=''
    ):
    with st.spinner('Gerando download'):
        output_file = io.BytesIO()
        Excel(output_file).exportar_excel(dicio_excel)
        output_file.seek(0)  # Voltar para o início do arquivo
        encoded_data = base64.b64encode(output_file.getvalue()).decode("utf-8")
        href = f'''
        <button style="{btn_style}" class="{btn_class}">
            <a style="text-decoration: none;" 
                href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{encoded_data}" download="{name}">
                    {texto_botao}
            </a>
        </button>'''
        return href

def gerar_botao_download_imagem(
    imagem: Image.Image,
    nome: str = "imagem.png",
    texto_botao: str = "Baixar Imagem",
    btn_style='border-radius: 5px; padding: 5px; margin-bottom: 15px',
    btn_class=''
    ):
    with st.spinner('Gerando download'):
        output_buffer = io.BytesIO()
        imagem.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        encoded_image = base64.b64encode(output_buffer.getvalue()).decode()
        href = f'''
        <button style="{btn_style}" class="{btn_class}">
            <a style="text-decoration: none;" 
                href="data:image/png;base64,{encoded_image}" download="{nome}">
                    {texto_botao}
            </a>
        </button>'''
        return href
