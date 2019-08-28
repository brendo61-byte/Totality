FROM python
ADD commandControllerServerApp.py /
ADD models.py /
ADD requirements.txt /
WORKDIR /
RUN pip install -r requirements.txt
CMD ["python", "commandControllerServerApp.py"]
