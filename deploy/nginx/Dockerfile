FROM nginx:alpine

# Remove default configs
RUN rm /etc/nginx/conf.d/*

# Copy main nginx config
COPY deploy/nginx/nginx-main.conf /etc/nginx/nginx.conf

# Copy site config template (DOMAIN_NAME substituted at runtime)
COPY deploy/nginx/site.conf.template /etc/templates/site.conf.template

# Create certbot webroot dir
RUN mkdir -p /var/www/certbot

EXPOSE 80 443

# Substitute env vars and start nginx
CMD ["/bin/sh", "-c", "envsubst '${DOMAIN_NAME}' < /etc/templates/site.conf.template > /etc/nginx/conf.d/site.conf && exec nginx -g 'daemon off;'"]
