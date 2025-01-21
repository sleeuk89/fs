import streamlit as st
import requests
from bs4 import BeautifulSoup
import spacy
from openai import ChatCompletion

# Streamlit App
st.title("Featured Snippet Opportunity Finder")
st.markdown("Identify and optimise content for Featured Snippets on Google.")

# OpenAI API Key Input
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

# Content and Keywords Input
content = st.text_area("Paste your content here:")
keywords = st.text_input("Enter target keywords (comma-separated):")

# Helper Functions
def analyse_content(content, keywords):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(content)
    keywords = [kw.strip().lower() for kw in keywords.split(",")]
    questions = []
    for sentence in doc.sents:
        if sentence.text.strip().endswith("?") or any(keyword in sentence.text.lower() for keyword in keywords):
            questions.append(sentence.text.strip())
    return questions

def get_serp_data(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    featured_snippet = None
    try:
        snippet = soup.find("div", class_="BNeawe").text
        featured_snippet = snippet
    except AttributeError:
        pass
    
    return featured_snippet

def generate_optimised_content(question, api_key):
    openai.api_key = api_key
    prompt = f"Write an SEO-optimised answer for the following question to win a Featured Snippet:\n\n{question}"
    response = ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# Streamlit Workflow
if st.button("Find Opportunities"):
    if not openai_api_key or not content or not keywords:
        st.error("Please provide all inputs: OpenAI API key, content, and keywords.")
    else:
        st.info("Analysing content and fetching Featured Snippet data...")
        questions = analyse_content(content, keywords)
        opportunities = {}
        
        for question in questions:
            st.write(f"**Analysing question:** {question}")
            snippet = get_serp_data(question)
            if snippet:
                st.success(f"Existing Featured Snippet found: {snippet}")
            else:
                st.warning("No Featured Snippet found. Generating optimised content...")
                optimised_content = generate_optimised_content(question, openai_api_key)
                opportunities[question] = optimised_content
                st.write(f"**Optimised Content:**\n{optimised_content}")
        
        if opportunities:
            st.markdown("### Featured Snippet Opportunities:")
            for question, content in opportunities.items():
                st.write(f"**Question:** {question}\n**Optimised Content:** {content}\n")
