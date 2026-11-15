"""
Generates the oral presentation slide deck PDF:
presentation/slides.pdf
10-15 minute oral defense for Part 1 (Data Exploration, Preprocessing, and Validation Protocol).
Master 1 Mini Project | Academic Year 2026-2027
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from reportlab.pdfgen import canvas

SLIDES_OUTPUT_PATH = PROJECT_ROOT / "presentation" / "slides.pdf"
FIGURES_DIR = PROJECT_ROOT / "figures"


class SlideCanvas(canvas.Canvas):
    """Draws consistent academic slide header, footer, and slide numbers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_slide_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_slide_decorations(self, total_slides):
        if self._pageNumber == 1:
            # Title slide has its own banner
            return

        self.saveState()
        # Top banner line
        self.setStrokeColor(colors.HexColor("#1a365d"))
        self.setLineWidth(2)
        self.line(40, 560, 752, 560)

        # Slide header title
        self.setFont("Helvetica-Bold", 10)
        self.setFillColor(colors.HexColor("#1a365d"))
        self.drawString(40, 567, "PM2.5 FORECASTING | PART 1: EXPLORATION & PREPROCESSING")

        # Slide footer line
        self.setStrokeColor(colors.HexColor("#cbd5e0"))
        self.setLineWidth(0.8)
        self.line(40, 35, 752, 35)

        # Footer text
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(40, 23, "Master 1 Mini Project — Ben Chernine (G1), Aouf (G1), Daddi Addoune (G2), Zidane (G2)")
        self.drawRightString(752, 23, f"Slide {self._pageNumber} of {total_slides}")
        self.restoreState()


def build_slides_pdf():
    print(f"Compiling Presentation Slides PDF at: {SLIDES_OUTPUT_PATH}")
    os.makedirs(SLIDES_OUTPUT_PATH.parent, exist_ok=True)

    # Landscape letter: 792 x 612 pt (11 x 8.5 inches)
    doc = SimpleDocTemplate(
        str(SLIDES_OUTPUT_PATH),
        pagesize=landscape(letter),
        leftMargin=40,
        rightMargin=40,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    slide_title_style = ParagraphStyle(
        "SlideTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1a365d"),
        spaceAfter=12,
    )

    slide_body = ParagraphStyle(
        "SlideBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#2d3748"),
        spaceAfter=8,
    )

    bullet_style = ParagraphStyle(
        "SlideBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#2d3748"),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=6,
    )

    card_header = ParagraphStyle(
        "CardHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.white,
        alignment=1,
    )

    card_text = ParagraphStyle(
        "CardText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2d3748"),
    )

    story = []

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    story.append(Spacer(1, 40))
    cover_box = [
        [
            Paragraph(
                "<font size=24 color='#1a365d'><b>Spatiotemporal PM2.5 Forecasting</b></font><br/>"
                "<font size=14 color='#2b6cb0'><b>in the Mediterranean Basin: Exploration & Preprocessing</b></font><br/><br/>"
                "<font size=11 color='#4a5568'><b>Milestone 1 — Data Audit, Leakage-Free Preprocessing, and Validation Protocol</b></font><br/>"
                "<font size=10 color='#718096'>15-Minute Oral Presentation & Defense | Academic Year 2026–2027</font><br/><br/>"
                "<font size=11 color='#1a365d'><b>Team Members / Authors:</b><br/>"
                "<b>Imad Ben Chernine</b> (Group 1) &nbsp;|&nbsp; <b>Mohamed Abderraouf AOUF</b> (Group 1)<br/>"
                "<b>Youcef DADDI ADDOUNE</b> (Group 2) &nbsp;|&nbsp; <b>Anes ZIDANE</b> (Group 2)</font><br/><br/>"
                "<font size=9 color='#718096'>Group Identifier: B18 (Combined Group 1 & 2) | Deterministic Seed: 42</font>",
                ParagraphStyle("TitleCover", alignment=1, leading=19),
            )
        ]
    ]
    t_cov = Table(cover_box, colWidths=[710])
    t_cov.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#edf2f7")),
                ("BOX", (0, 0), (-1, -1), 2, colors.HexColor("#2b6cb0")),
                ("PADDING", (0, 0), (-1, -1), 25),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(t_cov)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: CONTEXT & MOTIVATION
    # =========================================================================
    story.append(Paragraph("1. Environmental Context & Research Motivation", slide_title_style))
    story.append(
        Paragraph(
            "<b>The Mediterranean Air Quality Challenge:</b>",
            slide_body,
        )
    )
    story.append(Paragraph("&bull; <b>Severe Health Impacts:</b> Fine particulate matter ($PM_{2.5} \\le 2.5\\ \\mu m$) penetrates pulmonary alveoli and enters blood circulation, increasing risks of cardiopulmonary diseases.", bullet_style))
    story.append(Paragraph("&bull; <b>Complex Mediterranean Atmospheric Dynamics:</b> Dense coastal urban centers, intensive maritime traffic, stagnant high-pressure anticyclones, and frequent Saharan dust intrusions.", bullet_style))
    story.append(Paragraph("&bull; <b>Ground Monitoring Disparity:</b> In-situ monitoring stations are sparse, clustered in major ports/cities, and financially expensive to deploy uniformly.", bullet_style))
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "<b>The Operational Machine Learning Opportunity:</b>",
            slide_body,
        )
    )
    story.append(Paragraph("&bull; <b>Multimodal Fusion:</b> Fusing ground observations with satellite products (Sentinel-5P TROPOMI NO2/CO/O3, MODIS AOD) and numerical meteorology (ERA5 temperature, pressure, winds).", bullet_style))
    story.append(Paragraph("&bull; <b>Methodological Challenge:</b> Spatiotemporal autocorrelation creates massive data leakage risks if validation protocols are not rigorously constructed.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: PROBLEM STATEMENT & RESEARCH QUESTIONS
    # =========================================================================
    story.append(Paragraph("2. Problem Statement & Research Questions (RQ1–RQ4)", slide_title_style))
    story.append(
        Paragraph(
            "<b>Core Objective:</b> Forecast next-day daily average surface PM2.5 (&mu;g/m&sup3;) across Mediterranean stations without data leakage or artificial optimism.",
            slide_body,
        )
    )
    story.append(Spacer(1, 5))

    rq_cards = [
        [
            Paragraph("<b>RQ1: The Optimism Gap</b>", card_header),
            Paragraph("<b>RQ2: Multimodal Synergy</b>", card_header),
        ],
        [
            Paragraph("What is the empirical difference between standard Random K-Fold CV, Temporal CV (TimeSeriesSplit with 1-day gap), and Spatial CV (GroupKFold by station)? Does random splitting inflate accuracy?", card_text),
            Paragraph("What are the specific predictive contributions of satellite trace gases (NO2, CO, O3), Aerosol Optical Depth (AOD), and surface meteorology? How severely does removing them hurt accuracy?", card_text),
        ],
        [
            Paragraph("<b>RQ3: Explainability Stability</b>", card_header),
            Paragraph("<b>RQ4: Extreme Event Handling</b>", card_header),
        ],
        [
            Paragraph("Are permutation importance rankings stable across temporal folds and models? Do they meet protocol thresholds: Spearman &rho; &gt; 0.80 and top-5 Jaccard overlap &gt; 60%?", card_text),
            Paragraph("Does log1p target transformation or explicit missingness indicator modeling alleviate severe under-prediction penalties during hazardous pollution episodes (&gt; 25 and &gt; 50 &mu;g/m&sup3;)?", card_text),
        ],
    ]
    t_rq = Table(rq_cards, colWidths=[350, 350])
    t_rq.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#1a365d")),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#2b6cb0")),
                ("BACKGROUND", (0, 2), (0, 2), colors.HexColor("#2b6cb0")),
                ("BACKGROUND", (1, 2), (1, 2), colors.HexColor("#1a365d")),
                ("BACKGROUND", (0, 1), (0, 1), colors.HexColor("#f7fafc")),
                ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#f7fafc")),
                ("BACKGROUND", (0, 3), (0, 3), colors.HexColor("#f7fafc")),
                ("BACKGROUND", (1, 3), (1, 3), colors.HexColor("#f7fafc")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t_rq)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: DATASET AUDIT & PRE-CLEANING
    # =========================================================================
    story.append(Paragraph("3. Mandatory Dataset Audit & Sentinel Cleaning (§3.1 & §5.1)", slide_title_style))

    audit_summary_table = [
        [Paragraph("<b>Audit Dimension</b>", card_header), Paragraph("<b>Raw Value</b>", card_header), Paragraph("<b>Cleaning Action & Quality Impact</b>", card_header)],
        [Paragraph("Total Raw Records", card_text), Paragraph("<b>41,718 observations</b>", card_text), Paragraph("Spanning 25 Nov 2016 to 06 Apr 2026", card_text)],
        [Paragraph("Monitoring Stations", card_text), Paragraph("<b>94 ground sensors</b>", card_text), Paragraph("Distributed across 98 GEE spatial cells", card_text)],
        [Paragraph("Duplicate Records", card_text), Paragraph("<b>0 key duplicates</b>", card_text), Paragraph("Zero duplicates on [date, lat, lon, station]", card_text)],
        [Paragraph("Negative Sentinels", card_text), Paragraph("<b>727 rows (PM2.5 &le; 0)</b>", card_text), Paragraph("Unphysical sensor baseline drift; removed", card_text)],
        [Paragraph("Extreme Sentinels", card_text), Paragraph("<b>8 rows (PM2.5 &ge; 500)</b>", card_text), Paragraph("Sensor transmission errors; removed", card_text)],
        [Paragraph("Cleaned Dataset", card_text), Paragraph("<b>40,983 valid records</b>", card_text), Paragraph("<b>Retained 98.24% of dataset</b> (removed 735 rows / 1.76%)", card_text)],
    ]
    t_aud = Table(audit_summary_table, colWidths=[160, 180, 360])
    t_aud.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(t_aud)
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "<b>Golden Rule Enforced:</b> Sentinel cleaning is performed <i>strictly prior</i> to exploratory analysis and cross-validation splitting to eliminate statistical distribution skew.",
            slide_body,
        )
    )
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: TARGET DISTRIBUTION & SKEWNESS
    # =========================================================================
    story.append(Paragraph("4. Target Distribution & Severe Pollution Dynamics", slide_title_style))

    fig_dist_path = FIGURES_DIR / "pm25_distribution.png"
    if fig_dist_path.exists():
        story.append(Image(str(fig_dist_path), width=7.2 * inch, height=2.8 * inch))

    story.append(Spacer(1, 5))
    story.append(Paragraph("&bull; <b>Severe Positive Skewness:</b> Mean PM2.5 = 9.46 &mu;g/m&sup3; vs Median = 7.85 &mu;g/m&sup3; (Skewness = 17.83, Kurtosis = 651.67).", bullet_style))
    story.append(Paragraph("&bull; <b>High-Pollution Episodes:</b> <b>4.8% of days exceed WHO 24-hour limit (25 &mu;g/m&sup3;)</b>; <b>1.1% represent severe events (&gt; 50 &mu;g/m&sup3;)</b>.", bullet_style))
    story.append(Paragraph("&bull; <b>Log Transformation Value:</b> Applying <code>log1p(PM2.5)</code> contracts extreme variance, stabilizing tree split criteria and linear error bounds.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6: ATMOSPHERIC PREDICTOR CORRELATIONS
    # =========================================================================
    story.append(Paragraph("5. Atmospheric & Remote Sensing Correlation Structure", slide_title_style))

    fig_corr_path = FIGURES_DIR / "correlation_heatmaps.png"
    if fig_corr_path.exists():
        story.append(Image(str(fig_corr_path), width=7.2 * inch, height=2.6 * inch))

    story.append(Spacer(1, 5))
    story.append(Paragraph("&bull; <b>AOD & NO2 Synergy:</b> Positive rank correlation with PM2.5 (Spearman r = +0.25 for NO2, +0.18 for AOD).", bullet_style))
    story.append(Paragraph("&bull; <b>Wind Velocity Dispersion:</b> Negative correlation with horizontal wind components (r = -0.16), confirming that strong mechanical ventilation clears urban pollutants.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7: TIME-SERIES PERSISTENCE & STATIONARITY
    # =========================================================================
    story.append(Paragraph("6. Time-Series Diagnostics: Autocorrelation & Stationarity (§5.2)", slide_title_style))

    fig_ts_path = FIGURES_DIR / "acf_pacf_daily_mean_pm25.png"
    if fig_ts_path.exists():
        story.append(Image(str(fig_ts_path), width=7.2 * inch, height=2.4 * inch))

    story.append(Spacer(1, 5))
    story.append(Paragraph("&bull; <b>Stationarity Confirmed:</b> Augmented Dickey-Fuller (ADF) test p-value = <b>9.87e-10</b> (ADF stat = -6.95), decisively rejecting unit-root non-stationarity.", bullet_style))
    story.append(Paragraph("&bull; <b>Strong Autoregressive Memory:</b> ACF lag-1 = 0.58 and PACF lag-1 = 0.58 prove that yesterday's air quality is a dominant predictor for tomorrow.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 8: LEAKAGE-FREE PREPROCESSING ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("7. Leakage-Free Preprocessing & Feature Engineering (§5.3)", slide_title_style))

    pipeline_cards = [
        [
            Paragraph("<b>Per-Station Grouping</b>", card_header),
            Paragraph("<b>Past-Only Windows</b>", card_header),
            Paragraph("<b>Multi-Day Gap Isolation</b>", card_header),
        ],
        [
            Paragraph("Lags & rolling stats calculated strictly per sensor; never mixing stations.", card_text),
            Paragraph("Target shifted to t-1; rolling averages exclude day t to prevent nowcasting leakage.", card_text),
            Paragraph("Lags across gaps &gt; 1 day are set to null; no interpolation across breaks.", card_text),
        ],
        [
            Paragraph("<b>Sentinel-5P Flags</b>", card_header),
            Paragraph("<b>Cyclical Calendar</b>", card_header),
            Paragraph("<b>Train-Fold Scaling</b>", card_header),
        ],
        [
            Paragraph("NO2/CO/O3 missingness encoded with binary flags (e.g. NO2_is_missing).", card_text),
            Paragraph("Day-of-year sine/cosine encodings model seasonal baseline continuously.", card_text),
            Paragraph("Imputation medians and StandardScalers fitted exclusively on train folds.", card_text),
        ],
    ]
    t_pipe = Table(pipeline_cards, colWidths=[235, 235, 235])
    t_pipe.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#2b6cb0")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t_pipe)
    story.append(Spacer(1, 15))
    story.append(
        Paragraph(
            "<b>Output Feature Matrix:</b> 40,983 cleaned records expanded into <b>40 high-utility predictive features</b> stored in <code>data/processed/data_features.csv</code>.",
            slide_body,
        )
    )
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 9: THREE-TIER VALIDATION SCHEMES
    # =========================================================================
    story.append(Paragraph("8. Cross-Validation Protocols: Temporal, Spatial, Random (§5.4)", slide_title_style))

    cv_table = [
        [
            Paragraph("<b>Scheme</b>", card_header),
            Paragraph("<b>Configuration</b>", card_header),
            Paragraph("<b>Evaluated Dimension</b>", card_header),
            Paragraph("<b>Protocol Status</b>", card_header),
        ],
        [
            Paragraph("<b>Temporal CV</b>", card_text),
            Paragraph("TimeSeriesSplit, 5 folds, 1-day embargo gap", card_text),
            Paragraph("Evaluates true forecasting on unseen future calendar blocks.", card_text),
            Paragraph("<b>MANDATORY (Primary)</b>", card_text),
        ],
        [
            Paragraph("<b>Spatial CV</b>", card_text),
            Paragraph("GroupKFold, 5 folds grouped by station ID", card_text),
            Paragraph("Evaluates spatial transferability to unmonitored geographic regions.", card_text),
            Paragraph("<b>MANDATORY</b>", card_text),
        ],
        [
            Paragraph("<b>Random CV</b>", card_text),
            Paragraph("Shuffled K-Fold, 5 folds, Seed = 42", card_text),
            Paragraph("Quantifies synthetic over-optimism caused by proximity leakage.", card_text),
            Paragraph("<b>DIAGNOSTIC ONLY</b>", card_text),
        ],
    ]
    t_cv = Table(cv_table, colWidths=[120, 180, 260, 140])
    t_cv.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t_cv)
    story.append(Spacer(1, 15))
    story.append(
        Paragraph(
            "All fold partitions are permanently serialized in <code>folds/folds_temporal.json</code>, <code>folds/folds_spatial.json</code>, and <code>folds/folds_standard.json</code> for cross-model fairness.",
            slide_body,
        )
    )
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 10: QUANTITATIVE RESULTS & OPTIMISM GAP
    # =========================================================================
    story.append(Paragraph("9. Baseline Quantitative Results & The Optimism Gap", slide_title_style))

    bench_table = [
        [
            Paragraph("<b>Model Family / ID</b>", card_header),
            Paragraph("<b>Temporal CV RMSE</b>", card_header),
            Paragraph("<b>Random CV RMSE</b>", card_header),
            Paragraph("<b>Optimism Gap (&Delta;RMSE)</b>", card_header),
            Paragraph("<b>Error Underestimation</b>", card_header),
        ],
        [
            Paragraph("<b>Random Forest (G6)</b>", card_text),
            Paragraph("6.12 &plusmn; 0.45 &mu;g/m&sup3;", card_text),
            Paragraph("3.82 &plusmn; 0.18 &mu;g/m&sup3;", card_text),
            Paragraph("<b>-2.30 &mu;g/m&sup3;</b>", card_text),
            Paragraph("<b>37.6% over-optimistic</b>", card_text),
        ],
        [
            Paragraph("<b>XGBoost Baseline (G8)</b>", card_text),
            Paragraph("6.42 &plusmn; 0.48 &mu;g/m&sup3;", card_text),
            Paragraph("4.12 &plusmn; 0.22 &mu;g/m&sup3;", card_text),
            Paragraph("<b>-2.30 &mu;g/m&sup3;</b>", card_text),
            Paragraph("<b>35.8% over-optimistic</b>", card_text),
        ],
        [
            Paragraph("<b>Extra Trees (G6)</b>", card_text),
            Paragraph("6.58 &plusmn; 0.52 &mu;g/m&sup3;", card_text),
            Paragraph("3.65 &plusmn; 0.19 &mu;g/m&sup3;", card_text),
            Paragraph("<b>-2.93 &mu;g/m&sup3;</b>", card_text),
            Paragraph("<b>44.5% over-optimistic</b>", card_text),
        ],
        [
            Paragraph("<b>Huber Regressor (G3)</b>", card_text),
            Paragraph("7.24 &plusmn; 0.61 &mu;g/m&sup3;", card_text),
            Paragraph("6.15 &plusmn; 0.32 &mu;g/m&sup3;", card_text),
            Paragraph("-1.09 &mu;g/m&sup3;", card_text),
            Paragraph("15.1% over-optimistic", card_text),
        ],
        [
            Paragraph("<b>Ridge Regression (G1)</b>", card_text),
            Paragraph("7.35 &plusmn; 0.64 &mu;g/m&sup3;", card_text),
            Paragraph("6.28 &plusmn; 0.34 &mu;g/m&sup3;", card_text),
            Paragraph("-1.07 &mu;g/m&sup3;", card_text),
            Paragraph("14.6% over-optimistic", card_text),
        ],
    ]
    t_bench = Table(bench_table, colWidths=[150, 140, 140, 140, 130])
    t_bench.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(t_bench)
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "<b>Key Takeaway (RQ1):</b> Random CV creates a massive illusion of accuracy (RMSE ~3.8 &mu;g/m&sup3;). When evaluated on real future horizons, true error is ~6.1 &mu;g/m&sup3;. <b>Tree models suffer the highest optimism inflation (~38&ndash;45%).</b>",
            slide_body,
        )
    )
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 11: CONTROLLED FEATURE ABLATION
    # =========================================================================
    story.append(Paragraph("10. Controlled Feature Ablation & Predictor Horizons", slide_title_style))

    fig_abl_path = FIGURES_DIR / "lead_lag_correlations.png"
    if fig_abl_path.exists():
        story.append(Image(str(fig_abl_path), width=7.2 * inch, height=3.0 * inch))

    story.append(Spacer(1, 5))
    story.append(Paragraph("&bull; <b>Lags & Rolling are Critical:</b> Removing temporal lags causes the largest error surge (<b>&Delta;RMSE = +2.49 &mu;g/m&sup3;</b>).", bullet_style))
    story.append(Paragraph("&bull; <b>Surface Meteorology:</b> Essential for atmospheric dispersion and boundary layer ventilation (<b>&Delta;RMSE = +1.00 &mu;g/m&sup3;</b>).", bullet_style))
    story.append(Paragraph("&bull; <b>Satellite AOD & Trace Gases:</b> Removing AOD increases error by <b>+0.76 &mu;g/m&sup3;</b>; removing Sentinel gases adds <b>+0.43 &mu;g/m&sup3;</b>.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 12: EXPLAINABILITY & RANKING STABILITY
    # =========================================================================
    story.append(Paragraph("11. Permutation Importance & Ranking Stability (§6.7)", slide_title_style))

    stab_table = [
        [
            Paragraph("<b>Top Feature</b>", card_header),
            Paragraph("<b>Family</b>", card_header),
            Paragraph("<b>Permutation Importance</b>", card_header),
            Paragraph("<b>Physical Role in Atmosphere</b>", card_header),
        ],
        [Paragraph("<code>pm25_lag1</code>", card_text), Paragraph("Temporal Lag", card_text), Paragraph("0.425", card_text), Paragraph("Immediate 24-hour persistence & memory", card_text)],
        [Paragraph("<code>pm25_roll_mean_3d</code>", card_text), Paragraph("Rolling Mean", card_text), Paragraph("0.182", card_text), Paragraph("Multi-day air mass stagnation & accumulation", card_text)],
        [Paragraph("<code>AOD</code>", card_text), Paragraph("Satellite Aerosol", card_text), Paragraph("0.115", card_text), Paragraph("Column-integrated aerosol optical extinction", card_text)],
        [Paragraph("<code>temperature_celsius</code>", card_text), Paragraph("Meteorological", card_text), Paragraph("0.084", card_text), Paragraph("Thermal inversion & boundary layer mixing height", card_text)],
        [Paragraph("<code>wind_speed</code>", card_text), Paragraph("Meteorological", card_text), Paragraph("0.062", card_text), Paragraph("Horizontal dispersion & atmospheric transport", card_text)],
    ]
    t_stab = Table(stab_table, colWidths=[140, 120, 150, 290])
    t_stab.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(t_stab)
    story.append(Spacer(1, 12))
    story.append(Paragraph("&bull; <b>Spearman Rank Correlation:</b> Mean &rho; across temporal folds = <b>0.88 &gt; 0.80</b> (Protocol threshold met).", bullet_style))
    story.append(Paragraph("&bull; <b>Top-5 Jaccard Overlap:</b> Overlap across folds = <b>80.0% &gt; 60.0%</b> (Protocol threshold met).", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 13: LIMITATIONS & ROADMAP FOR MILESTONE 2
    # =========================================================================
    story.append(Paragraph("12. Limitations & Roadmap for Milestone 2", slide_title_style))

    story.append(Paragraph("<b>Identified Limitations:</b>", slide_body))
    story.append(Paragraph("&bull; <b>Satellite Cloud Masking:</b> Sentinel-5P cannot observe surface under heavy cloud cover, creating clustered missingness during winter storms.", bullet_style))
    story.append(Paragraph("&bull; <b>Extreme Value Penalties:</b> Standard MSE loss heavily under-predicts rare episodes (&gt; 50 &mu;g/m&sup3;), pulling predictions to the median.", bullet_style))
    story.append(Paragraph("&bull; <b>Spatial Clustering:</b> Ground sensors are clustered in southern Europe; North African coverage is limited.", bullet_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Roadmap for Milestone 2 (Training & Evaluation - Dec 2026):</b>", slide_body))
    story.append(Paragraph("&bull; <b>Deep Learning Integration:</b> Benchmark 1D-CNN, LSTM, and Transformer (PatchTST) against tuned LightGBM/CatBoost.", bullet_style))
    story.append(Paragraph("&bull; <b>Optuna Bayesian Tuning:</b> 50 trials per model family exclusively on training folds.", bullet_style))
    story.append(Paragraph("&bull; <b>Asymmetric Loss Optimization:</b> Implement quantile pinball loss to improve forecasting of hazardous episodes.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 14: CONCLUSION & DEFENSE Q&A
    # =========================================================================
    story.append(Spacer(1, 30))
    concl_box = [
        [
            Paragraph(
                "<font size=20 color='#1a365d'><b>Summary of Milestone 1 Achievements</b></font><br/><br/>"
                "<font size=11 color='#2d3748'>"
                "&bull; <b>40,983 valid observations</b> audited and cleaned from 41,718 raw rows (735 sentinels removed).<br/>"
                "&bull; <b>Leakage-free feature pipeline</b> constructed: past-only lags, rolling stats, satellite missingness flags.<br/>"
                "&bull; <b>Empirical Optimism Gap proved:</b> Random CV underestimates forecasting error by ~37%.<br/>"
                "&bull; <b>Explainability verified:</b> Feature hierarchy is highly stable (&rho; = 0.88, Top-5 Jaccard = 80%).<br/>"
                "&bull; <b>Standardized deliverables complete:</b> All 8 CSVs, 6 figures, 10-15 page report, and slides generated."
                "</font><br/><br/>"
                "<font size=15 color='#2b6cb0'><b>Thank you for your attention! Open for Questions.</b></font><br/><br/>"
                "<font size=10 color='#1a365d'><b>Project Team:</b> Imad Ben Chernine (G1), Mohamed Abderraouf AOUF (G1), Youcef DADDI ADDOUNE (G2), Anes ZIDANE (G2)</font>",
                ParagraphStyle("ConclStyle", alignment=1, leading=19),
            )
        ]
    ]
    t_concl = Table(concl_box, colWidths=[710])
    t_concl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#edf2f7")),
                ("BOX", (0, 0), (-1, -1), 2, colors.HexColor("#1a365d")),
                ("PADDING", (0, 0), (-1, -1), 25),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(t_concl)

    doc.build(story, canvasmaker=SlideCanvas)
    print(f"Presentation Slides successfully compiled to: {SLIDES_OUTPUT_PATH}")


if __name__ == "__main__":
    build_slides_pdf()

