import streamlit as st
import streamlit.components.v1 as components

def show_stand_uitprinten():
    st.title("🖨️ Wedstrijd Score Invoeren")

    team1 = "Mexico"
    team2 = "Zuid-Afrika"

    html_code = f"""
    <div style="font-family:Arial, sans-serif; max-width:600px; margin:0 auto; background:#fafafa; padding:20px; border-radius:12px; border:1px solid #eee;">
        
        <div style="display:grid; grid-template-columns: 1.5fr 2fr 1.5fr; gap:15px; align-items:center; margin-bottom:25px;">
            
            <div style="text-align:right; font-size:18px; font-weight:700; color:#333;">
                {team1} <br>
                <input id="score1" type="text" placeholder="0" readonly 
                    style="font-size:22px; text-align:center; padding:5px; border-radius:6px; border:1px solid #ccc; width:50px; margin-top:5px; background:#fff;">
            </div>
            
            <div style="display:flex; gap:8px; justify-content:center;">
                <button onclick="choosePrediction('1')" style="flex:1; height:45px; font-size:16px; font-weight:bold; cursor:pointer; background:#f0f0f0; border:1px solid #ccc; border-radius:6px;">1</button>
                <button onclick="choosePrediction('X')" style="flex:1; height:45px; font-size:16px; font-weight:bold; cursor:pointer; background:#f0f0f0; border:1px solid #ccc; border-radius:6px;">X</button>
                <button onclick="choosePrediction('2')" style="flex:1; height:45px; font-size:16px; font-weight:bold; cursor:pointer; background:#f0f0f0; border:1px solid #ccc; border-radius:6px;">2</button>
            </div>

            <div style="text-align:left; font-size:18px; font-weight:700; color:#333;">
                {team2} <br>
                <input id="score2" type="text" placeholder="0" readonly 
                    style="font-size:22px; text-align:center; padding:5px; border-radius:6px; border:1px solid #ccc; width:50px; margin-top:5px; background:#fff;">
            </div>
        </div>

        <div id="prediction-alert" style="text-align:center; font-weight:bold; color:#4b9fff; margin-bottom:15px; display:none;"></div>

        <div id="keyboard-panel" style="display:none; background:#edeff1; padding:15px; border-radius:10px; border:1px solid #ccd1d9;">
            
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; border-bottom:1px solid #ccc; padding-bottom:8px;">
                <span style="font-weight:bold; font-size:14px; color:#444;">Vul de exacte scores in:</span>
                <button onclick="closePanel()" style="background:#ff4b4b; color:white; border:none; border-radius:4px; padding:5px 12px; font-size:12px; font-weight:bold; cursor:pointer;">Sluiten</button>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
                
                <div>
                    <div style="font-size:12px; font-weight:bold; margin-bottom:5px; text-align:center; color:#555;">{team1} Score</div>
                    <div id="grid-t1" style="display:grid; grid-template-columns: repeat(3, 1fr); gap:5px;">
                        </div>
                </div>

                <div>
                    <div style="font-size:12px; font-weight:bold; margin-bottom:5px; text-align:center; color:#555;">{team2} Score</div>
                    <div id="grid-t2" style="display:grid; grid-template-columns: repeat(3, 1fr); gap:5px;">
                        </div>
                </div>

            </div>
        </div>
    </div>

    <script>
        var label1 = "{team1}";
        var label2 = "{team2}";

        // Actie als er op 1, X of 2 gedrukt wordt
        function choosePrediction(type) {{
            var text = "";
            if(type === '1') text = "Gekozen: Winst voor " + label1;
            if(type === 'X') text = "Gekozen: Gelijkspel (X)";
            if(type === '2') text = "Gekozen: Winst voor " + label2;
            
            document.getElementById('prediction-alert').innerText = text;
            document.getElementById('prediction-alert').style.display = 'block';
            
            // Toon het toetsenbord paneel en schud de knoppen
            document.getElementById('keyboard-panel').style.display = 'block';
            buildKeyboards();
        }}

        function closePanel() {{
            document.getElementById('keyboard-panel').style.display = 'none';
        }}

        // Specifieke invoerfuncties voor de twee aparte velden
        function addVal1(val) {{ document.getElementById('score1').value += val; }}
        function delVal1() {{ var v = document.getElementById('score1').value; document.getElementById('score1').value = v.substring(0, v.length - 1); }}
        
        function addVal2(val) {{ document.getElementById('score2').value += val; }}
        function delVal2() {{ var v = document.getElementById('score2').value; document.getElementById('score2').value = v.substring(0, v.length - 1); }}

        // Genereer de HTML voor de toetsenborden met geshuffelde nummers
        function buildKeyboards() {{
            // Schud nummers voor Team 1
            var nums1 = [0,1,2,3,4,5,6,7,8,9];
            nums1.sort(() => Math.random() - 0.5);
            
            // Schud nummers voor Team 2
            var nums2 = [0,1,2,3,4,5,6,7,8,9];
            nums2.sort(() => Math.random() - 0.5);

            var grid1 = document.getElementById('grid-t1');
            var grid2 = document.getElementById('grid-t2');
            
            // Bouw Toetsenbord 1
            var html1 = "";
            for(var i=0; i<9; i++) {{
                html1 += `<input type="button" value="${{nums1[i]}}" onclick="addVal1('${{nums1[i]}}')" style="height:38px; font-weight:bold; cursor:pointer; background:#fff; border:1px solid #ccc; border-radius:4px;">`;
            }}
            // Voeg de onderste rij toe (←, 0, en een lege opvulling)
            html1 += `<input type="button" value="←" onclick="delVal1()" style="height:38px; cursor:pointer; background:#d1d5db; border:1px solid #b6bbc2; border-radius:4px;">`;
            html1 += `<input type="button" value="${{nums1[9]}}" onclick="addVal1('${{nums1[9]}}')" style="height:38px; font-weight:bold; cursor:pointer; background:#fff; border:1px solid #ccc; border-radius:4px;">`;
            
            grid1.innerHTML = html1;

            // Bouw Toetsenbord 2
            var html2 = "";
            for(var i=0; i<9; i++) {{
                html2 += `<input type="button" value="${{nums2[i]}}" onclick="addVal2('${{nums2[i]}}')" style="height:38px; font-weight:bold; cursor:pointer; background:#fff; border:1px solid #ccc; border-radius:4px;">`;
            }}
            // Voeg de onderste rij toe (←, 0, en een lege opvulling)
            html2 += `<input type="button" value="←" onclick="delVal2()" style="height:38px; cursor:pointer; background:#d1d5db; border:1px solid #b6bbc2; border-radius:4px;">`;
            html2 += `<input type="button" value="${{nums2[9]}}" onclick="addVal2('${{nums2[9]}}')" style="height:38px; font-weight:bold; cursor:pointer; background:#fff; border:1px solid #ccc; border-radius:4px;">`;
            
            grid2.innerHTML = html2;
        }}
    </script>
    """

    # We geven de component voldoende hoogte (460px) mee zodat de openslaande toetsenborden goed passen.
    components.html(html_code, height=460)

if __name__ == "__main__":
    show_stand_uitprinten()
