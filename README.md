# Mental Health Dashboard

This project provides a dashboard for analyzing Reddit posts related to mental health. Using sentiment analysis and emotion classification, the app helps identify the general emotional tone of posts, highlight high-risk posts, and visualize the emotional distribution of the community.

## Features
- Fetches posts from a subreddit (default: "depression")
- Analyzes sentiment (positive, negative, or neutral) of posts
- Flags high-risk posts based on keywords related to mental health crises
- Displays:
  - A dataframe of posts with sentiment analysis results
  - High-risk posts identified by specific keywords
  - A bar chart showing the distribution of emotions in the posts
  - A word cloud visualizing the most common terms in the posts

## Requirements
- Streamlit
- Praw (Python Reddit API Wrapper)
- TextBlob
- Pandas
- WordCloud

## Installation

1. Clone the repository:
   ```git clone https://github.com/your-username/mental-health-dashboard.git```
2. Install required packages:
   ```pip install -r requirements.txt```
3. Run the Streamlit app:
   ```streamlit run mental_health_dashboard.py```

## How to Use
- Open the app and enter the name of a subreddit to analyze (default is "depression")
- Use the slider to select the number of posts you want to fetch (default is 50)
- Click the "Analyze" button to fetch posts and analyze them for sentiment, emotional content, and risk levels
- View the results in a dataframe, and explore the emotional distribution and word cloud

## Acknowledgements
- [PRAW](https://praw.readthedocs.io/en/latest/) for fetching Reddit posts.
- [TextBlob](https://textblob.readthedocs.io/en/dev/) for sentiment analysis.
- [WordCloud](https://github.com/amueller/word_cloud) for generating word clouds.
