"""Tests for the analytics CLI export commands."""

import json
import os
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from app.modules.analytics.cli import cli


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file with sample data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("price,quantity,revenue,cost\n")
        f.write("10.5,100,1050.0,500.0\n")
        f.write("15.0,80,1200.0,600.0\n")
        f.write("12.0,120,1440.0,720.0\n")
        f.write("8.5,150,1275.0,637.5\n")
        f.write("20.0,50,1000.0,500.0\n")
        f.write("11.0,110,1210.0,605.0\n")
        f.write("14.0,90,1260.0,630.0\n")
        f.write("9.0,130,1170.0,585.0\n")
        f.write("16.0,70,1120.0,560.0\n")
        f.write("13.0,100,1300.0,650.0\n")
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def sample_json_file():
    """Create a temporary JSON file with sample data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        data = [
            {"price": 10.5, "quantity": 100, "revenue": 1050.0},
            {"price": 15.0, "quantity": 80, "revenue": 1200.0},
            {"price": 12.0, "quantity": 120, "revenue": 1440.0},
            {"price": 8.5, "quantity": 150, "revenue": 1275.0},
            {"price": 20.0, "quantity": 50, "revenue": 1000.0},
            {"price": 11.0, "quantity": 110, "revenue": 1210.0},
            {"price": 14.0, "quantity": 90, "revenue": 1260.0},
            {"price": 9.0, "quantity": 130, "revenue": 1170.0},
            {"price": 16.0, "quantity": 70, "revenue": 1120.0},
            {"price": 13.0, "quantity": 100, "revenue": 1300.0},
        ]
        json.dump(data, f)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def timeseries_csv_file():
    """Create a temporary CSV file with time series data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("date,value\n")
        for i in range(30):
            f.write(f"2024-01-{i+1:02d},{100 + i * 2 + (i % 5)}\n")
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture
def ttest_csv_file():
    """Create a temporary CSV file with two groups for t-test."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("control,treatment\n")
        f.write("10.0,12.5\n")
        f.write("11.2,14.0\n")
        f.write("9.8,13.2\n")
        f.write("10.5,15.0\n")
        f.write("11.0,12.8\n")
        f.write("9.5,14.5\n")
        f.write("10.8,13.8\n")
        f.write("10.2,14.2\n")
        f.write("11.5,15.5\n")
        f.write("10.0,13.0\n")
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


class TestCLIHelp:
    """Tests for CLI help commands."""

    def test_main_help(self, runner):
        """Test main CLI help."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "KAI Analytics" in result.output

    def test_export_help(self, runner):
        """Test export group help."""
        result = runner.invoke(cli, ["export", "--help"])
        assert result.exit_code == 0
        assert "descriptive" in result.output
        assert "correlation" in result.output
        assert "forecast" in result.output

    def test_info_command(self, runner):
        """Test info command."""
        result = runner.invoke(cli, ["info"])
        assert result.exit_code == 0
        assert "Analytics Export" in result.output

    def test_list_formats_command(self, runner):
        """Test list-formats command."""
        result = runner.invoke(cli, ["list-formats"])
        assert result.exit_code == 0
        assert "json" in result.output
        assert "csv" in result.output
        assert "pdf" in result.output


class TestDescriptiveExport:
    """Tests for descriptive statistics export."""

    def test_export_descriptive_json(self, runner, sample_csv_file):
        """Test exporting descriptive stats to JSON."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "descriptive", sample_csv_file, "-c", "price", "-f", "json", "-o", output_path],
            )
            assert result.exit_code == 0
            assert "Exported to" in result.output

            with open(output_path, "r") as f:
                data = json.load(f)
            assert "result" in data or "mean" in data
        finally:
            os.unlink(output_path)

    def test_export_descriptive_csv(self, runner, sample_csv_file):
        """Test exporting descriptive stats to CSV."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "descriptive", sample_csv_file, "-c", "price", "-f", "csv", "-o", output_path],
            )
            assert result.exit_code == 0
            assert "Exported to" in result.output

            with open(output_path, "r") as f:
                content = f.read()
            # Should contain CSV headers/data
            assert "," in content
        finally:
            os.unlink(output_path)

    def test_export_descriptive_pdf(self, runner, sample_csv_file):
        """Test exporting descriptive stats to PDF."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "descriptive", sample_csv_file, "-c", "price", "-f", "pdf", "-o", output_path],
            )
            assert result.exit_code == 0
            assert "Exported to" in result.output

            # Verify it's a PDF file
            with open(output_path, "rb") as f:
                header = f.read(4)
            assert header == b"%PDF"
        finally:
            os.unlink(output_path)

    def test_export_descriptive_all_columns(self, runner, sample_csv_file):
        """Test exporting descriptive stats for all numeric columns."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "descriptive", sample_csv_file, "-f", "json", "-o", output_path],
            )
            assert result.exit_code == 0
        finally:
            os.unlink(output_path)

    def test_export_descriptive_invalid_column(self, runner, sample_csv_file):
        """Test error when column doesn't exist."""
        result = runner.invoke(
            cli,
            ["export", "descriptive", sample_csv_file, "-c", "nonexistent"],
        )
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_export_descriptive_json_file(self, runner, sample_json_file):
        """Test exporting descriptive stats from JSON input."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "descriptive", sample_json_file, "-c", "price", "-f", "json", "-o", output_path],
            )
            assert result.exit_code == 0
        finally:
            os.unlink(output_path)


class TestCorrelationExport:
    """Tests for correlation export."""

    def test_export_correlation_json(self, runner, sample_csv_file):
        """Test exporting correlation to JSON."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "correlation", sample_csv_file, "--x", "price", "--y", "revenue", "-f", "json", "-o", output_path],
            )
            assert result.exit_code == 0
            assert "Exported to" in result.output

            with open(output_path, "r") as f:
                data = json.load(f)
            # Should contain correlation results
            assert "result" in data or "coefficient" in data
        finally:
            os.unlink(output_path)

    def test_export_correlation_spearman(self, runner, sample_csv_file):
        """Test exporting Spearman correlation."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "correlation", sample_csv_file, "--x", "price", "--y", "revenue", "-m", "spearman", "-o", output_path],
            )
            assert result.exit_code == 0
        finally:
            os.unlink(output_path)

    def test_export_correlation_invalid_column(self, runner, sample_csv_file):
        """Test error when column doesn't exist."""
        result = runner.invoke(
            cli,
            ["export", "correlation", sample_csv_file, "--x", "price", "--y", "nonexistent"],
        )
        assert result.exit_code != 0
        assert "not found" in result.output


class TestCorrelationMatrixExport:
    """Tests for correlation matrix export."""

    def test_export_matrix_json(self, runner, sample_csv_file):
        """Test exporting correlation matrix to JSON."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "correlation-matrix", sample_csv_file, "-f", "json", "-o", output_path],
            )
            assert result.exit_code == 0
            assert "Exported to" in result.output
        finally:
            os.unlink(output_path)

    def test_export_matrix_pdf(self, runner, sample_csv_file):
        """Test exporting correlation matrix to PDF (with heatmap)."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "correlation-matrix", sample_csv_file, "-f", "pdf", "-o", output_path],
            )
            assert result.exit_code == 0

            # Verify it's a PDF file
            with open(output_path, "rb") as f:
                header = f.read(4)
            assert header == b"%PDF"
        finally:
            os.unlink(output_path)


class TestForecastExport:
    """Tests for forecast export."""

    def test_export_forecast_json(self, runner, timeseries_csv_file):
        """Test exporting forecast to JSON."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "forecast", timeseries_csv_file, "-c", "value", "-p", "10", "-f", "json", "-o", output_path],
            )
            assert result.exit_code == 0
            assert "Exported to" in result.output

            with open(output_path, "r") as f:
                data = json.load(f)
            # Should contain forecast data
            assert "result" in data or "forecast_values" in data
        finally:
            os.unlink(output_path)

    def test_export_forecast_csv(self, runner, timeseries_csv_file):
        """Test exporting forecast to CSV."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "forecast", timeseries_csv_file, "-c", "value", "-p", "10", "-f", "csv", "-o", output_path],
            )
            assert result.exit_code == 0

            with open(output_path, "r") as f:
                content = f.read()
            # CSV should contain structured columns
            assert "forecast" in content.lower() or "date" in content.lower()
        finally:
            os.unlink(output_path)

    def test_export_forecast_pdf(self, runner, timeseries_csv_file):
        """Test exporting forecast to PDF."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "forecast", timeseries_csv_file, "-c", "value", "-p", "10", "-f", "pdf", "-o", output_path],
            )
            assert result.exit_code == 0

            # Verify it's a PDF file
            with open(output_path, "rb") as f:
                header = f.read(4)
            assert header == b"%PDF"
        finally:
            os.unlink(output_path)

    def test_export_forecast_auto_column(self, runner, timeseries_csv_file):
        """Test forecast with auto-detected numeric column."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "forecast", timeseries_csv_file, "-p", "10", "-o", output_path],
            )
            assert result.exit_code == 0
            # Should auto-detect column
            assert "Using column" in result.output
        finally:
            os.unlink(output_path)


class TestAnomalyExport:
    """Tests for anomaly detection export."""

    def test_export_anomalies_zscore(self, runner, sample_csv_file):
        """Test exporting anomalies using z-score method."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "anomalies", sample_csv_file, "-c", "price", "-m", "zscore", "-t", "2.0", "-o", output_path],
            )
            assert result.exit_code == 0
            assert "Exported to" in result.output

            with open(output_path, "r") as f:
                data = json.load(f)
            assert "result" in data or "method" in data
        finally:
            os.unlink(output_path)

    def test_export_anomalies_iqr(self, runner, sample_csv_file):
        """Test exporting anomalies using IQR method."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "anomalies", sample_csv_file, "-c", "price", "-m", "iqr", "-o", output_path],
            )
            assert result.exit_code == 0
        finally:
            os.unlink(output_path)

    def test_export_anomalies_pdf(self, runner, sample_csv_file):
        """Test exporting anomalies to PDF."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "anomalies", sample_csv_file, "-c", "price", "-f", "pdf", "-o", output_path],
            )
            assert result.exit_code == 0

            # Verify it's a PDF file
            with open(output_path, "rb") as f:
                header = f.read(4)
            assert header == b"%PDF"
        finally:
            os.unlink(output_path)


class TestTTestExport:
    """Tests for t-test export."""

    def test_export_ttest_json(self, runner, ttest_csv_file):
        """Test exporting t-test results to JSON."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "t-test", ttest_csv_file, "-g1", "control", "-g2", "treatment", "-o", output_path],
            )
            assert result.exit_code == 0
            assert "Exported to" in result.output

            with open(output_path, "r") as f:
                data = json.load(f)
            # Should contain test results
            assert "result" in data or "p_value" in data
        finally:
            os.unlink(output_path)

    def test_export_ttest_pdf(self, runner, ttest_csv_file):
        """Test exporting t-test results to PDF."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "t-test", ttest_csv_file, "-g1", "control", "-g2", "treatment", "-f", "pdf", "-o", output_path],
            )
            assert result.exit_code == 0

            # Verify it's a PDF file
            with open(output_path, "rb") as f:
                header = f.read(4)
            assert header == b"%PDF"
        finally:
            os.unlink(output_path)

    def test_export_ttest_custom_alpha(self, runner, ttest_csv_file):
        """Test t-test with custom alpha level."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "t-test", ttest_csv_file, "-g1", "control", "-g2", "treatment", "-a", "0.01", "-o", output_path],
            )
            assert result.exit_code == 0
        finally:
            os.unlink(output_path)

    def test_export_ttest_invalid_column(self, runner, ttest_csv_file):
        """Test error when column doesn't exist."""
        result = runner.invoke(
            cli,
            ["export", "t-test", ttest_csv_file, "-g1", "control", "-g2", "nonexistent"],
        )
        assert result.exit_code != 0
        assert "not found" in result.output


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_file_not_found(self, runner):
        """Test error when file doesn't exist."""
        result = runner.invoke(
            cli,
            ["export", "descriptive", "nonexistent.csv"],
        )
        assert result.exit_code != 0

    def test_unsupported_file_format(self, runner):
        """Test error for unsupported file formats."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("some text")
            temp_path = f.name

        try:
            result = runner.invoke(
                cli,
                ["export", "descriptive", temp_path],
            )
            assert result.exit_code != 0
            assert "Unsupported file format" in result.output
        finally:
            os.unlink(temp_path)

    def test_no_metadata_flag(self, runner, sample_csv_file):
        """Test --no-metadata flag works."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            output_path = out.name

        try:
            result = runner.invoke(
                cli,
                ["export", "descriptive", sample_csv_file, "-c", "price", "--no-metadata", "-o", output_path],
            )
            assert result.exit_code == 0

            with open(output_path, "r") as f:
                data = json.load(f)
            # Should not have metadata wrapper
            assert "metadata" not in data
        finally:
            os.unlink(output_path)
