import streamlit as st
import streamlit.components.v1 as components


def show_stand_uitprinten():
    st.title("🖨️ Stand uitprinten")

    team1 = "Mexico"
    team2 = "Zuid-Afrika"

    html_code = f"""
    <div style="
        font-family: Arial, sans-serif;
        display: flex;
        justify-content: center;
        padding-top: 10px;
    ">
        <div style="
            width: 100%;
            max-width: 440px;
            padding: 24px;
            border-radius: 16px;
            border: 1px solid #ddd;
            background: #ffffff;
            color: #111827;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        ">

            <h2 style="
                text-align: center;
                margin-top: 0;
                margin-bottom: 20px;
                font-size: 22px;
            ">
                Score invullen
            </h2>

            <div style="
                display: grid;
                grid-template-columns: 1fr 120px 1fr;
                gap: 10px;
                align-items: center;
                margin-bottom: 20px;
            ">
                <div style="text-align: right; font-size: 16px; font-weight: 800;">
                    <div style="margin-bottom: 4px;">{team1}</div>
                    <input id="score1" type="text" placeholder="0" readonly
                        style="width: 55px; height: 38px; font-size: 22px; text-align: center; border: 2px solid #cbd5e1; border-radius: 8px; outline: none; background: #fff;">
                </div>

                <div style="display: flex; gap: 4px; justify-content: center;">
                    <button onclick="choosePrediction('1')" style="flex: 1; height: 42px; font-size: 16px; font-weight: bold; cursor: pointer; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px;">1</button>
                    <button onclick="choosePrediction('X')" style="flex: 1; height: 42px; font-size: 16px; font-weight: bold; cursor: pointer; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px;">X</button>
                    <button onclick="choosePrediction('2')" style="flex: 1; height: 42px; font-size: 16px; font-weight: bold; cursor: pointer; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px;">2</button>
                </div>

                <div style="text-align: left; font-size: 16px; font-weight: 800;">
                    <div style="margin-bottom: 4px;">{team2}</div>
                    <input id="score2" type="text" placeholder="0" readonly
                        style="width: 55px; height: 38px; font-size: 22px; text-align: center; border: 2px solid #cbd5e1; border-radius: 8px; outline: none; background: #fff;">
                </div>
            </div>

            <div id="prediction-alert" style="
                text-align: center;
                font-weight: bold;
                color: #2563eb;
                font-size: 14px;
                margin-bottom: 15px;
                display: none;
            "></div>

            <div id="keyboard-panel" style="
                display: none;
                background: #f8fafc;
                padding: 14px;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            ">

                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
                    border-bottom: 1px solid #e2e8f0;
                    padding-bottom: 6px;
                ">
                    <span style="font-weight: bold; font-size: 13px; color: #475569;">
                        Exacte doelpunten:
                    </span>

                    <button onclick="closePanel()" style="
                        background: #ef4444;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 4px 10px;
                        font-size: 11px;
                        font-weight: bold;
                        cursor: pointer;
                    ">
                        Sluiten
                    </button>
                </div>

                <div style="
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 16px;
                ">
                    <div>
                        <div style="
                            font-size: 12px;
                            font-weight: bold;
                            margin-bottom: 6px;
                            text-align: center;
                            color: #64748b;
                        ">
                            {team1}
                        </div>

                        <div id="grid-t1" style="
                            display: grid;
                            grid-template-columns: repeat(3, 1fr);
                            gap: 5px;
                        "></div>
                    </div>

                    <div>
                        <div style="
                            font-size: 12px;
                            font-weight: bold;
                            margin-bottom: 6px;
                            text-align: center;
                            color: #64748b;
                        ">
                            {team2}
                        </div>

                        <div id="grid-t2" style="
                            display: grid;
                            grid-template-columns: repeat(3, 1fr);
                            gap: 5px;
                        "></div>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <script>
        var label1 = "{team1}";
        var label2 = "{team2}";

        function choosePrediction(type) {{
            document.getElementById('score1').value = "";
            document.getElementById('score2').value = "";

            var text = "";

            if (type === '1') {{
                text = "Gekozen: " + label1 + " wint (1)";
            }}

            if (type === 'X') {{
                text = "Gekozen: Gelijkspel (X)";
            }}

            if (type === '2') {{
                text = "Gekozen: " + label2 + " wint (2)";
            }}

            document.getElementById('prediction-alert').innerText = text;
            document.getElementById('prediction-alert').style.display = 'block';

            document.getElementById('keyboard-panel').style.display = 'block';

            buildKeyboards();
        }}

        function closePanel() {{
            document.getElementById('keyboard-panel').style.display = 'none';
        }}

        function addVal1(val) {{
            var input = document.getElementById('score1');

            if (input.value.length >= 2) {{
                return;
            }}

            input.value += val;
        }}

        function delVal1() {{
            var input = document.getElementById('score1');
            input.value = input.value.substring(0, input.value.length - 1);
        }}

        function addVal2(val) {{
            var input = document.getElementById('score2');

            if (input.value.length >= 2) {{
                return;
            }}

            input.value += val;
        }}

        function delVal2() {{
            var input = document.getElementById('score2');
            input.value = input.value.substring(0, input.value.length - 1);
        }}

        function numberButton(value, target) {{
            return `
                <input
                    type="button"
                    value="${{value}}"
                    onclick="addVal${{target}}('${{value}}')"
                    style="
                        height:36px;
                        font-weight:bold;
                        cursor:pointer;
                        background:#fff;
                        border:1px solid #cbd5e1;
                        border-radius:4px;
                        font-size:14px;
                    "
                >
            `;
        }}

        function backspaceButton(target) {{
            return `
                <input
                    type="button"
                    value="←"
                    onclick="delVal${{target}}()"
                    style="
                        height:36px;
                        cursor:pointer;
                        background:#cbd5e1;
                        border:1px solid #94a3b8;
                        border-radius:4px;
                        font-size:12px;
                        font-weight:bold;
                    "
                >
            `;
        }}

        function buildKeyboards() {{
            var nums = [1, 2, 3, 4, 5, 6, 7, 8, 9];

            var grid1 = document.getElementById('grid-t1');
            var grid2 = document.getElementById('grid-t2');

            var html1 = "";
            var html2 = "";

            for (var i = 0; i < nums.length; i++) {{
                html1 += numberButton(nums[i], 1);
                html2 += numberButton(nums[i], 2);
            }}

            html1 += backspaceButton(1);
            html1 += numberButton(0, 1);

            html2 += backspaceButton(2);
            html2 += numberButton(0, 2);

            grid1.innerHTML = html1;
            grid2.innerHTML = html2;
        }}
    </script>
    """

    components.html(html_code, height=540)
