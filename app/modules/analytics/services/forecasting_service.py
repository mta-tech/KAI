"""Time series forecasting service."""

from __future__ import annotations

import pandas as pd

from app.modules.analytics.models import ForecastResult


class ForecastingService:
    """Service for time series forecasting."""

    def forecast_prophet(
        self,
        df: pd.DataFrame,
        date_column: str,
        value_column: str,
        periods: int = 30,
        confidence_level: float = 0.95,
    ) -> ForecastResult:
        """Generate forecast using Facebook Prophet."""
        try:
            from prophet import Prophet
        except ImportError:
            raise ImportError(
                "Prophet is required for forecasting. Install with: pip install prophet"
            )

        prophet_df = df[[date_column, value_column]].copy()
        prophet_df.columns = ["ds", "y"]
        prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])

        model = Prophet(interval_width=confidence_level)
        model.fit(prophet_df)

        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        forecast_only = forecast.tail(periods)

        start_val = forecast_only["yhat"].iloc[0]
        end_val = forecast_only["yhat"].iloc[-1]
        trend = (
            "increasing"
            if end_val > start_val
            else "decreasing" if end_val < start_val else "stable"
        )
        change_pct = (
            ((end_val - start_val) / abs(start_val) * 100) if start_val != 0 else 0
        )

        interpretation = (
            f"Forecast shows a {trend} trend over the next {periods} periods. "
            f"Expected change: {change_pct:+.1f}%. "
            f"Values range from {forecast_only['yhat_lower'].min():.2f} to "
            f"{forecast_only['yhat_upper'].max():.2f} ({confidence_level*100:.0f}% CI)."
        )

        return ForecastResult(
            model_name="Prophet",
            forecast_dates=forecast_only["ds"].dt.strftime("%Y-%m-%d").tolist(),
            forecast_values=forecast_only["yhat"].round(2).tolist(),
            lower_bound=forecast_only["yhat_lower"].round(2).tolist(),
            upper_bound=forecast_only["yhat_upper"].round(2).tolist(),
            confidence_level=confidence_level,
            trend=trend,
            interpretation=interpretation,
            metrics={
                "periods": periods,
                "change_percent": round(change_pct, 2),
            },
        )

    def forecast_simple(
        self,
        series: pd.Series,
        periods: int = 30,
    ) -> ForecastResult:
        """Simple moving average forecast (fallback when Prophet unavailable)."""
        window = min(7, len(series) // 2)
        ma = series.rolling(window=window).mean().iloc[-1]
        std = series.std()

        forecast_values = [float(ma)] * periods
        lower = [float(ma - 1.96 * std)] * periods
        upper = [float(ma + 1.96 * std)] * periods

        last_date = pd.Timestamp.now()
        dates = pd.date_range(last_date, periods=periods, freq="D")

        return ForecastResult(
            model_name="Simple Moving Average",
            forecast_dates=[d.strftime("%Y-%m-%d") for d in dates],
            forecast_values=forecast_values,
            lower_bound=lower,
            upper_bound=upper,
            confidence_level=0.95,
            trend="stable",
            interpretation=f"Simple forecast based on {window}-period moving average: {ma:.2f}",
            metrics={"window": window, "std": float(std)},
        )
