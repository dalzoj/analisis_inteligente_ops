import pandas as pd
import numpy as np
import traceback
from src.core import data_loader

def run(code):
    print('INFO: code_executor -> run')
    
    df_metrics = data_loader.get_df_metrics()
    df_orders = data_loader.get_df_orders()

    local_scope = {
        "df_metrics": df_metrics,
        "df_orders": df_orders,
        "pd": pd,
        "np": np,
    }
    
    try:
        exec(code, {}, local_scope)
        result = local_scope.get("result", None)

        if result is None:
            return False, None, "El código no tiene la variable 'result'"

        return True, result, None

    except Exception as e:
        
        tb = traceback.TracebackException.from_exception(e)
        
        last_frame = next((frame for frame in reversed(list(tb.stack)) if frame.filename == "<string>"),None)
        
        error_detail = {
            "type": type(e).__name__,
            "message": str(e),
            "line_number": last_frame.lineno if last_frame else None,
            "line_code": last_frame.line if last_frame else None,
        }
        
        print(f'ERROR: {error_detail}')
        return False, None, error_detail