# Atom Python SDK config file

SDK_VERSION = "1.5.0"
ATOM_URL = "http://track.atom-data.io/"

# Tracker Config
BATCH_SIZE = 500
BATCH_BYTES_SIZE = 64 * 1024

# Default flush interval in millisecodns
FLUSH_INTERVAL = 10000

# Batch Event Pool Config
# Default Number of workers(threads) for BatchEventPool
BATCH_WORKER_COUNT = 1
# Default Number of events to hold in BatchEventPool
BATCH_POOL_SIZE = 3000

# EventStorage Config (backlog)
# Default backlog queue size (per stream)
BACKLOG_SIZE = 12000

# Retry on 500 / Connection error conf

# Retry max time in seconds
RETRY_MAX_TIME = 1800
# Maximum number of retries
RETRY_MAX_COUNT = 12
# Base multiplier for exponential backoff calculation
RETRY_EXPO_BACKOFF_BASE = 3
