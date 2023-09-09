FROM python:3.11

WORKDIR /usr/src/app
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system
COPY main.py telegram.py ./
CMD ["python3", "main.py"]
