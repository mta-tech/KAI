"""Language-aware prompts for chart visualization."""

from __future__ import annotations

from app.modules.chartviz.models import ChartType


def get_chart_type_descriptions(language: str = "id") -> dict[str, str]:
    """Get chart type descriptions for prompts.

    Args:
        language: Language code ('id' for Indonesian, 'en' for English)

    Returns:
        Dict mapping chart type to description
    """
    if language == "id":
        return {
            ChartType.LINE: "Line chart - untuk data time series atau tren berurutan",
            ChartType.BAR: "Bar chart - untuk perbandingan antar kategori",
            ChartType.PIE: "Pie chart - untuk proporsi/persentase dari keseluruhan",
            ChartType.SCATTER: "Scatter plot - untuk korelasi antara dua variabel numerik",
            ChartType.AREA: "Area chart - untuk tren kumulatif atau stacked data",
            ChartType.KPI: "KPI/Big Number - untuk metrik tunggal dengan delta perubahan",
            ChartType.TABLE: "Table - untuk data detail yang perlu dibaca per baris",
        }
    else:
        return {
            ChartType.LINE: "Line chart - for time series or sequential trend data",
            ChartType.BAR: "Bar chart - for comparing across categories",
            ChartType.PIE: "Pie chart - for proportions/percentages of a whole",
            ChartType.SCATTER: "Scatter plot - for correlation between two numeric variables",
            ChartType.AREA: "Area chart - for cumulative trends or stacked data",
            ChartType.KPI: "KPI/Big Number - for single metric with change delta",
            ChartType.TABLE: "Table - for detailed data that needs row-by-row reading",
        }


def get_generation_system_prompt(chart_type: ChartType, language: str = "id") -> str:
    """Get system prompt for chart generation.

    Args:
        chart_type: Target chart type
        language: Language code

    Returns:
        System prompt string
    """
    if language == "id":
        base_prompt = f"""Anda adalah asisten visualisasi data. Tugas Anda adalah menghasilkan konfigurasi chart {chart_type.value} dalam format JSON yang dapat langsung digunakan oleh library JavaScript seperti Chart.js, ECharts, atau Recharts.

Aturan:
1. widget_title harus deskriptif dan dalam Bahasa Indonesia
2. widget_data harus menggunakan key yang sesuai dengan kolom data
3. Pilih x_axis_key dan y_axis_key yang tepat dari data
4. Untuk KPI, hitung widget_delta_percentages jika memungkinkan
5. Pastikan semua label dalam Bahasa Indonesia

Format output yang diharapkan adalah ChartWidget dengan field:
- widget_id: UUID (akan di-generate otomatis)
- widget_title: Judul chart yang deskriptif
- widget_type: "{chart_type.value}"
- widget_data: List data dengan key-value
- x_axis_label, y_axis_label: Label sumbu
- x_axis_key, y_axis_key: Key dari data untuk sumbu
- widget_delta_percentages: Persentase perubahan (opsional)"""
    else:
        base_prompt = f"""You are a data visualization assistant. Your task is to generate a {chart_type.value} chart configuration in JSON format that can be directly used by JavaScript libraries like Chart.js, ECharts, or Recharts.

Rules:
1. widget_title should be descriptive and in English
2. widget_data should use keys matching the data columns
3. Choose appropriate x_axis_key and y_axis_key from the data
4. For KPI, calculate widget_delta_percentages if possible
5. Ensure all labels are in English

Expected output format is ChartWidget with fields:
- widget_id: UUID (will be auto-generated)
- widget_title: Descriptive chart title
- widget_type: "{chart_type.value}"
- widget_data: List of key-value data
- x_axis_label, y_axis_label: Axis labels
- x_axis_key, y_axis_key: Data keys for axes
- widget_delta_percentages: Percentage change (optional)"""

    return base_prompt


def get_recommendation_system_prompt(language: str = "id") -> str:
    """Get system prompt for chart type recommendation.

    Args:
        language: Language code

    Returns:
        System prompt string
    """
    chart_descriptions = get_chart_type_descriptions(language)
    desc_text = "\n".join(f"- {k.value}: {v}" for k, v in chart_descriptions.items())

    if language == "id":
        return f"""Anda adalah asisten visualisasi data. Analisis data yang diberikan dan rekomendasikan tipe chart yang paling sesuai.

Tipe chart yang tersedia:
{desc_text}

Pertimbangan:
1. Jika ada kolom waktu/tanggal berurutan -> LINE atau AREA
2. Jika ada perbandingan kategori -> BAR
3. Jika ada proporsi (total = 100%) -> PIE
4. Jika ada 2 kolom numerik untuk korelasi -> SCATTER
5. Jika hanya 1 angka metrik -> KPI
6. Jika data kompleks dengan banyak kolom -> TABLE

Output harus berupa ChartRecommendation dengan:
- chart_type: Tipe chart yang direkomendasikan
- confidence: Skor kepercayaan 0-1
- rationale: Penjelasan singkat dalam Bahasa Indonesia"""
    else:
        return f"""You are a data visualization assistant. Analyze the given data and recommend the most suitable chart type.

Available chart types:
{desc_text}

Considerations:
1. If there's a sequential time/date column -> LINE or AREA
2. If comparing categories -> BAR
3. If showing proportions (total = 100%) -> PIE
4. If 2 numeric columns for correlation -> SCATTER
5. If just 1 metric number -> KPI
6. If complex data with many columns -> TABLE

Output must be ChartRecommendation with:
- chart_type: Recommended chart type
- confidence: Confidence score 0-1
- rationale: Brief explanation in English"""


def format_data_for_prompt(
    data: list[dict],
    user_prompt: str | None = None,
    language: str = "id",
) -> str:
    """Format data and context for the LLM prompt.

    Args:
        data: SQL result data
        user_prompt: Original user question
        language: Language code

    Returns:
        Formatted prompt string
    """
    # Show sample of data (first 10 rows)
    sample_data = data[:10] if len(data) > 10 else data
    data_preview = str(sample_data)

    # Get column info
    columns = list(data[0].keys()) if data else []
    row_count = len(data)

    if language == "id":
        prompt_parts = [
            f"Data SQL ({row_count} baris):",
            f"Kolom: {columns}",
            f"Preview data: {data_preview}",
        ]
        if user_prompt:
            prompt_parts.insert(0, f"Pertanyaan pengguna: {user_prompt}")
        prompt_parts.append("\nBuatkan konfigurasi chart berdasarkan data di atas.")
    else:
        prompt_parts = [
            f"SQL Data ({row_count} rows):",
            f"Columns: {columns}",
            f"Data preview: {data_preview}",
        ]
        if user_prompt:
            prompt_parts.insert(0, f"User question: {user_prompt}")
        prompt_parts.append("\nGenerate chart configuration based on the above data.")

    return "\n".join(prompt_parts)


def format_recommendation_prompt(
    data: list[dict],
    user_prompt: str | None = None,
    language: str = "id",
) -> str:
    """Format data for chart recommendation prompt.

    Args:
        data: SQL result data
        user_prompt: Original user question
        language: Language code

    Returns:
        Formatted prompt string
    """
    # Analyze data characteristics
    row_count = len(data)

    # Check for numeric and date-like columns
    numeric_cols = []
    potential_date_cols = []
    categorical_cols = []

    if data:
        sample = data[0]
        for col, val in sample.items():
            if isinstance(val, (int, float)):
                numeric_cols.append(col)
            elif isinstance(val, str):
                # Check if looks like date
                if any(x in col.lower() for x in ["date", "time", "tanggal", "bulan", "tahun"]):
                    potential_date_cols.append(col)
                else:
                    categorical_cols.append(col)

    sample_data = data[:5] if len(data) > 5 else data

    if language == "id":
        prompt_parts = [
            "Analisis data untuk rekomendasi chart:",
            f"- Jumlah baris: {row_count}",
            f"- Kolom numerik: {numeric_cols}",
            f"- Kolom tanggal/waktu: {potential_date_cols}",
            f"- Kolom kategori: {categorical_cols}",
            f"- Preview data: {sample_data}",
        ]
        if user_prompt:
            prompt_parts.insert(0, f"Pertanyaan pengguna: {user_prompt}")
        prompt_parts.append("\nRekomendasikan tipe chart yang paling sesuai.")
    else:
        prompt_parts = [
            "Analyze data for chart recommendation:",
            f"- Row count: {row_count}",
            f"- Numeric columns: {numeric_cols}",
            f"- Date/time columns: {potential_date_cols}",
            f"- Categorical columns: {categorical_cols}",
            f"- Data preview: {sample_data}",
        ]
        if user_prompt:
            prompt_parts.insert(0, f"User question: {user_prompt}")
        prompt_parts.append("\nRecommend the most suitable chart type.")

    return "\n".join(prompt_parts)


__all__ = [
    "get_chart_type_descriptions",
    "get_generation_system_prompt",
    "get_recommendation_system_prompt",
    "format_data_for_prompt",
    "format_recommendation_prompt",
]
