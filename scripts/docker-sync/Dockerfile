FROM python:3.11-slim

# Install git and openssh-client
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy sync script
COPY sync-all-agents.py ./

# Default command
ENTRYPOINT ["./entrypoint.sh"]
CMD []
