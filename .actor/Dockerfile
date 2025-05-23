# Dockerfile
# Using a more generic Apify Python base image to have full control over Playwright installation.
FROM apify/actor-python:3.10

# Set the working directory inside the Docker image
WORKDIR /usr/src/app

# Copy only requirements.txt first to leverage Docker's build cache.
COPY requirements.txt ./

# Install Python dependencies.
RUN echo "Python version:" \
    && python --version \
    && echo "Pip version:" \
    && pip --version \
    && echo "Installing dependencies:" \
    && pip install --no-cache-dir -r requirements.txt \
    && echo "All installed Python packages:" \
    && pip freeze

# Install Playwright's system-level browser dependencies.
# These are crucial for Chromium to run headless in a Docker environment.
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    libxdamage1 \
    libxcomposite1 \
    libxrandr2 \
    libgbm-dev \
    libasound2 \
    libdbus-1-3 \
    libgtk-3-0 \
    libcups2 \
    libdrm2 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libatk1.0-0 \
    libgconf-2-4 \
    libgdk-pixbuf2.0-dev \
    libnotify-dev \
    libnss3-dev \
    libx11-xcb-dev \
    libxcomposite-dev \
    libxcursor-dev \
    libxdamage-dev \
    libxext-dev \
    libxfixes-dev \
    libxi-dev \
    libxrandr-dev \
    libxrender-dev \
    libxss-dev \
    libxtst-dev \
    libappindicator1 \
    libasound2-dev \
    libdbus-glib-1-2 \
    libgconf-2-4 \
    libgtk2.0-0 \
    libnss3 \
    libxss1 \
    libxtst6 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Create the apify user and its home directory if it doesn't exist.
RUN useradd --create-home apify

# Copy the rest of your application code into the working directory.
COPY . ./

# Change ownership of the entire application directory to the 'apify' user.
# This is crucial for the 'apify' user to have write permissions (e.g., for __pycache__ and Playwright cache).
RUN chown -R apify:apify /usr/src/app

# Set the PLAYWRIGHT_BROWSERS_PATH environment variable for the 'apify' user.
# This directs Playwright to install browsers into a location owned by 'apify'.
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/src/app/.cache/ms-playwright

# Switch to the non-root 'apify' user for running the actor and installing Playwright browsers.
USER apify

# Explicitly install Playwright browsers (e.g., Chromium) as the 'apify' user.
# This command downloads and installs the browser binaries to the location specified by PLAYWRIGHT_BROWSERS_PATH.
# Using --force to ensure a fresh download, overriding any previous incomplete installations.
RUN playwright install chromium --with-deps --force

# Compile Python source files for faster startup (optional but good practice).
# Target the 'src' directory where your main.py is located.
RUN python3 -m compileall -q src/

# Define the command to run when the container starts.
# This will execute your main.py script, which is located inside the 'src' directory.
CMD ["python3", "-m", "src.main"]
