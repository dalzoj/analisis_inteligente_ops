from src.backend.core import data_loader, prompt_builder
from src.backend.insights import correlation, anomaly, trend, benchmark
from src.backend.llm import llm_client

example = """
CORRELACIÓN ENTRE MÉTRICAS:
  - Restaurants SST > SS CVR and Retail SST > SS CVR tiene una dirección positiva correlacionada de 0.671

ANOMALIAS:
  - Pitalito, Pitalito (CO): Retail SST > SS CVR cambió 51.9% (mejora)  desde la Semana No. L2W_ROLL a la Semana No. L1W_ROLL

TENDENCIAS EN DETERIORO:
  - Bocagrande (CO): Retail SST > SS CVR ha incrementando por 4+ semanas (Desde 0.9319 hasta 0.9759)
  - Centro (CO): Retail SST > SS CVR ha incrementando por 4+ semanas (Desde 0.9206 hasta 0.9531)
  - Cuba (CO): Retail SST > SS CVR ha incrementando por 4+ semanas (Desde 0.9296 hasta 0.944)
  - Soledad (CO): Retail SST > SS CVR ha incrementando por 4+ semanas (Desde 0.854 hasta 0.8862)
  - Los molinos (CO): Retail SST > SS CVR ha incrementando por 4+ semanas (Desde 0.907 hasta 0.9267)
  - Mosquera - Funza (CO): Retail SST > SS CVR ha incrementando por 4+ semanas (Desde 0.8937 hasta 0.9107)
  - Norte (CO): Retail SST > SS CVR ha incrementando por 4+ semanas (Desde 0.937 hasta 0.9687)

BENCHMARKING:
  - [L0W_ROLL] Pasto Pucalpa (Pasto, CO): Retail SST > SS CVR está 51.84000015258789% bajo rendimiento de la mediana de la agrupación por (zona: 0.4417, mediana: 0.9171000123023987)
  - [L0W_ROLL] Facatativa (Facatativa, CO): Retail SST > SS CVR está 54.36000061035156% bajo rendimiento de la mediana de la agrupación por (zona: 0.4186, mediana: 0.9171000123023987)
  - [L1W_ROLL] Pasto Pucalpa (Pasto, CO): Retail SST > SS CVR está 59.849998474121094% bajo rendimiento de la mediana de la agrupación por (zona: 0.3667, mediana: 0.9132000207901001)
  - [L1W_ROLL] Facatativa (Facatativa, CO): Retail SST > SS CVR está 58.33000183105469% bajo rendimiento de la mediana de la agrupación por (zona: 0.3806, mediana: 0.9132000207901001)
  - [L2W_ROLL] Pitalito (Pitalito, CO): Retail SST > SS CVR está 60.66999816894531% bajo rendimiento de la mediana de la agrupación por (zona: 0.358, mediana: 0.910099983215332)
  - [L2W_ROLL] Facatativa (Facatativa, CO): Retail SST > SS CVR está 58.58000183105469% bajo rendimiento de la mediana de la agrupación por (zona: 0.377, mediana: 0.910099983215332)
"""

def _filter_by_country(df, country):
    print('INFO: insights_service -> _filter_by_country')

    if country:
        return df[df["COUNTRY"] == country.upper()]
    return df


def _filter_by_metrics(df, metrics):
    print('INFO: insights_service -> _filter_by_metrics')

    if metrics:
        return df[df["METRIC"].isin(metrics)]
    return df


def _format_findings_for_llm(all_findings):
    print('INFO: insights_service -> _format_findings_for_llm')

    lines = []

    print('INFO: insights_service -> _format_findings_for_llm -> correlations')
    if all_findings["correlations"]:
        lines.append("\nCORRELACIÓN ENTRE MÉTRICAS:")
        for f in all_findings["correlations"]:
            lines.append(
                f"  - {f['metric_a']} and {f['metric_b']} tiene una dirección "
                f"{f['direction']} correlacionada de {f['correlation']}"
            )

    print('INFO: insights_service -> _format_findings_for_llm -> anomalies')
    if all_findings["anomalies"]:
        lines.append("\nANOMALIAS:")
        for f in all_findings["anomalies"]:
            lines.append(
                f"  - {f['city']}, {f['zone']} ({f['country']}): {f['metric']} cambió "
                f"{f['change_pct']}% ({f['direction']}) "
                f" desde la Semana No. {f['week_from']} a la Semana No. {f['week_to']}"
            )
    
    print('INFO: insights_service -> _format_findings_for_llm -> trends')  
    if all_findings["trends"]:
        lines.append("\nTENDENCIAS EN DETERIORO:")
        for f in all_findings["trends"]:
            lines.append(
                f"  - {f['zone']} ({f['country']}): {f['metric']} ha "
                f"{f['trend']} por {f['weeks_count']}+ semanas "
                f"(Desde {f['start_value']} hasta {f['end_value']})"
            )

    print('INFO: insights_service -> _format_findings_for_llm -> benchmark')  
    if all_findings["benchmark"]:
        lines.append("\nBENCHMARKING:")
        for f in all_findings["benchmark"]:
            lines.append(
                f"  - [{f['week']}] {f['zone']} ({f['city']}, {f['country']}): "
                f"{f['metric']} está {abs(f['deviation_pct'])}% "
                f"{f['flag']} "
                f"de la mediana de la agrupación por "
                f"(zona: {f['zone_value']}, mediana: {f['group_median']})"
            )
    return "\n".join(lines)

async def _create_llm_summary(insights_summary, country):
    print('INFO: insights_service -> _create_llm_summary')

    insights_prompt = prompt_builder.get_code_insights_prompt()

    user_message = (
        f"Estos son los hallazgos encontrados en el análisis:\n"
        f"{insights_summary}\n\n"
        f"Organizar la información según las instrucciones.\n\n"
    )

    if country:
        user_message = user_message + f'Información para el país de {country}'
    else:
        user_message = f'Información para todos los paises'

    return await llm_client.basic_call(insights_prompt, user_message)


async def generate(country, metrics, group_columns):
    print('INFO: insights_service -> generate')

    print('country',country)
    print('metrics',metrics)
    print('group_columns',group_columns)

    df_metrics = data_loader.get_df_metrics()
    df_metrics = _filter_by_country(df_metrics, country)
    df_metrics = _filter_by_metrics(df_metrics, metrics)
        
    print('df_metrics',df_metrics['METRIC'].unique().tolist())

    insights_findings = {
        "correlations": correlation.detect(df_metrics),
        "anomalies": anomaly.detect(df_metrics),
        "trends": trend.detect(df_metrics),
        "benchmark": benchmark.detect(df_metrics, group_columns),
    }

    insights_summary = _format_findings_for_llm(insights_findings)
    print(example)
    #insights_summary = await _create_llm_summary(insights_summary, country)
    insights_summary = await _create_llm_summary(example, country)

    return {
        "answer": insights_summary['answer'],
        "model_name": insights_summary['model_name'],
        "tokens_in": insights_summary['tokens_in'],
        "tokens_out": insights_summary['tokens_out'],
    }