FROM nginx:1.25-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy static frontend files
COPY . /usr/share/nginx/html

# Copy nginx template (uses envsubst at runtime to inject BACKEND_URL)
COPY nginx.conf /etc/nginx/templates/default.conf.template

EXPOSE 80

# At container start: replace ${BACKEND_URL} in nginx template, then start nginx
CMD ["sh", "-c", "envsubst '${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
