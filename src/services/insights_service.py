from src.core import data_loader, prompt_builder
from src.insights import correlation
from src.llm import llm_client


def _filter_by_country(df, country):
    print('INFO: insights_service -> _filter_by_country')

    if country:
        return df[df["COUNTRY"] == country.upper()]
    return df


def _format_findings_for_llm(all_findings):
    print('INFO: insights_service -> _format_findings_for_llm')

    lines = []
 
    if all_findings["correlations"]:
        lines.append("\nMETRIC CORRELATIONS:")
        for f in all_findings["correlations"][:10]:
            lines.append(
                f"  - {f['metric_a']} and {f['metric_b']} tiene una dirección "
                f"{f['direction']} correlacionada de {f['correlation']}"
            )
 
    return "\n".join(lines)


async def _create_llm_summary(insights_summary):
    print('INFO: insights_service -> _create_llm_summary')

    insights_prompt = prompt_builder.get_chat_prompt()
 
    user_message = (
        f"Estos son los hallazgos encontrados en el análisis:\n"
        f"{insights_summary}\n\n"
        f"Organizar la información según las instrucciones"
    )

    return await llm_client.basic_call(insights_prompt, user_message)


async def generate(country):
    print('INFO: insights_service -> generate')

    df_metrics = data_loader.get_df_metrics()
    df_metrics = _filter_by_country(df_metrics, country)

    insights_findings = {
        "correlations": correlation.detect(df_metrics),
    }

    insights_summary = _format_findings_for_llm(insights_findings)
    insights_summary = await _create_llm_summary(insights_summary)

    return {
        "answer": insights_summary['answer'],
        "model_name": insights_summary['model_name'],
        "tokens_in": insights_summary['tokens_in'],
        "tokens_out": insights_summary['tokens_out'],
    }