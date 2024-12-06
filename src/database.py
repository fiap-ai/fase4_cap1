import os
import cx_Oracle
import random
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables first
print("Loading .env file...")
load_dotenv(override=True)

# Get Oracle home from .env
instant_client_path = os.getenv('ORACLE_HOME')
if not instant_client_path:
    raise Exception("ORACLE_HOME not set in .env file")

# Initialize Oracle Client before any database operations
try:
    cx_Oracle.init_oracle_client(
        lib_dir=instant_client_path,
        config_dir=None,
        error_url=None,
        driver_name=None
    )
except Exception as e:
    # Ignore "already initialized" error
    if "already initialized" not in str(e):
        print(f"Warning: {str(e)}")

def generate_random_data():
    """Gera dados aleatórios simulando sensores."""
    return {
        'humidity': round(random.uniform(30, 80), 2),
        'temperature': round(random.uniform(10, 50), 2),
        'light': round(random.uniform(0, 700), 2),
        'btn_p': random.choice([0, 1]),
        'btn_k': random.choice([0, 1]),
        'relay_status': random.choice([0, 1])
    }

class DatabaseManager:
    def __init__(self):
        """Inicializa o gerenciador de banco de dados."""
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.dsn = os.getenv('DB_DSN')
        self.connection = None
        self.cursor = None

    def connect(self):
        """Estabelece conexão com o banco de dados."""
        try:
            self.connection = cx_Oracle.connect(
                user=self.user,
                password=self.password,
                dsn=self.dsn
            )
            self.cursor = self.connection.cursor()
            print("Conexão estabelecida com sucesso!")
        except cx_Oracle.Error as error:
            print(f"Erro ao conectar ao banco de dados: {error}")
            raise

    def disconnect(self):
        """Fecha a conexão com o banco de dados."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
                print("Conexão fechada com sucesso!")
        except cx_Oracle.Error as error:
            print(f"Erro ao fechar conexão: {error}")

    def create_tables(self):
        """Cria as tabelas necessárias se não existirem."""
        try:
            self.cursor.execute("""
                BEGIN
                    EXECUTE IMMEDIATE 'CREATE TABLE sensor_data (
                        id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        timestamp TIMESTAMP,
                        humidity NUMBER,
                        temperature NUMBER,
                        light NUMBER,
                        btn_p NUMBER(1),
                        btn_k NUMBER(1),
                        relay_status NUMBER(1)
                    )';
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE = -955 THEN
                            NULL;
                        ELSE
                            RAISE;
                        END IF;
                END;
            """)
            
            # Create index on timestamp for better performance
            try:
                self.cursor.execute("""
                    CREATE INDEX idx_sensor_data_timestamp 
                    ON sensor_data(timestamp)
                """)
            except cx_Oracle.Error:
                pass  # Index might already exist
            
            self.connection.commit()
            print("Tabelas criadas/verificadas com sucesso!")
        except cx_Oracle.Error as error:
            print(f"Erro ao criar tabelas: {error}")
            raise

    def insert_sensor_data(self, humidity, temperature, light, btn_p, btn_k, relay_status, timestamp=None):
        """Insere dados dos sensores no banco."""
        try:
            if timestamp is None:
                timestamp = datetime.now()
                
            self.cursor.execute("""
                INSERT INTO sensor_data 
                (timestamp, humidity, temperature, light, btn_p, btn_k, relay_status)
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """, (timestamp, humidity, temperature, light, btn_p, btn_k, relay_status))
            
            self.connection.commit()
        except cx_Oracle.Error as error:
            print(f"Erro ao inserir dados: {error}")
            raise

    def get_all_readings(self):
        """Recupera todas as leituras dos sensores."""
        try:
            self.cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp ASC")
            columns = [col[0] for col in self.cursor.description]
            readings = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            return readings
        except cx_Oracle.Error as error:
            print(f"Erro ao recuperar dados: {error}")
            raise

    def update_reading(self, id, field, value):
        """Atualiza um valor específico de uma leitura."""
        try:
            self.cursor.execute(f"""
                UPDATE sensor_data 
                SET {field} = :1
                WHERE id = :2
            """, (value, id))
            
            self.connection.commit()
            print(f"Registro {id} atualizado com sucesso!")
        except cx_Oracle.Error as error:
            print(f"Erro ao atualizar dados: {error}")
            raise

    def delete_reading(self, id):
        """Deleta uma leitura específica."""
        try:
            self.cursor.execute("DELETE FROM sensor_data WHERE id = :1", (id,))
            self.connection.commit()
            print(f"Registro {id} deletado com sucesso!")
        except cx_Oracle.Error as error:
            print(f"Erro ao deletar registro: {error}")
            raise

    def delete_all_readings(self):
        """Deleta todas as leituras."""
        try:
            self.cursor.execute("DELETE FROM sensor_data")
            self.connection.commit()
            print("Todos os registros foram deletados com sucesso!")
        except cx_Oracle.Error as error:
            print(f"Erro ao deletar registros: {error}")
            raise

def print_menu():
    """Imprime o menu de opções."""
    print("\n=== Sistema de Gerenciamento de Dados dos Sensores ===")
    print("1. Criar - Inserir dados aleatórios")
    print("2. Ler - Mostrar todos os registros")
    print("3. Atualizar - Modificar um registro")
    print("4. Deletar - Remover um registro")
    print("5. Deletar - Remover todos os registros")
    print("6. Sair")
    print("================================================")

def main():
    """Função principal com menu interativo."""
    db = DatabaseManager()
    
    try:
        # Conecta ao banco e cria tabelas
        db.connect()
        db.create_tables()
        
        while True:
            print_menu()
            choice = input("Escolha uma opção (1-6): ")
            
            if choice == '1':
                # Criar - dados aleatórios
                data = generate_random_data()
                db.insert_sensor_data(**data)
                print("Dados gerados:", data)
                
            elif choice == '2':
                # Ler - todos os registros
                readings = db.get_all_readings()
                if readings:
                    for reading in readings:
                        print("\nID:", reading['ID'])
                        print("Timestamp:", reading['TIMESTAMP'])
                        print(f"Temperatura: {reading['TEMPERATURE']}°C")
                        print(f"Umidade: {reading['HUMIDITY']}%")
                        print(f"Luz: {reading['LIGHT']}")
                        print(f"Botão P: {'Ativado' if reading['BTN_P'] else 'Desativado'}")
                        print(f"Botão K: {'Ativado' if reading['BTN_K'] else 'Desativado'}")
                        print(f"Relé: {'Ligado' if reading['RELAY_STATUS'] else 'Desligado'}")
                else:
                    print("Nenhum registro encontrado.")
                
            elif choice == '3':
                # Atualizar
                id = input("Digite o ID do registro a ser atualizado: ")
                print("\nEscolha o campo para atualizar:")
                print("1. Temperatura")
                print("2. Umidade")
                print("3. Luz")
                print("4. Botão P")
                print("5. Botão K")
                print("6. Status do Relé")
                
                field_choice = input("Escolha o campo (1-6): ")
                field_map = {
                    '1': 'temperature',
                    '2': 'humidity',
                    '3': 'light',
                    '4': 'btn_p',
                    '5': 'btn_k',
                    '6': 'relay_status'
                }
                
                if field_choice in field_map:
                    value = input("Digite o novo valor: ")
                    db.update_reading(id, field_map[field_choice], float(value))
                else:
                    print("Opção inválida!")
                
            elif choice == '4':
                # Deletar um registro
                id = input("Digite o ID do registro a ser deletado: ")
                db.delete_reading(id)
                
            elif choice == '5':
                # Deletar todos os registros
                confirm = input("Tem certeza que deseja deletar todos os registros? (s/n): ")
                if confirm.lower() == 's':
                    db.delete_all_readings()
                
            elif choice == '6':
                # Sair
                print("Encerrando o programa...")
                break
                
            else:
                print("Opção inválida! Por favor, escolha uma opção entre 1 e 6.")
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")
    
    finally:
        db.disconnect()

if __name__ == "__main__":
    main()
