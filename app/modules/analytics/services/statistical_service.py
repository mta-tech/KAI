"""Statistical analysis service."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from app.modules.analytics.models import (
    CorrelationMatrixResult,
    CorrelationResult,
    DescriptiveStats,
    StatisticalTestResult,
)


class StatisticalService:
    """Service for statistical analysis."""

    def descriptive_stats(self, series: pd.Series) -> DescriptiveStats:
        """Calculate descriptive statistics for a series."""
        desc = series.describe()
        return DescriptiveStats(
            column=series.name or "value",
            count=int(desc["count"]),
            mean=float(desc["mean"]),
            std=float(desc["std"]),
            min=float(desc["min"]),
            q25=float(desc["25%"]),
            median=float(desc["50%"]),
            q75=float(desc["75%"]),
            max=float(desc["max"]),
            skewness=float(series.skew()) if len(series) > 2 else None,
            kurtosis=float(series.kurtosis()) if len(series) > 3 else None,
        )

    def t_test_independent(
        self,
        group1: pd.Series | np.ndarray,
        group2: pd.Series | np.ndarray,
        alpha: float = 0.05,
    ) -> StatisticalTestResult:
        """Perform independent samples t-test."""
        # Convert to Series if numpy array
        if isinstance(group1, np.ndarray):
            group1 = pd.Series(group1)
        if isinstance(group2, np.ndarray):
            group2 = pd.Series(group2)

        stat, p_value = stats.ttest_ind(group1.dropna(), group2.dropna())

        n1, n2 = len(group1.dropna()), len(group2.dropna())
        dof = n1 + n2 - 2

        cohens_d = self._cohens_d(group1, group2)

        is_sig = p_value < alpha
        mean_diff = group1.mean() - group2.mean()

        interpretation = (
            f"The difference between groups is "
            f"{'statistically significant' if is_sig else 'not statistically significant'} "
            f"(t={stat:.3f}, p={p_value:.4f}, df={dof}). "
        )
        if is_sig:
            interpretation += (
                f"Group 1 (M={group1.mean():.2f}) is "
                f"{'higher' if mean_diff > 0 else 'lower'} than "
                f"Group 2 (M={group2.mean():.2f}) by {abs(mean_diff):.2f}. "
                f"Effect size (Cohen's d): {cohens_d:.3f} "
                f"({'small' if abs(cohens_d) < 0.5 else 'medium' if abs(cohens_d) < 0.8 else 'large'})."
            )

        return StatisticalTestResult(
            test_name="Independent Samples T-Test",
            test_type="t_test_independent",
            statistic=float(stat),
            p_value=float(p_value),
            degrees_of_freedom=float(dof),
            is_significant=is_sig,
            interpretation=interpretation,
            effect_size=cohens_d,
            effect_size_name="Cohen's d",
            details={
                "group1_mean": float(group1.mean()),
                "group1_std": float(group1.std()),
                "group1_n": n1,
                "group2_mean": float(group2.mean()),
                "group2_std": float(group2.std()),
                "group2_n": n2,
                "mean_difference": float(mean_diff),
            },
        )

    def anova(
        self,
        *groups: pd.Series | np.ndarray,
        alpha: float = 0.05,
    ) -> StatisticalTestResult:
        """Perform one-way ANOVA."""
        # Convert numpy arrays to Series
        groups = tuple(pd.Series(g) if isinstance(g, np.ndarray) else g for g in groups)
        clean_groups = [g.dropna() for g in groups]
        stat, p_value = stats.f_oneway(*clean_groups)

        k = len(groups)
        n = sum(len(g) for g in clean_groups)
        dof_between = k - 1
        dof_within = n - k

        is_sig = p_value < alpha

        interpretation = (
            f"One-way ANOVA: F({dof_between}, {dof_within}) = {stat:.3f}, p = {p_value:.4f}. "
            f"There {'is' if is_sig else 'is no'} statistically significant difference "
            f"between at least two groups."
        )

        return StatisticalTestResult(
            test_name="One-Way ANOVA",
            test_type="anova",
            statistic=float(stat),
            p_value=float(p_value),
            degrees_of_freedom=float(dof_between),
            is_significant=is_sig,
            interpretation=interpretation,
            details={
                "num_groups": k,
                "group_means": [float(g.mean()) for g in clean_groups],
                "group_sizes": [len(g) for g in clean_groups],
                "dof_between": dof_between,
                "dof_within": dof_within,
            },
        )

    def chi_square(
        self,
        contingency_table: pd.DataFrame | np.ndarray,
        alpha: float = 0.05,
    ) -> StatisticalTestResult:
        """Perform chi-square test of independence."""
        # Convert DataFrame to numpy array if needed
        if isinstance(contingency_table, pd.DataFrame):
            observed = contingency_table.values
        else:
            observed = contingency_table

        stat, p_value, dof, expected = stats.chi2_contingency(observed)

        is_sig = p_value < alpha

        interpretation = (
            f"Chi-square test: \u03c7\u00b2({dof}) = {stat:.3f}, p = {p_value:.4f}. "
            f"There {'is' if is_sig else 'is no'} statistically significant "
            f"association between the variables."
        )

        return StatisticalTestResult(
            test_name="Chi-Square Test of Independence",
            test_type="chi_square",
            statistic=float(stat),
            p_value=float(p_value),
            degrees_of_freedom=float(dof),
            is_significant=is_sig,
            interpretation=interpretation,
            details={
                "expected_frequencies": expected.tolist(),
                "observed": observed.tolist(),
            },
        )

    def correlation(
        self,
        x: pd.Series | np.ndarray,
        y: pd.Series | np.ndarray,
        method: str = "pearson",
        alpha: float = 0.05,
    ) -> CorrelationResult:
        """Calculate correlation between two series."""
        # Convert numpy arrays to Series
        if isinstance(x, np.ndarray):
            x = pd.Series(x)
        if isinstance(y, np.ndarray):
            y = pd.Series(y)

        x_clean = x.dropna()
        y_clean = y.dropna()

        common_idx = x_clean.index.intersection(y_clean.index)
        x_final = x_clean.loc[common_idx]
        y_final = y_clean.loc[common_idx]

        if method == "pearson":
            coef, p_value = stats.pearsonr(x_final, y_final)
        elif method == "spearman":
            coef, p_value = stats.spearmanr(x_final, y_final)
        else:
            coef, p_value = stats.kendalltau(x_final, y_final)

        is_sig = p_value < alpha

        strength = "no"
        if abs(coef) > 0.7:
            strength = "strong"
        elif abs(coef) > 0.4:
            strength = "moderate"
        elif abs(coef) > 0.2:
            strength = "weak"

        direction = "positive" if coef > 0 else "negative"

        interpretation = (
            f"{method.title()} correlation: r = {coef:.3f}, p = {p_value:.4f}. "
            f"There is {'a' if is_sig else 'no'} statistically significant "
            f"{strength} {direction} correlation between the variables."
        )

        return CorrelationResult(
            method=method,
            coefficient=float(coef),
            p_value=float(p_value),
            is_significant=is_sig,
            interpretation=interpretation,
            sample_size=len(x_final),
        )

    def correlation_matrix(
        self,
        df: pd.DataFrame,
        method: str = "pearson",
    ) -> CorrelationMatrixResult:
        """Calculate correlation matrix for numeric columns."""
        numeric_df = df.select_dtypes(include=[np.number])
        corr_matrix = numeric_df.corr(method=method)

        matrix_dict = corr_matrix.to_dict()
        columns = corr_matrix.columns.tolist()

        return CorrelationMatrixResult(
            method=method,
            matrix=matrix_dict,
            columns=columns,
        )

    def _cohens_d(self, group1: pd.Series, group2: pd.Series) -> float:
        """Calculate Cohen's d effect size."""
        n1, n2 = len(group1.dropna()), len(group2.dropna())
        var1, var2 = group1.var(), group2.var()
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        if pooled_std == 0:
            return 0.0
        return float((group1.mean() - group2.mean()) / pooled_std)
