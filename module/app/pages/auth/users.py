import streamlit as st
import streamlit_authenticator as stauth
from datetime import datetime
from module.app.pages.auth.auth import (
    select_usuarios,
    insert_usuario,
    delete_usuario,
    desativar_usuario,
    ativar_usuario,
    update_dados,
    update_senha
)


def pagina_gerenciar_usuarios():
    st.title("Gerenciar Usuários")

    df_usuarios = select_usuarios().drop(columns=['PASSWORD'])

    # Display the list of existing users
    st.subheader("Lista de Usuários:")
    st.dataframe(df_usuarios)

    # Manage User Form
    st.subheader("Gerenciar Usuário")

    # Choose the user to manage
    selected_user = st.selectbox("Selecione um usuário:", df_usuarios['USERNAME'])

    # Choose the action to perform
    actions = ["Adicionar Usuário","Trocar Senha", "Atualizar Dados", "Desativar Usuário", "Ativar Usuário", "Deletar Usuário"]
    selected_action = st.selectbox("Escolha uma ação:", actions)

    # Form for all actions
    with st.form(key='user_management_form'):
        if selected_action == "Trocar Senha":
            new_password = st.text_input("Nova Senha:", type="password")
            confirmar_senha = st.text_input("Confirmar Senha:", type="password")
            if st.form_submit_button("Trocar Senha"):
                if new_password == confirmar_senha:
                    try:
                        # Call the function to change the password
                        update_senha(selected_user, new_password)
                        st.success("Senha trocada com sucesso!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erro ao trocar senha do usuário: {str(e)}")
                else:
                    st.error("As senhas não coincidem.")
                    
        elif selected_action == "Atualizar Dados":
            # Form to update user data
            new_username = st.text_input("Novo Nome de Usuário:", value=selected_user)
            new_email = st.text_input("Novo Email:")
            new_role = st.selectbox("Nova Função:", ["user", "admin", "financeiro", "gestao", "ti"], index=0)
            new_name = st.text_input("Novo Nome:")
            if st.form_submit_button("Atualizar Dados"):
                # Call the function to update user data
                try:
                    update_dados(selected_user, new_username, new_email, new_role, new_name)
                    st.success("Dados atualizados com sucesso!")
                    st.experimental_rerun()
                except Exception as e:
                        st.error(f"Erro ao atualizar dados do usuário: {str(e)}")
                        
        elif selected_action == "Desativar Usuário":
            if st.form_submit_button("Desativar Usuário"):
                try:
                    desativar_usuario(selected_user)
                    st.success("Usuário desativado com sucesso!")
                    st.experimental_rerun()
                except Exception as e:
                        st.error(f"Erro ao desativar usuário: {str(e)}")
                
        elif selected_action == "Ativar Usuário":
            if st.form_submit_button("Ativar Usuário"):
                try:
                    ativar_usuario(selected_user)
                    st.success("Usuário ativado com sucesso!")
                    st.experimental_rerun()
                except Exception as e:
                        st.error(f"Erro ao ativar usuário: {str(e)}")
                
        elif selected_action == "Deletar Usuário":
            if st.form_submit_button("Deletar Usuário"):
                try:
                    delete_usuario(selected_user)
                    st.success("Usuário deletado com sucesso!")
                    st.experimental_rerun()
                except Exception as e:
                        st.error(f"Erro ao deletar usuário: {str(e)}")
                
        elif selected_action == "Adicionar Usuário":
            roles = ["user", "admin", "financeiro", "gestao"]
            
            nome = st.text_input("Nome:")
            username = st.text_input("Nome de Usuário:")
            password = st.text_input("Senha:", type="password")
            confirmar_senha = st.text_input("Confirmar Senha:", type="password")
            email = st.text_input("Email:")
            role = st.selectbox("Role:", ["user", "admin", "financeiro", "gestao", "ti"], index=0)

            if st.form_submit_button("Adicionar Usuário"):
                # Check if passwords match
                if password == confirmar_senha:
                    try:
                        # Call the function to insert a new user
                        insert_usuario(nome, username, password, email, role)
                        st.success("Usuário adicionado com sucesso!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erro ao adicionar usuário: {str(e)}")
                else:
                    st.error("As senhas não coincidem.")
