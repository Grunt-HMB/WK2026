# WK 2026 Pronostiek - mooie Streamlit layout

## Bestanden
- `app.py`
- `modules/`
- `requirements.txt`
- `.streamlit/secrets.example.toml`
- `google_sheets_templates/`

## Google Sheets tabs

Maak exact deze tabs:
- Users
- Matches
- Predictions
- Results

Importeer of plak de CSV's uit `google_sheets_templates`.

## Vlaggen

Vlaggen werken via ISO-2 codes in Matches:

- België = BE
- Canada = CA
- Mexico = MX
- Japan = JP
- Frankrijk = FR
- Brazilië = BR
- Nederland = NL
- Duitsland = DE

Kolommen in Matches:

```text
match_id;speeldag;ronde;groep;team1;team2;datum;tijd;team1_code;team2_code
```

## Streamlit Cloud

Zet in Settings → Secrets je echte secrets.
Gebruik `.streamlit/secrets.example.toml` als voorbeeld.

## Lokaal starten

```powershell
pip install -r requirements.txt
streamlit run app.py
```
