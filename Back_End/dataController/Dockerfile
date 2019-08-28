FROM python
ADD dataControllerServerApp.py /
ADD models.py /
ADD requirements.txt /
WORKDIR /
RUN pip install -r requirements.txt
CMD ["python", "dataControllerServerApp.py"]
