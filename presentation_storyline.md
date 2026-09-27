# Presentation Storyline

## Reframing 1: For an Executive (Situation-Complication-Resolution)

**Situation:** PharmEasy's Telugu-states regional desk covers 9 active regions across Telangana, Andhra Pradesh, and a Bengaluru hub. In April-June 2026, the desk processed 2,100 distinct orders totalling approximately INR 30.7 lakh in sales. Most regions show month-to-month sales variation within expected ranges, and Nellore has remained the desk's most stable region across both transitions.

**Complication:** Guntur, a Tier-2 region in Andhra Pradesh, recorded a +122.19% sales surge from April (INR 62,442.27) to May (INR 138,738.93) - the single largest swing across all 9 regions in either transition. This was followed by a -28.11% drop from May to June (INR 99,745.18). The spike is driven by both higher order volume (51 to 77 orders, +50.98%) and higher average order value (INR 1, 224.36 to INR 1,801.80), but the underlying cause - whether a one-time bulk order, a category mix shift, or a genuine demand increase - is unknown from the order data alone.

**Resolution:** The Guntur regional lead should conduct a category-level review of May 2026 orders to identify which product categories drove the AOV increase. A follow-up check against July 2026 data will confirm whether the June decline is a reversion to the April baseline or the beginning of a sustained change. Until then, no operational changes (staffing, inventory) should be triggered by the May number alone.

## Reframing 2: For a Regional Manager (Overview-Category-Detail)

**Overview:** Guntur's total sales increased +122.19% from April to May 2026 (INR 62,442.27 to INR 138, 738.93), making it the largest single-month swing across the entire Telugu-states desk. The order count rose from 51 to 77.

**Category:** The dataset contains 6 product categories: OTC Medicines, Prescription Medicines, Wellness & Nutrition, Personal Care, Medical Devices, and Lab Tests. The average order value in Guntur jumped from INR 1,224.36 (April) to INR 1,801.80 (May), suggesting that higher-value categories such as Medical Devices or Wellness & Nutrition may have disproportionately contributed to the spike. The category breakdown in the dashboard's filtered view for Guntur shows where the concentration lies.

**Detail:** The +122.19% figure is computed from SQL GROUP BY queries (region x month) against the cleaned 2,100-row dataset in pharmeasy.db. The cleaning pipeline removed 59 exact duplicates, normalized 16 raw region-name variants to 9 canonical names, and imputed 94 missing profit values and 48 missing category values using deterministic methods (product-category lookup and category-mean margin). The flagging threshold of 8% is an operational heuristic - at Guntur's order volumes (~50-80/month), this threshold will catch ordinary month-to-month noise, which is why the +122.19% swing stands out even in a noisy context.

---

## Anticipated Pushback QSA

### 01: "Why should I believe this +122.19% number?"

1. **Acknowledge:** That is the right question - any number this large should be scrutinised before acting on it.

2. **Verified vs. not verified:** The +122.19% figure is directly computed from a SQL GROUP BY query on the cleaned dataset (April sales INR 62,442.27, May sales INR 138,738.93), and the cleaning pipeline's output has been validated: 59 duplicates removed, 2,100 rows remaining, zero missing values after imputation. The raw dataset is deterministic (seed 2026), so anyone who runs generate_dataset.py and the pipeline will reproduce the same number. What is *not* verified is whether any of the 77 May orders for Guntur are anomalous (e.g. test orders, mis-tagged region, or a single bulk order skewing the total).

3. **Resolution:** A line-item review of Guntur's May orders - sorted by sales_inr descending - would confirm within one session whether a small number of high-value orders are responsible. This can be done by the regional load this week using the dashboard's detail view.

### Q2: "What if the spike is just normal seasonal variation?"

1. **Acknowledge:** With only 3 months of data and ~50-80 orders per region per month, it is entirely possible that this is within the range of ordinary month-to-month noise.

2. **Verified vs. not verified:** What is verified is that no other region shows a comparable magnitude swing in a single transition - the next largest is Visakhapatnam at -62.46%, which has a known dataset-level multiplier (0.45 in May) that explains it. What is *not* verified is whether Guntur has a historical baseline (from months prior to April 2026) against which the May spike can be contextualised, because the dataset only covers April-June.

3. **Resolution:** Extending the analysis to include at least 6-12 months of prior data - if available from PharmEasy's monthly exports - would establish a seasonal baseline for Guntur. Until that data is Loaded, the recommendation is to treat the spike as "worth investigating" but not to commit operational resources to it.