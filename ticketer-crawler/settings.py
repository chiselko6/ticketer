import os

APP_PORT = int(os.environ.get('PORT', 5000))
JOB_TOTAL_TIMEOUT = int(os.environ.get('JOB_TOTAL_TIMEOUT', 24))  # in hours
JOB_SINGLE_RUN_TIMEOUT = int(os.environ.get('JOB_SINGLE_RUN_TIMEOUT', 30))  # in seconds
APP_SERVER_URL = os.environ.get('APP_SERVER_URL', f'http://localhost:{APP_PORT}')
