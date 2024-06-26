from platform import system
from time import sleep

from module.core.utils import clear_folder
from module.directory import Directory
from module.core.customlogger import task_log_cleanup

from module import __codname__, __version__

#TODO: alterar a porta de acesso nos arquivos executaveis.

def main():
    pass

def task_arqs_cleanup():
    '''Faz a limpeza dos arquivos'''
    clear_folder(Directory.TEMP.value)


if __name__ == '__main__':
    from module.core.cli import CLI
    
    # Adicione aqui o mapeamento das funcoes da CLI
    all_arguments = {
        'main': main,
        
        'task_log_cleanup': task_log_cleanup,
        'task_arqs_cleanup': task_arqs_cleanup,
    }
    
    cli = CLI(
        description=f'{__codname__} CLI',
        all_arguments=all_arguments
    )
    
    cli.parse_args()