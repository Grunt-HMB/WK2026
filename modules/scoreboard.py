import pandas as pd
import streamlit as st


POINTS_RESULT = 1
POINTS_EXACT_SCORE = 3


def normalize_id(value):
    return str(value or "").strip()


def to_int_or_none(value):
    try:
        txt = str(value or "").strip()
        if txt == "":
            return None
        return int(float(txt))
    except Exception:
        return None


def result_from_score(score1, score2):
    s1 = to_int_or_none(score1)
    s2 = to_int_or_none(score2)

    if s1 is None or s2 is None:
        return ""

    if s1 > s2:
        return "1"

    if s1 < s2:
        return "2"

    return "X"


def ensure_columns(df, columns):
    df = df.copy()

    for col in columns:
        if col not in df.columns:
            df[col] = ""

    return df


def build_scoreboard(users_df, predictions_df, results_df):
    users_df = ensure_columns(
        users_df,
        ["user_id", "naam", "team_name"],
    )

    predictions_df = ensure_columns(
        predictions_df,
        ["user_id", "match_id", "prediction", "score1", "score2"],
    )

    results_df = ensure_columns(
        results_df,
        ["match_id", "real_team1", "real_team2"],
    )

    if predictions_df.empty or results_df.empty:
        return pd.DataFrame()

    users_df["user_id"] = users_df["user_id"].astype(str).str.strip()
    predictions_df["user_id"] = predictions_df["user_id"].astype(str).str.strip()
    predictions_df["match_id"] = predictions_df["match_id"].astype(str).str.strip()
    results_df["match_id"] = results_df["match_id"].astype(str).str.strip()

    results_df["official_result"] = results_df.apply(
        lambda row: result_from_score(
            row.get("real_team1", ""),
            row.get("real_team2", ""),
        ),
        axis=1,
    )

    results_df = results_df[
        results_df["official_result"].isin(["1", "X", "2"])
    ].copy()

    if results_df.empty:
        return pd.DataFrame()

    merged = predictions_df.merge(
        results_df[["match_id", "real_team1", "real_team2", "official_result"]],
        on="match_id",
        how="inner",
    )

    if merged.empty:
        return pd.DataFrame()

    merged["prediction"] = merged["prediction"].astype(str).str.upper().str.strip()

    merged["punten_resultaat"] = merged.apply(
        lambda row: POINTS_RESULT
        if row.get("prediction", "") == row.get("official_result", "")
        else 0,
        axis=1,
    )

    merged["punten_exact"] = merged.apply(
        lambda row: POINTS_EXACT_SCORE
        if (
            to_int_or_none(row.get("score1", "")) is not None
            and to_int_or_none(row.get("score2", "")) is not None
            and to_int_or_none(row.get("score1", "")) == to_int_or_none(row.get("real_team1", ""))
            and to_int_or_none(row.get("score2", "")) == to_int_or_none(row.get("real_team2", ""))
        )
        else 0,
        axis=1,
    )

    merged["punten"] = merged["punten_resultaat"] + merged["punten_exact"]

    summary = merged.groupby("user_id", as_index=False).agg(
        gespeeld=("match_id", "count"),
        juiste_resultaten=("punten_resultaat", lambda s: int((s > 0).sum())),
        exacte_scores=("punten_exact", lambda s: int((s > 0).sum())),
        punten=("punten", "sum"),
    )

    summary = summary.merge(
        users_df[["user_id", "naam", "team_name"]],
        on="user_id",
        how="left",
    )

    summary["naam"] = summary["naam"].fillna(summary["user_id"])
    summary["team_name"] = summary["team_name"].fillna("")

    summary = summary.sort_values(
        ["punten", "juiste_resultaten", "exacte_scores", "naam"],
        ascending=[False, False, False, True],
        kind="stable",
    ).reset_index(drop=True)

    summary["positie"] = range(1, len(summary) + 1)

    summary = summary[
        [
            "positie",
            "naam",
            "team_name",
            "gespeeld",
            "juiste_resultaten",
            "exacte_scores",
            "punten",
        ]
    ]

    return summary


def show_scoreboard(users_df, predictions_df, results_df):
    st.subheader("📊 Algemene standen")

    st.caption(
        f"Puntentelling: {POINTS_RESULT} punt voor juiste 1/X/2, "
        f"+ {POINTS_EXACT_SCORE} punten voor exacte score."
    )

    scoreboard_df = build_scoreboard(
        users_df=users_df,
        predictions_df=predictions_df,
        results_df=results_df,
    )

    if scoreboard_df.empty:
        st.info("Nog geen algemene stand beschikbaar. Vul eerst officiële uitslagen in.")
        return

    display_df = scoreboard_df.rename(
        columns={
            "positie": "#",
            "naam": "Naam",
            "team_name": "Ploeg",
            "gespeeld": "Wedstr.",
            "juiste_resultaten": "Juist",
            "exacte_scores": "Exact",
            "punten": "Punten",
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )
