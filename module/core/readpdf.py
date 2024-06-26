import os
import pdfplumber
from PyPDF2 import PdfWriter, PdfReader

from .customlogger import logger



class ReadPdf:
    '''Classe para ler arquivos pdf'''
    EXTENSION = '.pdf'

    def __init__(self, directory: str) -> None:
        self.directory = directory
        self.all_files = [os.path.join(self.directory, file) for file in os.listdir(self.directory)
                            if file.lower().endswith(self.EXTENSION)]

    def format_filename(self, file_name: str) -> str:
        '''Formata o nome do arquivo'''
        str(file_name)
        return file_name[len(self.directory):].replace(os.sep,"")

    def pdf_data(self, pdf: str) -> list[str]:
        '''Retorna uma lista com os dados do pdf'''
        file_name = self.format_filename(pdf)
        pages = []
        open_pdf = pdfplumber.open(os.path.join(self.directory,pdf))
        
        for e,page in enumerate(open_pdf.pages):
            page_text = page.extract_text().split()
            page_text = " ".join(page_text)
            
            dados = [
                f'Pagina {e+1}',
                file_name,
                page_text,
            ]
            pages.append(dados)
        
        if bool(page_text): logger.debug(f'PDF : {file_name} ::: Pages : {len(open_pdf.pages)}\n{page_text}')
        else: logger.error(f'Erro ao ler PDF ::: {file_name}')
        return pages

class SplitPdf(ReadPdf):
    '''Classe para separar os arquivos PDF'''

    def __init__(self,directory: str,output_directory: str) -> None:
        ReadPdf.__init__(self,directory)
        self.output_directory = output_directory

    def separar_pdf(self,pdf: str) -> None:
        '''Metodo para separar os arquivos PDF'''
        file_name = self.format_filename(pdf)
        file_name = file_name[:-len(self.EXTENSION)]
        pdf = os.path.join(self.directory,pdf)
        pdf_content = PdfReader(pdf)
        num_pages = pdf_content.getNumPages()

        for page in range(num_pages):
            pdf_writer = PdfWriter()
            pdf_writer.addPage(pdf_content.getPage(page))

            pdf_name = f'{file_name}_page_{page+1}.pdf'
            pdf_full_name = os.path.join(self.output_directory,pdf_name)
            with open(pdf_full_name,'wb') as new_pdf:
                pdf_writer.write(new_pdf)
    
    def juntar_pdf(self, pdf_name: str) -> None:
        '''Método para juntar os arquivos PDF em um único arquivo'''
        output_pdf = os.path.join(self.output_directory, pdf_name)

        pdf_writer = PdfWriter()

        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)

        for filename in os.listdir(self.directory):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(self.directory, filename)
                pdf_content = PdfReader(pdf_path)

                for page_num in range(len(pdf_content.pages)):
                    pdf_writer.add_page(pdf_content.pages[page_num])

        with open(output_pdf, 'wb') as output_file:
            pdf_writer.write(output_file)

if __name__ == "__main__":
    # Substitua 'diretorio_de_entrada' e 'diretorio_de_saida' pelos diretórios apropriados.
    diretorio_de_entrada = r'C:\Users\joao-almeida\Documents\repositorios_git\repositorios_git_original\robo_ateste_cef\module\arquivos_processo\entrada'
    diretorio_de_saida = r'C:\Users\joao-almeida\Documents\repositorios_git\repositorios_git_original\robo_ateste_cef\module\arquivos_processo\saida'

    split_pdf = SplitPdf(diretorio_de_entrada, diretorio_de_saida)
    split_pdf.juntar_pdf('arquivo_juntado.pdf')