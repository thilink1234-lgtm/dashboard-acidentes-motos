"""
Dashboard - Acidentes de Motos | Corpo de Bombeiros Militar do Paraná
Período: 01/04/2025 a 31/03/2026
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json
import requests
import os
import geopandas as gpd

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Acidentes de Motos – CBMPR",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# PALETA DE CORES – Manual de Identidade Visual CBMPR 2024
# ─────────────────────────────────────────────
COR_NAVY    = "#06273F"
COR_RED     = "#D43439"
COR_YELLOW  = "#FFCD28"
COR_GRAY_D  = "#606062"
COR_GRAY_L  = "#A39F9B"
COR_WHITE   = "#FEFEFE"
COR_BLACK   = "#373435"
COR_BG      = "#F0F2F5"

LESAO_CORES = {
    "Leve":            COR_YELLOW,
    "Grave s/ risco":  COR_GRAY_D,
    "Grave c/ risco":  COR_RED,
    "Óbito":           COR_BLACK,
    "Ilesa":           COR_GRAY_L,
}

# ─────────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700;800;900&display=swap');

  html, body, [class*="css"] {{
      font-family: 'Barlow', sans-serif;
      background-color: {COR_BG};
  }}

  /* ── HEADER ── */
  .header-bar {{
      background: {COR_NAVY};
      padding: 18px 32px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 24px;
  }}
  .header-title {{
      color: {COR_WHITE};
      font-size: 22px;
      font-weight: 800;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin: 0;
  }}
  .header-sub {{
      color: {COR_GRAY_L};
      font-size: 12px;
      letter-spacing: 2px;
      text-transform: uppercase;
      margin: 4px 0 0 0;
  }}
  .header-badge {{
      background: {COR_RED};
      color: white;
      padding: 6px 18px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 1.5px;
      text-transform: uppercase;
  }}

  /* ── CARDS KPI ── */
  .kpi-card {{
      background: {COR_WHITE};
      border-radius: 12px;
      padding: 20px 22px;
      border-left: 5px solid {COR_RED};
      box-shadow: 0 2px 12px rgba(6,39,63,0.08);
      height: 110px;
      display: flex;
      flex-direction: column;
      justify-content: center;
  }}
  .kpi-label {{
      font-size: 11px;
      font-weight: 700;
      color: {COR_GRAY_D};
      text-transform: uppercase;
      letter-spacing: 1.2px;
      margin-bottom: 6px;
  }}
  .kpi-value {{
      font-size: 32px;
      font-weight: 900;
      color: {COR_NAVY};
      line-height: 1;
  }}
  .kpi-value.red   {{ color: {COR_RED}; }}
  .kpi-value.navy  {{ color: {COR_NAVY}; }}
  .kpi-sub {{
      font-size: 11px;
      color: {COR_GRAY_L};
      margin-top: 4px;
  }}

  /* ── SECTION TITLE ── */
  .section-title {{
      font-size: 13px;
      font-weight: 800;
      color: {COR_NAVY};
      text-transform: uppercase;
      letter-spacing: 2px;
      border-left: 4px solid {COR_RED};
      padding-left: 12px;
      margin: 24px 0 12px 0;
  }}

  /* ── CHART CARD ── */
  .chart-card {{
      background: {COR_WHITE};
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 12px rgba(6,39,63,0.08);
  }}

  /* ── POPUP BAIRRO ── */
  .bairro-popup {{
      background: {COR_WHITE};
      border-radius: 12px;
      padding: 20px 24px;
      border-top: 5px solid {COR_RED};
      box-shadow: 0 4px 20px rgba(6,39,63,0.15);
  }}
  .popup-title {{
      font-size: 16px;
      font-weight: 800;
      color: {COR_NAVY};
      text-transform: uppercase;
      margin-bottom: 14px;
  }}
  .popup-metric {{
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid {COR_BG};
      font-size: 13px;
  }}
  .popup-metric-label {{ color: {COR_GRAY_D}; font-weight: 600; }}
  .popup-metric-val   {{ color: {COR_NAVY};   font-weight: 800; }}

  /* ── FOOTER ── */
  .footer {{
      text-align: center;
      color: {COR_GRAY_L};
      font-size: 11px;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      padding: 20px 0 8px 0;
  }}

  /* Oculta menu e rodapé do Streamlit */
  #MainMenu, footer {{ visibility: hidden; }}
  .block-container {{ padding-top: 1.5rem; padding-bottom: 1rem; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CARGA E LIMPEZA DOS DADOS
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    # Aceita o CSV tanto no diretório local quanto na pasta de uploads
    paths = [
        "Projeto_Final_Preenchido__1_.csv",
        "Projeto_Final_Preenchido.csv",
        "/mnt/user-data/uploads/Projeto_Final_Preenchido__1_.csv",
        "/mnt/user-data/uploads/Projeto_Final_Preenchido.csv",
    ]
    df = None
    csv_path = None
    for p in paths:
        if os.path.exists(p):
            csv_path = p
            break
    if csv_path is None:
        st.error("Arquivo CSV não encontrado. Coloque 'Projeto_Final_Preenchido.csv' na mesma pasta do script.")
        st.stop()

    # Tentar carregar com diferentes delimitadores comuns
    delimiters = [';', ',', '\t'] # Ponto e vírgula, vírgula, tabulação
    for sep_char in delimiters:
        try:
            df = pd.read_csv(csv_path, encoding="latin1", sep=sep_char, engine="python")
            if df.shape[1] > 1: # Verificar se parece um DataFrame válido (ex: mais de uma coluna)
                break # Carregado com sucesso com este separador
            else: df = None # Não é um CSV multi-coluna válido, tentar próximo delimitador
        except Exception:
            df = None # Falha ao carregar, tentar próximo delimitador
    
    if df is None:
        st.error(f"Não foi possível carregar o arquivo CSV '{csv_path}' com os delimitadores esperados (;, , ou tab). Verifique o formato do arquivo.")
        st.stop()

    # Renomear colunas (encoding corrompido → nomes limpos)
    df.columns = [
        "num_ocorrencia", "data", "hora", "bairro",
        "rua", "veiculo", "genero", "idade",
        "tipo_vitima", "lesao",
    ]

    # Datas e horas
    df["data"]  = pd.to_datetime(df["data"], errors="coerce")
    df["hora"]  = pd.to_datetime(df["hora"], format="%H:%M:%S", errors="coerce").dt.time
    df["hora_h"] = pd.to_datetime(df["hora"].astype(str), format="%H:%M:%S", errors="coerce").dt.hour

    # Padronizar lesão
    def classifica_lesao(txt):
        if not isinstance(txt, str): return "Desconhecida"
        if "4"   in txt or "bito"  in txt.lower():                   return "Óbito"
        if "3"   in txt:                                              return "Grave c/ risco"
        if "2"   in txt:                                              return "Grave s/ risco"
        if "1"   in txt or "leve"  in txt.lower():                   return "Leve"
        if "lesa" in txt.lower():                                     return "Ilesa"
        return "Desconhecida"

    df["lesao_cat"] = df["lesao"].apply(classifica_lesao)

    # Faixa etária
    bins   = [0, 17, 24, 34, 44, 54, 64, 120]
    labels = ["0-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    df["faixa_etaria"] = pd.cut(df["idade"], bins=bins, labels=labels, right=True)

    # Mês
    df["mes"]     = df["data"].dt.to_period("M")
    df["mes_str"] = df["data"].dt.strftime("%b/%Y")

    # Bairro em maiúsculas e sem espaços extras
    df["bairro"] = df["bairro"].str.strip().str.upper()

    return df


df = load_data()


# ─────────────────────────────────────────────
# GEOJSON DOS BAIRROS DE CURITIBA
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_geojson():
    """
    Carrega o mapa dos bairros de Curitiba usando GeoPandas com múltiplas fontes de redundância.
    """
    import io
    local_paths = [
        "bairros_curitiba.geojson",
        "/mnt/user-data/uploads/bairros_curitiba.geojson",
    ]
    urls = [
        "https://raw.githubusercontent.com/gjeanmart/curitiba-neighborhoods/main/curitiba_neighborhoods.geojson",
        "https://raw.githubusercontent.com/andrelambert/curitiba-bairros/main/bairros.geojson"
    ]
    
    gdf = None
    
    # 1. Tentar carregar arquivo local (somente se tiver múltiplos bairros)
    for local in local_paths:
        if os.path.exists(local):
            try:
                candidate = gpd.read_file(local)
                if len(candidate) > 5:  # deve ter muitos bairros
                    gdf = candidate
                    break
            except: pass
    
    # 2. Se não houver local, tentar as URLs
    if gdf is None:
        for url in urls:
            try:
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    gdf = gpd.read_file(io.StringIO(r.text))
                    break
            except: continue

    if gdf is None:
        return None

    try:
        # Garantir que o CRS está em WGS84 (EPSG:4326) para o Plotly Mapbox
        if gdf.crs is None:
            gdf.set_crs(epsg=4326, inplace=True)
        elif gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs(epsg=4326)
            
        # Identificar a coluna de nome do bairro e normalizar para MAIÚSCULAS
        candidates = ["NOME", "nome", "NM_BAIRRO", "BAIRRO", "name"]
        name_col = next((c for c in candidates if c in gdf.columns), gdf.columns[0])
        gdf["BAIRRO_NORM"] = gdf[name_col].astype(str).str.strip().str.upper()
        return json.loads(gdf.to_json())
    except Exception:
        return None

geojson_data = load_geojson()


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
  <div>
    <p class="header-title">🚒 Acidentes com Motocicletas – Curitiba/PR</p>
    <p class="header-sub">Corpo de Bombeiros Militar do Paraná &nbsp;|&nbsp; 01 Abr 2025 – 31 Mar 2026</p>
  </div>
  <div class="header-badge">Relatório Operacional</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BLOCO 1 – CARDS KPI
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Indicadores Gerais</div>', unsafe_allow_html=True)

total_vitimas    = len(df)
total_ocorrencias = df["num_ocorrencia"].nunique()
obitos           = (df["lesao_cat"] == "Óbito").sum()
hora_pico        = int(df["hora_h"].mode()[0])
pct_masc         = df["genero"].value_counts(normalize=True).get("Masculino", 0) * 100
pct_fem          = 100 - pct_masc
media_idade      = df["idade"].mean()

cols_kpi = st.columns(6)
kpi_data = [
    ("Total de Ocorrências", f"{total_ocorrencias:,}".replace(",", "."),    "",       "navy"),
    ("Total de Vítimas",     f"{total_vitimas:,}".replace(",", "."),        "",       "navy"),
    ("Óbitos",               f"{obitos}",                                    "",       "red"),
    ("Horário de Pico",      f"{hora_pico:02d}h",                           "maior frequência", "navy"),
    ("Gênero Masculino",     f"{pct_masc:.1f}%",                            f"Feminino {pct_fem:.1f}%", "navy"),
    ("Média de Idade",       f"{media_idade:.1f} anos",                     "",       "navy"),
]

for col, (label, value, sub, color) in zip(cols_kpi, kpi_data):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value {color}">{value}</div>
          {'<div class="kpi-sub">' + sub + '</div>' if sub else ''}
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BLOCO 2 – RANKING DE OCORRÊNCIAS POR BAIRRO
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Ranking de Ocorrências por Bairro</div>', unsafe_allow_html=True)

bairro_rank = (
    df.groupby("bairro")["num_ocorrencia"]
    .nunique()
    .sort_values(ascending=True)
    .tail(20)
)

fig_bar = go.Figure(go.Bar(
    x=bairro_rank.values,
    y=bairro_rank.index,
    orientation="h",
    marker=dict(
        color=bairro_rank.values,
        colorscale=[
            [0.0, COR_GRAY_L],
            [0.5, COR_NAVY],
            [1.0, COR_RED],
        ],
        showscale=False,
    ),
    text=bairro_rank.values,
    textposition="outside",
    textfont=dict(size=11, color=COR_NAVY, family="Barlow"),
    hovertemplate="<b>%{y}</b><br>Ocorrências: %{x}<extra></extra>",
))

fig_bar.update_layout(
    height=520,
    margin=dict(l=10, r=60, t=10, b=10),
    plot_bgcolor=COR_WHITE,
    paper_bgcolor=COR_WHITE,
    xaxis=dict(
        showgrid=True, gridcolor="#ECECEC",
        showline=False, zeroline=False,
        tickfont=dict(family="Barlow", size=11, color=COR_GRAY_D),
    ),
    yaxis=dict(
        tickfont=dict(family="Barlow", size=11, color=COR_NAVY, weight=600),
        showgrid=False,
    ),
    font=dict(family="Barlow"),
)

st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.plotly_chart(fig_bar, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BLOCO 3 + 4 – ROSCA E PIRÂMIDE (lado a lado)
# ─────────────────────────────────────────────
col_donut, col_piramide = st.columns(2)

# ── BLOCO 3: Gráfico Rosca – Tipos de Lesão ──
with col_donut:
    st.markdown('<div class="section-title">Tipos de Lesão</div>', unsafe_allow_html=True)

    lesao_counts = df["lesao_cat"].value_counts()
    cores_rosca  = [LESAO_CORES.get(l, COR_GRAY_L) for l in lesao_counts.index]

    fig_donut = go.Figure(go.Pie(
        labels=lesao_counts.index,
        values=lesao_counts.values,
        hole=0.56,
        marker=dict(colors=cores_rosca, line=dict(color=COR_WHITE, width=3)),
        textinfo="percent",
        textfont=dict(size=13, family="Barlow", color=COR_WHITE),
        hovertemplate="<b>%{label}</b><br>Vítimas: %{value}<br>%{percent}<extra></extra>",
        direction="clockwise",
        sort=False,
    ))

    fig_donut.add_annotation(
        text=f"<b>{total_vitimas:,}</b><br><span style='font-size:11px'>Vítimas</span>".replace(",", "."),
        x=0.5, y=0.5,
        font=dict(size=20, family="Barlow", color=COR_NAVY),
        showarrow=False,
        align="center",
    )

    fig_donut.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor=COR_WHITE,
        paper_bgcolor=COR_WHITE,
        showlegend=True,
        legend=dict(
            orientation="v",
            font=dict(family="Barlow", size=12, color=COR_NAVY),
            bgcolor="rgba(0,0,0,0)",
        ),
        font=dict(family="Barlow"),
    )

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── BLOCO 4: Pirâmide Etária ──
with col_piramide:
    st.markdown('<div class="section-title">Pirâmide Etária por Gênero</div>', unsafe_allow_html=True)

    piramide = (
        df.groupby(["faixa_etaria", "genero"])
        .size()
        .reset_index(name="count")
    )
    masc = piramide[piramide["genero"] == "Masculino"].set_index("faixa_etaria")["count"]
    fem  = piramide[piramide["genero"] == "Feminino"].set_index("faixa_etaria")["count"]

    faixas = ["0-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    masc_vals = [-masc.get(f, 0) for f in faixas]
    fem_vals  = [ fem.get(f,  0) for f in faixas]

    fig_pir = go.Figure()
    fig_pir.add_trace(go.Bar(
        y=faixas,
        x=masc_vals,
        name="Masculino",
        orientation="h",
        marker_color=COR_NAVY,
        text=[abs(v) for v in masc_vals],
        textposition="inside",
        textfont=dict(color=COR_WHITE, size=11, family="Barlow"),
        hovertemplate="<b>Masculino</b> | %{y}<br>Vítimas: %{customdata}<extra></extra>",
        customdata=[abs(v) for v in masc_vals],
    ))
    fig_pir.add_trace(go.Bar(
        y=faixas,
        x=fem_vals,
        name="Feminino",
        orientation="h",
        marker_color=COR_RED,
        text=fem_vals,
        textposition="inside",
        textfont=dict(color=COR_WHITE, size=11, family="Barlow"),
        hovertemplate="<b>Feminino</b> | %{y}<br>Vítimas: %{x}<extra></extra>",
    ))

    max_val = max(max([abs(v) for v in masc_vals]), max(fem_vals)) + 30

    fig_pir.update_layout(
        barmode="overlay",
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor=COR_WHITE,
        paper_bgcolor=COR_WHITE,
        xaxis=dict(
            range=[-max_val, max_val],
            tickvals=[-max_val//2, 0, max_val//2],
            ticktext=[str(max_val//2), "0", str(max_val//2)],
            tickfont=dict(family="Barlow", size=11, color=COR_GRAY_D),
            showgrid=True, gridcolor="#ECECEC",
            zeroline=True, zerolinecolor=COR_GRAY_L,
        ),
        yaxis=dict(
            tickfont=dict(family="Barlow", size=11, color=COR_NAVY, weight=600),
            showgrid=False,
        ),
        legend=dict(
            orientation="h",
            x=0.5, xanchor="center",
            y=1.05,
            font=dict(family="Barlow", size=12, color=COR_NAVY),
            bgcolor="rgba(0,0,0,0)",
        ),
        font=dict(family="Barlow"),
    )

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(fig_pir, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BLOCO 5 – LINHA: OCORRÊNCIAS POR MÊS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Ocorrências por Mês</div>', unsafe_allow_html=True)

mensal = (
    df.groupby("mes")["num_ocorrencia"]
    .nunique()
    .reset_index()
)
mensal["mes_label"] = mensal["mes"].dt.strftime("%b/%Y")
mensal = mensal.sort_values("mes")

fig_linha = go.Figure()

# Área preenchida sob a linha
fig_linha.add_trace(go.Scatter(
    x=mensal["mes_label"],
    y=mensal["num_ocorrencia"],
    fill="tozeroy",
    fillcolor=f"rgba(6,39,63,0.08)",
    line=dict(color=COR_NAVY, width=0),
    showlegend=False,
    hoverinfo="skip",
))

# Linha principal
fig_linha.add_trace(go.Scatter(
    x=mensal["mes_label"],
    y=mensal["num_ocorrencia"],
    mode="lines+markers+text",
    line=dict(color=COR_NAVY, width=3),
    marker=dict(color=COR_RED, size=10, line=dict(color=COR_WHITE, width=2)),
    text=mensal["num_ocorrencia"],
    textposition="top center",
    textfont=dict(size=12, family="Barlow", color=COR_NAVY),
    name="Ocorrências",
    hovertemplate="<b>%{x}</b><br>Ocorrências: %{y}<extra></extra>",
))

fig_linha.update_layout(
    height=320,
    margin=dict(l=10, r=10, t=20, b=10),
    plot_bgcolor=COR_WHITE,
    paper_bgcolor=COR_WHITE,
    xaxis=dict(
        showgrid=False,
        tickfont=dict(family="Barlow", size=11, color=COR_GRAY_D),
        showline=True,
        linecolor=COR_GRAY_L,
    ),
    yaxis=dict(
        showgrid=True, gridcolor="#ECECEC",
        tickfont=dict(family="Barlow", size=11, color=COR_GRAY_D),
        zeroline=False,
    ),
    showlegend=False,
    font=dict(family="Barlow"),
)

st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.plotly_chart(fig_linha, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BLOCO 6 – MAPA DE CALOR DOS BAIRROS
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Mapa de Calor – Ocorrências por Bairro</div>', unsafe_allow_html=True)

# ── Filtros ──
col_f1, col_f2 = st.columns([1, 3])
with col_f1:
    min_data = df["data"].min().date()
    max_data = df["data"].max().date()
    data_sel = st.date_input(
        "📅 Filtrar por data",
        value=(min_data, max_data),
        min_value=min_data,
        max_value=max_data,
    )

with col_f2:
    hora_range = st.slider(
        "🕐 Filtrar por faixa de horário",
        min_value=0,
        max_value=23,
        value=(0, 23),
        format="%02d:00h",
    )

# ── Aplicar filtros ──
if isinstance(data_sel, (list, tuple)) and len(data_sel) == 2:
    dt_ini = pd.Timestamp(data_sel[0])
    dt_fim = pd.Timestamp(data_sel[1])
else:
    dt_ini = pd.Timestamp(min_data)
    dt_fim = pd.Timestamp(max_data)

mask = (
    (df["data"] >= dt_ini) &
    (df["data"] <= dt_fim) &
    (df["hora_h"] >= hora_range[0]) &
    (df["hora_h"] <= hora_range[1])
)
df_filt = df[mask]

# ── Ocorrências por bairro (filtrado) ──
ocorr_bairro = (
    df_filt.groupby("bairro")["num_ocorrencia"]
    .nunique()
    .reset_index(name="ocorrencias")
)

# ── Seletor de bairro para popup ──
bairros_lista = sorted(df_filt["bairro"].dropna().unique().tolist())

col_mapa, col_popup = st.columns([3, 1])

with col_popup:
    st.markdown("#### 🔍 Detalhes do Bairro")
    bairro_sel = st.selectbox(
        "Selecione um bairro:",
        ["— Selecione —"] + bairros_lista,
        key="bairro_sel",
    )

    if bairro_sel != "— Selecione —":
        df_b = df_filt[df_filt["bairro"] == bairro_sel]

        qtd_ocorr  = df_b["num_ocorrencia"].nunique()
        genero_cnt = df_b["genero"].value_counts()
        total_g    = genero_cnt.sum()
        pct_m_b    = genero_cnt.get("Masculino", 0) / total_g * 100 if total_g else 0
        pct_f_b    = genero_cnt.get("Feminino",  0) / total_g * 100 if total_g else 0
        lesao_cnt  = df_b["lesao_cat"].value_counts()

        lesao_html = "".join(
            f'<div class="popup-metric">'
            f'<span class="popup-metric-label">{l}</span>'
            f'<span class="popup-metric-val">{v}</span>'
            f'</div>'
            for l, v in lesao_cnt.items()
        )

        st.markdown(f"""
        <div class="bairro-popup">
          <div class="popup-title">📍 {bairro_sel}</div>
          <div class="popup-metric">
            <span class="popup-metric-label">Ocorrências</span>
            <span class="popup-metric-val">{qtd_ocorr}</span>
          </div>
          <div class="popup-metric">
            <span class="popup-metric-label">♂ Masculino</span>
            <span class="popup-metric-val">{pct_m_b:.1f}%</span>
          </div>
          <div class="popup-metric">
            <span class="popup-metric-label">♀ Feminino</span>
            <span class="popup-metric-val">{pct_f_b:.1f}%</span>
          </div>
          <hr style="border:none;border-top:1px solid #eee;margin:10px 0">
          <div style="font-size:11px;font-weight:800;color:{COR_GRAY_D};
                      text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">
            Lesões
          </div>
          {lesao_html}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Clique em um bairro ou selecione na lista ao lado.")

with col_mapa:
    if geojson_data is not None:
        # Merge com ocorrências
        fig_mapa = px.choropleth_mapbox(
            ocorr_bairro,
            geojson=geojson_data,
            locations="bairro",
            featureidkey="properties.BAIRRO_NORM",
            color="ocorrencias",
            color_continuous_scale=[
                [0.0,  "#FEFEFE"],
                [0.25, COR_GRAY_L],
                [0.5,  COR_NAVY],
                [0.75, "#8B1E20"],
                [1.0,  COR_RED],
            ],
            mapbox_style="carto-positron",
            zoom=10.5,
            center={"lat": -25.4284, "lon": -49.2733},
            opacity=0.75,
            labels={"ocorrencias": "Ocorrências"},
            hover_name="bairro",
            hover_data={"ocorrencias": True, "bairro": False},
        )

        fig_mapa.update_traces(
            marker_line_width=1.2,
            marker_line_color="white"
        )

        fig_mapa.update_layout(
            height=520,
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_colorbar=dict(
                title="Ocorr.",
                tickfont=dict(family="Barlow", size=11),
                title_font=dict(family="Barlow", size=12),
                thickness=14,
                len=0.6,
            ),
            font=dict(family="Barlow"),
        )

        st.plotly_chart(fig_mapa, use_container_width=True)

    else:
        # ── Fallback: Mapa de Calor Tabular (quando GeoJSON não disponível) ──
        st.warning(
            "⚠️ GeoJSON dos bairros não disponível. "
            "Coloque o arquivo **bairros_curitiba.geojson** na mesma pasta do script "
            "ou verifique a conexão com a internet."
        )
        st.markdown("##### Top 30 Bairros – Mapa de Calor Tabular")

        top30 = ocorr_bairro.sort_values("ocorrencias", ascending=False).head(30)
        max_o = top30["ocorrencias"].max()

        rows_html = ""
        for _, row in top30.iterrows():
            pct = row["ocorrencias"] / max_o
            r = int(212 * pct + 6 * (1 - pct))
            g = int(52  * pct + 39 * (1 - pct))
            b = int(57  * pct + 63 * (1 - pct))
            bg = f"rgb({r},{g},{b})"
            txt_col = COR_WHITE if pct > 0.4 else COR_NAVY
            rows_html += (
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:8px 14px;border-radius:6px;margin-bottom:4px;'
                f'background:{bg};">'
                f'<span style="color:{txt_col};font-weight:700;font-size:12px;">'
                f'{row["bairro"]}</span>'
                f'<span style="color:{txt_col};font-weight:900;font-size:14px;">'
                f'{int(row["ocorrencias"])}</span>'
                f'</div>'
            )

        st.markdown(
            f'<div style="max-height:520px;overflow-y:auto;padding:4px;">{rows_html}</div>',
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
  Corpo de Bombeiros Militar do Paraná &nbsp;·&nbsp; Nós Salvamos Vidas &nbsp;·&nbsp;
  Dados: 01/04/2025 – 31/03/2026
</div>
""", unsafe_allow_html=True)