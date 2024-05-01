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

def stars(row):

    def get_stars(owner, repo):
        url = f"https://api.github.com/repos{row['href']}"
        response = requests.get(url)
        data = response.json()
        return data['stargazers_count']

    stars = get_stars('dpkp', 'kafka-python')
    print(stars)

sdf = sdf.update(stars)

# sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)