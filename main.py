import tweepy
import sys
import requests
import pandas as pd
import threading
from config import api_key, api_key_secret, access_token, access_token_secret, bearer_token, hf_token


#twitter api setup
client = tweepy.Client(bearer_token, 
						api_key, 
						api_key_secret, 
						access_token, 
						access_token_secret, 
						wait_on_rate_limit=True)


query = sys.argv[1] + " -is:retweet"
tweets_per_page = int(sys.argv[2]) #must be between 10 and 100
tweet_limit = int(sys.argv[3])



tweets = [tweet.text for tweet in tweepy.Paginator(client.search_recent_tweets, 
													query, 
													max_results=tweets_per_page).flatten(limit=tweet_limit)]


# with open("tweets.txt", 'w') as f:
# 	f.write("~~split~~".join(tweets))

# tweets = []

# with open("tweets.txt", 'r') as f:
# 	tweets = f.read().split("~~split~~")


#inference api setup
model = "cardiffnlp/twitter-roberta-base-sentiment-latest"
hf_url = "https://api-inference.huggingface.co/models/" + model
headers = {"Authorization": f"Bearer {hf_token}"}


#sentiment analysis
tweets_analysis = []
threads = []

def analysis(data):
	#feed through api
	payload = dict(inputs=data, options=dict(wait_for_model=True))
	response = requests.post(hf_url, headers=headers, json=payload)

	sentiment_result = response.json()

	#process response
	try:
		sentiment_result = sentiment_result[0]
		top_sentiment = max(sentiment_result, key=lambda x: x['score']) # Get the sentiment with the higher score
		tweets_analysis.append({'tweet': tweet, 'sentiment': top_sentiment['label']})

	except Exception as e:
		print(e)
		print(sentiment_result)


for tweet in tweets:
	t = threading.Thread(target=analysis, args=(tweet,), daemon=True)
	threads.append(t)

for thread in threads:
	thread.start()

for thread in threads:
	thread.join()
	

# Load the data in a dataframe
pd.set_option('max_colwidth', None)
pd.set_option('display.width', 3000)
df = pd.DataFrame(tweets_analysis)
 
sentiment_counts = df.groupby(['sentiment']).size()
print(sentiment_counts)