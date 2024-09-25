class ModelsArgs:
    MIN_TOKENS_COUNT_FOR_CONTEXT = 24
    MAX_CHAT_DOCS = 50
    MAX_CHAT_COLLECTIONS = 50

class EndpointsArgs:
    MAX_QUEUE_SIZE = 1000
    HOST = '0.0.0.0'
    PORT = 19220
    DEBUG = True
    THREADED = False
    REQ_PROTOCOL = 'http'
    REQ_PORT = 5000
    REQ_HOST = '127.0.0.1'