from module import settings


def test_conexao_padrao():
    assert type(settings.CONEXAO_PADRAO) == dict
    
def test_conexao_rabbit():
    assert type(settings.CONEXAO_RABBIT) == dict
    
def test_conexao_email():
    assert type(settings.CONEXAO_EMAIL) == dict
