"""AI-powered insights extraction tools."""
import json
import pandas as pd
from typing import Literal


def create_insights_tool():
    """Create automated insights extraction tool."""

    def extract_insights(
        data_json: str,
        context: str = "",
    ) -> str:
        """Extract key insights from data automatically.

        Args:
            data_json: JSON string of data (list of dicts)
            context: Optional context about what the data represents

        Returns:
            JSON with extracted insights
        """
        try:
            data = json.loads(data_json)
            df = pd.DataFrame(data)
            insights = []

            # 1. Summary statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                stats = df[col].describe()
                insights.append({
                    "category": "summary",
                    "title": f"{col} Overview",
                    "description": f"Range: {stats['min']:.2f} to {stats['max']:.2f}, "
                                   f"Average: {stats['mean']:.2f}, Median: {stats['50%']:.2f}",
                    "importance": "medium",
                    "supporting_data": {"column": col, "stats": stats.to_dict()}
                })

            # 2. Trend detection (if data has time-like column)
            if len(df) > 2 and len(numeric_cols) > 0:
                for col in numeric_cols[:3]:  # Check first 3 numeric columns
                    values = df[col].dropna().values
                    if len(values) > 2:
                        # Simple trend: compare first third vs last third
                        first_third = values[:len(values)//3].mean()
                        last_third = values[-len(values)//3:].mean()
                        change_pct = ((last_third - first_third) / first_third * 100) if first_third != 0 else 0

                        if abs(change_pct) > 10:
                            trend = "increasing" if change_pct > 0 else "decreasing"
                            insights.append({
                                "category": "trend",
                                "title": f"{col} is {trend}",
                                "description": f"{col} shows a {abs(change_pct):.1f}% {trend} trend",
                                "importance": "high" if abs(change_pct) > 25 else "medium",
                                "supporting_data": {"change_percent": change_pct}
                            })

            # 3. Anomaly detection (values outside 2 std devs)
            for col in numeric_cols[:3]:
                mean = df[col].mean()
                std = df[col].std()
                if std > 0:
                    outliers = df[(df[col] < mean - 2*std) | (df[col] > mean + 2*std)]
                    if len(outliers) > 0 and len(outliers) < len(df) * 0.1:
                        insights.append({
                            "category": "anomaly",
                            "title": f"Outliers detected in {col}",
                            "description": f"Found {len(outliers)} unusual values in {col}",
                            "importance": "high",
                            "supporting_data": {"outlier_count": len(outliers)}
                        })

            # 4. Top/Bottom performers (for categorical + numeric)
            cat_cols = df.select_dtypes(include=['object']).columns
            if len(cat_cols) > 0 and len(numeric_cols) > 0:
                cat_col = cat_cols[0]
                num_col = numeric_cols[0]
                top = df.nlargest(3, num_col)[[cat_col, num_col]]
                insights.append({
                    "category": "comparison",
                    "title": f"Top performers by {num_col}",
                    "description": f"Highest {num_col}: " + ", ".join(
                        f"{row[cat_col]} ({row[num_col]:.2f})" for _, row in top.iterrows()
                    ),
                    "importance": "medium",
                    "supporting_data": {"top_3": top.to_dict('records')}
                })

            return json.dumps({
                "success": True,
                "insight_count": len(insights),
                "insights": insights
            })

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return extract_insights
