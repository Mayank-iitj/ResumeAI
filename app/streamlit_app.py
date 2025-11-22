import streamlit as st
from pathlib import Path
import os
import pandas as pd
from io import BytesIO
from resume_screening.parser import parse_file
from resume_screening.nlp_extractor import extract_skills, extract_entities, embed_texts
from resume_screening.scoring_engine import (
    skill_score,
    experience_score,
    education_score,
    domain_score,
    soft_skill_score,
    aggregate_scores,
    categorize,
)
from resume_screening.suggestions import generate_suggestions
from resume_screening.similarity import responsibilities_similarity
from resume_screening.report import build_pdf
from resume_screening.evaluation import evaluate_fit
from resume_screening.config import MUST_HAVE_SKILLS
from resume_screening.logging_config import configure_logging
from resume_screening.anonymize import anonymize
from dotenv import load_dotenv

load_dotenv()
logger = configure_logging()

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "2"))
ENABLE_ANON = os.getenv("ENABLE_ANONYMIZATION", "false").lower() == "true"

st.set_page_config(page_title="AI Resume Screening", layout="wide")
st.title("AI Resume Screening & Fit Prediction")

with st.sidebar:
    st.header("Configuration")
    seniority = st.selectbox("Seniority", ["Junior", "Mid", "Senior"], index=1)
    jd_years_required = st.number_input("JD Required Years", min_value=0, max_value=30, value=3)
    min_edu = st.selectbox("Minimum Education", ["None", "Bachelor", "Master", "PhD"], index=1)
    required_skills_input = st.text_input("Required skills (comma)", ", ".join(MUST_HAVE_SKILLS))
    optional_skills_input = st.text_input("Optional skills (comma)", "docker, airflow")
    multi_jd_mode = st.checkbox("Multi-JD Mode")
    evaluation_mode = st.checkbox("Evaluation Mode (Upload Labeled CSV)")

st.subheader("Job Descriptions")
if multi_jd_mode:
    jd_files = st.file_uploader("Upload JD files (txt/pdf/docx)", type=["txt", "pdf", "docx"], accept_multiple_files=True)
    jd_texts_manual = st.text_area("Paste multiple JDs separated by \n---\n", height=200)
else:
    jd_file = st.file_uploader("Upload JD file (txt/pdf/docx) OR paste below", type=["txt", "pdf", "docx"], accept_multiple_files=False)
    jd_text_area = st.text_area("Paste JD text", height=160)

st.subheader("Resumes")
resume_files = st.file_uploader("Upload one or more resumes", type=["pdf", "docx", "txt"], accept_multiple_files=True)
anon_toggle = st.checkbox("Anonymize resumes before scoring", value=ENABLE_ANON)

process = st.button("Process & Rank Candidates")

required_skills = [s.strip().lower() for s in required_skills_input.split(",") if s.strip()]
optional_skills = [s.strip().lower() for s in optional_skills_input.split(",") if s.strip()]

if process:
    if not resume_files:
        st.error("Please upload at least one resume.")
    # Gather JDs
    jd_texts = []
    jd_names = []
    if multi_jd_mode:
        if jd_files:
            for f in jd_files:
                temp = Path(f"temp_jd_{f.name}")
                temp.write_bytes(f.read())
                content, _ = parse_file(str(temp))
                jd_texts.append(content)
                jd_names.append(f.name)
        if jd_texts_manual.strip():
            parts = [p.strip() for p in jd_texts_manual.split("---") if p.strip()]
            for i, p in enumerate(parts):
                jd_texts.append(p)
                jd_names.append(f"manual_{i+1}")
        if not jd_texts:
            st.error("Provide at least one JD via upload or text area.")
            st.stop()
    else:
        if jd_file:
            temp_jd_path = Path(f"temp_jd{Path(jd_file.name).suffix}")
            temp_jd_path.write_bytes(jd_file.read())
            jd_text, _ = parse_file(str(temp_jd_path))
        else:
            jd_text = jd_text_area
        if not jd_text.strip():
            st.error("Provide JD via upload or text area.")
            st.stop()
        jd_texts = [jd_text]
        jd_names = [jd_file.name if jd_file else "pasted_jd"]

    candidate_rows_multi = []  # for multi-JD summary
    best_rows = []
    detailed_results_all = []

    for rf in resume_files:
        temp_path = Path(f"temp_{rf.name}")
        temp_path.write_bytes(rf.read())
        size_mb = temp_path.stat().st_size / (1024*1024)
        if size_mb > MAX_UPLOAD_MB:
            st.warning(f"Skipping {rf.name}: file size {size_mb:.2f} MB exceeds limit {MAX_UPLOAD_MB} MB")
            continue
        resume_text, sections = parse_file(str(temp_path))

        if anon_toggle:
            resume_text, pii_map = anonymize(resume_text)
        else:
            pii_map = {}

        skills = extract_skills(resume_text)
        entities = extract_entities(resume_text)

        per_jd_scores = []
        per_jd_details = []

        for jd_idx, jd_t in enumerate(jd_texts):
            skill_part = skill_score(skills, required_skills, optional_skills)
            exp_part = experience_score(resume_text, jd_years_required, seniority)
            edu_part = education_score(resume_text, min_edu if min_edu != "None" else "")
            domain_part = domain_score(resume_text, jd_t)
            soft_part = soft_skill_score(skills, resume_text)

            parts = {
                "skill": skill_part,
                "experience": exp_part,
                "education": edu_part,
                "domain": domain_part,
                "soft": soft_part,
            }
            agg = aggregate_scores(parts)
            overall = agg["overall"]
            category = categorize(overall)
            suggestions = generate_suggestions(skill_part, exp_part, edu_part, jd_t)

            # Similarity (optional) using responsibilities vs experience section
            resp_section = jd_t.splitlines()
            exp_section = sections.get("experience", "").splitlines()
            similarity = responsibilities_similarity(resp_section[:30], exp_section[:50])

            per_jd_scores.append({
                "file": rf.name,
                "jd_name": jd_names[jd_idx],
                "overall": round(overall, 2),
                "category": category,
                "skill_score": round(skill_part["score"],2),
                "experience_score": round(exp_part["score"],2),
                "education_score": round(edu_part["score"],2),
                "domain_score": round(domain_part["score"],2),
                "soft_score": round(soft_part["score"],2),
                "similarity_avg": similarity["average_similarity"],
            })

            per_jd_details.append({
                "file": rf.name,
                "jd_name": jd_names[jd_idx],
                "sections": sections,
                "skills": skills,
                "entities": entities,
                "pii_removed": pii_map,
                "parts": parts,
                "overall": overall,
                "category": category,
                "suggestions": suggestions,
                "similarity": similarity,
            })

        # Choose best JD by highest overall
        best = max(per_jd_scores, key=lambda r: r["overall"]) if per_jd_scores else None
        if best:
            best_rows.append({"file": rf.name, **best})
        candidate_rows_multi.extend(per_jd_scores)
        detailed_results_all.extend(per_jd_details)

    if multi_jd_mode:
        st.subheader("Per-JD Scores")
        df_multi = pd.DataFrame(candidate_rows_multi).sort_values(by=["file","overall"], ascending=[True, False])
        st.dataframe(df_multi, use_container_width=True)
        st.subheader("Best JD Match per Candidate")
        df_best = pd.DataFrame(best_rows).sort_values(by="overall", ascending=False)
        st.dataframe(df_best, use_container_width=True)
        # CSV downloads
        st.download_button("Download Per-JD CSV", df_multi.to_csv(index=False), file_name="per_jd_scores.csv")
        st.download_button("Download Best JD CSV", df_best.to_csv(index=False), file_name="best_jd_scores.csv")
    else:
        st.subheader("Ranking")
        simple_df = pd.DataFrame(candidate_rows_multi).sort_values(by="overall", ascending=False)
        st.dataframe(simple_df, use_container_width=True)
        st.download_button("Download Scores CSV", simple_df.to_csv(index=False), file_name="scores.csv")

    # Detailed expandable results
    for result in detailed_results_all:
        with st.expander(f"Details: {result['file']} | JD: {result['jd_name']} ({result['category']}, {result['overall']:.2f})"):
            st.write("### Score Breakdown")
            bp = result["parts"]
            st.write({
                "skill": bp["skill"]["score"],
                "experience": bp["experience"]["score"],
                "education": bp["education"]["score"],
                "domain": bp["domain"]["score"],
                "soft": bp["soft"]["score"],
            })
            st.write("### Skills")
            st.write({
                "must_match": bp["skill"]["must_match"],
                "must_missing": bp["skill"]["must_missing"],
                "opt_match": bp["skill"]["opt_match"],
                "opt_missing": bp["skill"]["opt_missing"],
            })
            st.write("### Suggestions")
            for s in result["suggestions"]["suggestions"]:
                st.markdown(f"- {s}")
            st.write("### Entities (spaCy)")
            st.write(result["entities"])
            st.write("### Similarity (Responsibilities ↔ Experience)")
            st.write({"avg": result["similarity"]["average_similarity"], "top_pairs": result["similarity"]["pairs"][:5]})
            if anon_toggle:
                st.write("### Anonymization Map")
                st.write(result["pii_removed"])

            # PDF report download for this candidate/JD
            pdf_bytes = build_pdf(
                candidate_name=result["file"],
                jd_title=result["jd_name"],
                scores={
                    "overall": result["overall"],
                    "skill": bp["skill"]["score"],
                    "experience": bp["experience"]["score"],
                    "education": bp["education"]["score"],
                    "domain": bp["domain"]["score"],
                    "soft": bp["soft"]["score"],
                },
                missing_skills=bp["skill"]["must_missing"],
                suggestions=result["suggestions"]["suggestions"],
            )
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=f"report_{result['file']}_{result['jd_name']}.pdf",
                mime="application/pdf"
            )

    if evaluation_mode:
        st.subheader("Evaluation")
        eval_file = st.file_uploader("Upload labeled CSV (columns: resume, jd_name, label, predicted(optional))", type=["csv"], accept_multiple_files=False)
        if eval_file:
            df_eval = pd.read_csv(eval_file)
            if "label" not in df_eval.columns:
                st.error("CSV must contain a 'label' column with ground truth (0/1).")
            else:
                # If predicted provided use it, else map from best_rows/simple scores threshold 0.6
                if "predicted" in df_eval.columns:
                    y_pred = df_eval["predicted"].tolist()
                else:
                    # naive threshold using current processed best rows
                    score_map = {r["file"] + "|" + r.get("jd_name","pasted_jd"): r["overall"] for r in candidate_rows_multi}
                    y_pred = []
                    for _, row in df_eval.iterrows():
                        key = str(row["resume"]) + "|" + str(row.get("jd_name","pasted_jd"))
                        sc = score_map.get(key, 0)
                        y_pred.append(1 if sc >= 0.6 else 0)
                y_true = df_eval["label"].tolist()
                metrics = evaluate_fit(y_true, y_pred)
                st.write(metrics)
                st.download_button("Download Metrics JSON", pd.DataFrame([metrics]).to_json(), file_name="metrics.json")
