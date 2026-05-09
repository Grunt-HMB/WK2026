import streamlit as st


GROUP_ORDER = list("ABCDEFGHIJKL")


def get_phase_buttons(matches_df):
    phases = []

    if "groep" in matches_df.columns:
        raw_groups = [
            str(g).strip()
            for g in matches_df["groep"].dropna().unique()
        ]

        group_values = [
            g for g in GROUP_ORDER
            if g in raw_groups
        ]

        for group in group_values:
            phases.append({
                "key": f"Groep {group}",
                "label": group,
                "type": "groep",
                "value": group,
            })

    ronde_order = [
        ("1/16", "1/16"),
        ("1/8", "1/8"),
        ("1/4", "1/4"),
        ("1/2", "1/2"),
        ("Troostfinale", "Troost"),
        ("Finale", "Finale"),
    ]

    if "ronde" in matches_df.columns:
        ronde_values = set(
            matches_df["ronde"]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

        for ronde_value, label in ronde_order:
            if ronde_value in ronde_values:
                phases.append({
                    "key": ronde_value,
                    "label": label,
                    "type": "ronde",
                    "value": ronde_value,
                })

    return phases


def show_phase_row(row):
    cols = st.columns(len(row), gap="small")

    for idx, phase in enumerate(row):
        with cols[idx]:
            is_active = st.session_state["selected_phase_key"] == phase["key"]
            label = f"✅ {phase['label']}" if is_active else phase["label"]

            if st.button(
                label,
                key=f"phase_button_{phase['key']}",
                use_container_width=True,
            ):
                st.session_state["selected_phase_key"] = phase["key"]
                st.rerun()


def show_phase_buttons(phases):
    if not phases:
        return None

    valid_keys = [p["key"] for p in phases]

    if "selected_phase_key" not in st.session_state:
        st.session_state["selected_phase_key"] = valid_keys[0]

    if st.session_state["selected_phase_key"] not in valid_keys:
        st.session_state["selected_phase_key"] = valid_keys[0]

    st.markdown("### Kies groep / eindfase")

    # Rij 1: groepen A t/m I
    row1 = phases[:9]

    # Rij 2: groepen J/K/L + eindfases
    row2 = phases[9:]

    if row1:
        show_phase_row(row1)

    if row2:
        show_phase_row(row2)

    selected_key = st.session_state["selected_phase_key"]

    for phase in phases:
        if phase["key"] == selected_key:
            return phase

    return phases[0]


def filter_matches_by_phase(matches_df, phase):
    if phase["type"] == "groep":
        return matches_df[
            matches_df["groep"].astype(str).str.strip() == str(phase["value"])
        ].copy()

    if phase["type"] == "ronde":
        return matches_df[
            matches_df["ronde"].astype(str).str.strip() == str(phase["value"])
        ].copy()

    return matches_df.copy()
