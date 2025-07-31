FROM node:22-alpine AS base_image
WORKDIR /code/frontend
COPY --chown=node:node  ./package*.json ./
RUN npm ci


# Dev Stage
FROM base_image AS development
USER root

CMD [ "tail", "-f", "/dev/null" ]