import os
from quixstreams import Application, State
from datetime import timedelta

app = Application.Quix("transformation-v1", auto_offset_reset="latest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf.apply(lambda row: row["CPULoad"]) \
    .tumbling_window(timedelta(seconds=10)).mean().final()

sdf["window_duration_s"] = (sdf["end"] - sdf["start"]) / 1000

def is_alert(row: dict, state: State):
    
    is_alert_sent_state = state.get("is_alert_sent", False)
    
    if row["value"] > 20:
        if not is_alert_sent_state:
            state.set("is_alert_sent", True)
            return True        
        else:
            return False
    else:
        state.set("is_alert_sent", False)
        return False
        

sdf = sdf.filter(is_alert, stateful=True)

# Produce message payload with alert.
sdf = sdf.apply(lambda row: {
    "alert": {
        "timestamp": row["end"],
        "title": "CPU overload",
        "message": f"CPU {row["value"]} for duration of {row["window_duration_s"]} seconds."
    }
})

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)