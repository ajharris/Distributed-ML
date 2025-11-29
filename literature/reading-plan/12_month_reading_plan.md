# 12-Month Reading Plan for CT Phenotyping PhD Preparation

This plan is organized so that understanding compounds:
clinical foundations → CT physics → airway/parenchymal biomarkers →
deep learning → harmonization → high-scale ML → dissertation prep.

## Month 1 — Clinical Foundations of COPD & CT Imaging

Goal: understand the disease you are phenotyping.

**Weeks 1–2: COPD Pathophysiology**

- Hogg et al., 2004 — small airway obstruction in COPD.
- GOLD executive summary (latest version).
- Precision medicine approaches to COPD (review).

**Weeks 3–4: CT as a clinical measurement tool**

- Kirby et al., 2016 — CT-derived imaging biomarkers for COPD.
- CT densitometry overview papers.
- Galbán et al., 2012 — Parametric Response Mapping (PRM).

---

## Month 2 — Quantitative CT Biomarkers (Kirby Core Papers)

Goal: master functional small airway disease imaging and parenchymal phenotyping.

**Weeks 5–6**

- Kirby et al., 2015 — quantitative CT of airway disease.
- Kirby et al., 2017 — calibration / harmonization for phenotyping.
- Kirby et al., 2020 — PRM diagnostic performance in COPD.

**Weeks 7–8**

- Labaki et al., 2018 — PRM for emphysema vs air trapping.
- San José Estépar et al., 2015 — airway geometric phenotypes.
- Kirby harmonization papers (2018–2022).

---

## Month 3 — Airway & Parenchymal Morphology (Ward Cluster)

Goal: understand shape, texture, and radiomic bases of COPD quantification.

**Weeks 9–10**

- Ward et al., 2015 — texture-based lung phenotyping.
- Ward et al., 2017 — quantitative imaging biomarkers for COPD.
- Sorensen & Ward, 2019 — reproducibility of radiomic features.

**Weeks 11–12**

- Paris & Ward, 2020 — airway tree modeling and structural signatures.
- Goddard & Ward, 2021 — emphysema structural subtypes.
- van Griethuysen et al., 2017 — PyRadiomics and reproducibility.

---

## Month 4 — CT Preprocessing & Harmonization

Goal: deeply understand what your preprocessing pipeline does and why.

**Weeks 13–14: CT Physics & HU normalization**

- Chen et al., 2020 — standardization of lung densitometry.
- Kirby 2018 harmonization paper(s).

**Weeks 15–16: Lung segmentation and reconstruction effects**

- Hofmanninger et al., 2020 — robust U-Net for lung segmentation.
- Maier-Hein et al., 2018 — pitfalls of deep learning in medical imaging.

---

## Month 5 — Phenotyping Methods & Cluster Analysis

Goal: learn unsupervised and supervised COPD phenotyping methods.

**Weeks 17–18**

- Castaldi et al., 2014 — cluster-based COPD subtypes.
- San José Estépar et al., 2015 — airway geometry and subtypes.

**Weeks 19–20**

- Revisit PRM and air trapping papers (Galbán, Labaki, Kirby).
- Rahaghi et al., 2019 — automated airway phenotyping.

---

## Month 6 — Deep Learning for 3D CT

Goal: understand foundations of 3D CNNs and self-supervised learning (SSL).

**Weeks 21–22: 3D model foundations**

- Çiçek et al., 2016 — 3D U-Net.
- Kamnitsas et al., 2017 — DeepMedic.

**Weeks 23–24: Self-supervised and contrastive learning**

- Tang et al., 2022 — Models Genesis or equivalent 3D SSL work.
- Chen et al., 2020 — MoCo (core contrastive framework).
- Recent surveys on SSL in medical imaging.

---

## Month 7 — Deep Learning for COPD Phenotyping

Goal: see modern end-to-end deep learning approaches to lung phenotyping.

**Weeks 25–26**

- Kurugol et al., 2021 — 3D CNNs for COPD progression.
- Azarang et al., 2021 — deep feature learning for COPD risk.
- Related SPIROMICS imaging papers.

**Weeks 27–28**

- Ward et al., 2021 — deep features vs classical radiomics.
- Airway-oriented CNN pipelines for asthma/COPD.

---

## Month 8 — Large-Scale Pipelines & Distributed Computing

Goal: link reading to the Dask-based preprocessing in this repo.

**Weeks 29–30: Dask foundations**

- Rocklin, 2015 — Dask: parallel computation in Python.
- Khan et al., 2020 — scalable medical imaging pipelines.

**Weeks 31–32: Cloud-native imaging**

- Zarr format overview for large 3D arrays.
- MONAI data loading and preprocessing patterns.
- Overview of cloud-native imaging frameworks (e.g., Clara, open-source alternatives).

---

## Month 9 — Scanner Variability, Reproducibility & Bias

Goal: prepare to answer committee-level questions on rigor and generalization.

**Weeks 33–34**

- Maier-Hein et al., 2018 — reproducibility crisis in medical imaging.
- Ward/Sorensen radiomics robustness papers.

**Weeks 35–36**

- Papers on dataset bias in medical imaging.
- Harmonization and domain adaptation methods for CT.

---

## Month 10 — Evaluation Frameworks & Uncertainty

Goal: understand evaluation beyond a single metric.

**Weeks 37–38**

- Kendall & Gal, 2017 — aleatoric and epistemic uncertainty.
- Sokol & Flach, 2020 — explainability in medical ML.

**Weeks 39–40**

- Topol, 2019 — high-performance medicine.
- Imaging-based prognosis prediction / risk models.

---

## Month 11 — Datasets Deep Dive (NLST, COPDGene, LIDC)

Goal: full command of the datasets the pipeline targets.

**Weeks 41–42**

- Regan et al., 2010 — COPDGene study design.
- Black-Shinn et al., 2019 — NLST dataset overview.
- Armato et al., 2011 — LIDC-IDRI.

**Weeks 43–44**

- Kirby and Ward papers using COPDGene/NLST.
- Review metadata schemas and harmonization strategies used.

---

## Month 12 — Proposal, Synthesis & Research Direction

Goal: integrate everything into PhD-ready research aims.

**Weeks 45–48**

- Re-read your “top 20” most central papers.
- Summarize key methods in a comparative table.
- Identify gaps in literature.
- Draft 2–3 possible dissertation aims.

**Weeks 49–52**

- Write a preliminary research proposal (4–8 pages).
- Extend `literature-map.md` with a narrative of the field.
- Prepare draft slides for a mock committee presentation.
- Use these materials to support meetings with potential supervisors.
