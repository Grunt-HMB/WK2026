from datetime import datetime
from zoneinfo import ZoneInfo

APP_TIMEZONE = "Europe/Brussels"

TOURNAMENT_START = datetime(
    2026, 6, 11, 23, 59,
    tzinfo=ZoneInfo(APP_TIMEZONE)
)

REQUIRED_SHEETS = {
    "Users": ["user_id", "naam", "pincode", "admin"],
    "Matches": ["match_id", "speeldag", "ronde", "groep", "team1", "team2", "datum", "tijd", "team1_code", "team2_code"],
    "Predictions": ["user_id", "match_id", "prediction", "score1", "score2", "status", "timestamp"],
    "Results": ["match_id", "real_team1", "real_team2", "timestamp"],
}

PREDICTION_OPTIONS = ["1", "X", "2"]
