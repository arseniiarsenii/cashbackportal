FROM python:3.12 as requirements-stage
WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export --only main -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.12
WORKDIR /code
COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY cashbackportal /code/cashbackportal
EXPOSE 80
CMD ["uvicorn", "cashbackportal.api.app:app", "--host", "0.0.0.0", "--port", "80"]