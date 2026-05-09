import streamlit as st


def get_phase_buttons(matches_df):
    phases = []

    group_values = sorted([
        str(g)
        for g in matches_df["groep"].dropna().unique()
        if str(g).strip() not in ["", "-", "Knock-out"]
    ])

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


def show_phase_buttons(phases):
    if not phases:
        return None

    valid_keys = [p["key"] for p in phases]

    if "selected_phase_key" not in st.session_state:
        st.session_state["selected_phase_key"] = valid_keys[0]

    if st.session_state["selected_phase_key"] not in valid_keys:
        st.session_state["selected_phase_key"] = valid_keys[0]

    st.markdown("### Kies groep / eindfase")

    first_row = phases[:9]
    second_row = phases[9:]

    st.markdown('<div class="phase-grid">', unsafe_allow_html=True)

    for phase in first_row:
        is_active = st.session_state["selected_phase_key"] == phase["key"]
        label = f"✅ {phase['label']}" if is_active else phase["label"]

        if st.button(label, key=f"phase_button_{phase['key']}"):
            st.session_state["selected_phase_key"] = phase["key"]
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if second_row:
        st.markdown('<div class="phase-grid">', unsafe_allow_html=True)

        for phase in second_row:
            is_active = st.session_state["selected_phase_key"] == phase["key"]
            label = f"✅ {phase['label']}" if is_active else phase["label"]

            if st.button(label, key=f"phase_button_{phase['key']}"):
                st.session_state["selected_phase_key"] = phase["key"]
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    selected_key = st.session_state["selected_phase_key"]

    for phase in phases:
        if phase["key"] == selected_key:
            return phase

    return phases[0]


def filter_matches_by_phase(matches_df, phase):
    if phase["type"] == "groep":
        return matches_df[matches_df["groep"].astype(str) == str(phase["value"])].copy()

    if phase["type"] == "ronde":
        return matches_df[matches_df["ronde"].astype(str) == str(phase["value"])].copy()

    return matches_df.copy()
