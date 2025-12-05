"""Pandas data analysis tools."""
import json
import decimal
import uuid
from datetime import datetime, date
import pandas as pd

from app.utils.sql_database.sql_database import SQLDatabase


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


def create_python_execute_tool(database: SQLDatabase = None, max_rows: int = 1000):
    """Create safe Python code execution tool with optional SQL capabilities.

    Args:
        database: Optional SQLDatabase instance for SQL query execution
        max_rows: Maximum rows to return from SQL queries (default: 1000)
    """
    SAFE_BUILTINS = {
        # Core types and functions
        'print': print, 'len': len, 'range': range, 'sum': sum,
        'min': min, 'max': max, 'abs': abs, 'round': round,
        'sorted': sorted, 'list': list, 'dict': dict, 'str': str,
        'int': int, 'float': float, 'bool': bool, 'enumerate': enumerate,
        'zip': zip, 'map': map, 'filter': filter, 'set': set, 'tuple': tuple,
        'any': any, 'all': all, 'isinstance': isinstance, 'type': type,
        # Exception types for try/except handling
        'Exception': Exception, 'BaseException': BaseException,
        'ValueError': ValueError, 'TypeError': TypeError, 'KeyError': KeyError,
        'IndexError': IndexError, 'AttributeError': AttributeError,
        'ZeroDivisionError': ZeroDivisionError, 'RuntimeError': RuntimeError,
        'StopIteration': StopIteration, 'ImportError': ImportError,
        # Additional useful builtins
        'repr': repr, 'hash': hash, 'id': id, 'ord': ord, 'chr': chr,
        'hasattr': hasattr, 'getattr': getattr, 'setattr': setattr,
        'callable': callable, 'iter': iter, 'next': next, 'reversed': reversed,
        'slice': slice, 'frozenset': frozenset, 'bytes': bytes, 'bytearray': bytearray,
        'format': format, 'pow': pow, 'divmod': divmod, 'hex': hex, 'oct': oct, 'bin': bin,
        'True': True, 'False': False, 'None': None,
        # String/object introspection
        'dir': dir, 'vars': vars, 'locals': locals,
    }

    def _json_serializer(obj):
        """Custom JSON serializer for SQL types."""
        if isinstance(obj, (decimal.Decimal, float)):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        raise TypeError(f"Type {type(obj)} not serializable")

    def _sanitize_query(query: str) -> str:
        """Clean up SQL query by removing literal escape sequences."""
        import re
        # Replace literal \n, \t, \r with actual whitespace
        query = query.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ')
        # Normalize multiple spaces to single space
        query = re.sub(r'\s+', ' ', query)
        return query.strip()

    def _create_run_sql(db: SQLDatabase):
        """Create the run_sql function for the execution environment."""
        def run_sql(query: str, as_dataframe: bool = True):
            """Execute a SQL query and return results.

            Args:
                query: SQL SELECT query to execute
                as_dataframe: If True, return pandas DataFrame; if False, return list of dicts

            Returns:
                pandas DataFrame or list of dicts with query results

            Example:
                # Get DataFrame
                df = run_sql("SELECT * FROM orders LIMIT 10")

                # Get list of dicts
                data = run_sql("SELECT * FROM users", as_dataframe=False)
            """
            clean_query = _sanitize_query(query)
            result = db.run_sql(clean_query, max_rows)
            rows = result[1].get("result", []) if isinstance(result, tuple) else []

            if as_dataframe:
                return pd.DataFrame(rows)
            return rows
        return run_sql

    def _create_run_sql_multi(db: SQLDatabase):
        """Create the run_sql_multi function for executing multiple queries."""
        def run_sql_multi(queries: dict, as_dataframe: bool = True):
            """Execute multiple SQL queries and return results as a dictionary.

            Args:
                queries: Dictionary of {name: sql_query} pairs
                as_dataframe: If True, return DataFrames; if False, return list of dicts

            Returns:
                Dictionary of {name: result} pairs

            Example:
                results = run_sql_multi({
                    'orders': "SELECT * FROM orders LIMIT 10",
                    'customers': "SELECT * FROM customers LIMIT 10",
                    'products': "SELECT COUNT(*) as total FROM products"
                })

                # Access results
                orders_df = results['orders']
                customers_df = results['customers']
            """
            results = {}
            for name, query in queries.items():
                try:
                    clean_query = _sanitize_query(query)
                    result = db.run_sql(clean_query, max_rows)
                    rows = result[1].get("result", []) if isinstance(result, tuple) else []
                    if as_dataframe:
                        results[name] = pd.DataFrame(rows)
                    else:
                        results[name] = rows
                except Exception as e:
                    results[name] = {"error": str(e)}
            return results
        return run_sql_multi

    def python_execute(code: str) -> str:
        """Execute Python code in a restricted environment with SQL capabilities.

        Pre-imported modules: json, math, statistics, datetime, collections, pandas (as pd), numpy (as np), decimal, re, sklearn.

        SQL Functions (if database connected):
        - run_sql(query, as_dataframe=True): Execute single SQL query, returns DataFrame or list of dicts
        - run_sql_multi(queries_dict, as_dataframe=True): Execute multiple queries at once

        Example - Single query:
            df = run_sql("SELECT * FROM orders WHERE status = 'completed' LIMIT 100")
            print(df.describe())

        Example - Multiple queries:
            results = run_sql_multi({
                'sales': "SELECT SUM(amount) as total FROM orders",
                'customers': "SELECT COUNT(*) as count FROM customers",
                'top_products': "SELECT product_id, COUNT(*) as orders FROM order_items GROUP BY product_id ORDER BY orders DESC LIMIT 5"
            })

            total_sales = results['sales']['total'].iloc[0]
            customer_count = results['customers']['count'].iloc[0]
            print(f"Total Sales: ${total_sales}, Customers: {customer_count}")

            # Merge dataframes
            merged = pd.merge(results['orders'], results['customers'], on='customer_id')

        Example - Machine Learning with sklearn:
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler

            df = run_sql("SELECT amount, quantity FROM orders LIMIT 1000")
            X = df[['amount', 'quantity']].values
            X_scaled = StandardScaler().fit_transform(X)
            kmeans = KMeans(n_clusters=3, random_state=42).fit(X_scaled)
            df['cluster'] = kmeans.labels_
            print(df.groupby('cluster').mean())
        """
        import io, contextlib, math, statistics, collections
        import numpy as np
        import re as re_module

        # Import sklearn and its submodules
        try:
            import sklearn
            from sklearn import cluster, preprocessing, linear_model, tree, ensemble
            from sklearn import metrics, model_selection, decomposition
        except ImportError:
            sklearn = None

        # Allowed modules for import
        ALLOWED_MODULES = {
            'json': json,
            'math': math,
            'statistics': statistics,
            'datetime': datetime,
            'date': date,
            'collections': collections,
            'pandas': pd,
            'numpy': np,
            'decimal': decimal,
            're': re_module,
            'sklearn': sklearn,
            'sklearn.cluster': cluster if sklearn else None,
            'sklearn.preprocessing': preprocessing if sklearn else None,
            'sklearn.linear_model': linear_model if sklearn else None,
            'sklearn.tree': tree if sklearn else None,
            'sklearn.ensemble': ensemble if sklearn else None,
            'sklearn.metrics': metrics if sklearn else None,
            'sklearn.model_selection': model_selection if sklearn else None,
            'sklearn.decomposition': decomposition if sklearn else None,
        }

        def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name in ALLOWED_MODULES:
                module = ALLOWED_MODULES[name]
                if module is None:
                    raise ImportError(f"Module '{name}' is not available. Please install scikit-learn.")
                return module
            raise ImportError(f"Import of '{name}' is not allowed in restricted environment.")

        # Add safe_import to builtins
        local_builtins = SAFE_BUILTINS.copy()
        local_builtins['__import__'] = safe_import

        restricted_globals = {
            '__builtins__': local_builtins,
            'json': json, 'math': math, 'statistics': statistics,
            'datetime': datetime, 'date': date, 'collections': collections,
            'pd': pd, 'pandas': pd,
            'np': np, 'numpy': np,
            'decimal': decimal, 're': re_module,
            'sklearn': sklearn,
        }

        # Add SQL functions if database is available
        if database is not None:
            restricted_globals['run_sql'] = _create_run_sql(database)
            restricted_globals['run_sql_multi'] = _create_run_sql_multi(database)

        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                exec(code, restricted_globals)
            return output.getvalue() or "Code executed successfully (no output)"
        except Exception as e:
            return f"Execution error: {e}"

    return python_execute
