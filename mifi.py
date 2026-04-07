import streamlit as st

# Add this to make the page refresh itself every 30 seconds
st.empty()
# Advanced, but helps with refreshes
st.runtime.scriptrunner.add_script_run_ctx()

# 1. Connect to your Neon Database
conn = st.connection("neon", type="sql", autocommit=True)

st.set_page_config(page_title="MiFi Pro Manager", layout="centered")

st.title("📶 MiFi Pro Internet Portal")

# --- STEP 1: CHECK INVENTORY FIRST ---
# This checks if we actually have codes before the user even tries to pay
inventory_check = conn.query(
    f"SELECT COUNT(*) as count FROM vouchers WHERE is_sold = False")
stock_count = inventory_check.iloc[0]['count']

if stock_count == 0:
    st.error(
        "⚠️ WE ARE CURRENTLY OUT OF STOCK. Please do not send money until this message disappears.")
else:
    st.success(f"✅ Vouchers available! Current stock: {stock_count} codes.")

# --- STEP 2: USER REQUEST SECTION ---
with st.expander("🙋 Request a Voucher", expanded=True):
    phone = st.text_input("Enter your Mobile Money Number (e.g., 07XXXXXXXX)")
    amount_choice = st.selectbox("Amount Paid", [500, 1000, 2000])

    if st.button("I Have Paid - Request Code"):
        if phone:
            # FEEDBACK: This tells the user exactly what is happening
            st.info(
                f"🔔 Request Received! Admin is checking payment for {phone}. Please wait on this page...")
            st.toast("Request sent to Admin!", icon="📩")
        else:
            st.warning("Please enter your phone number to proceed.")

# --- STEP 3: REVEAL SECTION (AUTOMATIC REFRESH) ---
if phone:
    # Check if a voucher has been assigned to this phone number
    check_sold = conn.query(
        f"SELECT code FROM vouchers WHERE buyer_phone = '{phone}' AND is_sold = True ORDER BY id DESC LIMIT 1"
    )

    if not check_sold.empty:
        final_code = check_sold.iloc[0]['code']
        st.balloons()
        st.success("🎉 Payment Verified! Your code is below.")
        st.code(final_code, language="text")  # Makes it easy to copy
    else:
        # This keeps the user informed while they wait
        st.warning(
            "⏳ Waiting for Admin to verify your payment. This usually takes 1-2 minutes.")

# --- ADMIN PANEL ---
st.divider()
with st.expander("🔒 Admin Panel (Check for Requests)"):
    # See who is currently waiting (based on the phone number entered above)
    st.write("### Recent Activity")
    # In a simple app, we can just look at the 'phone' variable if it's entered
    if phone:
        st.write(
            f"Customer {phone} is waiting for a {amount_choice} UGX voucher.")
