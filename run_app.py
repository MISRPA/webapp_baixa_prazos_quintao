from module.app.app import main, st, logger

# Executa a aplicação
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical(e, exc_info=True)
        st.error("Ooops! Algo deu errado. Por favor, entre em contato com a equipe MIS.")