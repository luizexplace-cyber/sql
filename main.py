import csv
import os
from datetime import datetime, timedelta

# --- Constantes e Configurações ---
LIVROS_FILE = 'livros.csv'
ALUNOS_FILE = 'alunos.csv'
EMPRESTIMOS_FILE = 'emprestimos.csv'
DIAS_EMPRESTIMO = 7 # Livros emprestados por 7 dias

# --- Classes de Modelo (POO) ---

class Livro:
    """Representa um livro no acervo."""
    def __init__(self, titulo, autor, isbn, total_copias, copias_disponiveis):
        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
        self.total_copias = int(total_copias)
        self.copias_disponiveis = int(copias_disponiveis)

    def __str__(self):
        return f"Título: {self.titulo} | Autor: {self.autor} | ISBN: {self.isbn} | Disponíveis: {self.copias_disponiveis}/{self.total_copias}"

    def to_dict(self):
        return self.__dict__

class Aluno:
    """Representa um aluno da instituição."""
    def __init__(self, aluno_id, nome, banido='Não'):
        self.aluno_id = aluno_id
        self.nome = nome
        # Status de banimento: 'Sim' ou 'Não'
        self.banido = banido

    def __str__(self):
        status = "BANIDO" if self.banido == 'Sim' else "Ativo"
        return f"ID: {self.aluno_id} | Nome: {self.nome} | Status: {status}"

    def to_dict(self):
        return self.__dict__

# --- Classe Principal de Gerenciamento ---

class Biblioteca:
    """Gerencia a coleção de livros, alunos e as operações de empréstimo."""
    def __init__(self):
        self.livros = {}     # {isbn: Livro_objeto}
        self.alunos = {}     # {aluno_id: Aluno_objeto}
        # {isbn: {aluno_id: [data_emprestimo, data_vencimento]}}
        self.emprestimos = {} 
        self._carregar_dados()

    # --- Persistência de Dados ---

    def _carregar_dados(self):
        """Carrega dados dos arquivos CSV ao iniciar."""
        if os.path.exists(LIVROS_FILE):
            with open(LIVROS_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.livros[row['isbn']] = Livro(**row)
        
        if os.path.exists(ALUNOS_FILE):
            with open(ALUNOS_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.alunos[row['aluno_id']] = Aluno(**row)

        if os.path.exists(EMPRESTIMOS_FILE):
            with open(EMPRESTIMOS_FILE, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None) 
                for isbn, aluno_id, data_emprestimo, data_vencimento in reader:
                    if isbn not in self.emprestimos:
                        self.emprestimos[isbn] = {}
                    self.emprestimos[isbn][aluno_id] = [data_emprestimo, data_vencimento]

    def salvar_dados(self):
        """Salva todos os dados nos arquivos CSV."""
        print("\n⏳ Salvando dados...")

        # 1. Salvar Livros
        if self.livros:
            livros_data = [l.to_dict() for l in self.livros.values()]
            fieldnames = list(Livro.__init__.__code__.co_varnames)[1:]
            with open(LIVROS_FILE, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(livros_data)

        # 2. Salvar Alunos
        if self.alunos:
            alunos_data = [a.to_dict() for a in self.alunos.values()]
            fieldnames = list(Aluno.__init__.__code__.co_varnames)[1:]
            with open(ALUNOS_FILE, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(alunos_data)

        # 3. Salvar Empréstimos
        emprestimos_data = []
        for isbn, alunos_emprestados in self.emprestimos.items():
            for aluno_id, datas in alunos_emprestados.items():
                emprestimos_data.append([isbn, aluno_id, datas[0], datas[1]])
        
        with open(EMPRESTIMOS_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['isbn', 'aluno_id', 'data_emprestimo', 'data_vencimento'])
            writer.writerows(emprestimos_data)

        print("✅ Dados salvos com sucesso.")

    # --- Controle de Livros ---

    def adicionar_livro(self, titulo, autor, isbn, copias):
        """Adiciona um livro ou novas cópias a um existente."""
        if isbn in self.livros:
            livro = self.livros[isbn]
            livro.total_copias += copias
            livro.copias_disponiveis += copias
            print(f"✅ Cópias adicionadas ao livro: '{titulo}'. Total: {livro.total_copias}")
        else:
            self.livros[isbn] = Livro(titulo, autor, isbn, copias, copias)
            print(f"✅ Livro '{titulo}' adicionado com {copias} cópias.")
        self.salvar_dados()

    def listar_livros(self):
        """Exibe o acervo."""
        if not self.livros:
            print("Nenhum livro no acervo.")
            return
        print("\n--- Acervo de Livros ---")
        for livro in self.livros.values():
            print(livro)
        print("------------------------")

    # --- Controle de Alunos e Banimento ---

    def adicionar_aluno(self, aluno_id, nome):
        """Cadastra um novo aluno."""
        if aluno_id in self.alunos:
            print(f"❌ Aluno com ID '{aluno_id}' já cadastrado.")
            return
        self.alunos[aluno_id] = Aluno(aluno_id, nome)
        print(f"✅ Aluno '{nome}' cadastrado com sucesso.")
        self.salvar_dados()

    def listar_alunos(self):
        """Lista todos os alunos e seus status (incluindo banidos)."""
        if not self.alunos:
            print("Nenhum aluno cadastrado.")
            return
        print("\n--- Lista de Alunos ---")
        for aluno in self.alunos.values():
            print(aluno)
        print("------------------------")
    
    def banir_aluno(self, aluno_id):
        """Define o status do aluno como BANIDO."""
        aluno = self.alunos.get(aluno_id)
        if not aluno:
            print(f"❌ Aluno com ID '{aluno_id}' não encontrado.")
            return
        
        # Verificação de livros emprestados
        tem_emprestimo = any(aluno_id in alunos for alunos in self.emprestimos.values())
        if tem_emprestimo:
            print(f"❌ Erro: Aluno '{aluno.nome}' não pode ser banido, pois ainda tem livros emprestados.")
            return

        aluno.banido = 'Sim'
        print(f"🚨 Aluno '{aluno.nome}' (ID: {aluno_id}) foi BANIDO e bloqueado para novos empréstimos.")
        self.salvar_dados()

    def desbanir_aluno(self, aluno_id):
        """Define o status do aluno como Ativo."""
        aluno = self.alunos.get(aluno_id)
        if not aluno:
            print(f"❌ Aluno com ID '{aluno_id}' não encontrado.")
            return
        
        aluno.banido = 'Não'
        print(f"✅ Aluno '{aluno.nome}' (ID: {aluno_id}) foi DESBANIDO e está apto para empréstimos.")
        self.salvar_dados()

    # --- Controle de Empréstimos e Atrasos ---

    def emprestar_livro(self, isbn, aluno_id):
        """Registra o empréstimo."""
        livro = self.livros.get(isbn)
        aluno = self.alunos.get(aluno_id)

        # 1. Validações
        if not livro or not aluno:
            print("❌ Livro ou Aluno não encontrado.")
            return
        
        if aluno.banido == 'Sim':
            print(f"🚫 **BLOQUEADO:** Aluno '{aluno.nome}' está BANIDO e não pode fazer empréstimos.")
            return
        
        if livro.copias_disponiveis <= 0:
            print(f"❌ Todas as cópias de '{livro.titulo}' estão emprestadas.")
            return
        
        if isbn in self.emprestimos and aluno_id in self.emprestimos[isbn]:
            print(f"❌ Aluno '{aluno.nome}' já tem uma cópia de '{livro.titulo}' emprestada.")
            return

        # 2. Realizar Empréstimo
        livro.copias_disponiveis -= 1
        
        data_emprestimo = datetime.now().strftime('%Y-%m-%d')
        data_vencimento = (datetime.now() + timedelta(days=DIAS_EMPRESTIMO)).strftime('%Y-%m-%d')

        if isbn not in self.emprestimos:
            self.emprestimos[isbn] = {}
            
        self.emprestimos[isbn][aluno_id] = [data_emprestimo, data_vencimento]
        
        print(f"✅ Sucesso! Livro '{livro.titulo}' emprestado para '{aluno.nome}'.")
        print(f"   Data de Devolução Prevista: {data_vencimento}")
        self.salvar_dados()

    def devolver_livro(self, isbn, aluno_id):
        """Registra a devolução."""
        livro = self.livros.get(isbn)
        aluno = self.alunos.get(aluno_id)

        if isbn not in self.emprestimos or aluno_id not in self.emprestimos.get(isbn, {}):
            print(f"❌ Erro: Não há registro de empréstimo deste livro ({isbn}) para o aluno ({aluno_id}).")
            return
        
        # 1. Checagem de Atraso
        data_vencimento_str = self.emprestimos[isbn][aluno_id][1]
        data_vencimento = datetime.strptime(data_vencimento_str, '%Y-%m-%d')
        data_atual = datetime.now()

        if data_atual > data_vencimento:
            dias_atraso = (data_atual - data_vencimento).days
            print(f"🚨 **ATRASO:** Devolução com {dias_atraso} dias de atraso.")
            print(f"   Ação recomendada: Banir o aluno '{aluno.nome}' até a situação ser resolvida no menu de Alunos.")
        else:
            print("✅ Devolução realizada dentro do prazo.")

        # 2. Finalizar Devolução
        del self.emprestimos[isbn][aluno_id]
        if not self.emprestimos[isbn]:
            del self.emprestimos[isbn]
            
        livro.copias_disponiveis += 1

        print(f"✅ Livro '{livro.titulo}' devolvido por '{aluno.nome}'.")
        self.salvar_dados()

    def listar_emprestimos(self):
        """Lista todos os empréstimos atuais, destacando os atrasos."""
        if not self.emprestimos:
            print("Nenhum livro atualmente emprestado.")
            return
        
        print("\n--- Relatório de Empréstimos ---")
        for isbn, alunos_emprestados in self.emprestimos.items():
            livro = self.livros.get(isbn, "[Livro não encontrado]")
            for aluno_id, datas in alunos_emprestados.items():
                aluno = self.alunos.get(aluno_id, "[Aluno não encontrado]")
                _, data_vencimento = datas
                
                # Verificação de Atraso
                data_vencimento_dt = datetime.strptime(data_vencimento, '%Y-%m-%d')
                status = "Em Dia"
                if datetime.now() > data_vencimento_dt:
                    dias_atraso = (datetime.now() - data_vencimento_dt).days
                    status = f"**ATRASADO** ({dias_atraso} dias)"

                print(f"📚 {livro.titulo} (ISBN: {isbn}) | 👤 {aluno.nome} (ID: {aluno_id})")
                print(f"   Vencimento: {data_vencimento} | Status: {status}")
        print("---------------------------------")

# --- Interface de Usuário (Interação via Terminal) ---

def menu_principal():
    """Loop principal do sistema de menu."""
    biblioteca = Biblioteca()

    while True:
        print("\n" + "="*45)
        print("       📚 Sistema de Gerenciamento de Biblioteca")
        print("="*45)
        print("1. Gerenciar Livros (Acervo)")
        print("2. Gerenciar Alunos (Cadastro e Banimento)")
        print("3. Empréstimos e Devoluções")
        print("4. Sair e Salvar Dados")
        print("="*45)

        escolha = input("Escolha uma opção (1-4): ")

        if escolha == '1':
            menu_livros(biblioteca)
        elif escolha == '2':
            menu_alunos(biblioteca)
        elif escolha == '3':
            menu_emprestimos(biblioteca)
        elif escolha == '4':
            biblioteca.salvar_dados()
            print("👋 Sistema encerrado. Todos os dados foram salvos.")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

def menu_livros(biblioteca):
    """Menu para operações de livros."""
    while True:
        print("\n--- Gerenciar Livros ---")
        print("1. Adicionar/Atualizar Livro (por ISBN)")
        print("2. Listar Acervo")
        print("3. Voltar")
        
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            print("\n--- Adicionar/Atualizar Livro ---")
            isbn = input("ISBN (código único): ").strip()
            titulo = input("Título: ").strip()
            autor = input("Autor: ").strip()
            try:
                copias = int(input("Número de Cópias a Adicionar: ").strip())
                if copias <= 0: raise ValueError
            except ValueError:
                print("❌ Número de cópias deve ser um inteiro positivo.")
                continue
            biblioteca.adicionar_livro(titulo, autor, isbn, copias)

        elif escolha == '2':
            biblioteca.listar_livros()

        elif escolha == '3':
            break
        else:
            print("Opção inválida.")

def menu_alunos(biblioteca):
    """Menu para operações de alunos e controle de banimento."""
    while True:
        print("\n--- Gerenciar Alunos ---")
        print("1. Cadastrar Novo Aluno")
        print("2. Listar Alunos (Ver Status de Banimento)")
        print("3. **BANIR** Aluno (Bloquear Empréstimos)")
        print("4. **DESBANIR** Aluno (Liberar Empréstimos)")
        print("5. Voltar")
        
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            print("\n--- Cadastrar Aluno ---")
            aluno_id = input("ID do Aluno (ex: 12345): ").strip()
            nome = input("Nome Completo: ").strip()
            biblioteca.adicionar_aluno(aluno_id, nome)

        elif escolha == '2':
            biblioteca.listar_alunos()

        elif escolha == '3':
            aluno_id = input("ID do Aluno para BANIR: ").strip()
            biblioteca.banir_aluno(aluno_id)

        elif escolha == '4':
            aluno_id = input("ID do Aluno para DESBANIR: ").strip()
            biblioteca.desbanir_aluno(aluno_id)

        elif escolha == '5':
            break
        else:
            print("Opção inválida.")

def menu_emprestimos(biblioteca):
    """Menu para operações de empréstimo e devolução."""
    while True:
        print("\n--- Empréstimos ---")
        print("1. Realizar Empréstimo")
        print("2. Realizar Devolução")
        print("3. Listar Empréstimos Atuais (Checar Atrasos)")
        print("4. Voltar")
        
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            print("\n--- Realizar Empréstimo ---")
            isbn = input("ISBN do Livro: ").strip()
            aluno_id = input("ID do Aluno: ").strip()
            biblioteca.emprestar_livro(isbn, aluno_id)

        elif escolha == '2':
            print("\n--- Realizar Devolução ---")
            isbn = input("ISBN do Livro: ").strip()
            aluno_id = input("ID do Aluno: ").strip()
            biblioteca.devolver_livro(isbn, aluno_id)

        elif escolha == '3':
            biblioteca.listar_emprestimos()
            
        elif escolha == '4':
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu_principal()