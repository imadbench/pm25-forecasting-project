"""
Academic Technical Report Generator: reports/technical_report.pdf
Master 1 Mini Project | Academic Year 2026-2027
Milestone 1: Data Exploration, Preprocessing & Validation Protocol
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from reportlab.lib.pagesizes import letter
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
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = PROJECT_ROOT / "reports" / "technical_report.pdf"
FIGURES_DIR = PROJECT_ROOT / "figures"
RESULTS_DIR = PROJECT_ROOT / "results"


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic total page count."""

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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))

        # Header
        self.drawString(
            54,
            750,
            "Master 1 Mini Project | PM2.5 Forecasting: Part 1 - Data Exploration & Preprocessing",
        )
        self.setStrokeColor(colors.HexColor("#cbd5e0"))
        self.setLineWidth(0.5)
        self.line(54, 744, 558, 744)

        # Footer
        self.line(54, 45, 558, 45)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 33, page_str)
        self.drawString(
            54, 33, "Academic Year 2026-2027 | Ben Chernine, AOUF, Daddi Addoune, Zidane"
        )
        self.restoreState()


def build_technical_report():
    print(f"Building Technical Report PDF at: {PDF_OUTPUT_PATH}")
    os.makedirs(PDF_OUTPUT_PATH.parent, exist_ok=True)

    doc = SimpleDocTemplate(
        str(PDF_OUTPUT_PATH),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=25,
        textColor=colors.HexColor("#1a365d"),
        alignment=1,
        spaceAfter=12,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2b6cb0"),
        alignment=1,
        spaceAfter=20,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1a365d"),
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#2d3748"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#2d3748"),
        spaceAfter=5,
        alignment=4,
    )

    callout_style = ParagraphStyle(
        "Callout",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2c5282"),
        spaceAfter=5,
    )

    caption_style = ParagraphStyle(
        "Caption",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#4a5568"),
        alignment=1,
        spaceAfter=6,
    )

    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1,
    )

    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        alignment=0,
    )

    table_cell_center = ParagraphStyle(
        "TableCellCenter",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        alignment=1,
    )

    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("MASTER 1 MINI PROJECT — TECHNICAL REPORT", subtitle_style))
    story.append(
        Paragraph(
            "Daily PM2.5 Forecasting in the Mediterranean Basin:<br/>Data Audit, Leakage-Free Preprocessing, and Validation Protocol",
            title_style,
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        HRFlowable(
            width="55%",
            thickness=1.5,
            color=colors.HexColor("#2b6cb0"),
            spaceAfter=15,
            spaceBefore=2,
        )
    )

    meta_text = (
        "<b>Academic Year:</b> 2026–2027 &nbsp;|&nbsp; <b>Degree:</b> Master 1 Artificial Intelligence & Data Science<br/>"
        "<b>Milestone:</b> Part 1 — Data Exploration, Preprocessing & Validation Protocol<br/>"
        "<b>Target Variable:</b> Daily Surface PM2.5 Concentration (&mu;g/m&sup3;)<br/>"
        "<b>Source Dataset:</b> Kaggle Air Quality – Mediterranean Basin (2016–2026)<br/>"
        "<b>Random Seed:</b> SEED = 42 (fixed across all splits and transformations)"
    )
    story.append(Paragraph(meta_text, body_style))
    story.append(Spacer(1, 8))

    # Authors Table
    authors_data = [
        [
            Paragraph("<b>Author / Student Name</b>", table_header),
            Paragraph("<b>Study Group</b>", table_header),
            Paragraph("<b>Academic Program</b>", table_header),
        ],
        [
            Paragraph("<b>Imad Ben Chernine</b>", table_cell),
            Paragraph("Group 1", table_cell_center),
            Paragraph("Master 1 Artificial Intelligence & Data Science", table_cell),
        ],
        [
            Paragraph("<b>Mohamed Abderraouf AOUF</b>", table_cell),
            Paragraph("Group 1", table_cell_center),
            Paragraph("Master 1 Artificial Intelligence & Data Science", table_cell),
        ],
        [
            Paragraph("<b>Youcef DADDI ADDOUNE</b>", table_cell),
            Paragraph("Group 2", table_cell_center),
            Paragraph("Master 1 Artificial Intelligence & Data Science", table_cell),
        ],
        [
            Paragraph("<b>Anes ZIDANE</b>", table_cell),
            Paragraph("Group 2", table_cell_center),
            Paragraph("Master 1 Artificial Intelligence & Data Science", table_cell),
        ],
    ]
    t_auth = Table(authors_data, colWidths=[200, 80, 220])
    t_auth.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("PADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t_auth)
    story.append(Spacer(1, 10))

    exec_summary_box = [
        [
            Paragraph(
                "<b>Executive Summary:</b> This technical report details Milestone 1 of our PM2.5 forecasting project in the Mediterranean Basin. We analyze a multi-source spatiotemporal dataset (2016–2026) combining ground-level air quality observations with satellite remote sensing (AOD, Sentinel-5P trace gases) and ERA5 meteorological reanalysis. We first perform an exhaustive data audit, eliminating 735 invalid records (negative readings and unphysical values &ge; 500 &mu;g/m&sup3;), leaving 40,983 valid observations from 91 stations. Time-series diagnostics reveal strong daily persistence (ACF lag 1 = 0.58) and stationary properties (ADF test p < 1e-15). To prevent future-to-past data leakage, all feature engineering (lags, rolling aggregates, cyclical day-of-year encodings) is strictly station-isolated and past-only. We separate the complete 2025 calendar year (8,149 rows) as an untouched holdout test set and construct three distinct cross-validation schemes on development data (31,286 rows): 5-fold expanding Temporal CV (with a 1-day embargo gap), 5-fold Spatial CV grouped by station, and 5-fold Random CV. All fold indices and engineered feature matrices are serialized to guarantee complete experimental reproducibility.",
                callout_style,
            )
        ]
    ]
    t_exec = Table(exec_summary_box, colWidths=[500])
    t_exec.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ebf8ff")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#bee3f8")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t_exec)
    story.append(Spacer(1, 15))

    toc_data = [
        [Paragraph("<b>Section</b>", table_header), Paragraph("<b>Contents</b>", table_header)],
        [Paragraph("1", table_cell_center), Paragraph("Introduction and Problem Formulation", table_cell)],
        [Paragraph("2", table_cell_center), Paragraph("Dataset Ingestion, Inventory, and Data Quality Audit", table_cell)],
        [Paragraph("3", table_cell_center), Paragraph("Target Distribution, Cleaning Protocols, and Extreme Events", table_cell)],
        [Paragraph("4", table_cell_center), Paragraph("Atmospheric Predictor Relationships and Multicollinearity Audit", table_cell)],
        [Paragraph("5", table_cell_center), Paragraph("Time-Series Diagnostics: Autocorrelation, Stationarity, and Drift", table_cell)],
        [Paragraph("6", table_cell_center), Paragraph("Leakage-Free Feature Engineering Architecture", table_cell)],
        [Paragraph("7", table_cell_center), Paragraph("Preprocessing Pipeline: Missingness Indicators and Robust Scaling", table_cell)],
        [Paragraph("8", table_cell_center), Paragraph("Spatiotemporal Validation Protocol and Test Holdout Design", table_cell)],
        [Paragraph("9", table_cell_center), Paragraph("Milestone 1 Deliverables Summary and Part 2 Modeling Roadmap", table_cell)],
        [Paragraph("10", table_cell_center), Paragraph("Reproducibility Environment and References", table_cell)],
    ]
    t_toc = Table(toc_data, colWidths=[50, 450])
    t_toc.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("PADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    story.append(t_toc)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: INTRODUCTION AND PROBLEM FORMULATION
    # =========================================================================
    story.append(Paragraph("1. Introduction and Problem Formulation", h1_style))
    story.append(
        Paragraph(
            "Fine particulate matter with an aerodynamic diameter under 2.5 micrometers (PM2.5) represents one of the most hazardous atmospheric pollutants. Its small size allows it to penetrate deep into the human respiratory tract and enter systemic circulation, contributing to chronic pulmonary and cardiovascular diseases. In the Mediterranean Basin, air quality dynamics are shaped by a complex interplay of localized anthropogenic emissions (dense urban transport, shipping routes, industrial hubs) and regional meteorological phenomena, including sea-breeze recirculations and periodic Saharan dust transport events.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "The operational goal of this project is to develop a <b>one-day-ahead (t+1) daily forecasting system</b> for surface PM2.5 concentrations across ground monitoring stations in the Mediterranean Basin. Ground monitoring networks provide high-precision measurements but suffer from limited geographic coverage and occasional temporal gaps. By combining historical station data with satellite remote sensing (Aerosol Optical Depth from MODIS, column trace gases from Sentinel-5P) and meteorological reanalysis (ERA5 surface temperature, barometric pressure, horizontal wind vectors), predictive models can capture both atmospheric persistence and regional dispersion.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>Milestone 1 Objectives:</b> This phase establishes the foundations of the forecasting pipeline. Our work focuses on four core priorities: (1) auditing raw data and removing corrupted measurements; (2) conducting spatiotemporal exploratory analysis to understand persistence, stationarity, and correlations; (3) engineering past-only predictive features without future-to-past data leakage; and (4) defining realistic cross-validation protocols that reflect true operational conditions.",
            body_style,
        )
    )
    story.append(Spacer(1, 4))

    # =========================================================================
    # SECTION 2: DATASET INGESTION, INVENTORY, AND QUALITY AUDIT
    # =========================================================================
    story.append(Paragraph("2. Dataset Ingestion, Inventory, and Data Quality Audit", h1_style))
    story.append(
        Paragraph(
            "We analyze the Kaggle benchmark dataset <i>Air Quality – Mediterranean Basin (2016–2026)</i>. The merged input table <code>combined_gee_pm25.csv</code> contains <b>41,718 records</b> across 15 attributes, spanning from 25 November 2016 to 06 April 2026 across <b>91 distinct ground monitoring stations</b>. Each record represents a daily observation linking ground air quality to coincident satellite and meteorological grid values.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "We ran a systematic data audit in <code>src/preprocessing.py</code> to verify data types, coordinate validity, and missingness patterns. The results are summarized in Table 1.",
            body_style,
        )
    )

    # Insert Table 1 from Exploratory_Data.csv
    eda_csv_path = RESULTS_DIR / "Exploratory_Data.csv"
    if eda_csv_path.exists():
        df_raw_eda = pd.read_csv(eda_csv_path)
        table_rows = [
            [
                Paragraph("<b>Variable</b>", table_header),
                Paragraph("<b>Unit</b>", table_header),
                Paragraph("<b>Valid Obs</b>", table_header),
                Paragraph("<b>Missing %</b>", table_header),
                Paragraph("<b>Mean &plusmn; Std</b>", table_header),
                Paragraph("<b>Median [IQR]</b>", table_header),
                Paragraph("<b>Min &ndash; Max</b>", table_header),
                Paragraph("<b>Skew / Kurt</b>", table_header),
            ]
        ]
        num_vars = ["pm25", "AOD", "NO2", "CO", "O3", "temperature_celsius", "pressure_mb", "wind_u", "wind_v"]
        unit_map = {
            "pm25": "&mu;g/m&sup3;",
            "AOD": "dimless",
            "NO2": "mol/m&sup2;",
            "CO": "mol/m&sup2;",
            "O3": "mol/m&sup2;",
            "temperature_celsius": "&deg;C",
            "pressure_mb": "hPa",
            "wind_u": "m/s",
            "wind_v": "m/s",
        }
        num_summary = df_raw_eda[df_raw_eda["section"] == "numeric_summary"]
        audit_summary = df_raw_eda[df_raw_eda["section"] == "audit"]
        for v in num_vars:
            v_metrics = dict(zip(num_summary[num_summary["variable"] == v]["metric"], num_summary[num_summary["variable"] == v]["value"]))
            v_audit = dict(zip(audit_summary[audit_summary["variable"] == v]["metric"], audit_summary[audit_summary["variable"] == v]["value"]))
            if not v_metrics:
                continue
            missing_pct = v_audit.get("missing_percentage", 0.0)
            missing_cnt = v_audit.get("missing_count", 0.0)
            valid_obs = int(41718 - missing_cnt)
            mean_val = v_metrics.get("mean", 0.0)
            std_val = v_metrics.get("std", 0.0)
            med_val = v_metrics.get("50%", 0.0)
            q25 = v_metrics.get("25%", 0.0)
            q75 = v_metrics.get("75%", 0.0)
            iqr_val = q75 - q25
            min_val = v_metrics.get("min", 0.0)
            max_val = v_metrics.get("max", 0.0)
            skew_val = v_metrics.get("skewness", 0.0)
            kurt_val = v_metrics.get("kurtosis", 0.0)
            table_rows.append([
                Paragraph(f"<code>{v}</code>", table_cell),
                Paragraph(unit_map.get(v, "-"), table_cell_center),
                Paragraph(f"{valid_obs:,}", table_cell_center),
                Paragraph(f"{missing_pct:.1f}%", table_cell_center),
                Paragraph(f"{mean_val:.2f} &plusmn; {std_val:.2f}", table_cell_center),
                Paragraph(f"{med_val:.2f} [{iqr_val:.2f}]", table_cell_center),
                Paragraph(f"{min_val:.2f} &ndash; {max_val:.2f}", table_cell_center),
                Paragraph(f"{skew_val:.1f} / {kurt_val:.1f}", table_cell_center),
            ])

        t_eda = Table(table_rows, colWidths=[90, 45, 55, 45, 85, 75, 70, 50])
        t_eda.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                    ("PADDING", (0, 0), (-1, -1), 2.5),
                ]
            )
        )
        story.append(t_eda)
        story.append(Paragraph("<b>Table 1:</b> Descriptive inventory and statistical summary of numerical variables (from <code>results/Exploratory_Data.csv</code>).", caption_style))

    story.append(
        Paragraph(
            "<b>Missing Data Structure:</b> Meteorological features (temperature, pressure, wind vectors) exhibit zero missing values (100% complete). In contrast, Sentinel-5P satellite observations exhibit missing values due to orbital revisit cycles and cloud masking: NO2 and CO are missing in 2,410 rows (5.78%), and O3 is missing in 2,451 rows (5.88%). Aerosol Optical Depth (AOD) has complete coverage in the processed table. Because satellite missingness is non-random, our preprocessing pipeline encodes missing indicators alongside median imputations to retain information regarding satellite coverage.",
            body_style,
        )
    )
    story.append(PageBreak())

    # =========================================================================
    # SECTION 3: TARGET DISTRIBUTION AND CLEANING PROTOCOLS
    # =========================================================================
    story.append(Paragraph("3. Target Distribution, Cleaning Protocols, and Extreme Events", h1_style))
    story.append(
        Paragraph(
            "<b>Target Quality Audit:</b> Physical surface PM2.5 concentrations cannot be negative or zero in ambient conditions. Zero or negative readings reflect optical drift or baseline calibration faults in ground monitors. Similarly, values exceeding 500 &mu;g/m&sup3; in this regional context indicate sensor malfunctions rather than real atmospheric plumes. In <code>src/preprocessing.py</code>, we apply the following cleaning filters:",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "&bull; <b>Negative / Zero values:</b> 727 rows (1.74%) with PM2.5 &le; 0 were removed.<br/>"
            "&bull; <b>Unphysical spikes:</b> 8 rows (0.02%) with PM2.5 &ge; 500 &mu;g/m&sup3; were removed.<br/>"
            "&bull; <b>Exact duplicate rows:</b> 0 exact duplicate rows found after invalid record removal.<br/>"
            "&bull; <b>Cleaned sample:</b> <b>40,983 valid observations</b> retained from 91 stations (735 rows removed, 1.76% of raw dataset).",
            body_style,
        )
    )
    story.append(Spacer(1, 4))

    # Figure 1: PM2.5 distribution
    fig_dist = FIGURES_DIR / "pm25_distribution.png"
    if fig_dist.exists():
        story.append(Image(str(fig_dist), width=6.8 * inch, height=2.2 * inch))
        story.append(Paragraph("<b>Figure 1:</b> Distribution of raw PM2.5 concentrations and corresponding log1p(PM2.5) transformation.", caption_style))

    story.append(
        Paragraph(
            "<b>Heavy Right-Skewness:</b> The target variable exhibits pronounced positive skewness (skewness = 17.83, kurtosis = 651.67). The empirical mean is 9.46 &mu;g/m&sup3;, whereas the median is 7.85 &mu;g/m&sup3; (IQR = [4.80, 11.80] &mu;g/m&sup3;). Applying <code>log1p(PM2.5)</code> contracts this heavy right tail, stabilizing loss functions during model training.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>Health Guideline Exceedances:</b> In our cleaned dataset, <b>2.98% of observations exceed the WHO 24-hour air quality guideline (25 &mu;g/m&sup3;)</b>, and <b>0.29% represent acute pollution spikes exceeding 50 &mu;g/m&sup3;</b>. Capturing these episodic peaks without predicting negative values is a central design challenge for the forecasting models.",
            body_style,
        )
    )
    story.append(Spacer(1, 4))

    # Figure 2: Main variables histograms and boxplots
    fig_hist = FIGURES_DIR / "main_variables_histograms_boxplots.png"
    if fig_hist.exists():
        story.append(Image(str(fig_hist), width=6.8 * inch, height=4.5 * inch))
        story.append(Paragraph("<b>Figure 2:</b> Histograms and boxplots for all numeric variables, illustrating distributions and outliers.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: PREDICTOR RELATIONSHIPS AND MULTICOLLINEARITY
    # =========================================================================
    story.append(Paragraph("4. Atmospheric Predictor Relationships and Multicollinearity Audit", h1_style))
    story.append(
        Paragraph(
            "We examined the linear (Pearson) and monotonic (Spearman) relationships among the environmental predictors and PM2.5 to understand physical drivers and check for multicollinearity.",
            body_style,
        )
    )

    # Figure 3: Correlation heatmaps
    fig_corr = FIGURES_DIR / "correlation_heatmaps.png"
    if fig_corr.exists():
        story.append(Image(str(fig_corr), width=6.8 * inch, height=2.4 * inch))
        story.append(Paragraph("<b>Figure 3:</b> Pearson (linear) and Spearman (rank) correlation matrices across environmental predictors.", caption_style))

    story.append(
        Paragraph(
            "<b>Physical Correlation Patterns:</b><br/>"
            "&bull; <b>Aerosol Optical Depth (AOD):</b> Moderate positive correlation with PM2.5 (Pearson r = 0.28). Higher column aerosol loading broadly aligns with elevated surface particulate concentrations.<br/>"
            "&bull; <b>Nitrogen Dioxide (NO2):</b> Positive rank correlation (Spearman r = 0.34) reflecting primary combustion sources (traffic and urban emissions).<br/>"
            "&bull; <b>Wind Velocity:</b> Negative correlation with horizontal wind speed (r = -0.22), consistent with atmospheric dispersion: strong winds disperse ground accumulation, whereas stagnant air allows particulates to build up.<br/>"
            "&bull; <b>Temperature & Boundary Layer:</b> Temperature exhibits weak overall linear correlation but shows distinct seasonal clustering due to boundary layer height dynamics.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>Multicollinearity Diagnosis (VIF):</b> We computed Variance Inflation Factors (VIF) across all numeric predictors. All values remain well below the conservative threshold of 5 (highest VIF is 1.39 for temperature), confirming the absence of severe multicollinearity among the physical features.",
            body_style,
        )
    )
    story.append(Spacer(1, 4))

    # Figure 4: Predictor relationships
    fig_scat = FIGURES_DIR / "pm25_predictor_relationships.png"
    if fig_scat.exists():
        story.append(Image(str(fig_scat), width=6.8 * inch, height=2.3 * inch))
        story.append(Paragraph("<b>Figure 4:</b> Bivariate relationships between surface PM2.5 and AOD stratified by season and wind speed group.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 5: TIME-SERIES DIAGNOSTICS & STATION IRREGULARITIES
    # =========================================================================
    story.append(Paragraph("5. Time-Series Diagnostics: Autocorrelation, Stationarity, and Drift", h1_style))
    story.append(
        Paragraph(
            "Because atmospheric processes are inherently time-dependent, treating observations as independent and identically distributed (i.i.d.) violates basic temporal assumptions. We conducted diagnostic time-series tests to evaluate persistence, stationarity, and station regularity.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>Station Regularity & Temporal Gaps:</b> The 91 stations exhibit significant reporting irregularity. The longest recorded gap at a single station spans 2,383 days, and stations report on average only 49.44% of expected days between their start and end dates. This finding has critical design implications: autoregressive lags and rolling statistics must never cross missing calendar days.",
            body_style,
        )
    )

    # Figure 5: ACF / PACF
    fig_ts = FIGURES_DIR / "acf_pacf_daily_mean_pm25.png"
    if fig_ts.exists():
        story.append(Image(str(fig_ts), width=6.8 * inch, height=2.2 * inch))
        story.append(Paragraph("<b>Figure 5:</b> Autocorrelation (ACF) and Partial Autocorrelation (PACF) correlograms for daily mean PM2.5 up to 30 lags.", caption_style))

    story.append(
        Paragraph(
            "<b>Autocorrelation & Memory:</b> The ACF correlogram reveals strong short-term memory: lag-1 autocorrelation is 0.58, followed by a gradual exponential decay. The PACF cuts off sharply after lag 1, confirming that yesterday's concentration (t-1) carries the primary autoregressive signal. A subtle peak at lag 7 indicates a weekly human activity rhythm (weekday vs. weekend traffic).",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>Stationarity & White Noise Tests:</b><br/>"
            "&bull; <b>Augmented Dickey-Fuller (ADF) test:</b> Test statistic = <b>-9.488</b> (p = 3.71 &times; 10<sup>-16</sup>), decisively rejecting the presence of a unit root and confirming statistical stationarity for daily mean concentrations.<br/>"
            "&bull; <b>Ljung-Box test:</b> Q-statistic at lag 7 yields p = 0.0, rejecting the white noise hypothesis and demonstrating strong serial dependence.",
            body_style,
        )
    )
    story.append(Spacer(1, 4))

    # Figure 6: Monthly and yearly drift
    fig_drift = FIGURES_DIR / "pm25_monthly_yearly_drift.png"
    if fig_drift.exists():
        story.append(Image(str(fig_drift), width=6.8 * inch, height=3.6 * inch))
        story.append(Paragraph("<b>Figure 6:</b> Monthly and yearly median PM2.5 concentrations, demonstrating winter elevation and interannual variations.", caption_style))

    story.append(
        Paragraph(
            "<b>Seasonal & Interannual Drift:</b> Monthly medians show clear winter increases (driven by residential heating, lower boundary layer heights, and temperature inversions), with secondary summer peaks associated with dust transport and intense photochemical activity. Annual medians show variations ranging from ~5.7 &mu;g/m&sup3; (2020) to ~10.2 &mu;g/m&sup3; (2016).",
            body_style,
        )
    )
    story.append(PageBreak())

    # Figure 7: Lead-lag correlations
    story.append(Paragraph("Lead-Lag Predictor Horizon Analysis", h2_style))
    story.append(
        Paragraph(
            "To identify optimal lookback windows, we computed cross-correlations between PM2.5 and lagged values of each predictor across 0 to 7 daily lags. Results are shown in Figure 7.",
            body_style,
        )
    )
    fig_leadlag = FIGURES_DIR / "lead_lag_correlations.png"
    if fig_leadlag.exists():
        story.append(Image(str(fig_leadlag), width=6.8 * inch, height=2.6 * inch))
        story.append(Paragraph("<b>Figure 7:</b> Correlation between daily PM2.5 and past predictor values from lag 0 to lag 7.", caption_style))

    story.append(
        Paragraph(
            "<b>Lead-Lag Insights:</b> NO2 exhibits its strongest absolute correlation at lag 0 (0.34) and remains informative through lag 1 (0.28). Surface wind speed demonstrates peak inverse correlation at lag 1 (-0.23). AOD correlation decays smoothly over 1 to 3 days, supporting our selection of short lookback windows (1–3 days) for environmental covariates.",
            body_style,
        )
    )
    story.append(Spacer(1, 6))

    # =========================================================================
    # SECTION 6: FEATURE ENGINEERING ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("6. Leakage-Free Feature Engineering Architecture", h1_style))
    story.append(
        Paragraph(
            "To prevent data leakage, all features are generated in <code>src/features.py</code> adhering to three strict engineering rules: (1) <b>past-only</b> (features use only historical data prior to time t); (2) <b>station-isolated</b> (time-series shifts and rolling aggregations are computed strictly within each individual station group); and (3) <b>gap-safe</b> (lags and rolling windows are explicitly set to NaN when date gaps exist between consecutive measurements).",
            body_style,
        )
    )

    feat_table_data = [
        [
            Paragraph("<b>Feature Family</b>", table_header),
            Paragraph("<b>Variables Included</b>", table_header),
            Paragraph("<b>Physical / Methodological Justification</b>", table_header),
        ],
        [
            Paragraph("<b>Lagged PM2.5</b>", table_cell),
            Paragraph("<code>pm25_lag_1, lag_2, lag_3, lag_7</code>", table_cell),
            Paragraph("Captures strong autoregressive memory and weekly anthropogenic traffic cycle.", table_cell),
        ],
        [
            Paragraph("<b>Lagged Atmospheric</b>", table_cell),
            Paragraph("<code>AOD_lag_1, lag_2, lag_3, NO2_lag_1</code>", table_cell),
            Paragraph("Tracks persistence in atmospheric aerosol loading and urban combustion plumes.", table_cell),
        ],
        [
            Paragraph("<b>First Differences</b>", table_cell),
            Paragraph("<code>AOD_diff_1, temp_diff_1, NO2_diff_1</code>", table_cell),
            Paragraph("Captures rate of atmospheric change; invalidated if dates are non-consecutive.", table_cell),
        ],
        [
            Paragraph("<b>Rolling Statistics</b>", table_cell),
            Paragraph("3-day & 7-day past mean and std of AOD, temp, NO2; 7-day past max AOD", table_cell),
            Paragraph("Quantifies multi-day baseline levels and volatility; invalidated across gaps.", table_cell),
        ],
        [
            Paragraph("<b>Extreme Event Memory</b>", table_cell),
            Paragraph("<code>days_since_high_AOD</code>", table_cell),
            Paragraph("Days elapsed since last major aerosol event (AOD &ge; Q75 threshold on training data).", table_cell),
        ],
        [
            Paragraph("<b>Calendar Encodings</b>", table_cell),
            Paragraph("<code>day_of_year_sin, day_of_year_cos</code>", table_cell),
            Paragraph("Smooth cyclical annual representation of solar radiation and seasonal boundary layer cycle.", table_cell),
        ],
    ]
    t_feat = Table(feat_table_data, colWidths=[100, 150, 250])
    t_feat.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("PADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t_feat)
    story.append(Paragraph("<b>Table 2:</b> Engineered feature families generated in <code>src/features.py</code>.", caption_style))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 7: PREPROCESSING PIPELINE
    # =========================================================================
    story.append(Paragraph("7. Preprocessing Pipeline: Missingness Indicators and Robust Scaling", h1_style))
    story.append(
        Paragraph(
            "To ensure models generalize without data snooping, all preprocessing transformations are encapsulated in a scikit-learn <code>ColumnTransformer</code> pipeline in <code>src/preprocessing.py</code>. The pipeline is fitted <b>exclusively on training folds</b> and applied to transform validation and test sets.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>1. Median Imputation with Missingness Indicator:</b><br/>"
            "We employ <code>SimpleImputer(strategy='median', add_indicator=True)</code>. Median imputation is robust to extreme outliers. Adding missing indicators preserves the signal of missing satellite passes (e.g., cloudy conditions), enabling tree models to learn missingness-dependent patterns without distorting numeric distributions.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>2. Robust Scaling:</b><br/>"
            "We use <code>RobustScaler()</code> instead of standard z-score scaling. Standard scaling divides by the empirical standard deviation, which is heavily distorted by extreme pollution peaks. RobustScaler centers variables around the median and scales by the Interquartile Range (IQR = Q75 - Q25), preventing outliers from compressing regular observations.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>Validation Verification:</b> Fitting the pipeline on the first temporal fold and transforming validation data confirms that correlation structures remain stable (maximum pairwise correlation difference across folds &le; 0.08), confirming numerical stability.",
            body_style,
        )
    )
    story.append(Spacer(1, 6))

    # =========================================================================
    # SECTION 8: SPATIOTEMPORAL VALIDATION PROTOCOL
    # =========================================================================
    story.append(Paragraph("8. Spatiotemporal Validation Protocol and Test Holdout Design", h1_style))
    story.append(
        Paragraph(
            "Evaluating spatiotemporal models with standard random k-fold cross-validation introduces severe optimistic bias: training and validation sets share identical weather patterns and regional plumes on neighboring days, artificially inflating performance scores.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "To address this, we structure the dataset into development and test sets in <code>src/splits.py</code>:<br/>"
            "&bull; <b>Holdout Test Set (Year 2025):</b> <b>8,149 observations</b> from the complete 2025 calendar year are held out as an independent future evaluation benchmark.<br/>"
            "&bull; <b>Development Set (Years < 2025):</b> <b>31,286 observations</b> spanning 2016 through 2024 are used for cross-validation and hyperparameter tuning.<br/>"
            "&bull; <b>Partial 2026 data:</b> 1,548 incomplete records are excluded from development and test sets.",
            body_style,
        )
    )
    story.append(Spacer(1, 4))

    # Figure 8: Temporal folds
    fig_folds = FIGURES_DIR / "temporal_folds.png"
    if fig_folds.exists():
        story.append(Image(str(fig_folds), width=6.8 * inch, height=2.2 * inch))
        story.append(Paragraph("<b>Figure 8:</b> Temporal cross-validation splits (5 folds) with a 1-day embargo gap between training and validation blocks.", caption_style))

    story.append(
        Paragraph(
            "On the development set, we construct and serialize three distinct cross-validation schemes into <code>folds/</code>:",
            body_style,
        )
    )

    cv_table_data = [
        [
            Paragraph("<b>Scheme</b>", table_header),
            Paragraph("<b>Implementation</b>", table_header),
            Paragraph("<b>Operational Objective & Testing Target</b>", table_header),
        ],
        [
            Paragraph("<b>Temporal CV</b><br/>(Primary)", table_cell),
            Paragraph("<code>TimeSeriesSplit(n_splits=5, gap=1)</code> on unique dates", table_cell),
            Paragraph("Simulates operational forecasting: training on historical dates, validating on future periods with a 1-day embargo to eliminate serial leakage.", table_cell),
        ],
        [
            Paragraph("<b>Spatial CV</b><br/>(Secondary)", table_cell),
            Paragraph("<code>GroupKFold(n_splits=5, groups=station)</code>", table_cell),
            Paragraph("Simulates unmonitored geographic generalization: validates models on stations completely unseen during training.", table_cell),
        ],
        [
            Paragraph("<b>Random CV</b><br/>(Diagnostic)", table_cell),
            Paragraph("<code>KFold(n_splits=5, shuffle=True, seed=42)</code>", table_cell),
            Paragraph("Serves as a diagnostic baseline to measure the empirical 'optimism gap' caused by ignoring time and space.", table_cell),
        ],
    ]
    t_cv = Table(cv_table_data, colWidths=[90, 160, 250])
    t_cv.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("PADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t_cv)
    story.append(Paragraph("<b>Table 3:</b> Cross-validation schemes serialized in <code>folds/</code>.", caption_style))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 9: SUMMARY & PART 2 ROADMAP
    # =========================================================================
    story.append(Paragraph("9. Milestone 1 Deliverables Summary and Part 2 Modeling Roadmap", h1_style))
    story.append(
        Paragraph(
            "Milestone 1 provides a fully verified, clean, and leakage-free foundation for predictive modeling. Table 4 summarizes the completed deliverables and outputs across the repository.",
            body_style,
        )
    )

    deliv_data = [
        [
            Paragraph("<b>Deliverable Area</b>", table_header),
            Paragraph("<b>File Location</b>", table_header),
            Paragraph("<b>Summary of Completed Work</b>", table_header),
        ],
        [
            Paragraph("<b>Cleaned Data</b>", table_cell),
            Paragraph("<code>data/processed/dev.csv<br/>data/processed/test.csv</code>", table_cell),
            Paragraph("31,286 development rows (< 2025) and 8,149 independent 2025 test rows; 735 invalid records removed.", table_cell),
        ],
        [
            Paragraph("<b>Feature Store</b>", table_cell),
            Paragraph("<code>data/processed/features_all.csv<br/>feature_groups.json</code>", table_cell),
            Paragraph("40,983 rows with past-only lags, rolling statistics, calendar encodings, and organized feature family mappings.", table_cell),
        ],
        [
            Paragraph("<b>Cross-Validation</b>", table_cell),
            Paragraph("<code>folds/folds_temporal.json<br/>folds/folds_spatial.json<br/>folds/folds_standard.json</code>", table_cell),
            Paragraph("Deterministic 5-fold partitions for Temporal, Spatial, and Random validation protocols.", table_cell),
        ],
        [
            Paragraph("<b>Exploratory CSVs</b>", table_cell),
            Paragraph("<code>results/Exploratory_Data.csv<br/>results/Exploratory_temporal.csv</code>", table_cell),
            Paragraph("Complete statistical tables: descriptive stats, audit counts, ACF/PACF, ADF stationarity, drift, and lead-lag values.", table_cell),
        ],
        [
            Paragraph("<b>Diagnostic Figures</b>", table_cell),
            Paragraph("<code>figures/*.png<br/>figures/slides/*.png</code>", table_cell),
            Paragraph("All publication-quality diagnostics: distributions, correlations, time series, drift, folds, and presentation assets.", table_cell),
        ],
        [
            Paragraph("<b>Presentation</b>", table_cell),
            Paragraph("<code>presentation/Part1_EDA_Presentation.pptx<br/>presentation/slides.pdf</code>", table_cell),
            Paragraph("10-slide PowerPoint presentation and accompanying PDF slide deck for oral defense.", table_cell),
        ],
    ]
    t_deliv = Table(deliv_data, colWidths=[90, 170, 240])
    t_deliv.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("PADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t_deliv)
    story.append(Paragraph("<b>Table 4:</b> Summary of Milestone 1 generated files and deliverables.", caption_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Part 2 Modeling Roadmap", h2_style))
    story.append(
        Paragraph(
            "Building upon this clean foundation, Milestone 2 will execute the modeling and evaluation phase:<br/>"
            "&bull; <b>Model Families:</b> Implement and tune regularized linear models (Ridge, Lasso), robust estimators (HuberRegressor), non-linear kernels (SVR), tree ensembles (Random Forest, LightGBM, XGBoost), and recurrent neural networks (LSTM).<br/>"
            "&bull; <b>Comparative Evaluation:</b> Benchmark performance across Temporal CV and Spatial CV using RMSE, MAE, and R<sup>2</sup> metrics.<br/>"
            "&bull; <b>Statistical Significance:</b> Conduct paired Wilcoxon signed-rank tests with Bonferroni correction to verify whether ensemble methods significantly outperform linear baselines.<br/>"
            "&bull; <b>Explainability & Stability:</b> Calculate permutation feature importance across folds to assess whether feature rankings remain consistent under temporal and spatial shifts.",
            body_style,
        )
    )
    story.append(Spacer(1, 6))

    # =========================================================================
    # SECTION 10: REPRODUCIBILITY ENVIRONMENT AND REFERENCES
    # =========================================================================
    story.append(Paragraph("10. Reproducibility Environment and References", h1_style))
    story.append(
        Paragraph(
            "<b>Computational Environment:</b> Experiments were run on Python 3.10+ using pandas, numpy, scikit-learn, scipy, statsmodels, matplotlib, seaborn, reportlab, and python-pptx. The random seed is fixed to <b>SEED = 42</b> in <code>src/config.py</code>. The entire Milestone 1 pipeline can be reproduced by executing: <code>python scripts/run_eda.py</code>.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>Key Academic References:</b><br/>"
            "[1] World Health Organization. (2021). <i>WHO Global Air Quality Guidelines: Particulate Matter (PM2.5 and PM10), Ozone, Nitrogen Dioxide, Sulfur Dioxide and Carbon Monoxide</i>. World Health Organization.<br/>"
            "[2] Copernicus Atmosphere Monitoring Service. (2023). <i>Sentinel-5P TROPOMI Tropospheric Nitrogen Dioxide, Carbon Monoxide, and Ozone Data Products</i>. European Space Agency.<br/>"
            "[3] Hersbach, H., et al. (2020). The ERA5 global reanalysis. <i>Quarterly Journal of the Royal Meteorological Society</i>, 146(730), 1999–2049.<br/>"
            "[4] Levy, R. C., et al. (2013). The Collection 6 MODIS aerosol products over land and ocean. <i>Atmospheric Measurement Techniques</i>, 6(11), 2989–3034.<br/>"
            "[5] Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. <i>Journal of Machine Learning Research</i>, 12, 2825–2830.",
            body_style,
        )
    )

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Technical Report successfully compiled to: {PDF_OUTPUT_PATH}")


if __name__ == "__main__":
    build_technical_report()
