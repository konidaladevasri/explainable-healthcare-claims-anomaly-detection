from pathlib import Path
import json
import html

import pandas as pd
import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Healthcare Claims Review",
    page_icon="📋",
    layout="wide"
)

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUTS = PROJECT_ROOT / "outputs"
MODELS = PROJECT_ROOT / "models"

FEATURES = [
    "total_charge_amount",
    "diagnosis_count",
    "charge_count",
    "payment_count",
    "transfer_count",
    "unique_charge_procedure_count"
]

CATEGORY_ORDER = [
    "Both",
    "Rules only",
    "Model only",
    "Neither"
]


# --------------------------------------------------
# COLORS AND STYLING
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F8FAFC;
        color: #10243A;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* Main header */
    .hero {
        background: linear-gradient(115deg, #10243A, #164E63);
        border: 1px solid #216579;
        border-left: 7px solid #2DD4BF;
        border-radius: 18px;
        padding: 30px 34px;
        margin-bottom: 26px;
        box-shadow: 0 8px 24px rgba(16, 36, 58, 0.10);
    }

    .hero-eyebrow {
        color: #5EEAD4;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }

    .hero h1 {
        color: #FFFFFF;
        font-size: clamp(28px, 3vw, 42px);
        line-height: 1.2;
        padding: 0;
        margin: 0 0 16px;
    }

    .hero-description {
        color: #E2E8F0;
        font-size: 17px;
        margin-bottom: 16px;
    }

    .hero-meta {
        color: #A5F3FC;
        font-size: 13px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10243A, #164E63) !important;
        border-right: 3px solid #2DD4BF;
    }

    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #F0FDFA !important;
        font-weight: 600;
    }

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #CBD5E1 !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: #3B6475 !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #F0FDFA !important;
        color: #10243A !important;
        border-color: #99F6E4 !important;
        border-radius: 10px !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] input {
        color: #10243A !important;
        -webkit-text-fill-color: #10243A !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="input"] {
        background-color: #F0FDFA !important;
        border-color: #99F6E4 !important;
        border-radius: 10px !important;
    }

    section[data-testid="stSidebar"] input {
        background-color: #F0FDFA !important;
        color: #10243A !important;
        -webkit-text-fill-color: #10243A !important;
    }

    section[data-testid="stSidebar"] input::placeholder {
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
    }

    .filter-heading {
        background-color: #164E63;
        border: 1px solid #35798B;
        border-left: 4px solid #2DD4BF;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 24px;
    }

    .filter-heading h2 {
        color: #FFFFFF !important;
        font-size: 24px;
        margin: 0 0 8px;
        padding: 0;
    }

    .filter-heading p {
        color: #CCFBF1 !important;
        font-size: 14px;
        margin: 0;
    }

    /* Section headings */
    .section-banner {
        border: 1px solid;
        border-left-width: 5px;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 20px 0 18px;
    }

    .section-banner h2 {
        font-size: 23px;
        line-height: 1.3;
        margin: 0 0 6px;
        padding: 0;
        color: inherit;
    }

    .section-banner p {
        font-size: 14px;
        margin: 0;
        color: inherit;
    }

    .section-teal {
        background: #F0FDFA;
        border-color: #0F766E;
        color: #115E59;
    }

    .section-blue {
        background: #EFF6FF;
        border-color: #2563EB;
        color: #1E40AF;
    }

    .section-indigo {
        background: #EEF2FF;
        border-color: #6366F1;
        color: #3730A3;
    }

    /* KPI cards */
    .kpi-card {
        background: var(--surface);
        border: 1px solid #D8E3EE;
        border-top: 5px solid var(--accent);
        border-radius: 14px;
        padding: 20px 18px;
        min-height: 140px;
    }

    .kpi-label {
        color: #36536D;
        font-size: 14px;
        margin-bottom: 14px;
    }

    .kpi-value {
        color: #10243A;
        font-size: clamp(25px, 2.5vw, 36px);
        font-weight: 750;
        line-height: 1.2;
    }

    /* Queue controls */
    .st-key-queue_display_controls {
        background-color: #EAF2F8;
        border: 1px solid #C8DBE8;
        border-left: 4px solid #164E63;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 18px;
    }

    /* Claim investigation */
    .st-key-investigation_selector {
        background-color: #EAF2F8;
        border: 1px solid #C8DBE8;
        border-left: 4px solid #164E63;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }

    .st-key-financial_panel {
        background-color: #F0FDFA;
        border: 1px solid #B5E4DC;
        border-top: 4px solid #0F766E;
        border-radius: 14px;
        padding: 20px;
        height: 100%;
    }

    .st-key-signals_panel {
        background-color: #EFF6FF;
        border: 1px solid #C7DAF7;
        border-top: 4px solid #2563EB;
        border-radius: 14px;
        padding: 20px;
        height: 100%;
    }

    .st-key-peer_panel {
        background-color: #EAF2F8;
        border: 1px solid #C8DBE8;
        border-top: 4px solid #164E63;
        border-radius: 14px;
        padding: 20px;
    }

    /* Population patterns and methods */
    .st-key-category_chart_panel,
    .st-key-class_chart_panel {
        background-color: #FFFFFF;
        border: 1px solid #D8E3EE;
        border-top: 4px solid #0F766E;
        border-radius: 14px;
        padding: 18px;
    }

    .st-key-methods_panel {
        background-color: #F0FDFA;
        border: 1px solid #B5E4DC;
        border-left: 4px solid #0F766E;
        border-radius: 14px;
        padding: 20px;
    }

    /* Tables and buttons */
    [data-testid="stDataFrame"] {
        border: 1px solid #D8E3EE;
        border-radius: 10px;
        overflow: hidden;
    }

    [data-testid="stDownloadButton"] button {
        background-color: #164E63;
        color: #FFFFFF;
        border: 1px solid #164E63;
        border-radius: 9px;
    }

    [data-testid="stDownloadButton"] button:hover {
        background-color: #0F766E;
        color: #FFFFFF;
        border-color: #0F766E;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0F766E !important;
        font-weight: 700;
    }

    [data-baseweb="tab-highlight"] {
        background-color: #0F766E !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# SECTION HEADING HELPER
# --------------------------------------------------
def section_banner(title, description="", color="teal"):
    st.markdown(
        f"""
        <div class="section-banner section-{html.escape(color)}">
            <h2>{html.escape(title)}</h2>
            <p>{html.escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# LOAD SAVED RESULTS
# --------------------------------------------------
@st.cache_data
def load_data():
    claims = pd.read_csv(
        OUTPUTS / "evaluation_scored_claims.csv",
        dtype={"claim_id": "string"},
        parse_dates=["service_date"]
    )

    required_columns = [
        "claim_id",
        "service_date",
        "encounter_class",
        *FEATURES,
        "total_payment_amount",
        "payment_minus_charge_amount",
        "charge_review_threshold",
        "model_anomaly_score",
        "rule_payment_exceeds_charge",
        "rule_service_after_death",
        "rule_high_charge",
        "any_rule_flag",
        "model_anomaly_flag",
        "rule_reasons"
    ]

    missing_columns = sorted(set(required_columns) - set(claims.columns))

    if missing_columns:
        raise ValueError(
            f"Missing columns in scored claims: {missing_columns}"
        )

    boolean_columns = [
        "rule_payment_exceeds_charge",
        "rule_service_after_death",
        "rule_high_charge",
        "any_rule_flag",
        "model_anomaly_flag"
    ]

    for column in boolean_columns:
        values = claims[column].astype("string").str.strip().str.lower()
        converted = values.map({"true": True, "false": False})

        if converted.isna().any():
            raise ValueError(f"Invalid Boolean values in {column}")

        claims[column] = converted.astype(bool)

    if claims["claim_id"].isna().any():
        raise ValueError("Missing claim IDs in saved results.")

    if not claims["claim_id"].is_unique:
        raise ValueError("Duplicate claim IDs in saved results.")

    # Derive exclusive categories directly from the saved flags.
    claims["review_category"] = "Neither"

    claims.loc[
        claims["any_rule_flag"] & ~claims["model_anomaly_flag"],
        "review_category"
    ] = "Rules only"

    claims.loc[
        ~claims["any_rule_flag"] & claims["model_anomaly_flag"],
        "review_category"
    ] = "Model only"

    claims.loc[
        claims["any_rule_flag"] & claims["model_anomaly_flag"],
        "review_category"
    ] = "Both"

    claims["rule_reasons"] = (
        claims["rule_reasons"].fillna("No rule triggered")
    )

    peers = pd.read_csv(
        OUTPUTS / "training_peer_medians.csv",
        index_col="encounter_class"
    )

    with open(MODELS / "rule_config.json", encoding="utf-8") as file:
        rule_config = json.load(file)

    return claims, peers, rule_config


required_files = [
    OUTPUTS / "evaluation_scored_claims.csv",
    OUTPUTS / "training_peer_medians.csv",
    MODELS / "rule_config.json"
]

missing_files = [
    str(path.relative_to(PROJECT_ROOT))
    for path in required_files
    if not path.is_file()
]

if missing_files:
    st.error("Required project files are missing:")
    st.write(missing_files)
    st.stop()

try:
    claims_df, peer_medians_df, rule_config = load_data()
except (ValueError, KeyError, OSError) as error:
    st.error(f"Unable to load project data: {error}")
    st.stop()


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">
            HEALTHCARE ANALYTICS · PAYMENT INTEGRITY
        </div>
        <h1>Explainable Healthcare Claims Anomaly Detection</h1>
        <div class="hero-description">
            Explore unusual billing patterns using transparent rules
            and Isolation Forest.
        </div>
        <div class="hero-meta">
            Synthetic Synthea data · Retrospective evaluation ·
            Human review required
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="filter-heading">
            <h2>Claims Explorer</h2>
            <p>Filter claims for focused review.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    selected_category = st.selectbox(
        "Review category",
        [
            "All flagged claims",
            "Both",
            "Rules only",
            "Model only",
            "Neither",
            "All claims"
        ]
    )

    class_options = sorted(
        claims_df["encounter_class"].dropna().unique().tolist()
    )

    selected_class = st.selectbox(
        "Encounter class",
        ["All encounter classes", *class_options]
    )

    claim_search = st.text_input(
        "Search claim ID",
        placeholder="Enter all or part of an ID"
    )

    sort_option = st.selectbox(
        "Sort results",
        [
            "Highest model score",
            "Highest charge",
            "Most recent service"
        ]
    )

    st.divider()

    st.caption(
        f"Source: {len(claims_df):,} evaluation claims. "
        "Filters update the overview, charts, and review queue."
    )

    st.caption(
        "Model scores describe unusual patterns. "
        "They are not probabilities of fraud."
    )


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------
filtered_df = claims_df.copy()

if selected_category == "All flagged claims":
    filtered_df = filtered_df.loc[
        filtered_df["any_rule_flag"]
        | filtered_df["model_anomaly_flag"]
    ]

elif selected_category != "All claims":
    filtered_df = filtered_df.loc[
        filtered_df["review_category"].eq(selected_category)
    ]

if selected_class != "All encounter classes":
    filtered_df = filtered_df.loc[
        filtered_df["encounter_class"].eq(selected_class)
    ]

if claim_search.strip():
    filtered_df = filtered_df.loc[
        filtered_df["claim_id"].str.contains(
            claim_search.strip(),
            case=False,
            regex=False,
            na=False
        )
    ]

sort_columns = {
    "Highest model score": "model_anomaly_score",
    "Highest charge": "total_charge_amount",
    "Most recent service": "service_date"
}

filtered_df = filtered_df.sort_values(
    [sort_columns[sort_option], "claim_id"],
    ascending=[False, True]
).copy()


# --------------------------------------------------
# FILTERED OVERVIEW AND KPI CARDS
# --------------------------------------------------
section_banner(
    "Filtered claims overview",
    "All cards reflect the sidebar filters. "
    "Each claim belongs to exactly one review category.",
    color="teal"
)

category_counts = (
    filtered_df["review_category"]
    .value_counts()
    .reindex(CATEGORY_ORDER, fill_value=0)
)

kpi_values = [
    (
        "Matching claims",
        len(filtered_df),
        "#164E63",
        "#EAF2F8"
    ),
    (
        "Rules only",
        int(category_counts["Rules only"]),
        "#0F766E",
        "#F0FDFA"
    ),
    (
        "Model only",
        int(category_counts["Model only"]),
        "#2563EB",
        "#EFF6FF"
    ),
    (
        "Both methods",
        int(category_counts["Both"]),
        "#164E63",
        "#EAF2F8"
    ),
    (
        "Neither method",
        int(category_counts["Neither"]),
        "#64748B",
        "#F1F5F9"
    )
]

for column, (label, value, accent, surface) in zip(
    st.columns(5), kpi_values
):
    with column:
        st.markdown(
            f"""
            <div class="kpi-card"
                 style="--accent: {accent}; --surface: {surface};">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value:,}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.caption(
    "Matching claims = Rules only + Model only + "
    "Both methods + Neither method."
)


# --------------------------------------------------
# MAIN SECTIONS
# --------------------------------------------------
queue_tab, patterns_tab, methods_tab = st.tabs(
    ["Review workspace", "Population patterns", "Methods"]
)


# --------------------------------------------------
# REVIEW WORKSPACE
# --------------------------------------------------
with queue_tab:
    section_banner(
        "Review queue",
        "Explore matching claims and select a claim for investigation.",
        color="indigo"
    )

    summary_left, summary_right = st.columns([3, 1])

    with summary_left:
        st.write(
            f"**{len(filtered_df):,} claims** match your selections."
        )

    with summary_right:
        st.download_button(
            "Download results",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="filtered_claim_review_queue.csv",
            mime="text/csv"
        )

    if filtered_df.empty:
        st.info(
            "No claims match these selections. "
            "Change the filters in the sidebar."
        )

    else:
        with st.container(key="queue_display_controls"):
            row_limit = st.selectbox(
                "Rows to display",
                [25, 50, 100, 250],
                index=1
            )

            st.caption(
                "Choose how many rows appear in the table. "
                "Downloads include every matching claim."
            )

        queue_columns = [
            "claim_id",
            "service_date",
            "encounter_class",
            "total_charge_amount",
            "total_payment_amount",
            "model_anomaly_score",
            "review_category",
            "rule_reasons"
        ]

        st.dataframe(
            filtered_df[queue_columns].head(row_limit),
            hide_index=True,
            column_config={
                "claim_id": st.column_config.TextColumn("Claim ID"),
                "service_date": st.column_config.DateColumn(
                    "Service date",
                    format="YYYY-MM-DD"
                ),
                "encounter_class": st.column_config.TextColumn(
                    "Encounter"
                ),
                "total_charge_amount": st.column_config.NumberColumn(
                    "Charges ($)",
                    format="%.2f"
                ),
                "total_payment_amount": st.column_config.NumberColumn(
                    "Payments ($)",
                    format="%.2f"
                ),
                "model_anomaly_score": st.column_config.NumberColumn(
                    "Model score",
                    format="%.6f"
                ),
                "review_category": st.column_config.TextColumn(
                    "Review category"
                ),
                "rule_reasons": st.column_config.TextColumn(
                    "Rule reasons"
                )
            }
        )

        # ------------------------------------------
        # CLAIM INVESTIGATION
        # ------------------------------------------
        section_banner(
            "Claim investigation",
            "Inspect the selected claim’s financial details and review signals.",
            color="teal"
        )

        with st.container(key="investigation_selector"):
            selected_claim_id = st.selectbox(
                "Select a claim to investigate",
                filtered_df["claim_id"].tolist()
            )

            claim = filtered_df.loc[
                filtered_df["claim_id"].eq(selected_claim_id)
            ].iloc[0]

            service_date_label = (
                claim["service_date"].strftime("%Y-%m-%d")
                if pd.notna(claim["service_date"])
                else "Date unavailable"
            )

            st.caption(
                f"{str(claim['encounter_class']).title()} • "
                f"{service_date_label} • "
                f"{claim['review_category']}"
            )

        left, right = st.columns([3, 2])

        with left:
            with st.container(key="financial_panel"):
                st.subheader("Financial summary")

                charge_col, payment_col = st.columns(2)

                charge_col.metric(
                    "Recorded charges",
                    f"${claim['total_charge_amount']:,.2f}"
                )

                payment_col.metric(
                    "Recorded payments",
                    f"${claim['total_payment_amount']:,.2f}"
                )

                st.divider()

                st.write(
                    "**Payments minus charges:** "
                    f"${claim['payment_minus_charge_amount']:,.2f}"
                )

                st.write(
                    "**Encounter-class charge threshold:** "
                    f"${claim['charge_review_threshold']:,.2f}"
                )

                st.caption(
                    "The charge threshold is a statistical review cutoff, "
                    "not a maximum allowable charge."
                )

        with right:
            with st.container(key="signals_panel"):
                st.subheader("Review signals")

                st.metric(
                    "Model anomaly score",
                    f"{claim['model_anomaly_score']:.6f}"
                )

                st.write(
                    "**Model flag:** "
                    + (
                        "Flagged for review"
                        if claim["model_anomaly_flag"]
                        else "Not flagged"
                    )
                )

                st.divider()

                st.write("**Rule reasons**")
                st.write(claim["rule_reasons"])

                st.caption(
                    "A higher model score indicates a more unusual pattern. "
                    "It is not a fraud probability."
                )

        # ------------------------------------------
        # TRAINING PEER COMPARISON
        # ------------------------------------------
        section_banner(
            "Training peer comparison",
            "Compare original values with medians for the same encounter class.",
            color="blue"
        )

        encounter_class = claim["encounter_class"]

        with st.container(key="peer_panel"):
            if encounter_class in peer_medians_df.index:
                comparison_df = pd.DataFrame({
                    "Claim value": claim[FEATURES].astype(float),
                    "Training peer median": peer_medians_df.loc[
                        encounter_class, FEATURES
                    ].astype(float)
                })

                comparison_df.index = [
                    "Charge amount ($)",
                    "Populated diagnosis slots",
                    "Charge entries",
                    "Payment entries",
                    "Transfer entries",
                    "Distinct procedure codes"
                ]

                comparison_df.index.name = "Feature"

                st.dataframe(
                    comparison_df.style.format("{:,.2f}")
                )

            else:
                st.info(
                    "Training peer medians are unavailable "
                    "for this encounter class."
                )

            st.caption(
                "Peer comparisons provide context. They do not identify "
                "which features caused the model score."
            )


# --------------------------------------------------
# POPULATION PATTERNS
# --------------------------------------------------
with patterns_tab:
    section_banner(
        "Patterns within matching claims",
        "Charts reflect the current sidebar filters.",
        color="blue"
    )

    if filtered_df.empty:
        st.info(
            "No matching claims are available to chart. "
            "Change the sidebar filters."
        )

    else:
        left, right = st.columns(2)

        with left:
            with st.container(key="category_chart_panel"):
                st.subheader("Review categories")

                chart_category_counts = (
                    filtered_df["review_category"]
                    .value_counts()
                    .reindex(CATEGORY_ORDER, fill_value=0)
                    .rename("Claims")
                )

                st.bar_chart(
                    chart_category_counts,
                    color="#0F766E"
                )

                st.caption(
                    "Each matching claim appears in one category."
                )

        with right:
            with st.container(key="class_chart_panel"):
                st.subheader("Flagging rates by encounter")

                class_rates = (
                    filtered_df
                    .groupby("encounter_class")[
                        ["any_rule_flag", "model_anomaly_flag"]
                    ]
                    .mean()
                    .mul(100)
                    .rename(columns={
                        "any_rule_flag": "Rules flagged (%)",
                        "model_anomaly_flag": "Model flagged (%)"
                    })
                )

                st.bar_chart(
                    class_rates,
                    color=["#0F766E", "#2563EB"]
                )

                st.caption(
                    "Percentages use matching claims within each "
                    "encounter class as the denominator."
                )

        st.info(
            "Review-category filters affect these percentages. "
            "For example, selecting Both makes both flagging rates 100%. "
            "Select All claims to inspect rates across the evaluation "
            "population, subject to your other filters."
        )

        st.caption(
            "Flagging rates describe review activity, "
            "not confirmed errors or model accuracy."
        )


# --------------------------------------------------
# METHODS AND LIMITATIONS
# --------------------------------------------------
with methods_tab:
    section_banner(
        "Methods and limitations",
        "How claims are screened and how results should be interpreted.",
        color="teal"
    )

    tolerance = float(
        rule_config["payment_difference_tolerance"]
    )

    with st.container(key="methods_panel"):
        st.markdown(
            f"""
### Data and evaluation

- The prototype uses synthetic Synthea claims.
- Claims were linked to transactions, encounters, and patient records.
- Claim-level row counts and financial totals were reconciled.
- Earlier claims were used for training; later claims were reserved
  for evaluation.
- Some patients appear in both periods. This evaluates later claims,
  rather than performance exclusively on previously unseen patients.

### Transparent review rules

A claim is flagged when one or more conditions apply:

- Recorded payments exceed charges by more than **${tolerance:.2f}**.
- Service occurs after the recorded death date.
- Charges exceed the encounter-class threshold learned from training data.

High-charge thresholds use the **99th percentile of training charges**
within each encounter class. Classes with fewer than 100 training
claims use the overall training threshold.

### Isolation Forest

- The model uses six numerical features: charge amount, diagnosis count,
  charge entries, payment entries, transfer entries, and distinct
  charge procedure codes.
- Features were transformed using **log1p** before modeling.
- The forest contains **200 trees**, each trained on a random sample
  of **256 training claims**.
- Higher anomaly scores indicate patterns that the forest isolates
  more easily.
- The model review cutoff was set at the **99th percentile of training
  anomaly scores**, approximately **0.676036**.
- Rules were evaluated separately; their flags were not training labels.

### Interpretation

- Flags identify review candidates and require human investigation.
- Scores are not fraud probabilities.
- Legitimate complex care can produce unusual billing patterns.
- Peer medians provide context, rather than an attribution of the
  model score to particular features.
- No adjudicated fraud labels are available, so flagging rates
  cannot establish accuracy, precision, or recall.
- Payment information comes from the completed export. This is
  retrospective analysis rather than a point-of-service prediction.
- This dashboard displays saved evaluation results. It does not
  retrain the model or score newly uploaded claims.
"""
        )