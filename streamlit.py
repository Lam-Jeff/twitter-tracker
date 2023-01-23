import streamlit as st
import matplotlib.pyplot as plt
import twitter_api as api
import altair as alt
import pandas as pd

def display_tweet(tweet: dict, tweets_details: dict) -> None:
        """
        Display a tweet with details.

        tweet -- the tweet to display
        tweet_details -- details linked to the tweet
        """
        username = [item['username'] for item in tweets_details if item['id'] == tweet.id][0]
        likes = [item['likes'] for item in tweets_details if item['id'] == tweet.id][0]
        parsed_tweet = {
            "author": username,
            "created_at": tweet.created_at,
            "url": f'https://twitter.com/{username}/status/{str(tweet.id)}',
            "text": tweet.text,
            "likes": likes
        }
        for title, value in parsed_tweet.items():
            title_column, value_column = st.columns([1, 4])
            title_column.write(f"**{title}:**")
            value_column.write(value)
        "---"

with st.form("my_form"):
    st.markdown("<h1 style='text-align: center; color: grey; pointer-events: none;'>Twitter Sentiment Analysis</h1>", unsafe_allow_html=True)

    input_col1, input_col2 = st.columns (2)
    retweet_column, replies_column, empty_column = st.columns([2,2,3])
    column1, column2, column3 = st.columns([3,1,3])
    

    with input_col1:
        search_word = st.text_input('Search term', '')
    with input_col2:
        number_tweets = st.slider('Tweet limit', 0, 100, 10)

    with retweet_column:
        retweets = st.checkbox('Exclude retweets')
    with replies_column:
        replies = st.checkbox('Exclude replies')
    with column2:
        submitted = st.form_submit_button("Analyze")

    
    if submitted:
        tweets, tweets_details, sentiments, words_count = api.getTweets (search_word, number_tweets, retweets, replies)

polarity, subjectivity = st.columns(2)

if 'sentiments' in locals():
    with polarity:
        st.markdown(f"<div style='text-align: center;'><h2 color: grey; pointer-events: none;'>Polarity</h2><big style='color: grey;line-height=1'>{'%.2f' % sentiments['polarity']}</big></div>", unsafe_allow_html=True)
    with subjectivity:
        st.markdown(f"<div style='text-align: center;'><h2 color: grey; pointer-events: none;'>Subjectivity</h2><big style='color: grey;line-height=1'>{'%.2f' % sentiments['subjectivity']}</big></div>", unsafe_allow_html=True)

    labels = ['Negative','Neutral','Positive']
    colors = ['Red', 'Grey', 'Green']
    size_of_groups=[sentiments['negative'], sentiments['neutral'], sentiments['positive']]
    total = sum(size_of_groups)
    pie = plt.pie(size_of_groups, autopct=lambda p: '{:.0f}%'.format(p) if p else '', colors=colors)
    p = plt.gcf()
    p.patch.set_alpha(0.0)
    plt.legend(pie[0], labels, loc="lower right", frameon=False, bbox_transform=p.transFigure, bbox_to_anchor=(1,0),labelcolor='white', title='')
    st.pyplot(p)
    hide_plot_fs = '''
        <style>
        button[title="View fullscreen"]{
            visibility: hidden;}
        </style> '''
    st.markdown(hide_plot_fs, unsafe_allow_html=True)

if 'words_count' in locals():
    source = pd.DataFrame({
    'words': list(words_count.keys())[:20],
    'count': list(words_count.values())[:20]
})
    bars = st.altair_chart(
    alt.Chart(source)
    .mark_bar(tooltip=True)
    .encode(
        x=alt.X("count:Q", axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("words:N", sort="-x")
    ),
    use_container_width=True,
)
if 'tweets' in locals():
    with st.expander("Display tweets"):
        for tweet in tweets:
            display_tweet(tweet, tweets_details)
