FROM python
ADD commandControllerServerApp.py /
ADD models.py /
ADD requirements.txt /
ADD m /
WORKDIR /
RUN pip install -r requirements.txt
RUN chmod +x m
CMD ["python", "commandControllerServerApp.py"]
