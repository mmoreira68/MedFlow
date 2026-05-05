# Projeto Integrador desenvolvido no âmbito da graduação em **Ciência de Dados e Tecnologia** da **UNIVESP**.  

O **OdontoFlow** é um sistema web de gestão odontológica que facilita o controle de **consultórios, salas, equipamentos, profissionais** e **agendamentos de atendimento**.  

---

## 🚀 Funcionalidades principais  

- **API REST pública** com documentação automática (Swagger/OpenAPI).
  - Endpoints para consulta de agendamentos e disponibilidade.
  - Rate limiting e cache implementado.
  - Acesso público sem autenticação (para visualização de horários).
- **Autenticação** customizada para administradores.  
- **CRUD completo** para Consultórios, Salas, Funcionalidades, Equipamentos e Profissionais.
- **Validações inteligentes**:
  - Bloqueio da exclusão de consultórios com salas/agendamentos vinculados.
  - Bloqueio da exclusão de salas com agendamentos ativos.
  - Bloqueio da exclusão de profissionais vinculados a agendamentos.
  - Validação de unicidade de CRO para dentistas.
  - Normalização de nomes sem considerar acentuação (evita duplicados como *Térreo* e *Terreo*).
- **Agendamento de atendimentos** com verificação automática de conflitos de horário.
- **Interface moderna** com **Bootstrap 5 + HTMX**:
  - Inclusão rápida de consultórios e funcionalidades via modal.
  - Listagem de itens já cadastrados em cada tela de criação.
  - Botões com ícones intuitivos (editar, excluir, configurar).
- **Painel administrativo** com visão geral de consultórios, salas, equipamentos e profissionais.
- **Visualização pública de agendamentos** do dia, com navegação entre datas.  

---

## 🛠️ Tecnologias utilizadas  

- **Backend**: [Django 6.0](https://www.djangoproject.com/) (Python 3.13)  
- **API REST**: [Django REST Framework 3.17](https://www.django-rest-framework.org/)  
- **Documentação API**: [drf-spectacular](https://drf-spectacular.readthedocs.io/) (Swagger/OpenAPI)
- **Banco de dados**: SQLite (desenvolvimento) / PostgreSQL (produção recomendado)  
- **Frontend**: Bootstrap 5 + HTMX  
- **Testes**: pytest + pytest-django  
- **Segurança**: Rate limiting (django-ratelimit), CORS headers  
- **Deploy**: Gunicorn + WhiteNoise (Render)  
- **Ambiente**: Virtualenv (`.venv`)  
- **Controle de versão**: Git + GitHub  

---

## � API REST

A API REST pública está disponível em `/api/public/` com documentação automática:

### Endpoints principais
```
GET  /api/public/agendamentos/                           # Lista agendamentos
GET  /api/public/agendamentos/{id}/                      # Detalhe agendamento
GET  /api/public/agendamentos/calendar/disponibilidade/  # Horários por data
```

### Documentação
- **Swagger UI**: `/api/docs/`
- **Schema OpenAPI**: `/api/schema/`

### Exemplo de uso
```bash
# Listar agendamentos
curl "http://localhost:8000/api/public/agendamentos/"

# Filtrar por data
curl "http://localhost:8000/api/public/agendamentos/calendar/disponibilidade/?data_inicio=2026-05-05&data_fim=2026-05-31"
```

---

## �📦 Instalação  

### 1. Clone o repositório  
```bash
git clone https://github.com/seu-usuario/OdontoFlow.git
cd OdontoFlow
