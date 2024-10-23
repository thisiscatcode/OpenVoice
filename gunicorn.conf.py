# gunicorn.conf.py

# Adjust the timeout and graceful_timeout settings
timeout = 600  # Increase this value to allow longer processing time
graceful_timeout = 600
bind = "0.0.0.0:5002"

