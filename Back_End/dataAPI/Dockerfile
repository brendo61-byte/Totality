FROM python:3.7
ADD dataControllerServerApp.py /
ADD models.py /
ADD requirements.txt /
ADD m /
ADD app.ini /
ADD run.py /
WORKDIR /
RUN pip install -r requirements.txt
RUN chmod +x m
CMD ["uwsgi", "app.ini"]
