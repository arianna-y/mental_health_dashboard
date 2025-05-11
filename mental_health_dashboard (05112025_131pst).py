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

subreddit = st.text_input("Enter subreddit name", "depression", key="subreddit_input")
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
        if not post.stickied:
            post_data = {
                "title": post.title,
                "score": post.score,
                "num_comments": post.num_comments,
                "created_utc": post.created_utc,
                "url": post.url,
                "selftext": post.selftext
            }
            posts.append(post_data)
        
    return posts

# sentiment and risk classification with TextBlob
def classify_emotions(posts):
    results = []
    valid_posts = []

    for post in posts:
        print(post)

        sentiment = "unknown"
        risk_flag = "no"
        polarity = 0.0

        if isinstance(post, dict) and "selftext" in post and isinstance(post["selftext"], str):
            
            post["text"] = post["selftext"]
            polarity = TextBlob(post["text"]).sentiment.polarity
            sentiment = "positive" if polarity > 0 else "negative" if polarity < -0.2 else "neutral"

            risk_flag = "Yes" if any(word in post["text"].lower() for word in ["suicide", "kill", "hurt", "pain", "sad", "depressed", "worthless"]) else "No"
            
            results.append({
                "sentiment": sentiment,
                "risk_flag": risk_flag,
                "polarity": polarity
            })
            valid_posts.append(post)

        else:
            print(f"Invalid post data: {post}")
        
    
    print(f"Processed {len(valid_posts)} valid posts out of {len(posts)} total posts.")
    return results, valid_posts

# sample data for testing
posts = [
    {"title": "Regular check-in post, with essential information about our rules and resources", 
     "score": 33, 
     "num_comments": 46, 
     "created_utc": 1744611968.0, 
     "url": "https://www.reddit.com/r/depression/comments/1jys8x9/regular_checkin_post_with_essential_information/", 
     "selftext": "Welcome to /r/depression's check-in post - a place to take a moment and share what is going on and how you are doing. If you're having a tough time but prefer not to make your own post, or have an accomplishment you want to talk about (these aren't allowed standalone posts in the sub as they violate the 'role model' rule),  this is a place you can share."},
    
    {"title": "Feeling very down today", 
     "score": 10, 
     "num_comments": 2, 
     "created_utc": 1744613068.0, 
     "url": "https://www.reddit.com/r/depression/comments/1jys9x9/feeling_very_down_today/", 
     "selftext": "I feel hopeless and am struggling to see the point in anything. Life feels like it's just too much to handle."},
    
    {"title": "Just wanted to share something positive", 
     "score": 56, 
     "num_comments": 12, 
     "created_utc": 1744615068.0, 
     "url": "https://www.reddit.com/r/depression/comments/1jys0x9/just_wanted_to_share_something_positive/", 
     "selftext": "Today, I managed to take a walk and talk to a friend. It's not much, but it's a start, and I feel a little better."}
]

# classify the emotions and risk flags
emotions, valid_posts = classify_emotions(posts)

print(f"Length of posts: {len(valid_posts)}")
print(f"Length of emotions: {len(emotions)}")
print("Posts:")
print(valid_posts)
print("Emotions:")
print(emotions)

# ensure both lists are of the same length before creating DataFrame
if len(valid_posts) == len(emotions):
    # Create the DataFrame
    df = pd.DataFrame({'Post': valid_posts, 'Emotion': emotions})
    print(df)
else:
    print("Error: Length mismatch between posts and emotions")

# streamlit UI
def generate_dashboard():
    st.title("Mental Health Dashboard")
    subreddit_name = st.text_input("Enter subreddit name", "depression")
    post_count = st.slider("Number of posts", 10, 200, 50)

    if "analyze" not in st.session_state:
        st.session_state.analyze = False

    if st.button("Analyze"):
        st.session_state.analyze = True

    if st.session_state.analyze:
        posts_data = []
        all_text = ""

    # if st.button("Analyze"):
    #     posts_data = []
    #     all_text = ""

        for post in reddit.subreddit(subreddit_name).hot(limit=post_count):
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
            all_text += text + " "

        df = pd.DataFrame(posts_data)

        st.subheader("Posts Sentiment Analysis")
        st.dataframe(df)

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
    
generate_dashboard()