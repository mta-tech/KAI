"""Pandas data analysis tools."""
import json
import pandas as pd


def create_pandas_analysis_tool():
    """Create pandas data analysis tool."""

    def analyze_data(
        data_json: str,
        analysis_type: str = "summary",
    ) -> str:
        """Analyze data using pandas.

        Args:
            data_json: JSON string of data (list of dicts)
            analysis_type: One of "summary", "correlation", "describe", "value_counts", "groupby"

        Returns:
            Analysis results as string
        """
        try:
            data = json.loads(data_json)
            # Handle case where data is a dict with "data" key or "result" key
            if isinstance(data, dict):
                if "data" in data:
                    data = data["data"]
                elif "result" in data:
                    data = data["result"]
            
            df = pd.DataFrame(data)

            if analysis_type == "summary":
                return df.describe(include='all').to_string()
            elif analysis_type == "correlation":
                numeric_df = df.select_dtypes(include=['number'])
                if len(numeric_df.columns) < 2:
                    return "Need at least 2 numeric columns for correlation"
                return numeric_df.corr().to_string()
            elif analysis_type == "describe":
                return df.describe().to_string()
            elif analysis_type == "value_counts":
                results = {}
                for col in df.select_dtypes(include=['object']).columns[:5]:
                    results[col] = df[col].value_counts().head(10).to_dict()
                return json.dumps(results, indent=2)
            else:
                return f"Unknown analysis type: {analysis_type}"
        except Exception as e:
            return f"Analysis error: {e}"

    return analyze_data


def create_python_execute_tool():
    """Create safe Python code execution tool."""
    SAFE_BUILTINS = {
        'print': print, 'len': len, 'range': range, 'sum': sum,
        'min': min, 'max': max, 'abs': abs, 'round': round,
        'sorted': sorted, 'list': list, 'dict': dict, 'str': str,
        'int': int, 'float': float, 'bool': bool, 'enumerate': enumerate,
        'zip': zip, 'map': map, 'filter': filter,
    }

    def python_execute(code: str) -> str:
        """Execute Python code in a restricted environment.
        
        Pre-imported modules: json, math, statistics, datetime, collections, pandas (as pd), numpy (as np), decimal.
        """
        import io, contextlib, json, math, statistics, datetime, collections
        import pandas as pd
        import numpy as np
        import decimal

        # Allowed modules for import
        ALLOWED_MODULES = {
            'json': json,
            'math': math,
            'statistics': statistics,
            'datetime': datetime,
            'collections': collections,
            'pandas': pd,
            'numpy': np,
            'decimal': decimal,
            're': None, # Not pre-imported but useful
        }
        
        if 're' not in locals():
            import re
            ALLOWED_MODULES['re'] = re

        def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name in ALLOWED_MODULES:
                return ALLOWED_MODULES[name]
            raise ImportError(f"Import of '{name}' is not allowed in restricted environment.")

        # Add safe_import to builtins
        local_builtins = SAFE_BUILTINS.copy()
        local_builtins['__import__'] = safe_import

        restricted_globals = {
            '__builtins__': local_builtins,
            'json': json, 'math': math, 'statistics': statistics,
            'datetime': datetime, 'collections': collections,
            'pd': pd, 'pandas': pd,
            'np': np, 'numpy': np,
            'decimal': decimal,
        }

        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                exec(code, restricted_globals)
            return output.getvalue() or "Code executed successfully (no output)"
        except Exception as e:
            return f"Execution error: {e}"

    return python_execute
