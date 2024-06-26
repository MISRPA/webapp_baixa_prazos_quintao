<p align="center">
  <a href="" rel="noopener">
 <img width=150px height=50 src="https://totalweb.fcjur.com.br/Content/img/logoTotalWeb3.png" alt="Project logo"></a>
</p>

<h3 align="center">WebApp Baixa de Prazos (Leticia Quintao)</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> Aplicação para automatizar a baixa de prazos "prazo verificado pela operação" (cod. 1775) . Rotina automatizada para Leticia Quintão.
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Deployment](#deployment)

## About <a name = "about"></a>

Write about 1-2 paragraphs describing the purpose of your project.

## Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

Certifique-se de ter os seguintes requisitos instalados e configurados em seu ambiente de desenvolvimento antes de prosseguir:

- [Python](https://www.python.org/) (versão 3.x)
- [SQL Server](https://www.microsoft.com/en-us/sql-server)

- **Configure as credenciais dos bancos de dados no arquivo '.env' na pasta raiz.**

### Installing

Para a criação de um ambiente virtual:
``` bash
python3 -m venv venv
```

Para ativação do ambiente virtual:

Linux:
``` bash
source venv/bin/activate
```

Windows:
``` bash
./venv/Scripts/activate
```

Para instalação das dependência do robô:
``` bash
pip install -r ./requirements.txt
```

## Usage <a name = "usage"></a>

1. Alterar em /module/app/pages/prazos/baixa.py a variável:

    Para execução na tabela de produção (TOTAL_FC.DBO.TbPrazos)
    ``` bash
    PRODUCAO = True
    ```

    Para execução na tabela de desenvolvimento (mis.rpa.teste_webapp_baixa_prazos_quintao)
    ``` bash
    PRODUCAO = False
    ```

2. Execução da aplicação:
    ``` bash
    streamlit run .\run_app.py
    ```

## 🚀 Deployment <a name = "deployment"></a>

#TODO: fazer guia do deploy