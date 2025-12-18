# Stock21

**Stock21** é uma aplicação web de sistema de gerenciamento de estoque simples e leve voltado para pizzarias de pequeno e médio porte.

## Características

- Gerenciamento de usuários, cadastro, login, cargos como funcionário e administrador.
- Gerenciamento de Ingredientes e Produtos, podendo cadastrar, alterar, visualizar e deletar.
- Registro de movementações e geração de relatórios de faturamento por data

## Tecnologias

### Backend

- **Linguagem:** [Python](https://www.python.org/) - Linguagem de programação de alto nível, simples e poderosa, muito usada para automação e ciência de dados.
- **Framework:** [Django](https://www.djangoproject.com/) - Framework web em Python que permite criar aplicações completas de forma rápida, segura e escalável.
- **Banco de Dados:** [Sqlite3](https://sqlite.org/index.html) - Banco de dados relacional leve e embutido, ideal para testes e pequenos projetos.
- **visualização de Banco de Dados:** [Django Schema Viewer](https://pypi.org/project/django-schema-viewer/) - Visualize os relacionamentos entre as Models do Django e a estrutura do banco de dados de forma iterativa.

### Frontend

- **Templates:** [Django Templates](https://docs.djangoproject.com/en/5.2/topics/templates/) - Sistema de templates nativo do Django que permite gerar páginas HTML dinâmicas a partir de variáveis do backend.
- **Estilo:** [Tailwind CSS]() - Framework CSS utilitário que facilita a criação de interfaces responsivas e modernas com classes pré-definidas.

### DevOps

- **Docker:** [Docker](https://docs.docker.com/get-started/) – Ferramenta que cria ambientes isolados (containers) para rodar aplicações de forma padronizada em qualquer máquina.
- **Docker Compose:** [Docker Compose](https://docs.docker.com/compose/) – Ferramenta que orquestra múltiplos containers ao mesmo tempo, usando um arquivo YAML para configurar tudo com um só comando.

## Estrutura do projeto

```
devspizza
├── core                # Configurações principais do projeto
│   ├── asgi.py
│   ├── decorators.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── accounts            # Módulo responsável por gerenciar os usuários
│   ├── models.py
│   ├── templates
│   │   ├── ...
│   ├── urls.py
│   └── views.py
├── movements           # Módulo responsável por gerenciar as movimentações
│   ├── models.py
│   ├── templates
│   │   ├── ...
│   ├── urls.py
│   └── views.py
├── stock               # Módulo responsável por gerenciar o estoque
│   ├── models.py
│   ├── templates
│   │   ├── ...
│   ├── urls.py
│   └── views.py
├── static              # Arquivos estáticos usados pelo Django (JavaScript)
└── templates           # Templates HTML não associados a nenhum módulo
├── .gitignore          # Arquivo para especificar explicitamente os arquivos as serem ignorados pelo Git
├── .venv               # Ambiente Virtual do Python (Ignorado pelo Git)
├── .env                # Variáveis de ambiente para a configuração do Docker e Django
├── db.sqlite3          # Banco de Dados
├── docker-compose.yml  # Diz o passo a passo de como montar o ambiente para o projeto
├── Dockerfile          # Junta tudo em um só lugar e roda vários serviços com um único comando
├── manage.py           # Utilitário de linha de comando do Django para tarefas administrativas
├── readme.md           # Documentação do projeto
├── requirements.txt    # Lista de dependências do python para esse projeto
```

## Pre-Requisitos

- **Docker** e **Docker Compose**
- **Git**

## Instalação

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/GGB0T11/Stock21.git
   cd Stock21
   ```

2. **Defina as variáveis de ambiente:**

   Crie o arquivo `.env` na raiz do projeto com as seguintes variáveis:

   ```env
   SECRET_KEY=sua_chave_secreta_do_django # Gere um cheve única e complexa para produção
   DEBUG=True                             # Defina como False para produção
   DB_ENGINE=django.db.backends.sqlite3   # Sqlite3 para projetos simples
   DB_NAME=db.sqlite3                     # Nome do banco de dados
   ALLOWED_HOSTS=*                        # Hosts permitidos, por padrão, todos
   ```

3. **Build o Docker Compose:**
   ```bash
   docker-compose up --build
   ```

## Rodando a Aplicação

### Usando Docker Compose (Recomendado)

```bash
# Builda e inicia todos os serviços
docker-compose up --build

# Roda em segundo plano
docker-compose up -d

# Para o serviço
docker-compose down
```

Apos iniciar o serviço voce pode acessar:

- **Aplicação**: http://localhost:8000
- **Visualização do Banco de Dados**: http://127.0.0.1:8000/schema-viewer/

## Primeiro acesso

Para a primeira utilização da aplicação, é necessário criar um superusuário. Este superusuário é essencial para que seja possível criar outros usuários no sistema posteriormente. Para isso, execute o seguinte comando no seu terminal:

1.  **Criando o Superuser:**
    Execute o comando abaixo no seu terminal:
    ```bash
    docker-compose exec backend python manage.py createsuperuser
    ```
    Siga os prompts para configurar o seu nome, email e senha.

### Licença

Esse Projeto está sob a licença MIT - consulte o arquivo [LICENSE](LICENSE) para mais detalhes
