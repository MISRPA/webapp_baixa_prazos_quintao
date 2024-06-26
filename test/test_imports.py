

def test_import_module():
    from module import (
        directory,
        manager,
        models,
        querys,
        settings,
        __codname__,
        __version__,
    )

def test_import_core():
    from module.core import (
        aws_services,
        captcha,
        customexceptions,
        customlogger,
        db_pyodbc,
        db_sqlalchemy,
        enviar_email,
        excel,
        rabbit_mq,
        readpdf,
        runner,
        utils,
        webdrivers,
    )
    
