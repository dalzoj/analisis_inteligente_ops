import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import traceback
from src.backend.core import data_loader

def _transform_chart(chart):
    if chart is None:
        return None
    
    try:
        if hasattr(chart, 'to_json'):
            return json.loads(chart.to_json())
       
        if isinstance(chart, dict):

            return json.loads(go.Figure(chart).to_json())
    
    except Exception as e:
        print(f'WARNING: code_executor -> _clean_chart -> {e}')
    
    return None

def run(code):
    print('INFO: code_executor -> run')
    
    df_metrics = data_loader.get_df_metrics()
    df_orders = data_loader.get_df_orders()

    local_scope = {
        "df_metrics": df_metrics,
        "df_orders": df_orders,
        "pd": pd,
        "np": np,
        "px": px,
    }
    
    try:
        exec(code, {}, local_scope)
        result = local_scope.get("result", None)
        chart = _transform_chart(local_scope.get("chart", None))

        if result is None:
            return False, None, None, "El código no tiene la variable 'result'"

        return True, result, chart, None

    except Exception as e:
        
        tb = traceback.TracebackException.from_exception(e)
        
        last_frame = next(
            (frame for frame in reversed(list(tb.stack)) if frame.filename == "<string>"),
            None
        )
        
        error_detail = {
            "type": type(e).__name__,
            "message": str(e),
            "line_number": last_frame.lineno if last_frame else None,
            "line_code": last_frame.line if last_frame else None,
        }
        
        print(f'ERROR: code_executor -> run -> {error_detail}')
        return False, None, None, error_detail