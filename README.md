# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Sistema de Irrigação Inteligente - FarmTech Solutions

## � Links Importantes
- [Simulação no Wokwi (Fase 3)](https://wokwi.com/projects/414593759570745345)
- [Simulação no Wokwi (Fase 4)](https://wokwi.com/projects/416913349974451201)
- [Guia de Instalação](docs/installation.md)
- [Documentação do Banco de Dados](docs/database.md)

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/in/gabemule/">Gabriel Mule Monteiro</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/company/inova-fusca">Lucas Gomes Moreira</a>

## 📜 Descrição

Este projeto é parte da Fase 3 do sistema de gestão agrícola da empresa FarmTech Solutions, focando na implementação de um sistema de irrigação inteligente que integra sensores físicos a uma plataforma digital.

O sistema realiza o monitoramento em tempo real das seguintes variáveis:
- Níveis de nutriente Fósforo (P) - simulado por botão
- Níveis de nutriente Potássio (K) - simulado por botão
- pH do solo - simulado por sensor LDR
- Umidade - utilizando sensor DHT22

O sistema automaticamente controla a irrigação (representada por um relé) baseado nas leituras dos sensores, garantindo condições ideais para o cultivo.

### Parâmetros de Irrigação

O sistema utiliza os seguintes parâmetros para controle da irrigação:

1. Condições de Umidade:
   - Mínima: 30% (evita solo muito seco)
   - Máxima: 80% (evita encharcamento)
   - Justificativa: Esta faixa mantém o solo úmido o suficiente para absorção de nutrientes sem risco de apodrecimento das raízes

2. Condições de Temperatura:
   - Mínima: 10°C (evita irrigação em temperaturas muito baixas)
   - Máxima: 50°C (evita evaporação excessiva)
   - Justificativa: Irrigação nesta faixa de temperatura otimiza a absorção de água e nutrientes

3. Condições de pH (simulado pelo sensor LDR):
   - Faixa de leitura: 0-700 na escala do LDR
   - Justificativa: Embora seja uma simulação, representa a faixa de pH do solo onde a maioria das culturas se desenvolve bem

4. Nutrientes (simulados por botões):
   - Fósforo (P): Botão deve estar pressionado indicando presença
   - Potássio (K): Botão deve estar pressionado indicando presença
   - Justificativa: Simula a necessidade de presença mínima destes nutrientes para efetiva absorção da água

### Lógica de Ativação da Irrigação

O sistema ativa a irrigação (relé) APENAS quando TODAS as seguintes condições são atendidas:

1. Condições Ambientais:
   - Umidade está entre 30% e 80%
   - Temperatura está entre 10°C e 50°C
   - Leitura do LDR (pH simulado) está entre 0 e 700

2. Condições de Nutrientes:
   - Pelo menos um dos botões (P ou K) está pressionado
   - Justificativa: Indica presença mínima de nutrientes necessários

Esta lógica foi implementada para:
- Evitar desperdício de água
- Garantir condições ótimas de absorção
- Prevenir danos às culturas
- Otimizar o uso de recursos

## 📁 Estrutura de pastas

- <b>src</b>: Código-fonte do projeto
  - <b>main.cpp</b>: Implementação do sistema no ESP32
  - <b>database.py</b>: Código Python para operações CRUD no banco de dados

- <b>include</b>: Arquivos de cabeçalho

- <b>lib</b>: Bibliotecas do projeto

- <b>docs</b>: Documentação adicional
  - <b>installation.md</b>: Guia de instalação e configuração
  - <b>database.md</b>: Documentação do banco de dados

- <b>test</b>: Arquivos de teste

## � Funcionalidades

### Sistema de Banco de Dados

O sistema oferece um menu interativo com as seguintes operações:
- Criar - Inserir dados aleatórios
- Ler - Mostrar todos os registros
- Atualizar - Modificar um registro
- Deletar - Remover um registro
- Deletar - Remover todos os registros

### Formato dos Dados (JSON)

O sistema envia dados pela porta serial no formato:
```json
{
  "sensors": {
    "humidity": [valor],
    "temperature": [valor],
    "light": [valor]
  },
  "buttons": {
    "btnP": [true/false],
    "btnK": [true/false]
  },
  "validation": {
    "sensorsValid": [true/false],
    "buttonActive": [true/false]
  }
}
```

## 📺 Demonstração

[![Vídeo de Demonstração do Projeto](https://img.youtube.com/vi/stxOnMJhoHo/0.jpg)](https://youtu.be/stxOnMJhoHo)

Clique na imagem acima para assistir à demonstração completa do sistema, incluindo:
- Simulação do hardware no Wokwi
- Operações CRUD no banco de dados
- Interação com sensores e atuadores
- Validação das condições de irrigação

### Monitoramento com Serial Plotter
![Serial Plotter](assets/fase4-serial-plotter.png)
O gráfico do Serial Plotter mostra a variação em tempo real da temperatura, umidade e luminosidade, permitindo análise visual do comportamento do sistema.

### Sensores e Atuadores
![Temperatura](assets/fase4-temperatura.png)
![Umidade](assets/fase4-umidade.png)
![Luminosidade](assets/fase4-luminosidade.png)
![Circuito Completo](assets/fase4-full-circuit-overview.png)
![Sistema em Operação](assets/fase4-button-pressed-conditions-met.png)

### Dashboard Interativo
![Dashboard](assets/FarmTech-Solutions-Dashboard.png)
Interface Streamlit com visualização em tempo real, análises e previsões do modelo ML.

## 🗃 Histórico de lançamentos

* 0.1.0 - 25/03/2024
    * Implementação inicial do sistema de irrigação inteligente
    * Monitoramento de sensores simulados (P, K, pH, umidade)
    * Sistema de validação de condições
    * Integração com banco de dados (operações CRUD)
    * Saída formatada em JSON

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/">MODELO GIT FIAP por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
