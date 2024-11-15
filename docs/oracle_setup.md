# Configuração do Oracle Instant Client no MacOS

## 1. Download do Oracle Instant Client
1. Acesse: https://www.oracle.com/database/technologies/instant-client/macos-intel-x86-downloads.html
2. Faça login na sua conta Oracle (crie uma se necessário)
3. Baixe "Basic Package (ZIP)" para MacOS ARM64 (M1/M2)

## 2. Instalação

```bash
# Criar diretório para o Instant Client
sudo mkdir -p /opt/oracle

# Mover para o diretório
cd /opt/oracle

# Extrair o arquivo baixado (ajuste o nome do arquivo conforme necessário)
sudo unzip ~/Downloads/instantclient-basic-macos.zip

# Criar links simbólicos necessários
cd /opt/oracle/instantclient_*
sudo ln -s libclntsh.dylib.* libclntsh.dylib
sudo ln -s libocci.dylib.* libocci.dylib
```

## 3. Configuração do Ambiente

Adicione estas linhas ao seu arquivo ~/.zshrc:

```bash
# Oracle Instant Client
export ORACLE_HOME=/opt/oracle/instantclient_19_8  # Ajuste a versão conforme necessário
export DYLD_LIBRARY_PATH=$ORACLE_HOME
export PATH=$ORACLE_HOME:$PATH
```

## 4. Verificação

```bash
# Recarregar configurações
source ~/.zshrc

# Verificar variáveis de ambiente
echo $ORACLE_HOME
echo $DYLD_LIBRARY_PATH

# Verificar arquivos
ls -l $ORACLE_HOME/libclntsh.dylib
```

## 5. Teste com Python

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Testar importação
python -c "import cx_Oracle; print(cx_Oracle.clientversion())"
