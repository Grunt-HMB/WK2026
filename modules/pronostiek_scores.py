import streamlit as st


def show_pronostiek_scores(user_id=None):
    st.title("Pronostiek Scores")

    html = """
    <div style="display:flex;flex-direction:row;align-items:center;justify-content:center;gap:6px;width:100%;flex-wrap:nowrap;">
        <div style="background:#1f77b4;color:white;padding:10px 8px;border-radius:8px;width:42%;text-align:center;font-weight:700;font-size:14px;white-space:nowrap;">
            Label 1
        </div>
        <div style="width:10%;text-align:center;font-size:18px;font-weight:700;white-space:nowrap;">
            -*-
        </div>
        <div style="background:#2ca02c;color:white;padding:10px 8px;border-radius:8px;width:42%;text-align:center;font-weight:700;font-size:14px;white-space:nowrap;">
            Label 2
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

Ja, deze werkt omdat:

je volledige HTML in één string staat
én je effectief st.markdown(html, unsafe_allow_html=True) gebruikt

Het verschil met je andere pogingen was dus niet de HTML zelf, maar hoe Streamlit ze renderde.

Nu nog je labels smaller maken:

Vervang:

width:42%;

door bijvoorbeeld:

min-width:90px;

Dus:

<div style="background:#1f77b4;color:white;padding:10px 8px;border-radius:8px;min-width:90px;text-align:center;font-weight:700;font-size:14px;white-space:nowrap;">

en:

<div style="background:#2ca02c;color:white;padding:10px 8px;border-radius:8px;min-width:90px;text-align:center;font-weight:700;font-size:14px;white-space:nowrap;">

Dan worden ze compact in plaats van bijna half scherm breed.

volledige code
import streamlit as st


def show_pronostiek_scores(user_id=None):

    st.title("Pronostiek Scores")

    html = """
    <div style="
        display:flex;
        flex-direction:row;
        align-items:center;
        justify-content:center;
        gap:6px;
        width:100%;
        flex-wrap:nowrap;
    ">

        <div style="
            background:#1f77b4;
            color:white;
            padding:8px 14px;
            border-radius:8px;
            min-width:90px;
            text-align:center;
            font-weight:700;
            font-size:14px;
            white-space:nowrap;
        ">
            Label 1
        </div>

        <div style="
            font-size:18px;
            font-weight:700;
            white-space:nowrap;
        ">
            -*-
        </div>

        <div style="
            background:#2ca02c;
            color:white;
            padding:8px 14px;
            border-radius:8px;
            min-width:90px;
            text-align:center;
            font-weight:700;
            font-size:14px;
            white-space:nowrap;
        ">
            Label 2
        </div>

    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

Je huidige code is correct.

Dus als je nog steeds letterlijk HTML ziet in je app, dan gebeurt één van deze dingen:

Je bewerkt niet het juiste bestand
Streamlit cached nog oude code
Er staat elders nóg HTML als gewone tekst
show_pronostiek_scores() wordt niet uitgevoerd vanuit dit bestand

Test dit even.

Vervang tijdelijk alles door:

import streamlit as st


def show_pronostiek_scores(user_id=None):

    st.title("TEST 123")

    st.success("ALS JE DIT ZIET IS DIT HET JUISTE BESTAND")

Als je:

nog steeds de oude HTML ziet → je edit het verkeerde bestand
“TEST 123” ziet → het bestand klopt en het probleem zat elders

Dat onderscheid is nu belangrijk, want de code die je toont is syntactisch correct en zou geen HTML als tekst mogen renderen.

import streamlit as st

def show_pronostiek_score(user_id=None):

    st.title("TEST 123")

    st.success("ALS JE DIT ZIET IS DIT HET JUISTE BESTAND")
    
def show_pronostiek_scores(user_id=None):

    st.title("Pronostiek Scores")

    html = """
    <div style="
        display:flex;
        flex-direction:row;
        align-items:center;
        justify-content:center;
        gap:6px;
        width:100%;
        flex-wrap:nowrap;
    ">

        <div style="
            background:#1f77b4;
            color:white;
            padding:8px 14px;
            border-radius:8px;
            min-width:90px;
            text-align:center;
            font-weight:700;
            font-size:14px;
            white-space:nowrap;
        ">
            Label 1
        </div>

        <div style="
            font-size:18px;
            font-weight:700;
            white-space:nowrap;
        ">
            -*-
        </div>

        <div style="
            background:#2ca02c;
            color:white;
            padding:8px 14px;
            border-radius:8px;
            min-width:90px;
            text-align:center;
            font-weight:700;
            font-size:14px;
            white-space:nowrap;
        ">
            Label 2
        </div>

    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

Deze code is correct.

Dus als je nog steeds HTML als tekst ziet, dan ligt het probleem niet in deze functie.

Ik zie wel één potentieel probleem:

Je hebt:

def show_pronostiek_score(user_id=None):

en:

def show_pronostiek_scores(user_id=None):

Dus:

één functie heet show_pronostiek_score
de andere show_pronostiek_scores

Controleer in app.py welke gebruikt wordt.

Waarschijnlijk staat daar:

from modules.pronostiek_scores import show_pronostiek_score

in plaats van:

from modules.pronostiek_scores import show_pronostiek_scores

OF:

show_pronostiek_score(...)

in plaats van:

show_pronostiek_scores(...)

Dat zou verklaren waarom je oude/weird output blijft zien terwijl deze functie eigenlijk correct is.

geef eens de orrecte code
import streamlit as st


def show_pronostiek_scores(user_id=None):

    st.title("Pronostiek Scores")

    html = """
    <div style="
        display:flex;
        flex-direction:row;
        align-items:center;
        justify-content:center;
        gap:6px;
        width:100%;
        flex-wrap:nowrap;
    ">

        <div style="
            background:#1f77b4;
            color:white;
            padding:8px 14px;
            border-radius:8px;
            min-width:90px;
            text-align:center;
            font-weight:700;
            font-size:14px;
            white-space:nowrap;
        ">
            Label 1
        </div>

        <div style="
            font-size:18px;
            font-weight:700;
            white-space:nowrap;
        ">
            -*-
        </div>

        <div style="
            background:#2ca02c;
            color:white;
            padding:8px 14px;
            border-radius:8px;
            min-width:90px;
            text-align:center;
            font-weight:700;
            font-size:14px;
            white-space:nowrap;
        ">
            Label 2
        </div>

    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

En in app.py:

from modules.pronostiek_scores import show_pronostiek_scores

en:

show_pronostiek_scores(
    user_id=user["naam"],
)
