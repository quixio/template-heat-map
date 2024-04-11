import os
from quixstreams import Application
from dotenv import load_dotenv

load_dotenv()

app = Application.Quix("group-by-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf.update(lambda row: print(row))

sdf = sdf.to_topic(output_topic, key=lambda key: key["relative_path"])

if __name__ == "__main__":
    app.run(sdf)