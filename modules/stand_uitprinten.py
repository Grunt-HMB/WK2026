import streamlit as st
import streamlit.components.v1 as components

def show_stand_uitprinten():
    st.title("🖨️ Stand uitprinten")

    team1 = "Mexico"
    team2 = "Zuid-Afrika"

    # De HTML, CSS en JS voor de interface
    html_code = f"""
    <div style="font-family:Arial; max-width:500px; margin:0 auto;">
        <div style="display:grid; grid-template-columns: 1fr 80px 80px 1fr; gap:10px; align-items:center; margin-bottom:20px;">
            <div style="text-align:right; font-size:20px; font-weight:700;">{team1}</div>
            
            <input id="score1" type="text" placeholder="0" readonly 
                onclick="showKeyboard('score1')"
                style="font-size:24px; text-align:center; padding:10px; border-radius:8px; border:2px solid #ccc; width:70px; cursor:pointer; background:#fff;">

            <input id="score2" type="text" placeholder="0" readonly 
                onclick="showKeyboard('score2')"
                style="font-size:24px; text-align:center; padding:10px; border-radius:8px; border:2px solid #ccc; width:70px; cursor:pointer; background:#fff;">

            <div style="text-align:left; font-size:20px; font-weight:700;">{team2}</div>
        </div>

        <div id="keyboard-wrapper" style="display:none; background:#f0f0f0; padding:15px; border-radius:12px; border:1px solid #ddd; width:220px; margin: 0 auto; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-weight:bold; font-size:14px;">Invoeren...</span>
                <button onclick="closeKeyboard()" style="background:#ff4b4b; color:white; border:none; border-radius:4px; padding:4px 8px; cursor:pointer;">Sluiten</button>
            </div>
            
            <div id="VirtualKey" style="display:grid; grid-template-columns: repeat(3, 1fr); gap:8px;">
                <input id="btn1" type="button" onclick="addVal(this);" style="width:100%; height:45px; font-size:18px; cursor:pointer;">
                <input id="btn2" type="button" onclick="addVal(this);" style="width:100%; height:45px; font-size:18px; cursor:pointer;">
                <input id="btn3" type="button" onclick="addVal(this);" style="width:100%; height:45px; font-size:18px; cursor:pointer;">
                <input id="btn4" type="button" onclick="addVal(this);" style="width:100%; height:45px; font-size:18px; cursor:pointer;">
                <input id="btn5" type="button" onclick="addVal(this);" style="width:100%; height:45px; font-size:18px; cursor:pointer;">
                <input id="btn6" type="button" onclick="addVal(this);" style="width:100%; height:45px; font-size:18px; cursor:pointer;">
                <input id="btn7" type="button" onclick="addVal(this);" style="width:100%; height:45px; font-size:18px; cursor:pointer;">
                <input id="btn8" type="button" onclick="addVal(this);" style="width:100%; height:45px; font-size:18px; cursor:pointer;">
                <input id="btn9" type="button" onclick="addVal(this);" style="width:100%; height:45px; font-size:18px; cursor:pointer;">
                <input id="btn0" type="button" onclick="addVal(this);" style="width:100%; height:45px; font-size:18px; cursor:pointer;">
                <input type="button" value="←" onclick="delVal();" style="width:100%; height:45px; font-size:18px; cursor:pointer; background:#ddd;">
                <input type="button" value="C" onclick="clearVal();" style="width:100%; height:45px; font-size:18px; cursor:pointer; background:#ddd;">
            </div>
        </div>
    </div>

    <script>
        var activeInputId = null;

        function showKeyboard(id) {
            activeInputId = id;
            document.getElementById('keyboard-wrapper').style.display = 'block';
            
            // Highlight het actieve veld
            document.getElementById('score1').style.borderColor = '#ccc';
            document.getElementById('score2').style.borderColor = '#ccc';
            document.getElementById(id).style.borderColor = '#4b9fff';
            
            shuffleKeys();
        }

        function closeKeyboard() {
            document.getElementById('keyboard-wrapper').style.display = 'none';
            document.getElementById('score1').style.borderColor = '#ccc';
            document.getElementById('score2').style.borderColor = '#ccc';
        }

        function addVal(btn) {
            if (activeInputId) {
                var input = document.getElementById(activeInputId);
                input.value = input.value + btn.value;
            }
        }

        function delVal() {
            if (activeInputId) {
                var input = document.getElementById(activeInputId);
                input.value = input.value.substring(0, input.value.length - 1);
            }
        }

        function clearVal() {
            if (activeInputId) {
                document.getElementById(activeInputId).value = "";
            }
        }

        function shuffleKeys() {
            var nums = [0,1,2,3,4,5,6,7,8,9];
            nums.sort(() => Math.random() - 0.5);
            for (var i = 0; i < 10; i++) {
                document.getElementById("btn" + i).value = nums[i];
            }
        }
        
        // Start met een shuffle
        shuffleKeys();
    </script>
    """

    # Verhoog de height zodat het toetsenbord past als het uitklapt
    components.html(html_code, height=450)

if __name__ == "__main__":
    show_stand_uitprinten()
