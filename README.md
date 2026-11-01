# mindscreen — private autism-traits screening

A single-page, no-server site for completing the AQ-50, EQ-60 and RQ/CAST questionnaires from the 2012 Adult Asperger Assessment (AAA) workbook. Scoring runs entirely in the browser: no account, no tracking, no analytics, and nothing is sent anywhere.

**This is a screening and self-reflection tool, not a diagnosis.**

## Files

- `index.html` — the whole app (questions are embedded as JSON, so it also works opened straight from disk).
- `audio/` — pre-recorded narration for each question, played locally by the page.
- `build_audio.py` — regenerates `audio/` with [TTS_ka](https://pypi.org/project/TTS-ka/) (Microsoft Edge neural voices). Run `python3 build_audio.py` after editing any question text; only changed clips are re-recorded.

## Attribution

Questionnaire content: Autism Spectrum Quotient (AQ), Empathy Quotient (EQ) and Childhood Autism Spectrum Test (CAST), Autism Research Centre, University of Cambridge. Use of the questionnaire content may be subject to the original authors' permissions. No affiliation with the instrument authors. Educational use only.
