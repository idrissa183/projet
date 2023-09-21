FROM python:3.11

LABEL authors="DELL"

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.models:app", "--host", "0.0.0.0", "--port", "8000"]

#LABEL authors="DELL"

#ENTRYPOINT ["top", "-b"]

#RUN mkdir "/home/ticanalyse"
#WORKDIR /home/ticanalyse