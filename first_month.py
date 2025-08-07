
import streamlit as st

st.title("📅 Month 1 – Business Simulation")

# Setup
starting_cash = st.selectbox("Select Starting Capital:", ["£0", "£3,000", "£5,000", "£10,000", "£20,000", "£30,000+"])
business_model = st.radio("Choose Your Business Model:", ["Sole Trader – Service-Based", "Limited Company – Product-Based"])

st.markdown(f"### You selected:")
st.write(f"**Capital:** {starting_cash}")
st.write(f"**Model:** {business_model}")

# Example choices
st.markdown("#### 🛠️ First Investment Decisions")
investment = st.radio("Where would you like to invest first?", [
    "Build a website (£500)",
    "Buy equipment (£1,000)",
    "Hire a coach (£750)",
    "Do nothing this month"
])

if st.button("Submit Decision"):
    st.success(f"You chose to: {investment}")
    st.info("Strategic Tip: Invest in what brings clients fastest, not just what looks good.")
