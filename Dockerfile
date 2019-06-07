FROM python:3.7

RUN mkdir -p /var/www/src/
WORKDIR /var/www/src/
RUN mkdir media

COPY riclibre ./riclibre
COPY account_manager ./account_manager
COPY id_card_checker ./id_card_checker
COPY referendum ./referendum
COPY achievements ./achievements

COPY manage.py requirements.txt ./
RUN apt-get update -y && apt-get -y install tesseract-ocr libtesseract-dev
RUN pip install -r ./requirements.txt
RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && chmod +x wait-for-it.sh
EXPOSE 8000



CMD ./wait-for-it.sh db:5432 -t 0 -- python manage.py collectstatic --noinput \
&& python manage.py migrate \
&& newrelic-admin generate-config $NEW_RELIC_KEY newrelic.ini \
&& NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn riclibre.wsgi:application -b 0.0.0.0:8000

