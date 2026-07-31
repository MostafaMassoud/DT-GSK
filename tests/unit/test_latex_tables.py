"""Unit tests for gsk_family.analysis.latex_tables.

Verifies the Friedman rank table (column layout, best-value bolding, ordering)
and the Wilcoxon summary table (per-dimension 7-column blocks).
"""

from __future__ import annotations

from gsk_family.analysis.latex_tables import (
    WilcoxonRow,
    friedman_ranks_latex,
    wilcoxon_summary_latex,
)


class TestFriedmanRanksLatex:
    def test_structure_and_bolding(self):
        ranks = {
            10: {"dt-gsk": 2.0, "GSK": 3.0, "AGSK": 1.5},
            30: {"dt-gsk": 1.0, "GSK": 2.0, "AGSK": 3.0},
        }
        tex = friedman_ranks_latex(ranks, proposed="dt-gsk")
        assert "\\begin{tabular}{lrrr}" in tex
        assert "\\textbf{D10}" in tex and "\\textbf{D30}" in tex
        assert "\\textbf{Overall}" in tex
        # Best (lowest) per column gets \bestval: AGSK at D10 (1.5), dt-gsk at D30 (1.0)
        assert "\\bestval{1.50}" in tex  # AGSK D10
        assert "\\bestval{1.00}" in tex  # dt-gsk D30
        # dt-gsk overall = (2+1)/2 = 1.5 is the best overall
        assert tex.index("dt-gsk") < tex.index("AGSK")  # ordered best-overall first

    def test_missing_dim_renders_dash(self):
        ranks = {10: {"dt-gsk": 1.0, "GSK": 2.0}, 30: {"dt-gsk": 1.0}}
        tex = friedman_ranks_latex(ranks)
        # GSK has no D30 entry -> a dash cell
        gsk_line = [ln for ln in tex.splitlines() if ln.startswith("GSK")][0]
        assert "---" in gsk_line


class TestWilcoxonSummaryLatex:
    def test_columns_and_rows(self):
        rows = {
            10: [
                WilcoxonRow("GSK", 0.0012, 0.0070, 20, 5, 4, 0.545, "+"),
                WilcoxonRow("AGSK", 0.30, 0.91, 13, 3, 13, 0.492, "="),
            ],
        }
        tex = wilcoxon_summary_latex(rows, proposed="dt-gsk")
        assert "dt-gsk vs GSK-family" in tex
        assert "\\multicolumn{7}{c}{\\textbf{D10}}" in tex
        assert "$A_{12}$" in tex
        gsk_line = [ln for ln in tex.splitlines() if ln.startswith("GSK ")][0]
        assert "0.0012" in gsk_line and "0.0070" in gsk_line
        assert "0.545" in gsk_line
        assert gsk_line.rstrip().endswith("+ \\\\")

    def test_tiny_pvalue_scientific(self):
        rows = {10: [WilcoxonRow("GSK", 2.5e-7, 1.5e-6, 28, 1, 0, 0.99, "+")]}
        tex = wilcoxon_summary_latex(rows)
        assert "2.5E-07" in tex
