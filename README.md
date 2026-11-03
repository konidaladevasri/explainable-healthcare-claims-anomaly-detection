# Explainable Healthcare Claims Anomaly Detection

A retrospective claims review prototype combining transparent rules, Isolation Forest, and an interactive Streamlit dashboard.

**Author:** Konidala Devasri Choudary  
**Assessment topic:** Clinical Decision Making and Pattern Recognition in Health Care  
**Focus:** Payment and operations using synthetic Synthea data

## Project overview

Healthcare claims can contain unusual financial amounts, inconsistent service dates, or complex billing activity that warrants investigation. Fixed rules provide explicit reasons for review. Unsupervised anomaly detection adds a way to identify unusual combinations of claim characteristics without labeled fraud examples.

This project combines both approaches in a claim-level review workflow. Users can filter results, inspect financial details, read rule reasons, compare claims with training peers, and download a review queue.

**Flags identify review candidates. They do not establish fraud, billing errors, or recoverable savings. Model scores are not fraud probabilities.**

## Relevance to Cotiviti

The project illustrates pattern recognition for payment integrity and operational review. It supports evaluating whether anomaly ranking adds useful review candidates beyond explicit rules.

Cotiviti already uses AI and deterministic rules in payment integrity. This independent assessment prototype demonstrates an analytical concept rather than reproducing a Cotiviti product. The accompanying report proposes a controlled retrospective pilot, an evidence and reviewer-feedback layer, and expert-approved AI assistance for case summaries.

## Data and preparation

The source data consists of synthetic Synthea CSV exports. No real patient records are used.

| Source table | Records |
|---|---:|
| Claims | 117,889 |
| Claim transactions | 711,238 |
| Encounters | 61,459 |
| Patients | 1,163 |
| Payers | 10 |

Preparation uses PySpark in Microsoft Fabric. Bronze-to-Silver notebooks clean and type the data. Claim feature engineering aggregates transactions before joining patient and encounter context, preserving one row per claim. The validated table is saved as `gold.claim_anomaly_features` and exported for local Python analysis.

Validation covers:

- Claim, transaction, encounter, and patient identifiers and relationships.
- Consistent patient and encounter identifiers across linked records.
- Claim-level row counts and transaction counts after aggregation.
- Financial reconciliation before and after feature construction and storage.

All 117,889 claims have associated transactions. Aggregation accounts for all 711,238 transactions. Reconciled recorded charges total **$206,901,374.78**, and recorded payments total **$207,482,352.15**.

Missing primary or secondary payer identifiers are assessed separately from the validated patient and encounter relationships. Absence of secondary coverage is not automatically a data error.

## Analytical approach

### Chronological evaluation

Claims are partitioned by service date, with the entire boundary date retained in training.

| Partition | Claims | Service dates |
|---|---:|---|
| Training | 94,333 | September 26, 1912–November 14, 2017 |
| Evaluation | 23,556 | November 15, 2017–November 19, 2021 |

Statistical thresholds and preprocessing are learned from training data. Evaluation claims do not determine the review cutoffs. There are 967 patients present in both partitions, so this evaluates later claims rather than an exclusively unseen-patient population.

### Transparent rules

| Rule | Review condition |
|---|---|
| Payments exceed charges | Recorded payments exceed recorded charges by more than $0.01 |
| Service after death | Service date is after the patient's recorded death date |
| High charge | Charges exceed the training encounter-class 99th percentile |

The financial rule reuses the flag calculated with decimal amounts in Fabric. High-charge thresholds use a minimum of 100 training claims per encounter class, with the overall training threshold as a fallback for smaller or unavailable classes.

These rules are review heuristics, not a complete implementation of payer contracts, clinical guidelines, or billing policy.

### Isolation Forest

The model independently uses six numerical features:

1. Total charge amount
2. Populated diagnosis slots
3. Charge entry count
4. Payment entry count
5. Transfer entry count
6. Distinct charge procedure codes

A `log1p` transformation reduces skew. A median imputer is fitted on training data. Isolation Forest uses 200 trees, 256 sampled training claims per tree, and `random_state=42`.

Anomaly scores are calculated as the negative of `score_samples`, so larger values indicate more unusual patterns. The review cutoff is the **99th percentile of training scores**, approximately **0.676036**. Flags use scores strictly greater than this cutoff, rather than the estimator's default `predict` output.

Rule flags are not training labels or model inputs. The model learns without adjudicated fraud outcomes. This is claim-level anomaly detection with chronological evaluation, not a time-series forecasting model.

## Evaluation results

The evaluation partition contains **23,556 claims**.

| Review category | Claims | Percentage |
|---|---:|---:|
| Rules only | 2,302 | 9.77% |
| Model only | 326 | 1.38% |
| Both methods | 271 | 1.15% |
| Neither method | 20,657 | 87.69% |
| **Total** | **23,556** | **100.00%** |

Percentages are rounded independently and may not sum exactly to 100%.

- Rules identify **2,573 claims (10.92%)**.
- Isolation Forest identifies **597 claims (2.53%)**.
- Either method identifies **2,899 distinct claims (12.31%)**.
- The model contributes **326 additional candidates** beyond the implemented rules.

The overlap reconciles as `2,573 + 597 - 271 = 2,899`. Additional candidates represent additional selection, not confirmed incremental findings or savings.

### Example of a model-only claim

Claim `70315484-c4af-a090-d4a2-961bc3d32d86` is an inpatient claim with an anomaly score of **0.773027**, above the model cutoff. Its charges of **$21,415.62** remain below the inpatient charge threshold of **$23,506.46**, and no implemented rule triggers.

| Feature | Claim value | Inpatient training median |
|---|---:|---:|
| Charges | $21,415.62 | $1,303.66 |
| Populated diagnosis slots | 5 | 1 |
| Charge entries | 26 | 1 |
| Payment entries | 27 | 1 |
| Transfer entries | 52 | 0 |
| Distinct procedure codes | 4 | 1 |

Peer comparisons help a reviewer understand the claim's context. They do not establish which features caused the Isolation Forest score.

## Prototype checks

Controlled synthetic scenarios check whether the implementation responds as intended:

| Scenario | Observed response |
|---|---|
| Unchanged baseline | No rule or model flag |
| Payment exceeds charge by $500 | Payment rule triggers; model score stays unchanged |
| Service after recorded death | Date rule triggers; model score stays unchanged |
| Extreme billing activity | High-charge rule and model flag trigger |

Payment totals and death dates are not among the six model inputs, explaining the unchanged scores in those scenarios. These are functional checks, not estimates of sensitivity or accuracy. Reloading the saved model bundle also reproduces the checked scores.

## Streamlit application

The dashboard provides:

- Sidebar filters for review category, encounter class, and claim ID search.
- Sorting by model score, charge amount, or service date.
- Filter-responsive KPI cards with mutually exclusive review categories.
- A review queue with a selectable display limit and CSV download.
- Claim investigation with financial totals and rule reasons.
- Training peer comparisons and filtered population charts.
- Methods and limitations for interpreting the results.

The dashboard displays saved evaluation results. It does not retrain the model or score newly uploaded claims. Downloads include every matching claim, even when the displayed table has a smaller row limit.

## Repository organization

The intended project structure is:

```text
app.py
README.md
data/
    claim_anomaly_features.csv
notebooks/
    01_synthea_claims_source_audit.ipynb
    02_bronze_to_silver_transformation.ipynb
    02b_bronze_to_silver_encounters.ipynb
    02c_bronze_to_silver_payers.ipynb
    02e_bronze_to_silver_claims.ipynb
    02f_bronze_to_silver_claims_transactions.ipynb
    03_silver_data_quality_audit.ipynb
    06_claim_anomaly_features.ipynb
    07_claims_anomaly_detection.ipynb
models/
    isolation_forest_bundle.joblib
    rule_config.json
outputs/
    evaluation_scored_claims.csv
    training_peer_medians.csv
    training_charge_thresholds.csv
    review_category_summary.csv
    encounter_review_summary.csv
    synthetic_check_results.csv
deliverables/
    Cotiviti_Strategic_Report.docx
```

Notebook numbering preserves the existing Fabric workflow. The Bronze-to-Silver notebooks require the original source tables/files and an attached Microsoft Fabric Lakehouse. They are not standalone local pandas notebooks.

## Run the dashboard locally

Use the Python environment used for notebook 07. Package versions should match the environment used for the submitted outputs and saved model.

From the repository root, create a virtual environment:

```powershell
python -m venv .venv
```

Install the dashboard dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install pandas streamlit
```

Ensure these files are present:

```text
outputs/evaluation_scored_claims.csv
outputs/training_peer_medians.csv
models/rule_config.json
```

Launch the application:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit. The dashboard does not require an active Fabric session or the saved Isolation Forest bundle.

### Reproduce the modeling notebook

For local notebook execution, also install the analysis dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install numpy scikit-learn joblib matplotlib seaborn jupyter ipykernel
```

Open `notebooks/07_claims_anomaly_detection.ipynb`, select the project virtual environment as the kernel, and run cells in order. The notebook requires `data/claim_anomaly_features.csv` from Fabric feature engineering and produces the model artifacts and output CSVs.

The saved model bundle must be loaded with compatible package versions. Record the final tested environment in `requirements.txt` before submission. Only load joblib artifacts from a trusted source.

## Limitations and next steps

- Synthetic Synthea data may contain generator-specific patterns that do not represent real payer operations.
- No adjudicated fraud or billing-error labels are available. Flagging rates do not measure accuracy, precision, recall, or savings.
- Legitimate complex care and repeated services can produce model flags.
- The broad historical date range and changing billing practices limit generalization.
- Payment and transfer counts come from completed transaction histories. A prepayment use case would require rebuilding features using only information available at that time.
- Rule explanations are explicit. Training peer comparisons provide context rather than a formal attribution of the model score.
- Production evaluation would require expert-reviewed samples, assessment of unflagged claims, appropriate peer groups, drift monitoring, and thresholds aligned with reviewer capacity.

## Assessment deliverables

| Item | Current preparation status |
|---|---|
| Word report | Prepared: `Cotiviti_Strategic_Report.docx`, two report pages plus references on page three |
| Prototype | Implemented: Streamlit `app.py` and saved evaluation outputs |
| PowerPoint | Pending |
| Video | Pending: MP4, no longer than five minutes, including presenter camera and working POC screenshare |
| Resume | Current assessment copy to be added |

Place the report, PowerPoint, MP4, and resume directly in this repository under `deliverables/`. This preparation status does not assert that all files have already been uploaded. Update it and add relative links when the final files are present. The assessment requires a public GitHub repository containing the actual deliverables rather than external hosting links.

## Sources and acknowledgment

- Cotiviti. [Healthcare claim payment accuracy solutions](https://www.cotiviti.com/solutions/payment-accuracy).
- Synthetic Health. [Synthea patient generator](https://github.com/synthetichealth/synthea).
- scikit-learn developers. [IsolationForest documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html).
- Tabassi, E. (2023). [Artificial intelligence risk management framework (AI RMF 1.0)](https://doi.org/10.6028/NIST.AI.100-1). National Institute of Standards and Technology.

The Word report contains the bibliography for its researched trends and strategic analysis. Project metrics in this README come from the feature validation and modeling outputs described above.

ChatGPT assisted with coding guidance, explanations, documentation, and report drafting. Microsoft Fabric/PySpark supported data preparation; pandas, NumPy, scikit-learn, and joblib supported local analysis and model persistence; Streamlit supported the dashboard.
