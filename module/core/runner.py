from subprocess import Popen
from time import sleep
from threading import Thread
import psutil

from .customlogger import logger


class Runner:
    '''classe com métodos para rodar scripts'''

    def __init__(self,python_path: str='python'):
        """_summary_

        Args:
            python_path (str, optional): _description_. Defaults to 'python'.
        """
        self.python_path = python_path
        self.instancias = {}
        # self.stop_signal = False
        
    def __del__(self):
        try: self.parar_instancias(wait_stop=False)
        except: self.parar_instancias(wait_stop=False)
    
    def executar_em_instancias(self,qtd_inst: int,script: str='main.py',args: str='',wait_for_instancias=True):
        """Executa o script em instancias

        Args:
            qtd_inst (int): _description_
            script (str, optional): _description_. Defaults to 'main.py'.
            args (str, optional): _description_. Defaults to ''.
        """
        print(f'{self.python_path} ESTA INICIANDO {qtd_inst} INSTANCIAS DE {script} {args}\n')
        for _ in range(qtd_inst):
            robo = Popen([self.python_path,script,args], shell=False)
            pid_instancia = str(robo.pid)
            print(f'Booting worker with pid: {pid_instancia}')
            self.instancias[pid_instancia] = robo
            sleep(1)
        
        if wait_for_instancias:
            while bool(self.instancias):
                self.parar_instancias()
        else: return self.instancias
    
    def stop_child(self, pid_pai):
        try:
            processo_pai = psutil.Process(int(pid_pai))
            subprocessos = processo_pai.children(recursive=True)
        except:
            pass
        else:
            # Encerrar subprocessos
            for subprocesso in subprocessos:
                try:
                    subprocesso.terminate()
                except:
                    pass
            # Esperar até que todos os subprocessos sejam encerrados
            psutil.wait_procs(subprocessos, timeout=5)
        
    def parar_instancias(self,wait_stop=True):
        
        lista = list(self.instancias.keys())
        
        for e,instancia in enumerate(lista):
            if wait_stop:
                if self.instancias[instancia].poll() != None:
                    print(f'Stopping worker with pid: {instancia}')
                    self.stop_child(instancia)
                    
                    self.instancias[instancia].kill() # Encerrando instância
                    self.instancias.pop(instancia) # Apagando objeto da instância
            else:
                print(f'Stopping worker with pid: {instancia}')
                self.stop_child(instancia)

                self.instancias[instancia].kill() # Encerrando instância
                self.instancias.pop(instancia) # Apagando objeto da instância
            
        if not self.instancias:
            print(f'All workers stopped successfully!') 

    def executar_lista(self, lista: list,wait_for_instancias=True):

        for arg in lista:
            qtd_inst = arg['qtd_inst']

            script = arg['script']
            
            for _ in range(qtd_inst):
                print(f'{self.python_path} ESTA INICIANDO {qtd_inst} INSTANCIAS DE {script}\n')

                robo = Popen([self.python_path, script], shell=False)
                id_instancia = str(robo.pid)
                print(f'Booting worker with pid: {id_instancia}')
                self.instancias[id_instancia] = robo
                sleep(1)
                
        if wait_for_instancias:
            while bool(self.instancias):
                self.parar_instancias()
        else: return self.instancias

    # def iniciar_instancia_thread(self, script, args=''):
    #     robo = Popen([self.python_path, script, args], shell=False)
    #     pid_instancia = str(robo.pid)
    #     self.instancias[pid_instancia] = robo
    #     logger.warning(f'Booting worker with pid: {pid_instancia}')

    #     # Espera até que a instância seja concluída
    #     robo.wait()
    #     self.instancias.pop(pid_instancia)
    #     logger.warning(f'Worker with pid {pid_instancia} finished successfully!')

    # def executar_em_instancias_thread(self, qtd_inst, script='main.py', args=''):
    #     for _ in range(qtd_inst):
    #         t = Thread(target=self.iniciar_instancia_thread, args=(script, args))
    #         t.start()
    #         sleep(1)

    #     return self.instancias
    
    # def parar_instancias_thread(self):
    #     lista = list(self.instancias.keys())
    #     for e, instancia in enumerate(lista):
    #         if not self.stop_signal:  # Verifies if it should stop
    #             if self.instancias[instancia].poll() is None:
    #                 logger.warning(f'Stopping worker with pid: {instancia}')
    #                 self.instancias[instancia].kill()  # Ending instance
    #                 self.instancias.pop(instancia)  # Deleting instance object

    #     if not self.instancias:
    #         logger.warning(f'All workers stopped successfully!')
    
    # def stop_instances_async(self):
    #     self.stop_signal = True
    #     t = Thread(target=self.parar_instancias_thread)
    #     t.start()
    #     t.join()  # Wait for the thread to complete
    #     self.stop_signal = False  # Reset the stop_signal after the thread completes
    
