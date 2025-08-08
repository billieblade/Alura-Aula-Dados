import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Funções Utilitárias ---
@st.cache_data
def carregar_dados():
    url = "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
    return pd.read_csv(url)

@st.cache_data
def converter_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def aplicar_filtros(df):
    st.sidebar.header("🔍 Filtros")

    anos = st.sidebar.multiselect("Ano", sorted(df["ano"].unique()), default=sorted(df["ano"].unique()))
    senioridades = st.sidebar.multiselect("Senioridade", sorted(df["senioridade"].unique()), default=sorted(df["senioridade"].unique()))
    contratos = st.sidebar.multiselect("Tipo de Contrato", sorted(df["contrato"].unique()), default=sorted(df["contrato"].unique()))
    tamanhos = st.sidebar.multiselect("Tamanho da Empresa", sorted(df["tamanho_empresa"].unique()), default=sorted(df["tamanho_empresa"].unique()))

    df_filtrado = df[
        (df["ano"].isin(anos)) &
        (df["senioridade"].isin(senioridades)) &
        (df["contrato"].isin(contratos)) &
        (df["tamanho_empresa"].isin(tamanhos))
    ]

    return df_filtrado

def exibir_kpis(df):
    st.subheader("📊 Métricas gerais (Salário anual em USD)")

    salario_medio = df['usd'].mean()
    salario_maximo = df['usd'].max()
    total_registros = df.shape[0]
    cargo_mais_frequente = df['cargo'].mode()[0] if not df['cargo'].mode().empty else "N/A"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Salário médio", f"${salario_medio:,.0f}")
    col2.metric("📈 Salário máximo", f"${salario_maximo:,.0f}")
    col3.metric("📄 Total de registros", f"{total_registros:,}")
    col4.metric("👔 Cargo mais frequente", cargo_mais_frequente)

    st.markdown("---")

def exibir_graficos(df):
    st.subheader("📉 Análises Visuais")

    col1, col2 = st.columns(2)
    with col1:
        top_cargos = df.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        fig_cargos = px.bar(
            top_cargos, x='usd', y='cargo', orientation='h',
            title="Top 10 Cargos por Salário Médio",
            labels={'usd': 'Salário Médio (USD)', 'cargo': ''}
        )
        fig_cargos.update_layout(title_x=0.1)
        st.plotly_chart(fig_cargos, use_container_width=True)

    with col2:
        fig_hist = px.histogram(
            df, x='usd', nbins=30,
            title="Distribuição de Salários Anuais",
            labels={'usd': 'Salário (USD)'}
        )
        fig_hist.update_layout(title_x=0.1)
        st.plotly_chart(fig_hist, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        remoto = df['remoto'].value_counts().reset_index()
        remoto.columns = ['Tipo de Trabalho', 'Quantidade']
        fig_remoto = px.pie(
            remoto, names='Tipo de Trabalho', values='Quantidade',
            title="Distribuição dos Tipos de Trabalho", hole=0.5
        )
        fig_remoto.update_traces(textinfo='percent+label')
        fig_remoto.update_layout(title_x=0.1)
        st.plotly_chart(fig_remoto, use_container_width=True)

    with col4:
        df_ds = df[df['cargo'] == 'Data Scientist']
        media_por_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        fig_mapa = px.choropleth(
            media_por_pais, locations='residencia_iso3', color='usd',
            color_continuous_scale='rdylgn',
            title='Salário Médio de Cientistas de Dados por País',
            labels={'usd': 'Salário Médio (USD)'}
        )
        fig_mapa.update_layout(title_x=0.1)
        st.plotly_chart(fig_mapa, use_container_width=True)

def exibir_dados(df):
    with st.expander("🔍 Ver dados detalhados"):
        st.dataframe(df)

    csv = converter_csv(df)
    st.download_button(
        label="⬇️ Baixar dados como CSV",
        data=csv,
        file_name="dados_filtrados.csv",
        mime="text/csv"
    )

# --- App Principal ---
def main():
    st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
    st.markdown("Explore os salários de profissionais da área de dados com base em diversos filtros.")

    df = carregar_dados()
    df_filtrado = aplicar_filtros(df)

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros aplicados.")
        st.stop()

    exibir_kpis(df_filtrado)
    exibir_graficos(df_filtrado)
    exibir_dados(df_filtrado)

if __name__ == "__main__":
    main()
