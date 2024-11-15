# Documentação do Sistema de Banco de Dados

## Visão Geral
O sistema de banco de dados foi implementado para armazenar e gerenciar dados dos sensores do sistema de irrigação inteligente. Utilizamos Oracle como SGBD e Python com cx_Oracle para as operações de banco de dados.

## Configuração do Ambiente

### 1. Pré-requisitos
- Python 3.8 ou superior
- Oracle Instant Client 23.3
- Ambiente virtual Python (venv)
- Acesso ao banco de dados Oracle FIAP

### 2. Instalação das Dependências

```bash
# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install python-dotenv cx_Oracle
```

### 3. Configuração do Oracle Instant Client

Configure o arquivo .env:
```env
# Configurações do banco de dados Oracle
DB_USER=rm560586
DB_PASSWORD=080386
DB_DSN=oracle.fiap.com.br:1521/ORCL

# Path do Oracle Instant Client
ORACLE_HOME=/Users/$USER/Downloads/instantclient_23_3
```

## Executando o Sistema

```bash
ORACLE_HOME=/Users/$USER/Downloads/instantclient_23_3 DYLD_LIBRARY_PATH=/Users/$USER/Downloads/instantclient_23_3 python src/database.py
```

## Menu de Operações

O sistema oferece um menu interativo com as seguintes opções:

1. **Criar - Inserir dados aleatórios**
   - Gera e insere dados aleatórios simulando leituras dos sensores
   - Valores dentro dos ranges definidos para cada sensor

2. **Ler - Mostrar todos os registros**
   - Lista todos os registros armazenados
   - Exibe informações detalhadas de cada leitura

3. **Atualizar - Modificar um registro**
   - Permite atualizar valores específicos de um registro
   - Campos disponíveis: temperatura, umidade, luz, botões P/K, relé

4. **Deletar - Remover um registro**
   - Remove um registro específico pelo ID

5. **Deletar - Remover todos os registros**
   - Limpa todos os dados da tabela
   - Solicita confirmação antes de executar

6. **Sair**
   - Encerra o programa
   - Fecha a conexão com o banco de dados

## Estrutura do Banco de Dados

### Tabela: sensor_data
| Coluna        | Tipo      | Descrição                    |
|---------------|-----------|------------------------------|
| id            | NUMBER    | ID único (auto-incremento)   |
| timestamp     | TIMESTAMP | Data/hora da leitura         |
| humidity      | NUMBER    | Umidade (%)                  |
| temperature   | NUMBER    | Temperatura (°C)             |
| light         | NUMBER    | Luminosidade/pH (0-700)      |
| btn_p         | NUMBER(1) | Estado do botão P (0/1)      |
| btn_k         | NUMBER(1) | Estado do botão K (0/1)      |
| relay_status  | NUMBER(1) | Estado do relé (0/1)         |

## Ranges dos Sensores

- Temperatura: 10°C a 50°C
- Umidade: 30% a 80%
- Luz (pH): 0 a 700
- Botões (P/K): 0 ou 1 (desligado/ligado)
- Relé: 0 ou 1 (desligado/ligado)

## Troubleshooting

### Erro DPI-1047
Se encontrar o erro "Cannot locate a 64-bit Oracle Client library":
1. Verifique se o ORACLE_HOME está correto no .env
2. Use o método de execução com variáveis de ambiente
3. Verifique se libclntsh.dylib existe no diretório do Instant Client

### Erro de Conexão
1. Verifique as credenciais no .env
2. Confirme acesso à rede FIAP
3. Verifique se o serviço Oracle está acessível
