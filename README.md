# Asynchronous Site-parser with Flask and Celery

Example of how to handle background processes with Flask / Celery / Redis / PostgreSQL / Docker compose.

## Project details

The main task of the project was to write a site parser. 
An additional idea of the project was to build an application architecture with the ability to lazy load articles from a news site. 
As a news site - source was chosen: https://lenta.ru/
The project uses the following features:
- lazy loading of the list of articles (loading at the time of request)
- lazy loading of article content itself, including static page content
- periodic preloading of articles from the source site
- caching of frequently used articles to reduce the load on the database

## Want to use this project?

Spin up the containers:

```sh
$ docker-compose up -d --build
```

Open your browser to [http://localhost:5000](http://localhost:5000) to view the app.