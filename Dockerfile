FROM python:3.9

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt --use-deprecated=legacy-resolver
#RUN pip install -r requirements.txt

EXPOSE 8081
EXPOSE 80

ENTRYPOINT ["python"]
CMD ["app.py"]

