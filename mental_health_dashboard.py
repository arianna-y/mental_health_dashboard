import praw

# authenticate with reddit API
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="Q0TjRi8zi_FZl-5kqBm8VnbZpVWc9g",
    user_agent="mental_health_dashboard/0.1"
)

# fetch and analyze posts from reddit
def fetch_posts(subreddit_name="depression", limit=100):
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for post in subreddit.hot(limit=limit):
        post_data = {
            "title": post.title,
            "score": post.score,
            "num_comments": post.num_comments,
            "created_utc": post.created_utc,
            "url": post.url,
            "selftext": post.selftext
        }
        posts.append(post_data)
        
        if not post.stickied:
            posts.append(post.title + " " + post.selftext)
    
    return posts

# emotion classification with huggingface
from transformers import pipeline
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)

def classify_emotions(posts):
    results = []
    for post in posts:
        try:
            emotion = emotion_classifier(post[:512])[0][0]
            results.append({
                "title": post["title"],
                "emotion": emotion["label"],
                "score": emotion["score"]
            })
        except Exception as e:
            print(f"Error classifying post: {e}")
            results.append({
                "title": post["title"],
                "emotion": "unknown",
                "score": 0
            })

# streamlit UI
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np

def generate_dashboard():
    st.title("Mental Health Dashboard")
    subreddit_name = st.text_input("Enter subreddit name", "depression")
    post_count = st.slider("Number of posts", 10, 200, 50)

    if st.button("Analyze"):
        posts = fetch_posts(subreddit_name, post_count)
        emotions = classify_emotions(posts)
        df = pd.DataFrame({'Post': posts, 'Emotion': emotions})

        st.subheader("Emotion Distribution")
        st.bar_chart(df['Emotion'].value_counts())

        st.subheader("Word Cloud of Posts")
        worldcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(posts))
        st.image(worldcloud.to_array(), use_column_width=True)