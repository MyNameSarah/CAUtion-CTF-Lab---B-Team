FROM php:8.2-apache

COPY src/ /var/www/html/
COPY apache-upload.conf /etc/apache2/conf-enabled/apache-upload.conf

RUN mkdir -p /var/www/html/uploads \
    && chown -R www-data:www-data /var/www/html/uploads \
    && chmod 755 /var/www/html/uploads

EXPOSE 80
