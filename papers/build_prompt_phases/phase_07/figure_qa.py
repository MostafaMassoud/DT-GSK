"""Gate 7 automated figure QA (CR-0003).

Checks every Phase 7 produced figure (the 34 PNG+PDF pairs bound in
papers/governance/artifact_binding.csv) for:
  - horizontal/vertical overflow (content touching the canvas border)
  - clipped text (border-density heuristic)
  - legend presence and P1 ordering (GSK, AGSK, APGSK, FDB-AGSK,
    ATMALS-GSK, eGSK, DT-GSK)
  - 7-series count per convergence panel (cross-checked against the
    generators' companion *_missing.log files) or disclosed absence
  - P3 stroke-colour map presence (Okabe-Ito 5 + grey 0.6 + black)
  - correct function/dimension panel labels vs filename (panel titles
    extracted from the PDF text layer, expected set derived from the
    companion missing.log)
  - duplicate figures (byte hash) and duplicate/empty panels
  - axis-scaling sanity: log-error y-axis for convergence panels, with
    the disclosed linear fallback on negative-objective CEC2011 panels
  - raster resolution >= 200 dpi (PNG pixels vs PDF MediaBox)
  - no /CreationDate in any produced PDF (determinism)
  - no 'ablation' / standalone 'EGSK' / 'holdout' token in any figure
    text layer

Read-only over figures; writes nothing (report is authored separately in
visual_qa_report.md from this script's stdout). No results/ access.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[3]
FIG = ROOT / "papers" / "figures"

P1 = ["GSK", "AGSK", "APGSK", "FDB-AGSK", "ATMALS-GSK", "eGSK", "DT-GSK"]
P1_LEGEND_LINE = " ".join(P1)

# P3 colours (matplotlib writes 10-dp fractions; grey/black go out via G/g).
P3_RGB = {
    "agsk #E69F00": (0.9019607843, 0.6235294118, 0.0),
    "apgsk #56B4E9": (0.337254902, 0.7058823529, 0.9137254902),
    "fdb-agsk #009E73": (0.0, 0.6196078431, 0.4509803922),
    "atmals-gsk #CC79A7": (0.8, 0.4745098039, 0.6549019608),
    "egsk #0072B2": (0.0, 0.4470588235, 0.6980392157),
}
P3_GRAY = {"gsk #999999": 0.6, "dt-gsk #000000": 0.0}

findings: list[tuple[str, str, str]] = []  # (severity, figure, message)
passes: list[str] = []


def note(sev: str, fig: str, msg: str) -> None:
    findings.append((sev, fig, msg))


def ok(msg: str) -> None:
    passes.append(msg)


def parse_missing_log(path: Path) -> dict[str, dict[str, str]]:
    """grid -> {panel_title_func: 'n/7'} from 'grid:Fk_Dd: n/7' lines."""
    grids: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s+(\S+):(F\d+)_D(\d+): (\d)/7$", line)
        if m:
            grids.setdefault(m.group(1), {})[f"{m.group(2)} (D={m.group(3)})"] = (
                m.group(4)
            )
    return grids


def pdf_text_and_colors(pdf: Path) -> tuple[str, set, set, bool, float, float]:
    r = PdfReader(str(pdf))
    page = r.pages[0]
    text = page.extract_text()
    raw = page.get_contents().get_data().decode("latin-1")
    rgb = {
        tuple(round(float(v), 6) for v in m)
        for m in re.findall(r"([\d.]+) ([\d.]+) ([\d.]+) RG", raw)
    }
    gray = {round(float(m), 6) for m in re.findall(r"(?:^|\s)([\d.]+) G(?:\s|$)", raw)}
    has_creationdate = any(
        "/CreationDate" in str(r.metadata or {}) for _ in [0]
    ) or b"/CreationDate" in pdf.read_bytes()
    mb = page.mediabox
    return text, rgb, gray, has_creationdate, float(mb.width), float(mb.height)


def check_png(png: Path, mb_w_pt: float, mb_h_pt: float, fig: str) -> None:
    im = Image.open(png)
    w, h = im.size
    dpi = min(w / (mb_w_pt / 72.0), h / (mb_h_pt / 72.0))
    if dpi < 199.0:
        note("major", fig, f"raster resolution {dpi:.0f} dpi < 200 dpi")
    else:
        ok(f"{fig}: PNG {w}x{h}, effective {dpi:.0f} dpi (>=200)")
    g = im.convert("L")
    px = g.load()
    borders = {
        "top": [px[x, 0] for x in range(w)],
        "bottom": [px[x, h - 1] for x in range(w)],
        "left": [px[0, y] for y in range(h)],
        "right": [px[w - 1, y] for y in range(h)],
    }
    for side, vals in borders.items():
        frac = sum(1 for v in vals if v < 250) / len(vals)
        if frac > 0.30:
            note(
                "major",
                fig,
                f"possible {side} overflow/clipping: {frac:.0%} of border "
                "pixels are non-background",
            )
    # empty-figure check
    hist = g.histogram()
    nonwhite = sum(hist[:250]) / (w * h)
    if nonwhite < 0.001:
        note("critical", fig, "figure appears empty (<0.1% non-white pixels)")


def check_colors(rgb: set, gray: set, fig: str, series_fig: bool) -> None:
    if not series_fig:
        return
    missing = []
    for name, exp in P3_RGB.items():
        if not any(all(abs(c[i] - exp[i]) < 0.02 for i in range(3)) for c in rgb):
            missing.append(name)
    for name, exp in P3_GRAY.items():
        hit = any(abs(gv - exp) < 0.02 for gv in gray) or any(
            all(abs(c[i] - exp) < 0.02 for i in range(3)) for c in rgb
        )
        if not hit:
            missing.append(name)
    if missing:
        note("major", fig, f"P3 stroke colours not found: {', '.join(missing)}")
    else:
        ok(f"{fig}: all 7 P3 stroke colours present (5 Okabe-Ito RGB + grey + black)")


def check_legend_line(text: str, fig: str) -> None:
    if P1_LEGEND_LINE in text.replace("\n", " "):
        ok(f"{fig}: shared legend present in exact P1 order")
    else:
        note("major", fig, "P1-ordered shared legend line not found in text layer")


def log_axis_panels(text: str) -> int:
    """Count log-scale tick evidence: 10^k tokens ('10 12', '103', 'x 10 k')."""
    t = text.replace("�", "x")
    n = len(re.findall(r"\b10 ?\d{1,2}\b", t))
    return n


ALG_FILES = {}


def main() -> int:
    logs = {
        "cec2017": parse_missing_log(FIG / "convergence" / "cec2017_missing.log"),
        "cec2011": parse_missing_log(FIG / "convergence" / "cec2011_missing.log"),
        "cec2013": parse_missing_log(FIG / "convergence" / "cec2013_missing.log"),
    }
    total_panels = sum(len(v) for lg in logs.values() for v in lg.values())
    bad = [
        (g, p, c)
        for lg in logs.values()
        for g, panels in lg.items()
        for p, c in panels.items()
        if c != "7"
    ]
    if bad:
        for g, p, c in bad:
            note("critical", g, f"panel {p} carries {c}/7 series (undisclosed loss)")
    else:
        ok(
            f"missing-log cross-check: {total_panels} convergence panels, "
            "all 7/7 series, zero disclosed absences"
        )

    convergence = sorted((FIG / "convergence").glob("*.pdf"))
    hashes: dict[str, str] = {}

    for pdf in convergence:
        fig = pdf.stem
        suite = "cec2011" if "cec2011" in fig else (
            "cec2013" if "cec2013" in fig else "cec2017"
        )
        expected_panels = logs[suite].get(fig)
        if expected_panels is None:
            note("critical", fig, "grid not present in its companion missing.log")
            continue
        png = pdf.with_suffix(".png")
        if not png.exists():
            note("major", fig, "PNG alternate missing")
            continue
        text, rgb, gray, cdate, w_pt, h_pt = pdf_text_and_colors(pdf)
        if cdate:
            note("major", fig, "PDF contains /CreationDate (determinism breach)")
        check_png(png, w_pt, h_pt, fig)
        # panel titles vs filename-derived expectation (from missing.log)
        titles = re.findall(r"F\d+ \(D=\d+\)", text)
        if sorted(titles) != sorted(expected_panels):
            note(
                "critical",
                fig,
                f"panel titles {sorted(titles)} != expected "
                f"{sorted(expected_panels)}",
            )
        elif len(titles) != len(set(titles)):
            note("critical", fig, "duplicate panel titles inside grid")
        else:
            ok(f"{fig}: {len(titles)} panel titles match expected functions/dims")
        # dimension token in filename vs titles
        mdim = re.search(r"D(\d+)", fig)
        if mdim and suite != "cec2011":
            if not all(f"(D={mdim.group(1)})" in t for t in titles):
                note("critical", fig, "panel dimension label mismatch vs filename")
        check_legend_line(text, fig)
        check_colors(rgb, gray, fig, series_fig=True)
        # axis sanity
        n_linear = text.count("linear scale (negative objectives)")
        n_log_tokens = log_axis_panels(text)
        n_panels = len(expected_panels)
        if suite == "cec2011":
            exp_linear = {"cec2011_a": 3, "cec2011_b": 1, "cec2011_c": 0}[fig]
            if n_linear != exp_linear:
                note(
                    "major",
                    fig,
                    f"{n_linear} disclosed linear panels, expected {exp_linear} "
                    "(F2/F5/F6/F10 negative optima)",
                )
            else:
                ok(
                    f"{fig}: log y-axis with {exp_linear} disclosed linear "
                    "fallback panel(s)"
                )
        else:
            if n_linear:
                note("major", fig, "unexpected linear-scale disclosure on CEC17/13")
            if n_log_tokens < n_panels:  # at least ~1 power-of-ten tick per panel
                note(
                    "minor",
                    fig,
                    f"weak log-axis evidence ({n_log_tokens} power-of-ten tick "
                    f"tokens over {n_panels} panels) - verify visually",
                )
            else:
                ok(f"{fig}: log-error y-axis evidence ({n_log_tokens} 10^k ticks)")
        hashes.setdefault(hashlib.sha256(png.read_bytes()).hexdigest(), fig)

    # ---- Nemenyi CD diagrams ----
    for dim in (10, 30, 50, 100):
        fig = f"nemenyi_cd_cec2017_D{dim}"
        pdf = FIG / "nemenyi" / f"{fig}.pdf"
        png = pdf.with_suffix(".png")
        text, rgb, gray, cdate, w_pt, h_pt = pdf_text_and_colors(pdf)
        if cdate:
            note("major", fig, "PDF contains /CreationDate (determinism breach)")
        check_png(png, w_pt, h_pt, fig)
        missing_names = [a for a in P1 if a not in text]
        if missing_names:
            note("critical", fig, f"algorithm names missing: {missing_names}")
        if "CD = 1.67" not in text:
            note("critical", fig, "CD scale-bar value 'CD = 1.67' not found")
        if f"D = {dim}" not in text:
            note("critical", fig, "dimension label mismatch vs filename")
        if "k = 7, N = 29" not in text:
            note("major", fig, "k/N annotation missing")
        ranks = re.findall(r"\b\d\.\d\d\b", text)
        if len([r_ for r_ in ranks if r_ not in ("1.67", "0.05")]) != 7:
            note("major", fig, f"expected 7 rank labels, found {ranks}")
        else:
            ok(f"{fig}: 7 algorithms, 7 rank labels, CD=1.67, D={dim} label")
        hashes.setdefault(hashlib.sha256(png.read_bytes()).hexdigest(), fig)

    # ---- Rank charts ----
    rank_specs = {
        "rank_vs_dim_cec2017": ("Friedman Mean Rank vs. Dimension", True, True),
        "cec2017_mean_ranks": ("Friedman Mean Ranks per Dimension", True, False),
        "cec2011_ranks": ("CEC 2011, 22 Problems", False, False),
        "friedman_gsk_family": ("CEC 2017, Overall", False, False),
    }
    for fig, (title, p1_order, line_colors) in rank_specs.items():
        pdf = FIG / "ranks" / f"{fig}.pdf"
        png = pdf.with_suffix(".png")
        text, rgb, gray, cdate, w_pt, h_pt = pdf_text_and_colors(pdf)
        if cdate:
            note("major", fig, "PDF contains /CreationDate (determinism breach)")
        check_png(png, w_pt, h_pt, fig)
        if title not in text:
            note("major", fig, f"expected title fragment '{title}' not found")
        missing_names = [a for a in P1 if a not in text]
        if missing_names:
            note("critical", fig, f"algorithm names missing: {missing_names}")
        else:
            ok(f"{fig}: all 7 P1 algorithm names present; title OK")
        if p1_order:
            joined = "\n".join(P1)
            if joined not in text:
                note("major", fig, "legend entries not in P1 order")
        if line_colors:
            check_colors(rgb, gray, fig, series_fig=True)
        hashes.setdefault(hashlib.sha256(png.read_bytes()).hexdigest(), fig)

    # ---- Conceptual figures ----
    concept_specs = {
        "fig_architecture": ["SGSM", "eigenframe", "deep-stall"],
        "fig_sgsm_mechanism": ["SGSM", "E10"],
        "fig_dim_gating": ["dimension tier", "D10 D30 D50 D100"],
        "fig_taxonomy": ["ISM"],
        "fig_nlpsr_schedule": ["Budget fraction", "NLPSR"],
    }
    for fig, keywords in concept_specs.items():
        pdf = FIG / "concept" / f"{fig}.pdf"
        png = pdf.with_suffix(".png")
        text, rgb, gray, cdate, w_pt, h_pt = pdf_text_and_colors(pdf)
        if cdate:
            note("major", fig, "PDF contains /CreationDate (determinism breach)")
        check_png(png, w_pt, h_pt, fig)
        miss = [k for k in keywords if k not in text]
        if miss:
            note("major", fig, f"expected content keywords missing: {miss}")
        else:
            ok(f"{fig}: content keywords present ({', '.join(keywords)})")
        hashes.setdefault(hashlib.sha256(png.read_bytes()).hexdigest(), fig)

    # ---- duplicates + forbidden tokens over every produced text layer ----
    if len(hashes) != 34:
        note(
            "critical",
            "global",
            f"duplicate PNG detected: {len(hashes)} unique hashes over 34 figures",
        )
    else:
        ok("34/34 produced figures byte-unique (no duplicated figure)")

    all_dirs = ["convergence", "nemenyi", "ranks", "concept"]
    offenders = []
    for d in all_dirs:
        for pdf in (FIG / d).glob("*.pdf"):
            if d == "ranks" and pdf.stem == "nemenyi_cd_d50":
                continue  # superseded legacy, excluded from binding
            try:
                text = PdfReader(str(pdf)).pages[0].extract_text()
            except Exception as exc:  # pragma: no cover
                note("major", pdf.stem, f"text extraction failed: {exc}")
                continue
            if re.search(r"ablation", text, re.I):
                offenders.append((pdf.stem, "ablation"))
            if re.search(r"(?<![A-Za-z])EGSK", text):
                offenders.append((pdf.stem, "EGSK capitalization"))
            if re.search(r"hold[- ]?out", text, re.I):
                offenders.append((pdf.stem, "holdout"))
    if offenders:
        for f, tok in offenders:
            note("critical", f, f"forbidden token in figure text: {tok}")
    else:
        ok(
            "zero 'ablation' / standalone 'EGSK' / 'holdout' tokens in any "
            "produced figure text layer"
        )

    # ---- report ----
    print(f"PASS checks: {len(passes)}")
    for p in passes:
        print(f"  [ok] {p}")
    print(f"FINDINGS: {len(findings)}")
    for sev, fig, msg in findings:
        print(f"  [{sev.upper()}] {fig}: {msg}")
    crit = sum(1 for s, _, _ in findings if s == "critical")
    major = sum(1 for s, _, _ in findings if s == "major")
    print(f"SUMMARY: {crit} critical, {major} major, "
          f"{len(findings) - crit - major} minor")
    return 1 if crit or major else 0


if __name__ == "__main__":
    sys.exit(main())
