FROM python:3.12-slim AS builder

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir --target=/usr/src/app/dependencies -r requirements.txt

FROM python:3.12-slim

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/dependencies /usr/local/lib/python3.12/site-packages

COPY marzban_verify ./marzban_verify

CMD [ "python", "-m", "marzban_verify" ]