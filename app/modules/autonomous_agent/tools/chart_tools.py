"""Text-to-Chart generation tools."""
import json
import base64
from io import BytesIO
from typing import Literal

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend


def create_chart_tool(output_dir: str = "./agent_results"):
    """Create chart generation tool."""

    def generate_chart(
        data_json: str,
        chart_type: Literal["line", "bar", "pie", "scatter", "area", "heatmap"],
        x_column: str,
        y_column: str,
        title: str = "Chart",
        color_column: str | None = None,
        save_path: str | None = None,
    ) -> str:
        """Generate a chart from data.

        Args:
            data_json: JSON string of data (list of dicts)
            chart_type: Type of chart (line, bar, pie, scatter, area, heatmap)
            x_column: Column name for x-axis
            y_column: Column name for y-axis (or values for pie)
            title: Chart title
            color_column: Optional column for color grouping
            save_path: Optional path to save chart image

        Returns:
            JSON with chart info and base64 image data
        """
        try:
            data = json.loads(data_json)
            df = pd.DataFrame(data)

            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_type == "line":
                if color_column and color_column in df.columns:
                    for name, group in df.groupby(color_column):
                        ax.plot(group[x_column], group[y_column], label=name, marker='o')
                    ax.legend()
                else:
                    ax.plot(df[x_column], df[y_column], marker='o')

            elif chart_type == "bar":
                if color_column and color_column in df.columns:
                    pivot = df.pivot_table(index=x_column, columns=color_column, values=y_column)
                    pivot.plot(kind='bar', ax=ax)
                else:
                    ax.bar(df[x_column], df[y_column])

            elif chart_type == "pie":
                ax.pie(df[y_column], labels=df[x_column], autopct='%1.1f%%')

            elif chart_type == "scatter":
                ax.scatter(df[x_column], df[y_column])

            elif chart_type == "area":
                ax.fill_between(df[x_column], df[y_column], alpha=0.5)
                ax.plot(df[x_column], df[y_column])

            elif chart_type == "heatmap":
                pivot = df.pivot_table(index=x_column, columns=color_column or y_column, values=y_column)
                im = ax.imshow(pivot.values, aspect='auto')
                plt.colorbar(im, ax=ax)

            ax.set_title(title)
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            # Save to file or return base64
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                plt.close()
                return json.dumps({
                    "success": True,
                    "chart_type": chart_type,
                    "saved_to": save_path,
                })
            else:
                # Return base64 encoded image
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                plt.close()
                return json.dumps({
                    "success": True,
                    "chart_type": chart_type,
                    "image_base64": img_base64[:100] + "...",  # Truncated for context
                    "full_image_available": True,
                })

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return generate_chart
