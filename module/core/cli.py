import argparse

from module import __codname__,__version__
from module import settings


class CLI:
    
    def __init__(self, description, all_arguments={}, **kwargs):
        self.parser = argparse.ArgumentParser(description=description)
        if not all_arguments:
            all_arguments = kwargs
        self.all_arguments = all_arguments
        
        self.parser.add_argument('-v', '--version', action='store_true', help='Mostra a versão')
        self.parser.add_argument('-s', '--settings', nargs='?', const='all', help='Mostra a configuração atual (opcional: filtro de configuração)')
        self.parser.add_argument('--setenv', nargs=2, metavar=('VARIAVEL', 'VALOR'), help='Define uma variável de ambiente no arquivo .env')
        
    def parse_args(self):
        for key, value in self.all_arguments.items():
            self.parser.add_argument(f'--{key}', action='store_true',help=value.__doc__)
            
        args = self.parser.parse_args()

        # Defina aqui as chamadas para os comandos enviados pelo usuario
        for k, v in args.__dict__.items():
            if v: break
        else: print('Nenhum argumento foi enviado. Envie [--help] ou [-h] para ver os comandos.')
        
        if args.version: print(__codname__, ':', __version__)
        
        if args.settings:
            variaveis = [var for var in dir(settings) if not var.startswith("__")]
            if args.settings == 'all':
                for var in variaveis:
                    print(f"{var} = {getattr(settings, var)}")
            else:
                filter_string = args.settings
                variaveis = [var for var in variaveis if filter_string.lower() in var.lower()]
                for var in variaveis:
                    print(f"{var} = {getattr(settings, var)}")
        
        if args.setenv:
            encontrada = False
            env_variable, env_value = args.setenv
            with open(settings.ENV_LOC, 'r') as env_file:
                env_lines = env_file.readlines()
            with open(settings.ENV_LOC, 'w') as env_file:
                for line in env_lines:
                    if line.split('=')[0].strip() == env_variable:
                        env_file.write(f'{env_variable}={env_value}\n')
                        encontrada = True
                    else:
                        env_file.write(line)
            if encontrada:
                print(f'Variável de ambiente {env_variable} definida como {env_value} no arquivo .env')
            else:
                print(f"A variável de ambiente {env_variable} não foi encontrada no arquivo .env")

        
        for key, value in self.all_arguments.items():
            if hasattr(args, key):
                if bool(getattr(args, key)):
                    self.all_arguments[key]()
