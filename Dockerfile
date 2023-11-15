FROM python:3.11-alpine

ADD requirements.txt /winter/requirements.txt
RUN pip3 install -r /winter/requirements.txt

WORKDIR /winter
CMD ["python3", "-u", "main.py"]
