import streamlit as st

st.title("test secrets setup")

try:
    api_key=st.secrets["OPENAI_API_KEY"]
    st.success("api key downloaded succesfully")
    st.write(f"key starts with: {api_key[:10]}...")

except Exception as e:
    st.error(f"error loading api key:{e}")