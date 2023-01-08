import tweepy
import sys
from config import api_key, api_key_secret, access_token, access_token_secret, bearer_token

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

print(tweets)