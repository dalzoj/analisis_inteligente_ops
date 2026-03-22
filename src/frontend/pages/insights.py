import streamlit as st

from api_client import generate_insights

COUNTRIES = ["All", "AR", "BR", "CL", "CO", "CR", "EC", "MX", "PE", "UY"]

COUNTRY_NAMES = {
    "All": "🌎 Todos los países",
    "AR": "🇦🇷 Argentina",  "BR": "🇧🇷 Brasil",   "CL": "🇨🇱 Chile",
    "CO": "🇨🇴 Colombia",   "CR": "🇨🇷 Costa Rica", "EC": "🇪🇨 Ecuador",
    "MX": "🇲🇽 México",     "PE": "🇵🇪 Perú",       "UY": "🇺🇾 Uruguay",
}

ALL_METRICS = [
    "% PRO Users Who Breakeven",
    "% Restaurants Sessions With Optimal Assortment",
    "Gross Profit UE",
    "Lead Penetration",
    "MLTV Top Verticals Adoption",
    "Non-Pro PTC > OP",
    "Perfect Orders",
    "Pro Adoption (Last Week Status)",
    "Restaurants Markdowns / GMV",
    "Restaurants SS > ATC CVR",
    "Restaurants SST > SS CVR",
    "Retail SST > SS CVR",
    "Turbo Adoption",
]

ALL_GROUP_COLUMNS = ["ZONE_TYPE", "ZONE_PRIORITIZATION", "CITY"]

GROUP_COLUMN_LABELS = {
    "ZONE_TYPE":           "Tipo de zona (Wealthy / Non Wealthy)",
    "ZONE_PRIORITIZATION": "Priorización de zona",
    "CITY":                "Ciudad",
}

CATEGORY_COLORS = {
    "anomaly": "🔴",
    "trend": "🟡",
    "benchmark": "🔵",
    "correlation": "🟢",
    "opportunity": "🟣",
}


def _render_finding(finding):
    category = finding.get("category", "anomaly")
    icon = CATEGORY_COLORS.get(category, "⚪")
    title = finding.get("title", "")

    with st.expander(f"{icon} {title}"):
        st.markdown(finding.get("description", ""))

        zones = finding.get("zones_affected", [])
        if zones:
            st.markdown(f"**Zones affected:** {', '.join(zones)}")

        st.info(f"**Recomendación:** {finding.get('recommendation', '')}")


def render():
    st.title("📊 Reporte de Hallazgos")
    st.caption("El sistema analiza automáticamente los datos y genera un reporte ejecutivo con los insights más relevantes.")

    with st.expander("⚙️ Configuración de Reporte", expanded=True):

        col1, col2 = st.columns(2)

        with col1:
            selected_country = st.selectbox(
                "🌎 Filtrar por",
                options=COUNTRIES,
                format_func=lambda c: COUNTRY_NAMES.get(c, c),
                index=0,
                help="Seleccione un país específico o deje la opción 'Todos' para analizar todos los países.",
            )

        with col2:
            selected_group_columns = st.multiselect(
                "📐 Agrupamiento de Benchmark",
                options=ALL_GROUP_COLUMNS,
                default=["ZONE_TYPE", "CITY"],
                format_func=lambda c: GROUP_COLUMN_LABELS.get(c, c),
                help=(
                    "Dimensiones utilizadas para agrupar zonas para la comparación de referencia."
                    "Las zonas se comparan únicamente con otras zonas del mismo grupo."
                ),
            )

        selected_metrics = st.multiselect(
            "📈 Métricas a incluir",
            options=ALL_METRICS,
            default=[
                "Lead Penetration",
                "Perfect Orders",
                "Gross Profit UE",
                "Pro Adoption (Last Week Status)",
            ],
            help=(
                "Elige qué métricas analizar."
                "Déjelo en blanco para incluir TODAS las métricas disponibles (más lento pero más completo)."
            ),
        )

        if not selected_metrics:
            st.info(
                "No se ha seleccionado ninguna métrica: el informe incluirá **todas** las métricas disponibles. "
                "Esto puede llevar mucho más tiempo."
            )

    if st.button("🚀 Generar Reporte", type="primary"):

        country_param = None if selected_country == "All" else selected_country
        metrics_param = selected_metrics if selected_metrics else None
        group_columns_param = selected_group_columns if selected_group_columns else None

        with st.spinner("Realizando un análisis, esto puede tardar varios minutos..."):
            try:
                result = generate_insights(
                    country=country_param,
                    metrics=metrics_param,
                    group_columns=group_columns_param,
                )

                st.success("✅ Reporte Generado Correctamente")

                col_m, col_ti, col_to = st.columns(3)
                col_m.metric("Model", result.get("model_name", "—"))
                col_ti.metric("Tokens in", f'{result.get("tokens_in",  0):,}')
                col_to.metric("Tokens out", f'{result.get("tokens_out", 0):,}')

                st.markdown("---")

                answer = result.get("answer", "")

                if answer:
                    st.markdown(answer, unsafe_allow_html=False)
                    st.markdown("---")
                    st.download_button(
                        label="⬇️ Descargar como .md",
                        data=answer,
                        file_name=f"rappi_insights_{country_param or 'ALL'}.md",
                        mime="text/markdown",
                    )
                else:
                    summary  = result.get("executive_summary", "")
                    findings = result.get("findings", [])

                    if summary:
                        st.subheader("Resumen ejecutivo")
                        st.markdown(summary)

                    if findings:
                        st.subheader("Hallazgos detallados")
                        for finding in findings:
                            _render_finding(finding)
                    else:
                        st.info(
                            "No se detectaron hallazgos significativos para los filtros seleccionados."
                        )

            except Exception as error:
                st.error(f"No se pudo generar el informe:{error}")