import praw
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from textblob import TextBlob

# authenticate with reddit API
reddit = praw.Reddit(
    client_id="Xwt22mMj3YOP_iqOv8HOLw",
    client_secret="Q0TjRi8zi_FZl-5kqBm8VnbZpVWc9g",
    user_agent="mental_health_dashboard/0.1"
)

st.title("Mental Health Dashboard")

subreddit = st.text_input("Enter subreddit name", "depression")
if subreddit:
    st.write(f"Fetching posts from r/{subreddit}...")

    posts_data = []
    for post in reddit.subreddit(subreddit).hot(limit=30):
        text = post.title + " " + post.selftext
        polarity = TextBlob(text).sentiment.polarity
        sentiment = "positive" if polarity > 0 else "negative" if polarity < -0.2 else "neutral"
        risk_flag = any(word in text.lower() for word in ["suicide", "kill", "hurt", "pain", "sad", "depressed", "worthless"])

        posts_data.append({
            "Title": post.title,
            "Sentiment": sentiment,
            "High Risk": "Yes" if risk_flag else "No",
            "Polarity": polarity,
            "Comments": post.num_comments,
            "Score": post.score,
        })
    
    df = pd.DataFrame(posts_data)
    st.dataframe(df)

    st.write("High Risk Posts")
    st.dataframe(df[df["High Risk"] == "Yes"])

    
# fetch posts from reddit
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

# sentiment and risk classification with TextBlob
def classify_emotions(posts):
    results = []
    for post in posts:
        polarity = TextBlob(post).sentiment.polarity
        sentiment = "positive" if polarity > 0 else "negative" if polarity < -0.2 else "neutral"

        risk_flag = any(word in post.lower() for word in ["suicide", "kill", "hurt", "pain", "sad", "depressed", "worthless"])
        results.append({
            "sentiment": sentiment,
            "risk_flag": "Yes" if risk_flag else "No",
            "polarity": polarity
        })
    return results

# streamlit UI
def generate_dashboard():
    st.title("Mental Health Dashboard")
    subreddit_name = st.text_input("Enter subreddit name", "depression")
    post_count = st.slider("Number of posts", 10, 200, 50)

    if st.button("Analyze"):
        posts = fetch_posts(subreddit_name, post_count)
        emotions = classify_emotions(posts)

        df = pd.DataFrame({'Post': posts, 'Emotion': emotions})

        st.subheader("Emotion Distribution")
        st.bar_chart(df['sentiment'].value_counts())

        st.subheader("Risk Classification")
        st.bar_chart(df['risk_flag'].value_counts())

        st.subheader("Word Cloud of Posts")
        worldcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(posts))
        st.image(worldcloud.to_array(), use_column_width=True)

        st.subheader("High Risk Posts")
        high_risk_posts = [posts[i] for i in range(len(posts)) if emotions[i]['risk_flag'] == "Yes"]
        st.write("\n".join(high_risk_posts))