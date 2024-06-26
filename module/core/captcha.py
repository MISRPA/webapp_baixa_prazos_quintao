'''
Módulo de resolução de CAPTCHAs utilizando APIs externas.

Este módulo contém funções que utilizam APIs externas para resolver desafios 
CAPTCHA presentes em páginas web. As seguintes APIs são atualmente suportadas:

- BestCaptchaSolver: uma API de resolução de CAPTCHAs que suporta uma ampla 
variedade de tipos de CAPTCHAs, incluindo reCAPTCHA e hCaptcha.

Para utilizar as funções deste módulo, é necessário obter um token de acesso 
para a API desejada e passá-lo como argumento para a função correspondente. 
É possível também configurar o nível de detalhamento dos registros de log 
gerados pelas funções, através da definição da variável global `LOG_LEVEL`.

Este módulo requer as seguintes bibliotecas externas:
- requests
- pydub
- SpeechRecognition
- urllib

Para obter mais informações sobre as APIs suportadas e suas respectivas 
funções, consulte a documentação de cada função individualmente.
'''


from bestcaptchasolverapi3.bestcaptchasolverapi import BestCaptchaSolverAPI
import os
import speech_recognition as sr
import ffmpy
import requests
import urllib
import pydub
import sys
from time import sleep

from .customlogger import logger

from module.directory import Directory
from module import settings


class CaptchaSolver:
    '''Classe com metodos para solucionar Captchas'''
    CAPTCHA_ERROR: int = 0
    BCS_TOKEN = settings.BCS_TOKEN

    def __init__(self) -> None:
        self.temp_folder = Directory.TEMP.value

    def remove_file(self,file) -> None:
        try: os.remove(os.path.join(self.temp_folder, file))
        except Exception as WarnDeleteTempFiles:
            logger.error(f'{WarnDeleteTempFiles} ::: FAILED TO DELETE FILE: {file} ::: {sys.exc_info()}',exc_info=True)

    def __remove_audio_file(self, audio_file_name: str) -> None:
        """Remove audio file from the temporary folder

        Args:
            audio_file_name (str): nome do arquivo a ser removido
        """
        try:
            os.remove(os.path.join(self.temp_folder,f"{audio_file_name}.mp3"))
            os.remove(os.path.join(self.temp_folder,f"{audio_file_name}.wav"))
        except Exception as WarnDeleteTempFiles:
            logger.error(f'{WarnDeleteTempFiles} ::: FAILED TO DELETE AUDIO FILES ::: {sys.exc_info()}',exc_info=True)

    def audio_captcha_solver(self, audio_source_link: str) -> str:
        """
        Download de um arquivo de áudio de uma URL fornecida e transcrição do 
        conteúdo para texto usando a biblioteca SpeechRecognition.
        
        Argumentos:
        - audio_source_link: uma string que contém a URL do arquivo de áudio a 
        ser baixado e transcritos;
        - temp_folder: uma string que contém o caminho para a pasta temporária 
        onde o arquivo de áudio será armazenado.

        Retorna:
        - Uma string contendo o texto transcritos do arquivo de áudio, se a 
        transcrição for bem-sucedida;
        - False, se a transcrição falhar.

        Observações:
        - O arquivo de áudio baixado é convertido em um arquivo .wav antes da 
        transcrição;
        - A função utiliza uma string `audio_file_name` para nomear o arquivo 
        de áudio baixado e gerar uma chave para identificá-lo durante o processo;
        - Se a transcrição falhar, um registro de erro é criado no arquivo de 
        log e a variável `self.CAPTCHA_ERROR` é incrementada em 1.
        """
        audio_file_name: str = 'sample'
        for i in range(4):
            audio_file_name+='_'+self.random_generator()
        try:
            urllib.request.urlretrieve(audio_source_link, os.path.join(self.temp_folder,f"{audio_file_name}.mp3"))
            sound = pydub.AudioSegment.from_mp3(os.path.join(self.temp_folder,f"{audio_file_name}.mp3"))
            sound.export(os.path.join(self.temp_folder,f"{audio_file_name}.wav"), format="wav")
            sample_audio = sr.AudioFile(os.path.join(self.temp_folder,f"{audio_file_name}.wav"))
            r = sr.Recognizer()
            with sample_audio as source:
                audio = r.record(source)
            key = r.recognize_google(audio)
            logger.info("CAPTCHA PASSCODE: %s" % key)
            return key

        except Exception as WarnCaptchaError:
            self.CAPTCHA_ERROR += 1
            logger.error(f'{WarnCaptchaError} ::: {sys.exc_info()} ::: CAPTCHA_ERROR: {self.CAPTCHA_ERROR}',exc_info=True)
            return False

        finally: 
            self.__remove_audio_file(audio_file_name)

    def best_captcha_solver_api(self,page_url: str, site_key: str) -> str:
        """
            
        Solução de um desafio reCAPTCHA utilizando a API BestCaptchaSolver.

        Argumentos:
        - ACCESS_TOKEN: uma string que contém o token de acesso para a API 
        BestCaptchaSolver;
        - page_url: uma string que contém a URL da página onde o desafio 
        reCAPTCHA está presente;
        - site_key: uma string que contém a chave do site reCAPTCHA, que 
        identifica o desafio específico a ser resolvido.

        Retorna:
        - Uma string contendo a resposta (g-recaptcha-response) para o desafio 
        reCAPTCHA, se a solução for bem-sucedida;
        - None, se a solução falhar.

        Observações:
        - O desafio reCAPTCHA é enviado para a API BestCaptchaSolver para 
        resolução através do método `submit_recaptcha()`;
        - A função aguarda 60 segundos antes de tentar recuperar a resposta 
        do desafio, para permitir tempo suficiente para a resolução;
        - A resposta é recuperada através do método `retrieve()` e armazenada 
        na variável `response`;
        - Se a solução falhar, a função aguarda 1 segundo antes de tentar 
        recuperar novamente a resposta do desafio;
        - Um registro é criado no arquivo de log contendo o saldo da conta na 
        API BestCaptchaSolver e a resposta do desafio reCAPTCHA, se a solução for bem-sucedida.
        
        Exemplo:
        >>> g_captcha = soup.find(class_='g-recaptcha')\n
        >>> site_key = g_captcha.attrs['data-sitekey']\n
        >>> elemento_recaptcha_token = browser.find_element(By.ID,"g-recaptcha-response")\n
        >>> token_bestcaptchasolver = best_captcha_solver_api[0].retrieve[2]['gresponse']\n
        >>> browser.execute_script(f"$(arguments[0]).val(arguments[1])",elemento_recaptcha_token,token_bestcaptchasolver)
        """
        bcs = BestCaptchaSolverAPI(self.BCS_TOKEN)
        balance = bcs.account_balance()
        logger.info(f'BEST CAPTCHA SOLVER API BALANCE: {balance}')
        recaptcha_id = bcs.submit_recaptcha(
            {
                "page_url": page_url,
                "site_key": site_key,
                "type":1
            }
        )
        sleep(60)
        response = None
        while response == None:
            response = bcs.retrieve(recaptcha_id)['gresponse']
            if response != None:
                logger.info(f"{response}")
                break
            else:
                sleep(1)
        return response
    
    def best_captcha_solver_api_image(self,image_name: str) -> str:
        
        bcs = BestCaptchaSolverAPI(self.BCS_TOKEN)
        balance = bcs.account_balance()
        logger.info(f'BEST CAPTCHA SOLVER API BALANCE: {balance}')
        
        data = {}
        caminho_imagem = os.path.join(self.temp_folder,image_name)
        data['image'] = caminho_imagem
        data['is_case'] = True

        id = bcs.submit_image_captcha(data)
        image_text = None

        while image_text == None:
            image_text = bcs.retrieve(id)['text']
            sleep(1)
        
        self.remove_file(image_name)
        return image_text


if __name__ == '__main__':
    solver = CaptchaSolver()
    # bcs = BestCaptchaSolverAPI(CaptchaSolver.BCS_TOKEN)
    # balance = bcs.account_balance()
    # print(solver.best_captcha_solver_api_image(r'captcha_image_27052_ywej5xmue5.png'))

    url = 'https://loginweb.bb.com.br/sso/XUI/?realm=paj#login'
    site_key: str = '6Le8KaUUAAAAALNgyiDf6Pz1If-AR5sdhU9aCTdX'
    
    print(solver.best_captcha_solver_api(url,site_key))