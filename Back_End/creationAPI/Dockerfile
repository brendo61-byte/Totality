FROM python
ADD creationServerApp.py /
ADD models.py /
ADD requirements.txt /
WORKDIR /
RUN pip install -r requirements.txt
CMD ["python", "creationServerApp.py"]
