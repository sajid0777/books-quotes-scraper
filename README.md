# Books and Quotes Scraper Assignment

## Requirements and run

Python 3.10–3.12. From this directory, create and activate a virtual environment, install `requirements.txt`, then run `python main.py`. The program scrapes Books to Scrape and Quotes to Scrape, then writes `output/final_dataset.csv`, `output/summary_report.json`, and `logs/scraper.log`. Run offline unit tests with `python -m pytest`.

## Optional live demo UI

`app.py` adds a small Streamlit interface for viewing, filtering, and downloading the generated dataset and summary. It also has a button to run the scraper again. Start it locally from this directory with `streamlit run app.py`. The app does not need MongoDB credentials; Atlas is only used by the optional local `run_with_atlas.py` launcher.

To publish the demo, push this project to a GitHub repository and deploy `app.py` using Streamlit Community Cloud. Community Cloud provides a public app URL. Do not add Atlas passwords, connection URIs, or other secrets to the repository. The live demo uses the bundled sample output until a visitor clicks **Run the scraper**.

Optional MongoDB Atlas output: run `python run_with_atlas.py` to open a local form for the Atlas database username and password. The launcher builds and encodes the connection URI for the configured cluster; the password is masked, and credentials are not saved in the project. `MONGODB_DATABASE` and `MONGODB_COLLECTION` optionally select the destination (defaults: `scraping_assignment` and `records`). Records are upserted using their normalized fingerprint as `_id`, so reruns do not add duplicate documents. Without credentials, running `python main.py` creates the local files and skips Atlas. Keep Atlas credentials private; never commit them or put them in source code.

## Site observations

Books use `article.product_pod`; title and relative detail link are in `h3 > a` (the full title is in its `title` attribute), price is in `p.price_color`, rating is a word in the classes on `p.star-rating`, and pagination uses `li.next > a`. Quotes use `div.quote`; quote text is in `span.text`, author in `small.author`, tags in zero or more `a.tag`, and pagination also uses `li.next > a`.

## Data model

The CSV columns are `source`, `source_url`, `name_or_title`, `category`, `price`, `rating`, `author`, `tags`, `description`, and `scraped_at`. Empty values mean that a field does not apply or was not collected. For books, category and description are blank: listing pages do not provide them, and this implementation does not make roughly 1,000 extra detail-page requests. For quotes, `source_url` uses the author page when present, otherwise the listing page. Quote tags are lowercased, sorted, and joined with semicolons.

## Processing decisions

The shared HTTP client uses a descriptive User-Agent, 10-second timeout, and retries temporary HTTP errors. Scrapers follow each page's actual next link; they do not hard-code page counts. Requests are separated by a 0.5-second pause. Whitespace and non-breaking spaces are normalized, quote marks removed, prices converted to numbers, ratings converted to integers 1–5, tags normalized, and URLs made absolute. Validation returns reason codes for unknown source, missing name, invalid URL, invalid price, and invalid rating. Invalid rows are rejected and counted. Duplicate fingerprints use source + title for books, and source + author + first 50 quote characters for quotes, normalized for case, punctuation, and spacing. Duplicates are dropped from the CSV and counted in the report.

Each source is isolated so a failed request is logged and does not prevent the other source from running. Per-record parse problems are logged and skipped. The report's counts should satisfy raw records minus rejected records minus duplicates equals final rows (rejection reasons may overlap for one record, so rejected_total counts records and rejected_by_reason counts each reason).

## Limitations

Book category and description are not collected. The two practice sites are expected to yield roughly 1,000 books and 100 quotes, but network failures or site changes can reduce the observed counts. No login, CAPTCHA, or access protection is bypassed.

