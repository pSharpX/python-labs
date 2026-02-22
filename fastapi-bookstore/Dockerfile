FROM python:3.12-slim

# Install system tools including make
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -Ls https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Copy only dependency files first (better caching)
COPY pyproject.toml uv.lock Makefile ./

# Install dependencies
RUN make install

# Copy app code
COPY . .

EXPOSE 3000

HEALTHCHECK CMD curl --fail http://localhost:3000/api/v1/health

CMD ["make", "run"]