# Dockerfile
# Use the Apify base image specifically designed for Python and Playwright.
# This image already contains many system dependencies and a pre-installed Playwright.
FROM apify/actor-python-playwright

# Set the working directory inside the Docker image
WORKDIR /usr/src/app

# Copy only requirements.txt first to leverage Docker's build cache.
# If requirements.txt doesn't change, this layer won't rebuild.
COPY requirements.txt ./

# Install Python dependencies.
# The --no-cache-dir flag helps reduce the final image size.
RUN echo "Python version:" \
    && python --version \
    && echo "Pip version:" \
    && pip --version \
    && echo "Installing dependencies:" \
    && pip install --no-cache-dir -r requirements.txt \
    && echo "All installed Python packages:" \
    && pip freeze

# Explicitly install Playwright browsers.
# This is crucial to ensure the browser binaries are present and correctly linked,
# even if the base image already has Playwright installed.
# It ensures compatibility with the installed 'playwright' Python package.
RUN playwright install chromium --with-deps

# Copy the rest of your application code into the working directory.
COPY . ./

# Compile Python source files for faster startup (optional but good practice).
# Assuming your main script and other Python files are in the 'src' directory.
# If main.py is directly in the root, you might adjust this or remove if not using a 'src' folder.
# If your main.py is at the root and not in 'src', this line might need adjustment or removal.
RUN python3 -m compileall -q .

# Create a non-root user 'apify' for security best practices.
# This user will run the actor process.
RUN useradd --create-home apify && \
    chown -R apify:apify ./
USER apify

# Define the command to run when the container starts.
# This will execute your main.py script.
# Assuming main.py is at the root level of your copied project.
# If your main.py is inside a 'src' directory, change this to CMD ["python3", "-m", "src.main"]
CMD ["python3", "-m", "src"]