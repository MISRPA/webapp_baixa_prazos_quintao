from selenium import webdriver
import portpicker
import requests
from platform import system
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.ie.service import Service as IEService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import WebDriverException
from unidecode import unidecode
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
import zipfile
import random
from time import sleep
import zipfile
import random
import sys
import base64

from .customlogger import logger

from module.directory import Directory
from module import settings

class Proxies:
    '''Classe contendo Proxies'''

    PROXIES = [
            {
            "PROXY_HOST":...,
            "PROXY_PORT":...,
            "USER":...,
            "PASSWORD":...
        },
        ]

    def __init__(self,file_name: str,folder: str) -> None:
        """_summary_

        Args:
            file_name (str): _description_
            folder (str): _description_
        """
        self.file_name = os.path.join(folder, file_name)
        self.folder = folder
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

    def get_random_proxie(self) -> str:
        """Pega um proxie randomicamente do dicionario de proxies

        Returns:
            str: _description_
        """
        PROXIES = self.PROXIES

        rand = random.randint(0,len(PROXIES)-1)

        PROXY_HOST = PROXIES[rand]["PROXY_HOST"]
        PROXY_PORT = PROXIES[rand]["PROXY_PORT"]
        PROXY_USER = PROXIES[rand]["USER"]
        PROXY_PASS = PROXIES[rand]["PASSWORD"]

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

        logger.warning(f'Proxies: {(PROXY_HOST, PROXY_PORT)}')

        pluginfile = self.file_name
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        return self.file_name

class DriverArgs:
    '''Classe com DriverArgs'''
    disable_blink = '--disable-blink-features=AutomationControlled'
    headless = '--headless' # Enfrentando problemas com o headless ativado
    disable_dev_shm_usage = '--disable-dev-shm-usage' # error dev shm usage NAO ATIVAR
    disable_logging = '--disable-logging'
    no_sandbox = '--no-sandbox'
    disable_notifications =  '--disable-notifications'
    window_size_500 = '--window-size=500,500'
    window_size_1920 = '--window-size=1920,1080'
    start_maximized = '--start-maximized'
    disable_gpu = '--disable-gpu'
    disable_infobars = '--disable-infobars'
    user_agent = f'user-agent={settings.USER_AGENT}'
    allow_insecure_cont = '--allow-running-insecure-content'
    
    disable_render_bg= "--disable-renderer-backgrounding"
    disable_timer_ttbg = "--disable-background-timer-throttling"
    disable_bgoc_window = "--disable-backgrounding-occluded-windows"
    disable_client_side_det = "--disable-client-side-phishing-detection"
    disable_crash_rep = "--disable-crash-reporter"

    disable_oppr = "--disable-oopr-debug-crash-dump"
    no_crash_up = "--no-crash-upload"
    disable_ext =  "--disable-extensions"
    
    disable_low_res =  "--disable-low-res-tiling"
    log_level_3 =  "--log-level=3"
    silent =  "--silent"
    
class ExperimentalArgs:
    '''Classe com ExperimentalArgs'''
    excludeSwitches = 'excludeSwitches'
    enable_automation = ['enable-automation']
    useAutomationExtension = 'useAutomationExtension'

class Driver(Proxies,DriverArgs,ExperimentalArgs):
    '''Classe contendo os Webdrivers'''


    def __init__(self,file_name='proxy_auth_plugin.zip',folder=Directory.EXTENSIONS.value) -> None:
        """_summary_

        Args:
            file_name (str, optional): _description_. Defaults to 'proxy_auth_plugin.zip'.
            folder (_type_, optional): _description_. Defaults to path.join(path.dirname(path.realpath(__file__)),'chrome_extensions').
        """
        Proxies.__init__(self,file_name,folder)


    def chrome(self,
               *args,random_user_agent: bool=False,
               use_proxy: bool=False,
               install:bool=False,
               extensions:list[str]=[],
               download_dir=Directory.DOWNLOAD.value,
               low_cpu_usage=False
               ) -> webdriver.Chrome:
        """Chrome Webdriver

        Args:
            random_user_agent (bool, optional): _description_. Defaults to False.
            use_proxy (bool, optional): _description_. Defaults to False.
            install (bool, optional): _description_. Defaults to False.
            extensions (list[str], optional): _description_. Defaults to [].

        Raises:
            GlobalError: _description_

        Returns:
            webdriver.Chrome: _description_
        """
        service = None
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True})
        options.add_argument(self.no_sandbox)
        options.add_argument(self.disable_infobars)
        options.add_argument(self.disable_blink)
        options.add_argument(self.start_maximized)
        options.add_argument(self.window_size_1920)
        options.add_experimental_option(self.excludeSwitches,self.enable_automation)
        options.add_experimental_option(self.useAutomationExtension,False)
        options.add_argument(self.log_level_3)
        
        # options.add_argument('--disk-cache-size=1')
        # options.add_argument('--media-cache-size=1')
        # options.add_argument('--disable-images')
        # options.add_argument('--disable-web-sockets')
        
        if low_cpu_usage:
            options.add_argument(self.disable_dev_shm_usage)
            options.add_argument(self.disable_render_bg)
            options.add_argument(self.disable_timer_ttbg)
            options.add_argument(self.disable_bgoc_window)
            options.add_argument(self.disable_client_side_det)
            options.add_argument(self.disable_crash_rep)
            options.add_argument(self.disable_oppr)
            options.add_argument(self.no_crash_up)
            options.add_argument(self.disable_ext)
            options.add_argument(self.disable_low_res)
            options.add_argument(self.silent)

        if use_proxy == True:
            pluginfile = self.get_random_proxie()
            options.add_extension(pluginfile)

        if random_user_agent:
            ua = UserAgent()
            random_user_agent = ua.random
            options.add_argument(f'user-agent={random_user_agent}')

        if len(args) >= 1:
            for i in args:
                options.add_argument(i)

        if install:
            service = ChromeService(executable_path=ChromeDriverManager().install())

        if 'nopecha' in extensions:
            file_name = 'nopecha.crx'

            if not file_name in os.listdir(self.folder):
                with open(os.path.join(self.folder,file_name), 'wb') as f:
                    f.write(requests.get('https://nopecha.com/f/ext.crx').content)

            options.add_extension(os.path.join(self.folder,file_name))

            browser = webdriver.Chrome(options=options,port=portpicker.pick_unused_port(),service=service)
            browser.get(f'https://nopecha.com/setup#{settings.TOKEN_NOPECHA}')

            cont = 0
            while True:
                if cont >= 5:
                    raise Exception('Erro ao carregar Token NOPECHA.')
                soup = BeautifulSoup(browser.page_source,'html.parser')
                if 'Successfully imported settings.' in soup.prettify() or 'Key set!' in soup.prettify():
                    logger.debug('Nopecha ::: Successfully imported settings')
                    break
                else:
                    cont+=1
                    logger.warning('Nopecha ::: Error importing settings')
                    browser.refresh()
                    sleep(1)
        else:
            browser = webdriver.Chrome(service=service,options=options)

        return browser

    def edge(self,*args,random_user_agent: bool=False,install: bool=False) -> webdriver.Edge:
        """Edge Webdriver

        Args:
            random_user_agent (bool, optional): _description_. Defaults to False.
            install (bool, optional): _description_. Defaults to False.

        Returns:
            webdriver.Edge: _description_
        """
        service = None
        options = webdriver.EdgeOptions()
        options.use_chromium = True
        options.set_capability("platform", system())
        if random_user_agent:
            ua = UserAgent()
            random_user_agent = ua.random
            options.add_argument(f'user-agent={random_user_agent}')
        if len(args) >= 1:
            for i in args:
                options.add_argument(i)
        if install:
            service = EdgeService(executable_path=EdgeChromiumDriverManager().install())

        browser = webdriver.Edge(service=service,options=options)
        return browser

    def firefox(self,*args,random_user_agent: bool=False,install: bool=False) -> webdriver.Firefox:
        """Firefox Webdriver

        Args:
            random_user_agent (bool, optional): _description_. Defaults to False.

        Returns:
            webdriver.Firefox: _description_
        """
        service = None
        options = webdriver.FirefoxOptions()
        options.set_capability("platform", system())
        if random_user_agent:
            ua = UserAgent()
            random_user_agent = ua.random
            options.add_argument(f'user-agent={random_user_agent}')
        if len(args) >= 1:
            for i in args:
                options.add_argument(i)
        if install:
            service = FirefoxService(executable_path=GeckoDriverManager().install())

        browser = webdriver.Firefox(service=service,options=options)
        return browser


class ChromeDriver:
    def __init__(self):
        self.driver = Driver()
        self._browser = None
        self._action = None
    
    def __del__(self):
        self.fechar_navegador()
    
    @property
    def action(self):
        return self._browser
    
    @property
    def browser(self):
        return self._browser
    
    def iniciar_navegador(self, headless=False, install=False) -> None:
        '''Inicia o browser com a extensao nopecha'''
        if not self._browser:
            print('Iniciando navegador')
            if headless:
                self._browser = self.driver.chrome(Driver.headless,Driver.user_agent,Driver.disable_gpu,install=install)
            else: 
                self._browser = self.driver.chrome(install=install)
            self._action = ActionChains(self._browser)
            print(f' ::: NAVEGADOR INICIADO ::: ')
        else: 
            print('Navegador já foi inciado, reiniciando navegador.')
            self.fechar_navegador()
            self.iniciar_navegador(headless, install)
    
    def fechar_abas_restantes(self):
        if len(self._browser.window_handles) > 1:
            for w in self._browser.window_handles[1:]:
                self._browser.switch_to.window(w)
                self._browser.close()
        self._browser.switch_to.window(self._browser.window_handles[0])
    
    def fechar_navegador(self):
        '''Fecha o navegador'''
        if self._browser:
            print(f'Fechando navegador')
            self._browser.quit()
            print(f' ::: NAVEGADOR ENCERRADO ::: ')
            self._browser = None
            
    def page_to_pdf(self,folder,filename):
        arquivo = {}
        pdf = self._browser.execute_cdp_cmd("Page.printToPDF", {
                "printBackground": False
                })

        arquivo['FOLDER'] = folder
        arquivo['NOME_ARQUIVO'] = filename
        arquivo['CAMINHO_ARQUIVO'] = os.path.join(arquivo['FOLDER'],arquivo['NOME_ARQUIVO'])
        
        if not os.path.exists(arquivo['FOLDER']):
            os.mkdir(arquivo['FOLDER'])
        
        with open(arquivo['CAMINHO_ARQUIVO'], "wb") as f:
            f.write(base64.b64decode(pdf['data']))
        
        return arquivo
    
    def esperar_abrir_aba(self,max_wait=1000):
        for _ in range(max_wait):
            janelas = self._browser.window_handles
            if len(janelas) > 1: break
            else: sleep(0.1)
        else: raise Exception('Seguna aba não abriu')

    def selecionar_option_select(self,webelement,pesquisa):
        """Checa o resultado do preenchimento
        """    
        select = Select(webelement)
        for result in select.options:
            if unidecode(pesquisa).strip().lower() == unidecode(result.text).strip().lower():
                select.select_by_visible_text(result.text)
                break
        else: raise Exception(f'[{pesquisa}] não encontrado nas opções: {list(op.text for op in select.options)}')

    def verificar_alerta(self,time_wait=15, accept=True):
        WebDriverWait(self._browser,time_wait).until(EC.alert_is_present())
        alert = Alert(self._browser)
        print(alert.text)
        if accept:
            self._browser.switch_to.alert.accept()
        return alert.text

#TODO: reformular a classe abaixo, nao funciona
class WebElementCommand:
    
    def __init__(self, webelement, driver):
        self.driver = driver
        self.webelement : webdriver.Chrome = webelement
    
    def remove_class(self):
        for i in self.webelement.find_elements(By.XPATH, '*'):
            self.driver.browser.execute_script("arguments[0].setAttribute('class','')",i)
    
    def set_attribute(self,atribute,value):
        self.driver.browser.execute_script(f"arguments[0].setAttribute('{atribute}','{value}')",self.webelement)

    def get_childs(self):
        return self.webelement.find_elements(By.XPATH, '*')

    @property
    def parent(self):
        return self.webelement.find_element(By.XPATH, '..')

