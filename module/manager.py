from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .settings import DATABASE_URI, PID, DATABASE_URI_PROTHEUS, DATABASE_URI_PRODUCAO_ESCRITA
from .core.db_sqlalchemy import Database
from .models import Base, text


from module import __codname__, __version__

# Inicialização e criação das tabelas do banco de dados
engine_espelho = create_engine(DATABASE_URI, isolation_level='SERIALIZABLE', echo=False)
engine_protheus = create_engine(DATABASE_URI_PROTHEUS, isolation_level='SERIALIZABLE', echo=False)

#Nao utilizar a engine de escrita na producao
engine_producao_escrita = create_engine(DATABASE_URI_PRODUCAO_ESCRITA, isolation_level='SERIALIZABLE', echo=False)

Base.metadata.create_all(engine_espelho)
Session = sessionmaker(bind=engine_espelho)

# Inicialização classe personalizada Database
db = Database(Session)