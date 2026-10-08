from prometheus_client import Counter, Histogram


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

CACHE_HITS_TOTAL = Counter(
    "cache_hits_total",
    "Total number of cache hits",
    ["key_type"],
)

CACHE_MISSES_TOTAL = Counter(
    "cache_misses_total",
    "Total number of cache misses",
    ["key_type"],
)

OUTBOX_EVENTS_PUBLISHED_TOTAL = Counter(
    "outbox_events_published_total",
    "Total number of outbox events published to Kafka",
    ["event_type"],
)

OUTBOX_EVENTS_FAILED_TOTAL = Counter(
    "outbox_events_failed_total",
    "Total number of outbox event publish failures",
    ["event_type"],
)

KAFKA_EVENTS_PROCESSED_TOTAL = Counter(
    "kafka_events_processed_total",
    "Total number of Kafka events processed successfully",
    ["event_type"],
)

KAFKA_EVENTS_DUPLICATES_TOTAL = Counter(
    "kafka_events_duplicates_total",
    "Total number of duplicate Kafka events skipped",
    ["event_type"],
)