# Atom Python SDK config file

SDK_VERSION = "1.5.2"
ATOM_ENDPOINT = "http://track.atom-data.io/"

# Tracker Config
BATCH_SIZE = 64
BATCH_BYTES_SIZE = 64 * 1024

# Default flush interval in millisecodns
FLUSH_INTERVAL = 10000

# Batch Event Pool Config
# Default Number of workers(threads) for BatchEventPool
BATCH_WORKER_COUNT = 1
# Default Number of batch events to hold in BatchEventPool
BATCH_POOL_SIZE = 1

# EventStorage Config (backlog)
# Default backlog queue size (per stream)
BACKLOG_SIZE = 500

# Retry on 500 / Connection error conf
# Retry max time in seconds
RETRY_MAX_TIME = 1800
# Maximum number of retries (set it to 1 in order to disable retry). This value is ignored if RETRY_FOREVER = True
RETRY_MAX_COUNT = 12
# Base multiplier for exponential backoff calculation
RETRY_EXPO_BACKOFF_BASE = 3
# Should the worker in BatchEventPool retry forever on server error (recommended)
RETRY_FOREVER = True

# Tracker backlog conf
# Tracker backlog Queue GET & PUT Block or not.
BACKLOG_BLOCKING = True
# Queue GET & PUT timeout in seconds (ignored if backlog is blocking)
BACKLOG_TIMEOUT = 1
