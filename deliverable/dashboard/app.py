import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------------------------------------
# Configuração básica da página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Operation Helius – Resilience Dashboard",
    page_icon="🛰️",
    layout="wide",
)

st.title("🛰️ Operation Helius – Resilience Simulation Dashboard")
st.markdown(
    """
    Este painel resume os resultados da **Fase 3** da Operação Helius:  
    comparação da arquitetura **LEGACY** vs **RESILIENT** sob cenários de falha
    (outage regional, backpressure MQTT e drift de IA).
    """
)

# ---------------------------------------------------------
# Carregamento de dados
# ---------------------------------------------------------
DEFAULT_CSV_PATH = "deliverable/3_simulation_report.csv"

st.sidebar.header("⚙️ Configuração de Dados")

csv_path = st.sidebar.text_input(
    "Caminho do CSV de simulação",
    value=DEFAULT_CSV_PATH,
    help="Por padrão, usa deliverable/3_simulation_report.csv",
)

uploaded_file = st.sidebar.file_uploader(
    "Ou envie um CSV manualmente",
    type=["csv"],
    help="Opcional: substitui o caminho padrão se você enviar um arquivo.",
)

@st.cache_data
def load_data(path_or_file):
    try:
        if isinstance(path_or_file, str):
            if not os.path.exists(path_or_file):
                st.error(f"Arquivo CSV não encontrado em: `{path_or_file}`")
                return None
            # --- CORREÇÃO APLICADA ---
            df = pd.read_csv(path_or_file, sep=';')
        else:
            # --- CORREÇÃO APLICADA ---
            df = pd.read_csv(path_or_file, sep=';')
        
        # Opcional: Limpar espaços em branco dos nomes das colunas
        df.columns = df.columns.str.strip()
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar CSV: {e}")
        return None

if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    df = load_data(csv_path)

if df is None:
    st.stop()

st.sidebar.success("CSV carregado com sucesso!")

# ---------------------------------------------------------
# Inspeção mínima do schema (CORRIGIDO para nosso CSV)
# ---------------------------------------------------------
# Estas são as colunas exatas geradas pelo report.ipynb
expected_cols = [
    "scenario",
    "architecture",
    "run_id",
    "RTO_steps",
    "failed_nodes_count",
    "failed_critical_fraction",
    "max_queue_length",
    "time_queue_above_threshold",
    "avg_invalid_rate",
    "fallback_activation_ratio",
]

# Verifica se o DataFrame (df) realmente contém as colunas
missing_cols = [c for c in expected_cols if c not in df.columns]
if missing_cols:
    st.error(
        f"Erro Crítico de Schema. O CSV carregado não contém as colunas esperadas: {missing_cols}\n"
        f"Colunas encontradas: {list(df.columns)}"
    )
    st.stop() # Interrompe a execução se as colunas-chave estiverem faltando

# ---------------------------------------------------------
# Filtros interativos
# ---------------------------------------------------------
st.sidebar.header("🎛️ Filtros")

# Esta linha (antiga linha 97) agora é segura, pois verificamos as colunas acima
architectures_available = sorted(df["architecture"].unique())
arch_filter = st.sidebar.multiselect(
    "Arquiteturas",
    options=architectures_available,
    default=architectures_available,
)

scenarios_available = sorted(df["scenario"].unique())
scenario_filter = st.sidebar.multiselect(
    "Cenários",
    options=scenarios_available,
    default=scenarios_available,
)

df_filtered = df[
    (df["architecture"].isin(arch_filter))
    & (df["scenario"].isin(scenario_filter))
].copy()

if df_filtered.empty:
    st.warning("Nenhum dado após aplicação dos filtros.")
    st.stop()

# ---------------------------------------------------------
# KPIs principais (por arquitetura)
# ---------------------------------------------------------
st.subheader("📌 Indicadores de Resiliência (KPIs por Arquitetura)")

group_cols = ["architecture"]
agg_df = (
    df_filtered.groupby(group_cols)
    .agg(
        # Métricas Corrigidas (baseadas no CSV real)
        RTO_steps_mean=("RTO_steps", "mean"),
        failed_critical_fraction_mean=("failed_critical_fraction", "mean"),
        max_queue_mean=("max_queue_length", "mean"),
        time_queue_above_threshold_mean=("time_queue_above_threshold", "mean"),
        avg_invalid_rate_mean=("avg_invalid_rate", "mean"),
        fallback_activation_ratio_mean=("fallback_activation_ratio", "mean"),
        n_runs=("run_id", "nunique"),
    )
    .reset_index()
)

# Layout em colunas para KPIs
kpi_cols = st.columns(len(agg_df))

for i, arch in enumerate(agg_df["architecture"]):
    row = agg_df[agg_df["architecture"] == arch].iloc[0]
    col = kpi_cols[i % len(kpi_cols)]

    with col:
        st.markdown(f"### 🧱 Arquitetura: `{arch}`")
        st.metric(
            label="Fração Crítica de Falha (Média)",
            value=f"{row['failed_critical_fraction_mean']:.3f}",
            help="Fração de nós críticos (IA, Dados) que falharam. Menor é melhor."
        )
        st.metric(
            label="Backpressure – Máx. Fila (Msgs)",
            value=f"{row['max_queue_mean']:.1f}",
            help="Pico de backlog na simulação MQTT. Menor é melhor."
        )
        st.metric(
            label="Drift IA – Taxa Inválida (Vista pelo Cliente)",
            value=f"{row['avg_invalid_rate_mean']:.3f}",
            help="Taxa de erro de IA que chega ao cliente. Menor é melhor."
        )
        st.metric(
            label="Taxa de Ativação de Fallback",
            value=f"{row['fallback_activation_ratio_mean']:.3f}",
            help="Fração de vezes que a autocontenção foi ativada. Maior é melhor (em falha)."
        )
        st.caption(f"Execuções consideradas: {int(row['n_runs'])}")


# ---------------------------------------------------------
# Gráficos comparativos – Topologia / Backpressure / IA
# ---------------------------------------------------------
st.subheader("📊 Comparação de Métricas por Arquitetura e Cenário")

# Agregação por cenário
agg_df_scenario = (
    df_filtered.groupby(["architecture", "scenario"])
    .agg(
        failed_critical_fraction_mean=("failed_critical_fraction", "mean"),
        max_queue_mean=("max_queue_length", "mean"),
        avg_invalid_rate_mean=("avg_invalid_rate", "mean"),
        fallback_activation_ratio_mean=("fallback_activation_ratio", "mean"),
    )
    .reset_index()
)


metric_options = {
    # Métricas Corrigidas (baseadas no CSV real)
    "Fração de Nós Críticos Falhos (Regional)": ("failed_critical_fraction_mean", "regional_outage"),
    "Pico da Fila de Ingestão (Backpressure)": ("max_queue_mean", "mqtt_backpressure"),
    "Taxa de Erro de IA (Drift)": ("avg_invalid_rate_mean", "ia_drift"),
    "Ativação de Fallback (IA Drift)": ("fallback_activation_ratio_mean", "ia_drift"),
}

metric_label = st.selectbox(
    "Métrica para comparação",
    options=list(metric_options.keys()),
    index=0,
)

metric_col, metric_scenario = metric_options[metric_label]

# Filtra o DF agregado para o cenário relevante da métrica
df_plot = agg_df_scenario[agg_df_scenario["scenario"] == metric_scenario]

fig_bar = px.bar(
    df_plot,
    x="architecture",
    y=metric_col,
    color="architecture",
    title=f"Comparação – {metric_label}",
    text_auto=".3f",
)
fig_bar.update_layout(xaxis_title="Arquitetura", yaxis_title=metric_label)

st.plotly_chart(fig_bar, use_container_width=True)


# ---------------------------------------------------------
# Distribuições – olhar para a variabilidade
# ---------------------------------------------------------
st.subheader("📈 Distribuições das Métricas (Monte Carlo)")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("**Distribuição: Fração Crítica de Falha (Cenário: Regional)**")
    fig_failed = px.histogram(
        df_filtered[df_filtered["scenario"] == "regional_outage"],
        x="failed_critical_fraction",
        color="architecture",
        nbins=30,
        marginal="box",
        opacity=0.7,
        title="Distribuição – Fração de Nós Críticos Falhos",
    )
    st.plotly_chart(fig_failed, use_container_width=True)

with col_right:
    st.markdown("**Distribuição: Pico da Fila (Cenário: Backpressure)**")
    fig_invalid = px.histogram(
        df_filtered[df_filtered["scenario"] == "mqtt_backpressure"],
        x="max_queue_length",
        color="architecture",
        nbins=30,
        marginal="box",
        opacity=0.7,
        title="Distribuição – Pico Máximo da Fila de Ingestão",
    )
    st.plotly_chart(fig_invalid, use_container_width=True)


# ---------------------------------------------------------
# Resumo textual final (interpretativo)
# ---------------------------------------------------------
st.subheader("🧠 Resumo Interpretativo (Gerado a partir dos dados)")

def interpret_summary(agg_df: pd.DataFrame) -> str:
    lines = []
    if "legacy" in agg_df["architecture"].values and "resilient" in agg_df["architecture"].values:
        try:
            legacy = agg_df[agg_df["architecture"] == "legacy"].iloc[0]
            resilient = agg_df[agg_df["architecture"] == "resilient"].iloc[0]

            def pct_diff(a, b):
                if a == 0:
                    return np.inf # Divisão por zero se o legado for 0
                return abs(a - b) / a * 100.0

            dfail_crit = pct_diff(legacy["failed_critical_fraction_mean"], resilient["failed_critical_fraction_mean"])
            dqueue = pct_diff(legacy["max_queue_mean"], resilient["max_queue_mean"])
            dinvalid = pct_diff(legacy["avg_invalid_rate_mean"], resilient["avg_invalid_rate_mean"])
            
            lines.append(
                f"- A arquitetura **Resiliente** apresenta uma **redução de {dfail_crit:.1f}%** na fração média de nós *críticos* falhos durante um outage regional (Fase 1)."
            )
            lines.append(
                f"- Em cenários de *backpressure* (duplicação MQTT), o pico da fila de ingestão cai **{dqueue:.1f}%** na arquitetura Resiliente (devido ao Buffer Assíncrono e Circuit Breakers da Fase 2)."
            )
            lines.append(
                f"- Em relação ao *drift* de IA, a taxa de erro vista pelo cliente é reduzida em **{dinvalid:.1f}%** (devido ao Fail-Open e Validação da Fase 3)."
            )
        except Exception as e:
            lines.append(f"Erro ao gerar resumo: {e}")
    else:
        lines.append(
            "Os dados atuais incluem apenas uma arquitetura, portanto a análise comparativa "
            "entre legacy e resiliente não pode ser realizada."
        )

    return "\n".join(lines)


st.markdown(interpret_summary(agg_df))