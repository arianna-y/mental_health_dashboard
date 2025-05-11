import praw
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob

# Reddit API Authentication
reddit = praw.Reddit(
    client_id="Xwt22mMj3YOP_iqOv8HOLw",
    client_secret="Q0TjRi8zi_FZl-5kqBm8VnbZpVWc9g",
    user_agent="mental_health_dashboard/0.1"
)

# Classify Sentiment and Risk
def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    sentiment = (
        "positive" if polarity > 0 else
        "negative" if polarity < -0.2 else
        "neutral"
    )
    risk_flag = "Yes" if any(word in text.lower() for word in ["suicide", "kill", "hurt", "pain", "sad", "depressed", "worthless"]) else "No"
    return sentiment, risk_flag, polarity

# Fetch posts
def fetch_posts(subreddit_name="depression", limit=50):
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for post in subreddit.hot(limit=limit):
        if not post.stickied:
            posts.append({
                "title": post.title,
                "selftext": post.selftext,
                "text": post.title + " " + post.selftext,
                "score": post.score,
                "num_comments": post.num_comments,
                "url": post.url
            })
    return posts

# Classify Sentiment & Risk
def classify_emotions(posts):
    for post in posts:
        polarity = TextBlob(post["text"]).sentiment.polarity
        post["polarity"] = polarity
        post["sentiment"] = (
            "positive" if polarity > 0 else
            "negative" if polarity < -0.2 else
            "neutral"
        )
        post["risk_flag"] = (
            "Yes" if any(word in post["text"].lower() for word in
                         ["suicide", "kill", "hurt", "pain", "sad", "depressed", "worthless"])
            else "No"
        )
    return posts

# Streamlit Dashboard
def generate_dashboard():
    st.title("Mental Health Reddit Dashboard")
    subreddit_name = st.text_input("Enter subreddit", "depression")
    post_count = st.slider("Number of posts", 10, 100, 30)

    if st.button("Analyze"):
        posts = fetch_posts(subreddit_name, post_count)
        posts = classify_emotions(posts)

        df = pd.DataFrame(posts)

        st.subheader("Posts Overview")
        st.dataframe(df[["title", "sentiment", "risk_flag", "polarity", "num_comments", "score"]])

        st.subheader("Sentiment Distribution")
        st.bar_chart(df["sentiment"].value_counts())

        st.subheader("Risk Classification")
        st.bar_chart(df["risk_flag"].value_counts())

        st.subheader("Word Cloud")
        all_text = " ".join(df["text"])
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_text)
        st.image(wordcloud.to_array(), use_column_width=True)

        st.subheader("High Risk Posts")
        high_risk = df[df["risk_flag"] == "Yes"]
        for idx, row in high_risk.iterrows():
            st.markdown(f"- [{row['title']}]({row['url']})")

generate_dashboard()