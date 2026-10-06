"""Small public demo UI for the Books + Quotes scraping assignment."""
import csv
import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "output" / "final_dataset.csv"
REPORT_PATH = ROOT / "output" / "summary_report.json"

st.set_page_config(page_title="Books & Quotes Scraper", page_icon="📚", layout="wide")
st.title("Books & Quotes Scraper")
st.write(
    "A small ETL demo that collects public practice data, cleans and validates it, "
    "removes duplicates, and combines books and quotes into one dataset."
)

if st.button("Run the scraper", type="primary"):
    try:
        with st.spinner("Scraping both practice sites. This usually takes about a minute…"):
            import main

            main.run()
        st.success("Scrape finished. The results below have been refreshed.")
    except Exception as exc:
        st.error("The scraper could not finish. See the error details below.")
        st.exception(exc)

if not CSV_PATH.exists() or not REPORT_PATH.exists():
    st.info("No output files are available yet. Click **Run the scraper** to create them.")
    st.stop()

with REPORT_PATH.open(encoding="utf-8") as handle:
    report = json.load(handle)
with CSV_PATH.open(encoding="utf-8", newline="") as handle:
    records = list(csv.DictReader(handle))

collected = report.get("collected_per_source", {})
metric_columns = st.columns(4)
metric_columns[0].metric("Books collected", collected.get("Books to Scrape", 0))
metric_columns[1].metric("Quotes collected", collected.get("Quotes to Scrape", 0))
metric_columns[2].metric("Duplicates removed", report.get("duplicates_detected", 0))
metric_columns[3].metric("Final records", report.get("final_record_count", len(records)))

st.caption(
    f"Run time: {report.get('duration_seconds', '—')} seconds · "
    f"Rejected records: {report.get('rejected_total', 0)}"
)

download_columns = st.columns(2)
download_columns[0].download_button(
    "Download CSV dataset",
    data=CSV_PATH.read_bytes(),
    file_name="final_dataset.csv",
    mime="text/csv",
)
download_columns[1].download_button(
    "Download summary report",
    data=REPORT_PATH.read_bytes(),
    file_name="summary_report.json",
    mime="application/json",
)

st.subheader("Consolidated data")
source_filter = st.selectbox(
    "Filter by source",
    ["All sources", "Books to Scrape", "Quotes to Scrape"],
)
search = st.text_input("Search titles, quotes, authors, or tags")
visible_records = records
if source_filter != "All sources":
    visible_records = [row for row in visible_records if row["source"] == source_filter]
if search.strip():
    query = search.strip().casefold()
    visible_records = [
        row
        for row in visible_records
        if any(query in (value or "").casefold() for value in row.values())
    ]
st.caption(f"Showing {len(visible_records):,} of {len(records):,} records")
st.dataframe(visible_records, use_container_width=True, hide_index=True, height=520)

with st.expander("About the data and limitations"):
    st.write(
        "Data comes from the public Books to Scrape and Quotes to Scrape practice sites. "
        "Book category and description are blank because the listing pages do not provide them; "
        "the scraper does not make roughly 1,000 extra detail-page requests."
    )
    st.write("This demo does not need Atlas credentials. MongoDB Atlas is an optional output for local runs.")
