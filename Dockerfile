FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN --mount=type=cache, target=/var/cache/apt \
    apt-get update && apt-get install -yqq --no-install-recommends wget unzip \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -yqq --no-install-recommends ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get clean

RUN pip install -e .

# Set the command to run the application
CMD ["python", "lambda_function.py"]
