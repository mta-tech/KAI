"""Dashboard layout optimization service."""
from __future__ import annotations

import logging
from typing import Optional

from app.modules.dashboard.models import (
    DashboardLayout,
    Widget,
    WidgetSize,
    WidgetType,
)

logger = logging.getLogger(__name__)


class LayoutService:
    """Service for optimizing dashboard widget layout."""

    def __init__(self, columns: int = 12):
        self.columns = columns

    def auto_layout(
        self,
        widgets: list[Widget],
        columns: int = 12,
    ) -> list[Widget]:
        """
        Automatically position widgets in a grid layout.

        Algorithm:
        1. Sort widgets by priority (KPIs first, then charts, then tables)
        2. Place widgets row by row, respecting column spans
        3. Move to next row when current row is full

        Args:
            widgets: List of widgets to layout
            columns: Number of grid columns (default 12)

        Returns:
            Widgets with updated row/col positions
        """
        if not widgets:
            return widgets

        # Sort by priority
        sorted_widgets = self._sort_by_priority(widgets)

        # Track grid occupancy
        current_row = 0
        current_col = 0

        for widget in sorted_widgets:
            col_span = widget.get_col_span()
            row_span = widget.get_row_span()

            # Check if widget fits in current row
            if current_col + col_span > columns:
                # Move to next row
                current_row += 1
                current_col = 0

            # Assign position
            widget.row = current_row
            widget.col = current_col
            widget.col_span = col_span
            widget.row_span = row_span

            # Move to next position
            current_col += col_span

            # If row span > 1, account for tall widgets
            if row_span > 1:
                # For simplicity, just move to next row
                current_row += row_span - 1

        return sorted_widgets

    def _sort_by_priority(self, widgets: list[Widget]) -> list[Widget]:
        """Sort widgets by display priority."""
        priority_map = {
            WidgetType.KPI: 0,  # KPIs first (top row)
            WidgetType.FILTER: 1,  # Filters next
            WidgetType.CHART: 2,  # Charts in middle
            WidgetType.TEXT: 3,  # Text blocks
            WidgetType.TABLE: 4,  # Tables at bottom
        }

        # Secondary sort by size (larger first within same type)
        size_map = {
            WidgetSize.FULL: 0,
            WidgetSize.WIDE: 1,
            WidgetSize.LARGE: 2,
            WidgetSize.TALL: 3,
            WidgetSize.MEDIUM: 4,
            WidgetSize.SMALL: 5,
        }

        return sorted(
            widgets,
            key=lambda w: (
                priority_map.get(w.widget_type, 99),
                size_map.get(w.size, 99),
            ),
        )

    def optimize_layout(self, layout: DashboardLayout) -> DashboardLayout:
        """
        Optimize an existing layout for better visual balance.

        Args:
            layout: Dashboard layout to optimize

        Returns:
            Optimized layout
        """
        if not layout.widgets:
            return layout

        # Re-layout all widgets
        optimized_widgets = self.auto_layout(
            widgets=layout.widgets.copy(),
            columns=layout.columns,
        )

        layout.widgets = optimized_widgets
        return layout

    def validate_layout(self, layout: DashboardLayout) -> list[str]:
        """
        Validate layout for issues.

        Args:
            layout: Layout to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not layout.widgets:
            return errors

        # Check for overlapping widgets
        occupied = {}  # (row, col) -> widget_id

        for widget in layout.widgets:
            col_span = widget.col_span or widget.get_col_span()
            row_span = widget.row_span or widget.get_row_span()

            for r in range(widget.row, widget.row + row_span):
                for c in range(widget.col, widget.col + col_span):
                    cell = (r, c)
                    if cell in occupied:
                        errors.append(
                            f"Widget '{widget.name}' overlaps with widget at ({r}, {c})"
                        )
                    else:
                        occupied[cell] = widget.id

            # Check bounds
            if widget.col + col_span > layout.columns:
                errors.append(
                    f"Widget '{widget.name}' exceeds grid width "
                    f"(col {widget.col} + span {col_span} > {layout.columns})"
                )

        return errors

    def add_widget_to_layout(
        self,
        layout: DashboardLayout,
        widget: Widget,
    ) -> DashboardLayout:
        """
        Add a widget to the layout at the best available position.

        Args:
            layout: Current layout
            widget: Widget to add

        Returns:
            Updated layout
        """
        # Find the next available position
        if not layout.widgets:
            widget.row = 0
            widget.col = 0
        else:
            # Find the last row and column
            max_row = max(w.row + w.get_row_span() for w in layout.widgets)
            last_row_widgets = [w for w in layout.widgets if w.row == max_row - 1]

            if last_row_widgets:
                last_col = max(w.col + w.get_col_span() for w in last_row_widgets)
                col_span = widget.get_col_span()

                if last_col + col_span <= layout.columns:
                    # Fits in current row
                    widget.row = max_row - 1
                    widget.col = last_col
                else:
                    # New row
                    widget.row = max_row
                    widget.col = 0
            else:
                widget.row = max_row
                widget.col = 0

        widget.col_span = widget.get_col_span()
        widget.row_span = widget.get_row_span()

        layout.widgets.append(widget)
        return layout

    def remove_widget_from_layout(
        self,
        layout: DashboardLayout,
        widget_id: str,
        reflow: bool = True,
    ) -> DashboardLayout:
        """
        Remove a widget from the layout.

        Args:
            layout: Current layout
            widget_id: ID of widget to remove
            reflow: Whether to reflow remaining widgets

        Returns:
            Updated layout
        """
        layout.widgets = [w for w in layout.widgets if w.id != widget_id]

        if reflow and layout.widgets:
            layout.widgets = self.auto_layout(layout.widgets, layout.columns)

        return layout

    def get_layout_stats(self, layout: DashboardLayout) -> dict:
        """Get statistics about the layout."""
        if not layout.widgets:
            return {
                "widget_count": 0,
                "row_count": 0,
                "total_cells": 0,
                "occupied_cells": 0,
                "utilization": 0.0,
            }

        # Calculate occupied cells
        occupied_cells = sum(
            w.get_col_span() * w.get_row_span() for w in layout.widgets
        )

        # Calculate total rows
        max_row = max(w.row + w.get_row_span() for w in layout.widgets)

        # Total available cells
        total_cells = max_row * layout.columns

        return {
            "widget_count": len(layout.widgets),
            "row_count": max_row,
            "total_cells": total_cells,
            "occupied_cells": occupied_cells,
            "utilization": round(occupied_cells / total_cells * 100, 1) if total_cells > 0 else 0,
        }


__all__ = ["LayoutService"]
