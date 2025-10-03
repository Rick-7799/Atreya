import streamlit as st
import requests
import os
from streamlit_tags import st_tags

st.set_page_config(page_title="Atreya — Wellness Demo", page_icon="🌿", layout="centered")
st.title("🌿 Atreya — Personalized Wellness (Demo)")
st.caption("Educational demo using LangChain + Neo4j + FastAPI. **Not medical advice.**")

api_base = os.getenv("ATREYA_API_BASE", "http://127.0.0.1:8000")

with st.sidebar:
    st.header("Connection")
    api_base = st.text_input("API base URL", api_base, help="FastAPI server base, e.g., http://127.0.0.1:8000")
    if st.button("Check API"):
        try:
            r = requests.get(f"{api_base}/health", timeout=5)
            st.success(r.json())
        except Exception as e:
            st.error(str(e))

st.subheader("Tell us about you")
age = st.number_input("Age", min_value=0, max_value=120, value=25)
gender = st.selectbox("Gender", ["male","female","other"], index=0)

symptoms = st_tags(
    label="Symptoms",
    text="Press Enter to add",
    value=[],
    suggestions=["cough","fever","anxiety","fatigue","bloating","gas","nausea","joint ache"]
)

lifestyle = st_tags(
    label="Lifestyle",
    text="Press Enter to add",
    value=[],
    suggestions=["sedentary","smoker","alcohol","poor sleep","high stress","balanced diet"]
)

conditions_history = st_tags(
    label="Known conditions",
    text="Press Enter to add",
    value=[],
    suggestions=["Diabetes","Hypertension","Asthma"]
)

if st.button("🧪 Get Recommendations"):
    try:
        payload = {
            "age": int(age),
            "gender": gender,
            "symptoms": symptoms,
            "lifestyle": lifestyle,
            "conditions_history": conditions_history
        }
        r = requests.post(f"{api_base}/recommendations", json=payload, timeout=20)
        r.raise_for_status()
        data = r.json()
        st.success("Suggestions ready! (Not medical advice)")
        for s in data.get("suggestions", []):
            with st.container(border=True):
                st.markdown(f"**Herb:** {s['name']}")
                st.write(f"**Why:** {s['why']}")
                if s.get("how_to_use"):
                    st.write(f"**How to use:** {s['how_to_use']}")
                if s.get("avoid_with"):
                    st.write(f"**Avoid with:** {', '.join(s['avoid_with'])}")
        with st.expander("General Tips"):
            for t in data.get("tips", []):
                st.write("• " + t)
        st.info(data.get("disclaimer","Not medical advice"))
        if data.get("debug"):
            with st.expander("Debug (LLM prompt/result)"):
                st.code(data["debug"].get("llm",""), language="markdown")
    except Exception as e:
        st.error(str(e))

st.divider()
st.subheader("Quick herb search")
q = st.text_input("Find a herb")
if st.button("Search herb"):
    try:
        r = requests.get(f"{api_base}/herbs/search", params={"q": q}, timeout=10)
        r.raise_for_status()
        data = r.json()
        for h in data.get("herbs", []):
            st.write(f"- **{h['name']}** — properties: {', '.join(h.get('properties', []))}")
    except Exception as e:
        st.error(str(e))

st.divider()
st.subheader("💬 Chat with Atreya (no API key needed)")

if "chat" not in st.session_state:
    st.session_state.chat = [
        {"role": "assistant", "content": "Hi! Tell me your symptoms or lifestyle, and I’ll suggest gentle, Ayurvedic-oriented options. (Not medical advice.)"}
    ]

for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_msg = st.chat_input("Type your message...")
if user_msg:
    st.session_state.chat.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    try:
        r = requests.post(f"{api_base}/chat", json={"message": user_msg}, timeout=30)
        r.raise_for_status()
        data = r.json()
        reply = data.get("reply", "Sorry, I couldn't compose a reply.")
    except Exception as e:
        reply = f"Oops, something went wrong: {e}"

    st.session_state.chat.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

st.caption("© 2025 Atreya demo • Built for learning • Stay safe 🌱")
