# 🚒 Dashboard de Acidentes com Motocicletas – Curitiba/PR

Dashboard interativo desenvolvido para o **Corpo de Bombeiros Militar do Paraná (CBMPR)** que analisa dados de acidentes com motocicletas em Curitiba no período de **01 de Abril de 2025 a 31 de Março de 2026**.

## 📊 Funcionalidades

- **Indicadores Gerais (KPIs)**: Total de ocorrências, vítimas, óbitos, horário de pico, distribuição por gênero e média de idade
- **Ranking de Bairros**: Top 20 bairros com maior número de ocorrências
- **Tipos de Lesão**: Distribuição em gráfico de rosca com classificação por gravidade
- **Pirâmide Etária**: Análise demográfica comparativa entre gêneros
- **Série Temporal**: Evolução de ocorrências ao longo dos meses
- **Mapa de Calor Interativo**: Visualização geográfica com filtros por data e horário
- **Detalhes por Bairro**: Popup com informações específicas de cada região

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Framework para criar aplicações web interativas
- **Plotly**: Gráficos interativos e responsivos
- **GeoPandas**: Processamento de dados geoespaciais
- **Pandas**: Manipulação e análise de dados
- **NumPy**: Computação numérica

## 📦 Instalação Local

### Pré-requisitos
- Python 3.8+
- pip ou conda

### Passos

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/dashboard-acidentes-motos.git
cd dashboard-acidentes-motos
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o dashboard:
```bash
streamlit run app.py
```

5. Acesse em seu navegador:
```
http://localhost:8501
```

## 📁 Estrutura do Projeto

```
dashboard-acidentes-motos/
├── app.py                              # Aplicação principal do Streamlit
├── Projeto_Final_Preenchido.csv        # Dataset com dados de acidentes
├── requirements.txt                    # Dependências do projeto
├── .streamlit/
│   └── config.toml                    # Configurações do Streamlit
└── README.md                           # Este arquivo
```

## 📊 Formato dos Dados

O arquivo CSV deve conter as seguintes colunas:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| num_ocorrencia | int | Número único da ocorrência |
| data | date | Data do acidente (formato: DD/MM/YYYY) |
| hora | time | Hora do acidente (formato: HH:MM:SS) |
| bairro | string | Nome do bairro em Curitiba |
| rua | string | Nome da rua |
| veiculo | string | Tipo/modelo da motocicleta |
| genero | string | Gênero da vítima (Masculino/Feminino) |
| idade | int | Idade da vítima |
| tipo_vitima | string | Tipo de vítima (Condutor/Passageiro) |
| lesao | string | Classificação da lesão (1-Leve, 2-Grave s/risco, 3-Grave c/risco, 4-Óbito, Ilesa) |

## 🎨 Paleta de Cores

A aplicação segue o **Manual de Identidade Visual CBMPR 2024**:

- **Navy**: `#06273F` - Cor primária
- **Red**: `#D43439` - Cor de destaque
- **Yellow**: `#FFCD28` - Lesões leves
- **Gray Dark**: `#606062` - Lesões graves
- **Gray Light**: `#A39F9B` - Lesões leves/ilesas
- **White**: `#FEFEFE` - Fundo dos cards
- **Black**: `#373435` - Óbitos
- **Background**: `#F0F2F5` - Fundo da página

## 🚀 Deploy no Streamlit Cloud

1. Faça push do repositório para GitHub
2. Acesse [Streamlit Cloud](https://streamlit.io/cloud)
3. Clique em "New app" e selecione seu repositório
4. Configure:
   - **Repository**: seu-usuario/dashboard-acidentes-motos
   - **Branch**: main
   - **Main file path**: app.py
5. Clique em "Deploy"

Seu dashboard estará disponível em: `https://dashboard-acidentes-motos.streamlit.app`

## 📈 Filtros Interativos

- **Filtro de Data**: Selecione o intervalo de datas desejado
- **Filtro de Horário**: Escolha a faixa de horário (0-23h)
- **Seletor de Bairro**: Visualize detalhes específicos de cada região

## 🔄 Atualização de Dados

Para atualizar os dados do dashboard:

1. Substitua o arquivo `Projeto_Final_Preenchido.csv` com novos dados
2. Faça commit e push para GitHub
3. O Streamlit Cloud fará redeploy automaticamente

## 📝 Notas Importantes

- O arquivo CSV deve estar no mesmo diretório que `app.py`
- Os nomes dos bairros devem estar em **MAIÚSCULAS**
- As datas devem estar no formato `DD/MM/YYYY`
- O GeoJSON dos bairros é carregado automaticamente de repositórios públicos

## 🤝 Contribuições

Sugestões de melhorias e correções são bem-vindas! Abra uma issue ou pull request.

## 📄 Licença

Este projeto é desenvolvido para o Corpo de Bombeiros Militar do Paraná.

## 📞 Suporte

Para dúvidas ou problemas, entre em contato com a equipe de desenvolvimento.

---

**Desenvolvido com ❤️ para o CBMPR**
