FROM public.ecr.aws/docker/library/python:latest

ARG PASSWORD
ENV PASSWORD=$PASSWORD

EXPOSE 8080
WORKDIR /workspace
COPY . /workspace

RUN pip install -r requirements.txt
RUN python --version

CMD ["python", "./app.py"]
