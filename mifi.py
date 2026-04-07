import streamlit as st
import pandas as pd

# 1. Connect to your Neon Database
conn = st.connection("neon", type="sql")

st.set_page_config(page_title="MiFi Pro Manager", layout="centered")

# --- USER INTERFACE ---
st.title("📶 MiFi Pro Internet Portal")
st.markdown("""
### How to get a code:
1. Send money to **0763212490**.
2. Enter your phone number below.
3. Wait for the Admin to verify and release your code!
""")

# User Section
with st.expander("🙋 Purchase a Voucher", expanded=True):
    phone = st.text_input("Enter your Mobile Money Number")
    amount_choice = st.selectbox("Amount Paid", [500, 1000, 2000])

    if st.button("Request Voucher"):
        if phone:
            st.success(
                "Request sent! Please stay on this page. Once the Admin verifies your payment, your code will appear below.")
        else:
            st.warning("Please enter your phone number.")

# --- ADMIN SECTION (Hidden in an expander for you) ---
st.divider()
with st.expander("🔒 Admin Panel (For 0763212490 Only)"):
    st.write("Check your phone for the SMS. If the money arrived, click 'Release'.")

    # Show available (unsold) vouchers
    inventory = conn.query("SELECT * FROM vouchers WHERE is_sold = False")
    st.write("Current Stock:", inventory)

    if not inventory.empty:
        target_id = st.number_input("Enter ID to release", step=1, min_value=1)
        confirm_phone = st.text_input("Confirm Buyer Phone")

        if st.button("✅ Verify Payment & Release Code"):
            with conn.session as s:
                s.execute(
                    "UPDATE vouchers SET is_sold = True, buyer_phone = :p WHERE id = :id",
                    {"p": confirm_phone, "id": target_id}
                )
                s.commit()
            st.success("Voucher Released!")
            st.rerun()

# --- REVEAL SECTION ---
# This part automatically shows the code to the user once you "Release" it
if phone:
    # Look for a sold voucher assigned to this phone number
    check_sold = conn.query(
        f"SELECT code FROM vouchers WHERE buyer_phone = '{phone}' AND is_sold = True ORDER BY id DESC LIMIT 1"
    )

    if not check_sold.empty:
        final_code = check_sold.iloc[0]['code']
        st.balloons()
        st.markdown(f"""
        <div style="background-color:#d4edda; padding:20px; border-radius:10px; text-align:center;">
            <h2 style="color:#155724;">Your WiFi Code:</h2>
            <h1 style="font-size:50px;">{final_code}</h1>
        </div>
        """, unsafe_allow_html=True)
