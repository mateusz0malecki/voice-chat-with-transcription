FROM nginx:1.23.1-alpine

COPY cert.nginx.conf /etc/nginx/nginx.conf
RUN mkdir /etc/nginx/logs
RUN touch /etc/nginx/logs/error.log