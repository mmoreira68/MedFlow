# Vamos gerar o arquivo README.md com o conteúdo em markdown

content = """# 🏥 MedFlow – Gestão de Salas Hospitalares  

Projeto Integrador desenvolvido no âmbito da graduação em **Ciência de Dados e Tecnologia** da **UNIVESP**.  
O **MedFlow** é um sistema web de gestão hospitalar que facilita o controle de **andares, salas, equipamentos, profissionais** e **agendamentos de uso de salas**.  

---

## 🚀 Funcionalidades principais  

- **Autenticação** customizada para administradores.  
- **CRUD completo** para Andares, Salas, Funcionalidades, Equipamentos e Profissionais.  
- **Validações inteligentes**:  
  - Bloqueio da exclusão de andares com salas/agendamentos vinculados.  
  - Bloqueio da exclusão de salas com agendamentos ativos.  
  - Bloqueio da exclusão de profissionais vinculados a agendamentos.  
  - Validação de unicidade de CRM para profissionais.  
  - Normalização de nomes sem considerar acentuação (evita duplicados como *Térreo* e *Terreo*).  
- **Agendamento de salas** com verificação automática de conflitos de horário.  
- **Interface moderna** com **Bootstrap 5 + HTMX**:  
  - Inclusão rápida de andares e funcionalidades via modal.  
  - Listagem de itens já cadastrados em cada tela de criação.  
  - Botões com ícones intuitivos (editar, excluir, configurar).  
- **Painel administrativo** com visão geral de andares, salas, equipamentos e profissionais.  
- **Visualização pública de agendamentos** do dia, com navegação entre datas.  

---

## 🛠️ Tecnologias utilizadas  

- **Backend**: [Django 5](https://www.djangoproject.com/) (Python 3.13)  
- **Banco de dados**: SQLite (desenvolvimento) / PostgreSQL (produção recomendado)  
- **Frontend**: Bootstrap 5 + HTMX  
- **Ambiente**: Virtualenv (`.venv`)  
- **Controle de versão**: Git + GitHub  

---

## 📦 Instalação  

### 1. Clone o repositório  
```bash
git clone https://github.com/seu-usuario/MedFlow.git
cd MedFlow
