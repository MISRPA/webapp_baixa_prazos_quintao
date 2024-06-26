import streamlit_authenticator as stauth
from datetime import datetime
import pandas as pd
import streamlit as st
import bcrypt 

from module.manager import engine_espelho
from module import __codname__, __version__
from module.models import text


def check_pw(password, user_password) -> bool:
    """
    Checks the validity of the entered password.

    Returns
    -------
    bool
        The validity of the entered password by comparing it to the hashed password on disk.
    """
    return bcrypt.checkpw(password.encode(), user_password.encode())


def select_usuarios():
    with engine_espelho.begin() as con:
        df = pd.read_sql(text(f'''
            select * from mis.rpa.TbUsuarioStreamlit 
            where robo = '{__codname__}'
            or role = 'admin'
            '''), con)
    return df

def insert_usuario(
    nome,username,password,email, role
):  
    df_usuarios = select_usuarios()
    if df_usuarios[df_usuarios['USERNAME'] == username].empty:
        hashed_pass = stauth.Hasher([password]).generate()
        with engine_espelho.begin() as con:
            con.execute(text(f'''
                INSERT INTO mis.rpa.TbUsuarioStreamlit
                (ROBO, NOME, EMAIL, USERNAME, PASSWORD, DATA_ALTERACAO, ROLE, ATIVO)
                VALUES (
                    
                    :ROBO
                    ,:NOME
                    ,:EMAIL
                    ,:USERNAME
                    ,:PASSWORD
                    ,:DATA_ALTERACAO
                    ,:ROLE
                    ,:ATIVO
                )
                
                '''),[{
                    'ROBO':__codname__,
                    'NOME':nome.strip(),
                    'EMAIL':email.strip(),
                    'USERNAME':username.strip(),
                    'PASSWORD':hashed_pass[0],
                    'DATA_ALTERACAO':datetime.now(),
                    'ATIVO':1,
                    'ROLE':role
                }])
    else:
        raise Exception('Já existe um usuário com esse username.')

def update_dados(username,new_username,new_email,new_role,new_name):  
    df_usuarios = select_usuarios()
    df_usuario = df_usuarios[df_usuarios['USERNAME'] == username].copy()
    df_new_usuario = df_usuarios[df_usuarios['USERNAME'] == new_username.strip()].copy()
    if not df_usuario.empty:
        if not df_new_usuario.empty:
            nome = df_usuario['NOME'].values[0]
            email = df_usuario['EMAIL'].values[0]
            password = df_usuario['PASSWORD'].values[0]
            role = df_usuario['ROLE'].values[0]
            
            if not new_username:
                new_username = username
            if not new_name:
                new_name = nome
            if not new_email:
                new_email = email
            if not new_role:
                new_role = role
            
            with engine_espelho.begin() as con:
                con.execute(text(f'''
                    UPDATE mis.rpa.TbUsuarioStreamlit
                    SET
                        USERNAME = :USERNAME
                        ,EMAIL = :EMAIL
                        ,ROLE = :ROLE
                        ,NOME = :NOME
                        ,DATA_ALTERACAO = :DATA_ALTERACAO
                        
                    WHERE USERNAME = :USERNAME
                    
                    '''),[{
                        'USERNAME':new_username.strip(),
                        'EMAIL':new_email.strip(),
                        'ROLE':new_role.strip(),
                        'NOME':new_name.strip(),
                        
                        'DATA_ALTERACAO':datetime.now(),
                    }])
        else:
            raise Exception('Já existe um usuário com esse username.')
    else:
        raise Exception('Não existe usuário com esse username.')
    
def update_senha(username,
        new_password,
                ):  
    df_usuarios = select_usuarios()
    df_usuario = df_usuarios[df_usuarios['USERNAME'] == username].copy()
    if not df_usuario.empty:
        nome = df_usuario['NOME'].values[0]
        password = df_usuario['PASSWORD'].values[0]
        role = df_usuario['ROLE'].values[0]
        
        hashed_pass = stauth.Hasher([new_password]).generate()
        
        with engine_espelho.begin() as con:
            con.execute(text(f'''
                UPDATE mis.rpa.TbUsuarioStreamlit
                SET
                    PASSWORD = :PASSWORD
                    ,DATA_ALTERACAO = :DATA_ALTERACAO
                    
                WHERE USERNAME = :USERNAME
                
                '''),[{
                    'PASSWORD':hashed_pass[0],
                    'DATA_ALTERACAO':datetime.now(),
                    'USERNAME':username,
                }])
    else:
        raise Exception('Não existe usuário com esse username.')
    
def delete_usuario(username):
    with engine_espelho.begin() as con:
        con.execute(text(f'''
            DELETE mis.rpa.TbUsuarioStreamlit
            WHERE 
                USERNAME = :USERNAME
                AND ROBO = :ROBO
            '''),[{
                'ROBO':__codname__,
                'USERNAME':username,
            }])

def desativar_usuario(username):
    with engine_espelho.begin() as con:
        con.execute(text(f'''
            UPDATE mis.rpa.TbUsuarioStreamlit
            SET ATIVO = 0
            WHERE 
                USERNAME = :USERNAME
                AND ROBO = :ROBO
            '''),[{
                'ROBO':__codname__,
                'USERNAME':username,
            }])
        
def ativar_usuario(username):
    with engine_espelho.begin() as con:
        con.execute(text(f'''
            UPDATE mis.rpa.TbUsuarioStreamlit
            SET ATIVO = 1
            WHERE 
                USERNAME = :USERNAME
                AND ROBO = :ROBO
            '''),[{
                'ROBO':__codname__,
                'USERNAME':username,
            }])