FROM python:3.8-slim
RUN mkdir /src

COPY requirements.txt /src/
RUN cd /src && pip install -r requirements.txt

COPY . /src/

EXPOSE 8080
WORKDIR /src/

CMD python bot.py