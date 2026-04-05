from prometheus_client import Summary, Counter


REQUEST_TIME = Summary("request_processing_seconds", "Time spent processing request")
TOTAL_REQUEST = Counter("predictions_total", "Total number of predictions made")
CLASS_ALLOCATION = Counter(
    "class_distribution",
    "How often model selects class",
    ["predicted_class"],
)
