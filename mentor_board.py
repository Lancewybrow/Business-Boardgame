
import streamlit as st

# Sample mentor data (to be expanded)
mentors = {
    "The Strategic Thinker": {
        "icon": "🧠",
        "role": "Visionary strategist and growth architect",
        "philosophies": [
            "Use other people’s resources to grow.",
            "Ethical preeminence: be the best and be seen as the best.",
            "Focus on 3 ways to grow a business."
        ],
        "tips": [
            "Look for a joint venture instead of spending marketing budget.",
            "Add a premium-priced offer for the top 10% of customers.",
            "You don’t have to create – you can collaborate."
        ]
    }
}

st.title("📘 Mentor Board")

# Display each mentor
for name, details in mentors.items():
    with st.expander(f"{details['icon']} {name}"):
        st.markdown(f"**Role:** {details['role']}")
        st.markdown("**Key Philosophies:**")
        for item in details["philosophies"]:
            st.markdown(f"- {item}")
        st.markdown("**Tips Received:**")
        for tip in details["tips"]:
            st.markdown(f"✅ {tip}")
        if st.button(f"Read More from {name}", key=name):
            st.info("More content coming soon...")
