import streamlit as st
import time

# --- DATABASE CONNECTION ---
# In Streamlit Cloud, you'll put your Neon Connection String in "Secrets"
conn = st.connection("neon", type="sql")

# --- SIMULATED PAYMENT CHECKER ---


def check_payment_status(phone, expected_amount):
    """
    Since we don't have a real API yet, this simulates 
    checking your 0763212490 line for a transaction.
    """
    st.write(f"🔍 Searching for payment from {phone}...")
    time.sleep(3)  # Simulates network delay
    return True  # Change to False to test 'Payment Not Found'


# --- THE USER INTERFACE ---
st.set_page_config(page_title="Mifi Pro Vouchers", page_icon="📶")

st.title("📶 MiFi Pro Internet")
st.info("Step 1: Send money to **0763212490**\n\nStep 2: Enter your details below to get your code.")

with st.form("purchase_form"):
    user_phone = st.text_input("Your Phone Number", placeholder="07XXXXXXXX")
    amount = st.selectbox("Amount Paid", [500, 1000, 2000, 5000])
    submit = st.form_submit_button("Claim Voucher")

if submit:
    if not user_phone:
        st.error("Please enter the phone number you used to pay.")
    else:
        # 1. Verify Payment
        if check_payment_status(user_phone, amount):

            # 2. Find an available voucher in Neon
            query = f"SELECT id, voucher_code FROM mifi_vouchers WHERE is_sold = False AND amount_ugx = {amount} LIMIT 1;"
            result = conn.query(query)

            if not result.empty:
                v_id = result.iloc[0]['id']
                v_code = result.iloc[0]['voucher_code']

                # 3. Mark it as sold in the database
                with conn.session as s:
                    s.execute(
                        "UPDATE mifi_vouchers SET is_sold = True, customer_phone = :phone WHERE id = :id",
                        {"phone": user_phone, "id": int(v_id)}
                    )
                    s.commit()

                st.success(
                    f"✅ Payment Verified! Your WiFi Code is: **{v_code}**")
                st.balloons()
            else:
                st.error(
                    "Sorry! We are out of vouchers for that amount. Please contact support.")
        else:
            st.error("We couldn't find a payment for that amount from your number.")
