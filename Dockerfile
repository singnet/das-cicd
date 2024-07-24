FROM python:3.10-alpine AS builder

WORKDIR /das-cicd

COPY ./requirements.txt .

RUN pip3 install -r ./requirements.txt -t .

FROM gcr.io/distroless/python3 as das-cicd

COPY --from=builder /das-cicd /das-cicd

WORKDIR /das-cicd

COPY . .

ENTRYPOINT ["python3"]
CMD ["/das-cicd/main.py"]