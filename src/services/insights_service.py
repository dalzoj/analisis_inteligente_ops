from src.core import data_loader, prompt_builder
from src.insights import correlation, anomaly
from src.llm import llm_client

COUNTRY = None

def _filter_by_country(df, country):
    print('INFO: insights_service -> _filter_by_country')

    if country:
        return df[df["COUNTRY"] == country.upper()]
    return df


def _format_findings_for_llm(all_findings):
    print('INFO: insights_service -> _format_findings_for_llm')

    lines = []

    print('INFO: insights_service -> _format_findings_for_llm -> correlations')
    if all_findings["correlations"]:
        lines.append("\nMETRIC CORRELATIONS:")
        for f in all_findings["correlations"]:
            lines.append(
                f"  - {f['metric_a']} and {f['metric_b']} tiene una dirección "
                f"{f['direction']} correlacionada de {f['correlation']}"
            )

    print('INFO: insights_service -> _format_findings_for_llm -> anomalies')
    if all_findings["anomalies"]:
        lines.append("ANOMALIES:")
        for f in all_findings["anomalies"]:
            lines.append(
                f"  - {f['city']}, {f['zone']} ({f['country']}): {f['metric']} cambió "
                f"{f['change_pct']}% ({f['direction']}) "
                f" desde la Semana No. {f['week_from']} a la Semana No. {f['week_to']}"
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


async def generate(country):
    print('INFO: insights_service -> generate')

    print('country',country)

    df_metrics = data_loader.get_df_metrics()
    df_metrics = _filter_by_country(df_metrics, country)

    insights_findings = {
        "correlations": correlation.detect(df_metrics),
        "anomalies": anomaly.detect(df_metrics),
    }

    print('anomalies',insights_findings['correlations'])

    insights_summary = _format_findings_for_llm(insights_findings)
    
    insights_summary = await _create_llm_summary(insights_summary, country)

    return {
        "answer": insights_summary['answer'],
        "model_name": insights_summary['model_name'],
        "tokens_in": insights_summary['tokens_in'],
        "tokens_out": insights_summary['tokens_out'],
    }