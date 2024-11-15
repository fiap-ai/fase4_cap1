# Guia de Instalação e Configuração

## 🔧 Pré-requisitos

1. VSCode com extensão PlatformIO
2. Python 3.8+
3. Oracle Instant Client 23.3
4. Conta no Wokwi.com

## 🚀 Getting Started

1. **Clone o Repositório**
   ```bash
   git clone [url-do-repositorio]
   cd [nome-do-projeto]
   ```

2. **Instale o Oracle Instant Client**
   - Baixe o Oracle Instant Client 23.3 Basic Package para seu sistema:
     - [Download Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client/downloads.html)
   - Extraia para sua pasta Downloads:
     ```bash
     cd ~/Downloads
     unzip instantclient-basic-macos.zip  # ou seu arquivo correspondente
     ```

3. **Configure o Ambiente Python**
   ```bash
   # Crie e ative o ambiente virtual
   python -m venv venv
   source venv/bin/activate  # No Windows: .\venv\Scripts\activate
   
   # Instale as dependências
   pip install -r requirements.txt
   ```

4. **Configure o Arquivo .env**
   ```env
   # Configurações do banco de dados Oracle
   DB_USER=seu_user
   DB_PASSWORD=sua_senha
   DB_DSN=oracle.fiap.com.br:1521/ORCL
   ORACLE_HOME=/Users/$USER/Downloads/instantclient_23_3
   ```

5. **Teste a Instalação**
   ```bash
   # Configure variáveis de ambiente
   export ORACLE_HOME=/Users/$USER/Downloads/instantclient_23_3
   export DYLD_LIBRARY_PATH=$ORACLE_HOME
   
   # Teste o Oracle Client
   python -c "import cx_Oracle; print(cx_Oracle.clientversion())"
   ```

## 🔌 Conexões do Hardware

### Componentes Necessários
- ESP32 DevKit
- Sensor DHT22 (umidade)
- Sensor LDR (simulando pH)
- 2x Botões push (simulando sensores P e K)
- LED
- Módulo Relé (sistema de irrigação)

### Pinagem
- DHT22 → Pino 22
- LDR → Pino 34 (Entrada Analógica)
- Botão P → Pino 18
- Botão K → Pino 19
- LED → Pino 23
- Relé → Pino 16

## 💻 Execução do Projeto

### ESP32 (Wokwi)

1. Acesse o [projeto no Wokwi](https://wokwi.com/projects/414593759570745345)
2. Clique em "Start" para iniciar a simulação
3. Interaja com os botões e observe as leituras dos sensores

### Sistema de Banco de Dados

1. Execute o script Python para operações CRUD:
   ```bash
   ORACLE_HOME=/Users/$USER/Downloads/instantclient_23_3 DYLD_LIBRARY_PATH=/Users/$USER/Downloads/instantclient_23_3 python src/database.py
   ```

2. Menu de Operações:
   - 1: Criar - Inserir dados aleatórios
   - 2: Ler - Mostrar todos os registros
   - 3: Atualizar - Modificar um registro
   - 4: Deletar - Remover um registro
   - 5: Deletar - Remover todos os registros
   - 6: Sair

## ⚠️ Troubleshooting

### Erro DPI-1047
Se encontrar o erro "Cannot locate a 64-bit Oracle Client library":
1. Verifique se o ORACLE_HOME está correto no .env
2. Use o método de execução com variáveis de ambiente
3. Verifique se libclntsh.dylib existe no diretório do Instant Client

### Erro de Conexão
1. Verifique as credenciais no .env
2. Confirme acesso à rede FIAP
3. Verifique se o serviço Oracle está acessível
