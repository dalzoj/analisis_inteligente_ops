from src.core import data_loader, prompt_builder
from src.insights import correlation, anomaly, trend, benchmark
from src.llm import llm_client

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
        lines.append("ANOMALIAS:")
        for f in all_findings["anomalies"]:
            lines.append(
                f"  - {f['city']}, {f['zone']} ({f['country']}): {f['metric']} cambió "
                f"{f['change_pct']}% ({f['direction']}) "
                f" desde la Semana No. {f['week_from']} a la Semana No. {f['week_to']}"
            )
    
    print('INFO: insights_service -> _format_findings_for_llm -> trends')  
    if all_findings["trends"]:
        lines.append("\n TENDENCIAS EN DETERIORO:")
        for f in all_findings["trends"]:
            lines.append(
                f"  - {f['zone']} ({f['country']}): {f['metric']} ha "
                f"{f['trend']} por {f['weeks_count']}+ semanas "
                f"(Desde {f['start_value']} hasta {f['end_value']})"
            )

    print('INFO: insights_service -> _format_findings_for_llm -> benchmarks')  
    if all_findings["benchmarks"]:
        lines.append("\nBENCHMARKING:")
        for f in all_findings["benchmarks"]:
            lines.append(
                f"  - {f['zone']} ({f['country']}, {f['zone_type']}): {f['metric']} "
                f"es {f['deviation_pct']}% por debajo de la mediana del grupo ({f['group_median']})"
            )
            print(
                f"  - {f['zone']} ({f['country']}, {f['zone_type']}): {f['metric']} "
                f"es {f['deviation_pct']}% por debajo de la mediana del grupo ({f['group_median']})"
            )
 
    return "\n".join(lines)

async def _create_llm_summary(insights_summary, country):
    print('INFO: insights_service -> _create_llm_summary')

    insights_prompt = prompt_builder.get_chat_prompt()

    user_message = (
        f"Estos son los hallazgos encontrados en el análisis:\n"
        f"{insights_summary}\n\n"
        f"Organizar la información según las instrucciones.\n\n"
    )

    if country:
        user_message = user_message + f'Información para el país de {country}'
    else:
        user_message = f'Información para todos los paises'

    #return await llm_client.basic_call(insights_prompt, user_message)


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

    print('proceso completo')

    insights_summary = _format_findings_for_llm(insights_findings)
    insights_summary = await _create_llm_summary(insights_summary, country)

    return {
        "answer": insights_summary['answer'],
        "model_name": insights_summary['model_name'],
        "tokens_in": insights_summary['tokens_in'],
        "tokens_out": insights_summary['tokens_out'],
    }