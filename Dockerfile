FROM apify/actor-python-playwright

COPY . ./

ENTRYPOINT ["python", "main.py"]