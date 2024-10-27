"""
Diagrama de Atividade do CRUD

      Início
        |
Adicionar Funcionário
        |
Solicitar Dados
        |
        V
 Dados Válidos?
   |        |
  Sim      Não
   |        |
Inserir | Mostrar Erro
   |
Listar Funcionários
        |
    Mostrar Lista
        |
        V
 Editar Funcionário
         |
     Solicitar ID
         |
         V
Funcionário Existe?
   |             |
  Sim           Não
   |             |
Recuperar | Mostrar Erro
   |
 Solicitar Novos Dados
          |
          V
    Dados Válidos?
   |            |
  Sim          Não
   |            |
Atualizar | Mostrar Erro
   |
Deletar Funcionário
   |
Solicitar ID
   |
   V
Funcionário Existe?
   |                        |
  Sim                      Não
   |                        |
Marcar como inativo | Mostrar Erro
        |
        V
       Fim
"""


"""
Resposta Relatório 1

SELECT funcionario as Funcionario,
cargo as Cargo,
salario as Salário
from empresa 
WHERE ativo = 1
order by cargo



Resposta Relatório 2

SELECT cargo as Cargo,
COUNT(funcionario) as Qtde_Funcionarios,
SUM(salario) as Salário
FROM empresa
WHERE ativo = 1
group by cargo

"""
from flet import *
import sqlite3 as sql

# Conexão com o banco de dados
conexao = sql.connect("data.db", check_same_thread=False)
cursor = conexao.cursor()

# Criando tabela se caso nao existir
def criar_tabela():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario TEXT NOT NULL,
            cargo TEXT NOT NULL,
            salario REAL NOT NULL,
            endereco TEXT NOT NULL,
            ativo INTEGER NOT NULL DEFAULT 1
        )
    ''')
    conexao.commit()
criar_tabela()

# Função para inativar um funcionário 
def deletar(id_user, y, page, todos_dados):
    cursor.execute(""" UPDATE empresa SET ativo = 0 WHERE id = ?""", [id_user])
    conexao.commit()
    y.open = False
    renderizar_todos(todos_dados,page, todos_dados)
    page.update()

# Função para atualizar os dados de um funcionário
def atualizar(id_user, nome_funcionario, cargo, salario,endereco, alerta_dialogo, page, todos_dados):
    cursor.execute("""UPDATE empresa SET funcionario = ?, cargo = ?, endereco = ?, salario = ?, ativo = 1 WHERE id = ?""", (nome_funcionario, cargo, salario,endereco, id_user))
    conexao.commit()
    alerta_dialogo.open = False
    renderizar_todos(todos_dados,page, todos_dados)
    page.update()

# Função para abrir a interface de edição
def abrir_editar(e, page, todos_dados):
    id_user = e.control.subtitle.value
    cursor.execute("""SELECT funcionario, cargo, salario, endereco FROM empresa WHERE id = ?""", [id_user])
    funcionario, cargo, salario, endereco = cursor.fetchone()

    editar_dado = TextField(label='Nome do Funcionario', value=funcionario)
    adicionar_cargo = TextField(label='Cargo', value=cargo)
    adicionar_salario = TextField(label='Salário', value=str(salario))
    adicionar_endereco = TextField(label='Endereço', value=endereco)

    alerta_dialogo = AlertDialog(
        title=Text(f"📝 Editar Funcionario {funcionario}", font_family='Poppins'),
        content=Column([
            editar_dado,
            adicionar_cargo,
            adicionar_salario,
            adicionar_endereco
        ]),
        actions=[
            ElevatedButton('Inativar', bgcolor='Red',color='black',  on_click=lambda e: deletar(id_user, alerta_dialogo, page, todos_dados),icon=icons.EXIT_TO_APP),
            ElevatedButton('Atualizar', bgcolor='Green',color='black', on_click=lambda e: atualizar(id_user, editar_dado.value, adicionar_cargo.value, adicionar_salario.value,adicionar_endereco.value, alerta_dialogo, page, todos_dados),icon=icons.REFRESH)
        ],
        actions_alignment='spaceBetween'
    )
    page.overlay.append(alerta_dialogo)
    alerta_dialogo.open = True
    page.update()
    
def abrir_editar_inativos(e, page, todos_dados):
    id_user = e.control.subtitle.value
    cursor.execute("""SELECT funcionario, cargo, salario,endereco FROM empresa WHERE id = ? and ativo = 0""", [id_user])
    funcionario, cargo,endereco, salario = cursor.fetchone()
    nome = Text('Nome:',font_family='Poppins',size=13)
    editar_dado = Text(f'{funcionario}',font_family='Poppins2')
    cargo1 = Text('Cargo:',font_family='Poppins',size=13)
    adicionar_cargo = Text(f'{cargo}',font_family='Poppins2')
    endereco1 = Text('Endereço:',font_family='Poppins',size=13)
    adicionar_endereco = Text(f'{endereco}',font_family='Poppins2')
    salario1 = Text('Salario:',font_family='Poppins',size=13)
    adicionar_salario = Text(f'{salario}',font_family='Poppins2')

    alerta_dialogo = AlertDialog(
        title=Text(f"📝 {funcionario} - Inativo", color='Red', font_family='Poppins2'),
        content=Column([
            nome, editar_dado,
            cargo1,adicionar_cargo,
            salario1,adicionar_salario,
            endereco1,adicionar_endereco
        ]),
        actions=[
            ElevatedButton('Ativar', bgcolor='Green',color='White', on_click=lambda e: atualizar(id_user, editar_dado.value, adicionar_cargo.value,adicionar_salario.value, adicionar_endereco.value, alerta_dialogo, page, todos_dados),icon=icons.LOCAL_ACTIVITY)
        ],
    )
    page.overlay.append(alerta_dialogo)
    alerta_dialogo.open = True
    page.update()

# Função para renderizar todos os funcionários ativos
def renderizar_todos(e, page, todos_dados):
    cursor.execute(""" SELECT * FROM empresa WHERE ativo = 1 """)
    dados_atualizados = cursor.fetchall()
    todos_dados.controls.clear()

    for row in dados_atualizados:
        todos_dados.controls.append(
            ListTile(
                subtitle=Text(row[0], font_family='Poppins2'),  # ID
                title=Text(row[1], font_family='Poppins2'),  # Nome do funcionário
                leading=Text(row[2], font_family='Poppins2'),  # Cargo
                on_click=lambda e: abrir_editar(e, page, todos_dados)
            )
        )
    page.update()

# Função para renderizar todos os funcionários inativos
def renderizar_todos_inativos(e, page, todos_dados):
    cursor.execute("""SELECT * FROM empresa WHERE ativo = '0' """)
    dados_atualizados = cursor.fetchall()
    todos_dados.controls.clear()

    for row in dados_atualizados:
        todos_dados.controls.append(
            ListTile(
                title=Text(row[1], font_family='Poppins2'),  # Nome do funcionário
                subtitle=Text(row[0], font_family='Poppins2'),  # ID
                leading=Text(row[2], font_family='Poppins2'),  # Cargo
                on_click=lambda e: abrir_editar_inativos(e, page, todos_dados)
            )
        )
    page.update()

# Função para adicionar novo funcionário
def adicionar_novo_funcionario(e, page, todos_dados, adicionar_funcionario, adicionar_cargo, adicionar_salario, adicionar_endereco):
    if not adicionar_funcionario.value or not adicionar_cargo.value or not adicionar_salario.value.isdigit() or not adicionar_endereco.value:
        page.snack_bar = SnackBar(Text("Por favor, preencha todos os campos corretamente."))
        page.snack_bar.open = True
        page.update()
        return

    cursor.execute(""" 
    INSERT INTO empresa (funcionario, cargo, salario, endereco, ativo) 
    VALUES (?, ?, ?, ?, ?) 
    """, 
    [adicionar_funcionario.value, adicionar_cargo.value, adicionar_salario.value, adicionar_endereco.value, 1])
    conexao.commit()
    renderizar_todos(todos_dados, page, todos_dados)

# Função principal de build
def build(page):
    todos_dados = Column(scroll=True)
    adicionar_funcionario = TextField(label='Nome do Funcionario:')
    adicionar_cargo = TextField(label='Cargo:')
    adicionar_endereco = TextField(label='Endereço:')
    adicionar_salario = TextField(label='Salário:')

    page.add(
        Column([
            Text("GESTÃO DE FUNCIONARIOS", size=20, font_family="Poppins"),
            adicionar_funcionario,
            adicionar_cargo,
            adicionar_endereco,
            adicionar_salario,
            Row([ElevatedButton('Adicionar Funcionario',color='White', on_click=lambda e: adicionar_novo_funcionario(e, page, todos_dados, adicionar_funcionario, adicionar_cargo,adicionar_salario,adicionar_endereco)),
                ElevatedButton('Ativos',bgcolor= 'Green',color='White', on_click=lambda e: renderizar_todos(todos_dados,page, todos_dados)),
                ElevatedButton('Inativos',bgcolor= 'Orange',color='White', on_click=lambda e: renderizar_todos_inativos(e, page, todos_dados)),]),
            todos_dados
        ])
    )
    renderizar_todos(todos_dados, page, todos_dados)

def main(page: Page):
    page.fonts = {
        "Poppins": "fonts/Poppins-Bold.ttf",
        "Poppins2": "fonts/Poppins-Light.ttf",
        "Poppins3": "fonts/Poppins-Regular.ttf",
    }
    build(page)
    page.update()

app(target=main)
