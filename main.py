#%%
import streamlit as st
import pandas as pd
# %%
# crio um dataframe a partir da tabela
table = pd.read_excel('agrupado.xlsx', 'Tabela1') 

#Organizo as colunas e as linhas da forma correta

#Nomeio as colunas da forma correta
table.columns=table.iloc[0] 

#Coloco os itens a partir das linhas certas
table = table.iloc[1:]
# %%
# A partir daqui, crio os resumos aos 3 principais itens contados.

# Ar condicionado
arcond = table.loc[table['TIPO DO EQUIPAMENTO']=='AR CONDICIONADO'] #primeiro filtro os itens pelo tipo
arcond = pd.DataFrame(arcond.groupby('VILLA')['CÓDIGO DO EQUIPAMENTO'].count().reset_index()) #Agrupo e conto quantos tem em cada villa


# Aquecedores: Boiler e Cardal

# Cardal
cardal = table.loc[table['TIPO DO EQUIPAMENTO'] == 'CARDAL']  # primeiro filtro os itens pelo tipo
cardal = cardal.groupby('VILLA')['CÓDIGO DO EQUIPAMENTO'].count()  # agrupo e conto quantos tem em cada villa


# Boiler
boiler = table.loc[table['TIPO DO EQUIPAMENTO'] == 'BOILER']  # primeiro filtro os itens pelo tipo
boiler = boiler.groupby('VILLA')['CÓDIGO DO EQUIPAMENTO'].count()  # agrupo e conto quantos tem em cada villa

#junto os dois

aquecedores = pd.concat([boiler, cardal], axis=1) #pego e junto os dois itens a partir do index villa com o concat

aquecedores.columns = ['BOILER', 'CARDAL'] #renomeio as colunas
aquecedores = aquecedores.reset_index()#ajusto a villa como coluna


# Bombas
bomba = table.loc[table['TIPO DO EQUIPAMENTO'] == 'BOMBAS']
bomba = pd.DataFrame(bomba.groupby('VILLA')['CÓDIGO DO EQUIPAMENTO'].count()).reset_index()



#%%
#%%
#Layout streamlit abaixo

st.set_page_config(page_title="Resumo de Equipamentos", layout="wide", page_icon="📋")

# CSS customizado pra deixar o visual mais profissional
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px 20px;
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #555;
    }
    [data-testid="stMetricValue"] {
        color: #1f77b4;
    }
    div.stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    div.stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 16px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Resumo de Equipamentos por Villa")
st.caption("Painel de acompanhamento de equipamentos cadastrados")
st.divider()

# Pego a lista de todas as villas presentes na tabela original,
# pra montar o filtro de forma dinâmica (sem precisar digitar manualmente)
villas_disponiveis = sorted(table['VILLA'].dropna().unique())

# Divido a tela em duas colunas: uma estreita pro filtro (fica fixo ao lado),
# outra larga pras abas com o conteúdo — troquei a sidebar por isso
col_filtro, col_conteudo = st.columns([1, 4])

with col_filtro:
    st.markdown("#### 🔍 Filtros")
    villas_selecionadas = st.multiselect(
        "Villa",
        options=villas_disponiveis,
        default=villas_disponiveis  # começa com todas marcadas
    )

# Função auxiliar pra aplicar o filtro de villa em cada resumo
# (arcond, aquecedores e bomba são todos DataFrames com VILLA como coluna)
def filtrar_por_villa(df, coluna_villa='VILLA'):
    return df[df[coluna_villa].isin(villas_selecionadas)]

# Aplico o filtro em cada um dos resumos
arcond_filtrado = filtrar_por_villa(arcond)
aquecedores_filtrado = filtrar_por_villa(aquecedores)
bomba_filtrado = filtrar_por_villa(bomba)

with col_conteudo:
    # Crio as 4 abas: os 3 tipos fixos + a aba de filtragem dinâmica
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "❄️ Ar Condicionado", "🔥 Aquecedores", "💧 Bombas", "🔎 Filtro Dinâmico", "🏠 Equipamento por Área"
])

    with tab1:
        st.subheader("Ar Condicionado por Villa")

        col_tabela, col_grafico = st.columns([1, 1.5])

        with col_tabela:
            st.dataframe(arcond_filtrado, use_container_width=True, hide_index=True)
            st.metric("Total de unidades", int(arcond_filtrado['CÓDIGO DO EQUIPAMENTO'].sum()))

        with col_grafico:
            st.bar_chart(
                arcond_filtrado.set_index('VILLA')['CÓDIGO DO EQUIPAMENTO'],
                use_container_width=True,
                color="#1f77b4"
            )

    with tab2:
        st.subheader("Aquecedores (Boiler e Cardal) por Villa")

        col_tabela, col_grafico = st.columns([1, 1.5])

        with col_tabela:
            st.dataframe(aquecedores_filtrado, use_container_width=True, hide_index=True)
            col1, col2 = st.columns(2)
            col1.metric("Total Boiler", int(aquecedores_filtrado['BOILER'].sum()))
            col2.metric("Total Cardal", int(aquecedores_filtrado['CARDAL'].sum()))

        with col_grafico:
            st.bar_chart(
                aquecedores_filtrado.set_index('VILLA')[['BOILER', 'CARDAL']],
                use_container_width=True
            )

    with tab3:
        st.subheader("Bombas por Villa")

        col_tabela, col_grafico = st.columns([1, 1.5])

        with col_tabela:
            st.dataframe(bomba_filtrado, use_container_width=True, hide_index=True)
            st.metric("Total de unidades", int(bomba_filtrado['CÓDIGO DO EQUIPAMENTO'].sum()))

        with col_grafico:
            st.bar_chart(
                bomba_filtrado.set_index('VILLA')['CÓDIGO DO EQUIPAMENTO'],
                use_container_width=True,
                color="#1f77b4"
            )

    with tab4:
        st.subheader("Filtragem Dinâmica por Tipo de Equipamento")
        st.caption("Escolha um ou mais tipos para comparar entre villas")

        # Pego todos os tipos de equipamento disponíveis na tabela original,
        # pra montar o seletor de forma dinâmica
        tipos_disponiveis = sorted(table['TIPO DO EQUIPAMENTO'].dropna().unique())

        tipos_selecionados = st.multiselect(
            "Tipo(s) de equipamento",
            options=tipos_disponiveis,
            default=tipos_disponiveis[0] if tipos_disponiveis else []
        )

        if not tipos_selecionados:
            # Aviso amigável caso o usuário limpe a seleção
            st.info("Selecione ao menos um tipo de equipamento para ver o resumo.")
        else:
            # Filtro a tabela original pelos tipos escolhidos (agora .isin, pois é lista)
            # e pela villa selecionada no filtro lateral
            dinamico = table.loc[
                (table['TIPO DO EQUIPAMENTO'].isin(tipos_selecionados)) &
                (table['VILLA'].isin(villas_selecionadas))
            ]

            # Agrupo por Villa e Tipo, contando os códigos de equipamento
            resumo_dinamico = (
                dinamico.groupby(['VILLA', 'TIPO DO EQUIPAMENTO'])['CÓDIGO DO EQUIPAMENTO']
                .count()
                .reset_index()
                .rename(columns={'CÓDIGO DO EQUIPAMENTO': 'QUANTIDADE'})
            )

            col_tabela, col_grafico = st.columns([1, 1.5])

            with col_tabela:
                st.dataframe(resumo_dinamico, use_container_width=True, hide_index=True)
                st.metric("Total de unidades (seleção)", int(resumo_dinamico['QUANTIDADE'].sum()))

            with col_grafico:
                # Pivoto pra ter Villa no index e cada TIPO como uma coluna própria —
                # é isso que faz o bar_chart desenhar uma barra separada por tipo
                pivot_dinamico = resumo_dinamico.pivot(
                    index='VILLA', columns='TIPO DO EQUIPAMENTO', values='QUANTIDADE'
                ).fillna(0)

                # stack=False é o que faz as barras ficarem lado a lado (agrupadas)
                # em vez de empilhadas umas sobre as outras — cada tipo vira uma
                # barra própria, com cor própria, dentro de cada villa
                st.bar_chart(pivot_dinamico, use_container_width=True, stack=False)
    with tab5:
        st.subheader("Equipamento por Área")
        st.caption(
            "Selecione uma villa, os tipos de equipamento e as áreas "
            "para gerar o comparativo."
        )

        # =========================================================
        # FILTROS
        # =========================================================

        col1, col2, col3 = st.columns([1, 1.5, 1.5])

        with col1:
            villa_selecionada = st.selectbox(
                "Villa",
                options=villas_disponiveis,
                index=0
            )

        tipos_disponiveis_area = sorted(
            table['TIPO DO EQUIPAMENTO'].dropna().unique()
        )

        with col2:
            tipos_selecionados_area = st.multiselect(
                "Tipo(s) de equipamento",
                options=tipos_disponiveis_area,
                default=tipos_disponiveis_area[1]
                if tipos_disponiveis_area else []
            )

            areas_disponiveis = sorted(
                table.loc[
                    (table['VILLA'] == villa_selecionada) &
                    (table['TIPO DO EQUIPAMENTO'].isin(tipos_selecionados_area)),
                    'AREA'
                ].dropna().unique()
            )

            with col3:
                areas_selecionadas = st.multiselect(
                    "Área(s)",
                    options=areas_disponiveis,
                    default=areas_disponiveis
                )
        st.divider()

        # =========================================================
        # RESULTADO
        # =========================================================

        if not tipos_selecionados_area or not areas_selecionadas:

            st.info(
                "Selecione ao menos um tipo de equipamento "
                "e uma área para visualizar o comparativo."
            )

        else:

            equip_area = table.loc[
                (table['VILLA'] == villa_selecionada) &
                (table['TIPO DO EQUIPAMENTO'].isin(tipos_selecionados_area)) &
                (table['AREA'].isin(areas_selecionadas))
            ]

            resumo_area = (
                equip_area
                .groupby(
                    ['AREA', 'TIPO DO EQUIPAMENTO']
                )['CÓDIGO DO EQUIPAMENTO']
                .count()
                .reset_index()
                .rename(
                    columns={
                        'CÓDIGO DO EQUIPAMENTO': 'QUANTIDADE'
                    }
                )
            )

            # =====================================================
            # TABELA
            # =====================================================

            st.markdown("### Resumo por área")

            st.dataframe(
                resumo_area.sort_values(
                    ['AREA', 'TIPO DO EQUIPAMENTO']
                ),
                width="stretch",
                hide_index=True,
                column_config={
                    "AREA": st.column_config.TextColumn(
                        "Área",
                        width="medium"
                    ),
                    "TIPO DO EQUIPAMENTO": st.column_config.TextColumn(
                        "Tipo de equipamento",
                        width="medium"
                    ),
                    "QUANTIDADE": st.column_config.NumberColumn(
                        "Quantidade",
                        width="small",
                        format="%d"
                    )
                }
            )

            # =====================================================
            # GRÁFICO
            # =====================================================

            st.markdown("### Comparativo por área")

            import altair as alt

            grafico = alt.Chart(resumo_area).mark_bar(
                size=18
            ).encode(
                x=alt.X(
                    "AREA:N",
                    title=None,
                    axis=alt.Axis(
                        labelAngle=0,
                        labelLimit=150
                    )
                ),
                y=alt.Y(
                    "QUANTIDADE:Q",
                    title="Quantidade",
                    scale=alt.Scale(
                        zero=True
                    )
                ),
                color=alt.Color(
                    "TIPO DO EQUIPAMENTO:N",
                    title="Tipo de equipamento",
                    legend=alt.Legend(
                        orient="top",
                        direction="horizontal",
                        columns=3,
                        labelLimit=200
                    )
                ),
                tooltip=[
                    alt.Tooltip("AREA:N", title="Área"),
                    alt.Tooltip(
                        "TIPO DO EQUIPAMENTO:N",
                        title="Equipamento"
                    ),
                    alt.Tooltip(
                        "QUANTIDADE:Q",
                        title="Quantidade"
                    )
                ]
            ).properties(
                height=350
            )

            st.altair_chart(
                grafico,
                use_container_width=True
            )