import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from googlesearch import search
import spacy
from collections import Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer

class SEOAnalyzer:
    def __init__(self):
        # Download required NLTK data
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        
        # Load spaCy model
        self.nlp = spacy.load('en_core_web_sm')
        
        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("SEO Content Analyzer")
        self.root.geometry("1200x800")
        
        self.create_gui()
    
    def create_gui(self):
        # Left panel - Content Editor
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Editor label
        ttk.Label(left_frame, text="Content Editor", font=('Arial', 14, 'bold')).pack()
        
        # Text editor
        self.content_editor = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, height=20)
        self.content_editor.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Analyze button
        ttk.Button(left_frame, text="Analyze Content", command=self.analyze_content).pack(pady=10)
        
        # Right panel - Results
        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # SEO Score
        score_frame = ttk.LabelFrame(right_frame, text="Content Score")
        score_frame.pack(fill=tk.X, pady=10)
        self.score_label = ttk.Label(score_frame, text="95", font=('Arial', 24, 'bold'))
        self.score_label.pack()
        
        # Keyword suggestions
        suggestions_frame = ttk.LabelFrame(right_frame, text="Keyword Suggestions")
        suggestions_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.suggestions_text = scrolledtext.ScrolledText(suggestions_frame, wrap=tk.WORD, height=15)
        self.suggestions_text.pack(fill=tk.BOTH, expand=True)
    
    def analyze_content(self):
        content = self.content_editor.get("1.0", tk.END).strip()
        if not content:
            return
        
        # Analyze the content
        score, suggestions = self.perform_seo_analysis(content)
        
        # Update the score
        self.score_label.config(text=f"{score}")
        
        # Update suggestions
        self.suggestions_text.delete("1.0", tk.END)
        self.suggestions_text.insert("1.0", suggestions)
    
    def perform_seo_analysis(self, content):
        try:
            # Extract main keywords from content
            doc = self.nlp(content)
            main_keywords = [token.text.lower() for token in doc if token.pos_ in ['NOUN', 'PROPN']]
            
            # Get Google search results
            query = " ".join(main_keywords[:3])  # Use top 3 keywords for search
            search_results = list(search(query, num_results=10))
            
            # Analyze competitor content
            competitor_keywords = self.analyze_competitor_content(search_results)
            
            # Calculate content score
            score = self.calculate_content_score(content, competitor_keywords)
            
            # Generate suggestions
            suggestions = self.generate_suggestions(content, competitor_keywords)
            
            return score, suggestions
            
        except Exception as e:
            return 0, f"Error during analysis: {str(e)}"
    
    def analyze_competitor_content(self, urls):
        all_text = []
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract text content
                text = ' '.join([p.text for p in soup.find_all('p')])
                all_text.append(text)
            except:
                continue
        
        # Use TF-IDF to find important keywords
        vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(all_text)
        
        feature_names = vectorizer.get_feature_names_out()
        return feature_names
    
    def calculate_content_score(self, content, competitor_keywords):
        # Basic scoring based on various factors
        score = 100
        
        # Check content length
        if len(content.split()) < 300:
            score -= 20
        
        # Check keyword presence
        content_words = set(word_tokenize(content.lower()))
        keyword_matches = content_words.intersection(set(competitor_keywords))
        keyword_score = (len(keyword_matches) / len(competitor_keywords)) * 30
        score += keyword_score - 30  # Normalize
        
        # Ensure score stays within bounds
        return max(0, min(100, int(score)))
    
    def generate_suggestions(self, content, competitor_keywords):
        suggestions = "Recommended Keywords to Add:\n\n"
        
        # Find missing important keywords
        content_words = set(word_tokenize(content.lower()))
        missing_keywords = set(competitor_keywords) - content_words
        
        for keyword in missing_keywords:
            suggestions += f"• {keyword}\n"
        
        return suggestions
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SEOAnalyzer()
    app.run()
