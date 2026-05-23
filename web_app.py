import os
from PIL import Image
import streamlit as st

# Set up mobile-responsive page framing
st.set_page_config(page_title="AU Smart Vending System", page_icon="🪙", layout="centered")

# Custom CSS styling to emulate an industrial neon matrix screen and layout panels
st.markdown("""
    <style>
    .stApp { background-color: #121214; }
    .vfd-display {
        background-color: #0D1F1D;
        border: 2px solid #1F4E49;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
    }
    .chute-closed {
        background-color: #1A1A1A;
        border: 2px dashed #333333;
        border-radius: 6px;
        padding: 15px;
        text-align: center;
        color: #555555;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize persistent FSM registers inside the cloud session state
if 'Q1' not in st.session_state: st.session_state.Q1 = 0
if 'Q0' not in st.session_state: st.session_state.Q0 = 0
if 'msg' not in st.session_state: st.session_state.msg = "SYSTEM READY: INSERT COIN"
if 'dispense_triggered' not in st.session_state: st.session_state.dispense_triggered = False
if 'change_triggered' not in st.session_state: st.session_state.change_triggered = False

# --- UI Layout: Split Into 2 Columns (Just like your desktop app) ---
col_left, col_right = st.columns([1.1, 1])

# ====================================================================
# LEFT COLUMN: PHYSICAL VENDING MACHINE BODY
# ====================================================================
with col_left:
    st.subheader("📦 Machine Status")
    
    # Render your vending machine JPEG asset from the assets folder
    image_path = os.path.join("assets", "vending_machine.jpg")
    if os.path.exists(image_path):
        img = Image.open(image_path)
        st.image(img, use_container_width=True)
    else:
        st.warning("⚠️ Graphic Asset 'vending_machine.jpg' not found in assets folder.")

    # Interactive Delivery Chute Animation Panel
    st.caption("Product Delivery Slot")
    if st.session_state.dispense_triggered:
        st.success("🥤 ITEM DISPENSED! PUSH TO GRAB DRINK")
    else:
        st.markdown('<div class="chute-closed">🚪 PUSH FLAP CLOSED</div>', unsafe_allow_html=True)


# ====================================================================
# RIGHT COLUMN: INDUSTRIAL KEYPAD & CONTROL PANEL
# ====================================================================
with col_right:
    st.subheader("🕹️ Control Interface")

    # Calculate values directly from current state bits
    current_bal = 10 if st.session_state.Q1 == 1 else (5 if st.session_state.Q0 == 1 else 0)
    curr_state_num = f"S2 (10 Rs)" if st.session_state.Q1 == 1 else (f"S1 (5 Rs)" if st.session_state.Q0 == 1 else "S0 (0 Rs)")

    # 1. Neon Matrix Display Panel
    display_html = f"""
    <div class="vfd-display">
        <span style="color: #39FF14; font-size: 20px; font-weight: bold; letter-spacing: 2px;">
            {st.session_state.msg}
        </span><br/>
        <span style="color: #00FFFF; font-size: 16px;">
            CURRENT BAL: Rs. {current_bal} | STATE: {curr_state_num}
        </span>
    </div>
    """
    st.markdown(display_html, unsafe_allow_html=True)
    st.write("")

    # 2. Hardware Micro-switch Monitors (Emulating Proteus LEDs)
    st.caption("📟 Hardware Status Monitors")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        if st.session_state.dispense_triggered:
            st.info("🟢 DISPENSE ON")
        else:
            st.text("⚫ DISPENSE OFF")
    with m_col2:
        if st.session_state.change_triggered:
            st.warning("🟡 CHANGE ON")
        else:
            st.text("⚫ CHANGE OFF")
    
    st.write("---")

    # 3. Peripheral Entry Triggers (Coins)
    st.markdown("**🪙 COIN INPUT ACCEPTOR**")
    x, y, c = 0, 0, 0
    
    if st.button("🪙 Drop Rs. 5 Coin (Input X)", use_container_width=True): x = 1
    if st.button("🪙 Drop Rs. 10 Coin (Input Y)", use_container_width=True): y = 1
    
    st.write("")
    if st.button("🛑 COIN RETURN / CANCEL (Input C)", type="primary", use_container_width=True): c = 1

# ====================================================================
# BACKEND CORE ENGINE EVALUATION (Your Exact Logic Gates)
# ====================================================================
if x or y or c:
    # Capture local register states
    Q1, Q0 = st.session_state.Q1, st.session_state.Q0
    
    # Logical inverted values matching your derived homework tables
    Q1_bar = 1 if Q1 == 0 else 0
    Q0_bar = 1 if Q0 == 0 else 0
    X_bar = 1 if x == 0 else 0
    Y_bar = 1 if y == 0 else 0

    # Evaluate outputs using your custom Boolean expressions
    dispense_out = (Q1_bar & Q0 & y) | (Q1 & Q0_bar & x) | (Q1 & Q0_bar & y)
    change_out = (Q1 & Q0_bar & y) | c
    
    # Map next flip-flop input bits (D-FF attributes)
    next_bit_Q1 = (Q1_bar & Q0 & x) | (Q1_bar & Q0_bar & y) | (Q1 & Q0_bar & X_bar & Y_bar)
    next_bit_Q0 = (Q1_bar & Q0_bar & x) | (Q1_bar & Q0 & X_bar & Y_bar)

    # Force synchronous master clear if cancel button hit
    if c == 1:
        next_bit_Q1, next_bit_Q0 = 0, 0

    # Save calculated attributes directly back into cloud register storage
    st.session_state.Q1 = next_bit_Q1
    st.session_state.Q0 = next_bit_Q0
    st.session_state.dispense_triggered = bool(dispense_out)
    st.session_state.change_triggered = bool(change_out)

    # Contextual routing string overrides for display
    if c:
        st.session_state.log = 0
        st.session_state.msg = "⚠️ TRANSACTION VOID"
    elif dispense_out and change_out:
        st.session_state.msg = "🎉 VENDED + Rs. 5 CHG"
    elif dispense_out:
        st.session_state.msg = "🎉 VENDED: CHUTE OPEN"
    else:
        st.session_state.msg = "🪙 COIN ACCEPTED"
        
    st.rerun()