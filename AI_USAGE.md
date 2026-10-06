# AI usage disclosure

## Tool used

OpenAI Codex was used throughout the project to interpret the assignment, create and revise the Python implementation, debug the Atlas connection setup, and prepare documentation and this optional Streamlit demo interface.

## Representative prompts

- “tell me what to do from the assignment”
- “start” (in context, asking Codex to build the assignment in the workspace)
- “give me commands one after one (copyable)”
- “take access and do it” (in context, asking for help connecting the scraper to the user's Atlas cluster)
- “ok do it” (in context, asking Codex to prepare a small web demo for publishing)

## AI-assisted parts and review changes

Codex drafted the scrapers, shared HTTP helper, cleaning, validation, duplicate detection, output generation, tests, README, Atlas integration, and the optional Streamlit demo. The Atlas launcher was revised to collect credentials in a masked local dialog and URL-encode them, after the first connection attempt exposed a URI-escaping issue. The Streamlit demo reads only the generated local CSV and JSON files and does not contain or require Atlas credentials.

## Verification

The original scraper run collected 1,000 books and 100 quotes, found one duplicate title, and wrote 1,099 final rows. Four unit tests passed. A subsequent run successfully upserted or refreshed 1,099 records in the user's MongoDB Atlas cluster. The Streamlit interface was added after those checks; it has not yet been run or deployed. Review and understand the implementation before submission, as the assignment expects the candidate to explain it in an interview.

