import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from langgraph.graph import StateGraph, END  # Not used, consider removing if unused
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# --- Setup Streamlit UI ---
st.set_page_config(page_title="Conscious Cart AI", layout="centered")
st.title("Conscious Cart AI Agent 🛒")

# --- API Key Input ---
if "GOOGLE_API_KEY" not in os.environ:
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key 

# --- Initialize LLM if key is available ---
if "GOOGLE_API_KEY" in os.environ:
    try:
        llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest", temperature=0)
    except Exception as e:
        st.error(f"Error initializing Gemini model: {e}")
        st.stop()

    product_input = st.text_input("Enter a Product NAME or URL:")

    # --- Define Function: Scrape Product Details ---
    def scrape_product_details(state):
        url = state["user_input"]
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.title.string.strip() if soup.title else "Unknown Product"
            state["product_details"] = title
        except Exception as e:
            state["product_details"] = f"Error scraping: {e}"
        return state

    # --- Define Function: Generate Details from Name ---
    def generate_details_from_name(state):
        name = state["user_input"]
        try:
            response = llm.invoke([HumanMessage(content=f"Describe the product: {name}")])
            state["product_details"] = response.content
        except Exception as e:
            state["product_details"] = f"Error generating details: {e}"
        return state

    # --- Define Function: Analyze Environmental Impact ---
    def analyze_environmental_impact(state):
        details = state.get("product_details", "")
        try:
            response = llm.invoke([HumanMessage(content=f"Analyze the environmental impact of this product: {details}")])
            state["environmental_impact"] = response.content
        except Exception as e:
            state["environmental_impact"] = f"Error analyzing impact: {e}"
        return state

    # --- Define Function: Generate Recommendation ---
    def generate_recommendation(state):
        impact = state.get("environmental_impact", "")
        try:
            response = llm.invoke([HumanMessage(content=f"Based on this environmental impact, what would you recommend?: {impact}")])
            state["recommendation"] = response.content
        except Exception as e:
            state["recommendation"] = f"Error generating recommendation: {e}"
        return state

    # --- Analyze Button ---
    if st.button("Analyze"):
        if not product_input:
            st.warning("Please enter a product URL or name.")
        else:
            state = {"user_input": product_input}

            if product_input.lower().startswith("http"):
                state = scrape_product_details(state)
            else:
                state = generate_details_from_name(state)

            state = analyze_environmental_impact(state)
            state = generate_recommendation(state)

            st.markdown("### 📝 Final Recommendation")
            st.markdown(state.get("recommendation", "No recommendation could be generated."))

else:
    st.info("Please enter your Gemini API key above to start.")

