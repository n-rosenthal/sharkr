#   sharkr - Plataforma de Competição de Startups
![Flask](https://img.shields.io/badge/Flask-2.0.3-important)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4.36-blueviolet)

Sistema web para simulação de um torneio entre startups, onde competidoras disputam em rodadas eliminatórias com eventos que impactam suas pontuações. Desenvolvido como solução para o desafio técnico ao programa de admissão à IT Academy.

## ⚙️ Funcionalidades Principais

- **Cadastro de Startups**  
  Registre inúmeras startups para competir em torneios de 4, 6 ou 8 participantes.

- **Sistema de Eventos**  
  Adição de eventos como `Pitch Convincente (+6pts)` e `Fake News no Pitch (-8pts)`, que impactam as pontuações dos competidores.

- **Shark Fight**  
  Resolução automática de empates com bônus de +2pts para um competidor aleatório.

- **Progressão de Rounds**  
  Avança automaticamente para próxima rodada quando todas as batalhas são concluídas.

- **Relatórios**  
  Exibição de relatórios sobre as startups, batalhas e torneios.

- **Feature Extra**: Histórico detalhado de todas as batalhas com pontuações e eventos registrados.

## 🚀 Como Executar

### Pré-requisitos
- Python 3.9+
- Pip
- Git (opcional)

### Passo a Passo

1. **Clonar repositório**

```bash
git clone https://github.com/n-rosenthal/sharkr.git
cd startup-rush
```
2. **Configurar ambiente virtual**

```bash
python -m venv venv

#   Windows:
venv\Scripts\activate

#   Linux:
source venv/bin/activate
```

3. **Instalar dependências**

```bash
pip install -r requirements.txt
```

4. **Inicializar o banco de dados**

```bash
flask db init
flask db migrate -m "Criando banco de dados"
flask db upgrade
```

5. **Executar o servidor**

```bash
python3 run.py
```

Se todas as instruções foram executadas com sucesso, o servidor estara pronto para ser acessado em http://127.0.0.1:5000/ (ou http://localhost:5000, normalmente, salvo modificações) e o banco de dados estara pronto para ser usado.