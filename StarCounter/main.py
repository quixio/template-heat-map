import os
import requests
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application.Quix("transformation-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

# put transformation logic here
# see docs for what you can do
# https://quix.io/docs/get-started/quixtour/process-threshold.html

token = os.environ['gh_token']
def stars(row):
    
    try:

        headers = {'Authorization': f'token {token}'}

        # Check rate limit
        response = requests.get('https://api.github.com/rate_limit', headers=headers)
        remaining = response.json()['rate']['remaining']
        if remaining < 10:  # If less than 10 requests remaining, sleep for a while
            print("Rate limit approaching, sleeping for a minute...")
            time.sleep(60)  # Sleep for 60 seconds       
        if remaining < 1:  # If less than 10 requests remaining, sleep for a while
            print("Rate limit approaching, sleeping for an hour...")
            time.sleep(60*60)  # Sleep for 60 seconds   


        url = f"https://api.github.com/repos{row['href']}"
        
        response = requests.get(url, headers=headers)
        data = response.json()
        stars = data['stargazers_count']
        print(f"{row['href']} has {stars}")
    except Exception as e:
        print(f'Error: {e}')

sdf = sdf.update(stars)

# sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)