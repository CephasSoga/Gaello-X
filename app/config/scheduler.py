class Schedule:
    NO_DELAY = 0
    DEFAULT_RELOAD_DELAY = 5000
    ASSET_JOB_START_DELAY = 100
    FOREX_JOB_START_DELAY = 200
    INDEX_JOB_START_DELAY = 300
    CRYPTO_JOB_START_DELAY = 400
    COMMODITY_JOB_START_DELAY = 500
    BATCH_ASSETS_JOBS_DELAY = 600
    BATCH_MARKET_JOBS_DELAY = 800
    DEFAULT_DELAY = 1000
    DEFAULT_MULTIPLIER = 2
    MAX_MULTIPLIER = 10
    STRICT_DELAY = 30000
    LONG_WAITING_DELAY = 3000

    ACCUMULATED_TASKS = 100