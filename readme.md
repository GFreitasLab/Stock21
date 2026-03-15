# Stock21

**Stock21** é uma aplicação web de gerenciamento de estoque simples e leve voltada para pequenas e médias empresas do ramo alimentício, especialmente pizzarias.

## Funcionalidades

- Gerenciamento de usuários: registro, login e funções como funcionário e administrador.
- Gerenciamento de Ingredientes e Produtos: permitindo criação, modificação, visualização e exclusão.
- Registro de movimentações e geração de relatórios de faturamento por data.

## Tecnologias

### Backend

- **Linguagem:** [Python](https://www.python.org/) - Linguagem de programação de alto nível, simples e poderosa, amplamente utilizada para automação e ciência de dados.
- **Framework:** [Django](https://www.djangoproject.com/) - Framework web em Python que permite criar aplicações completas de forma rápida, segura e escalável.
- **Banco de Dados:** [Sqlite3](https://sqlite.org/) - Banco de dados relacional leve e embutido, ideal para testes e pequenos projetos.
- **Visualização do Banco de Dados:** [Django Schema Viewer](https://pypi.org/project/django-schema-viewer/) - Visualize as relações entre os Modelos do Django e a estrutura do banco de dados de forma interativa.

### Frontend

- **Templates:** [Django Templates](https://docs.djangoproject.com/en/5.2/topics/templates/) - Sistema de templates nativo do Django que permite gerar páginas HTML dinâmicas a partir de variáveis do backend.
- **Estilo:** [Tailwind CSS](https://tailwindcss.com/) - Framework CSS utility-first que facilita a criação de interfaces responsivas e modernas com classes predefinidas.

### DevOps

- **Docker:** [Docker](https://docs.docker.com/get-started/) – Ferramenta que cria ambientes isolados (contêineres) para executar aplicações de forma padronizada em qualquer máquina.
- **Docker Compose:** [Docker Compose](https://docs.docker.com/compose/) – Ferramenta que orquestra múltiplos contêineres simultaneamente, usando um arquivo YAML para configurar tudo com um único comando.

## Estrutura do Projeto

```
devspizza
├── core                # Configurações principais do projeto
│   ├── asgi.py
│   ├── decorators.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── accounts            # Módulo responsável pelo gerenciamento de usuários
│   ├── models.py
│   ├── templates
│   │   ├── ...
│   ├── urls.py
│   └── views.py
├── movements           # Módulo responsável pelo gerenciamento de movimentações
│   ├── models.py
│   ├── templates
│   │   ├── ...
│   ├── urls.py
│   └── views.py
├── stock               # Módulo responsável pelo gerenciamento de estoque
│   ├── models.py
│   ├── templates
│   │   ├── ...
│   ├── urls.py
│   └── views.py
├── static              # Arquivos estáticos usados pelo Django (JavaScript)
└── templates           # Templates HTML não associados a nenhum módulo
├── .gitignore          # Arquivo para especificar explicitamente os arquivos a serem ignorados pelo Git
├── .venv               # Ambiente Virtual Python (Ignorado pelo Git)
├── .env                # Variáveis de ambiente para configuração do Docker e Django
├── db.sqlite3          # Banco de Dados
├── docker-compose.yml  # Diz passo a passo como configurar o ambiente para o projeto
├── Dockerfile          # Reúne tudo em um só lugar e executa múltiplos serviços com um único comando
├── manage.py           # Utilitário de linha de comando do Django para tarefas administrativas
├── readme.md           # Documentação do projeto
├── readme_en.md        # Documentação do projeto em inglês
├── requirements.txt    # Lista de dependências python para este projeto
```

## Pré-requisitos

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
SECRET_KEY=sua_chave_secreta_django   # Gere uma chave única e complexa para produção
DEBUG=True                            # Defina como False para produção
DB_ENGINE=django.db.backends.sqlite3  # Sqlite3 para projetos simples
DB_NAME=db.sqlite3                    # Nome do banco de dados
ALLOWED_HOSTS=*                       # Hosts permitidos, por padrão, todos
```

3. **Faça o build do Docker Compose:**

```bash
docker-compose up --build
```

## Executando a Aplicação

### Usando o Docker Compose (Recomendado)

```bash
# Compila e inicia todos os serviços
docker-compose up --build

# Executa em segundo plano
docker-compose up -d

# Para o serviço
docker-compose down
```

Após iniciar o serviço você pode acessar:

- **Aplicação**: http://localhost:8000
- **Visualização do Banco de Dados**: [http://127.0.0.1:8000/schema-viewer/](http://127.0.0.1:8000/schema-viewer/)

## Primeiro Acesso

Para o primeiro uso da aplicação, é necessário criar um superusuário. Este superusuário é essencial para permitir a criação de outros usuários no sistema posteriormente. Para isso, execute o seguinte comando no seu terminal:

1. **Criando o Superusuário:**
   Execute o comando abaixo no seu terminal:

```bash
docker-compose exec backend python manage.py createsuperuser
```

Siga os prompts para configurar seu nome, e-mail e senha.

### Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](https://github.com/GFreitasLab/Stock21/blob/main/LICENSE) para mais detalhes
