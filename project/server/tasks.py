import os
import requests
from urllib.parse import urlparse

from celery import Celery, shared_task
from celery.schedules import crontab
from flask.cli import with_appcontext
from redis import Redis

from project.server.models import db, Article
from project.server.parser import parse_content, parse_meta

DEFAULT_PAGE_SIZE = 15
MAX_PAGES = 20
ARTICLE_RAW_DATA_EXP_TIME = 60 * 30

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
celery.conf.beat_schedule = {
    'load_created_articles':
        {
            'task': 'project.server.tasks.load_new',
            'schedule': crontab(minute=0, hour='*/1')
        }
}

redis = Redis(host='redis')


@celery.task(name="load_article_content")
@with_appcontext
def load_article_content(slug: str) -> dict:
    content: bytes = redis.get(slug)
    if content is None:
        article = db.session.query(Article).filter_by(slug=slug).first()
        if not article.is_loaded:
            try:
                article.raw_html_content, query = parse_content(article.raw_html_content_url)
                print(query)
                load_static.subtask().delay(query)
                article.is_loaded = True
                db.session.add(article)
                db.session.commit()
            except:
                db.session.rollback()
        content = article.raw_html_content
        redis.set(slug, content, ex=ARTICLE_RAW_DATA_EXP_TIME)
    else:
        content = content.decode()  # get str from bytes
    return {'raw_html_content': content}


def commit_preview_raw_data(page_num: int = 1):
    url = f'https://lenta.ru/parts/text/{page_num}/'
    domain = urlparse(url).netloc
    headers, raw_preview_html, article_urls, post_time, query = parse_meta(url)
    load_static.subtask().delay(query)
    success_num = 0
    for header, preview_html, url, _time in zip(headers, raw_preview_html, article_urls, post_time):
        try:
            raw = str(preview_html)
            rel_path_pos = raw.find(url)
            related_path = raw[rel_path_pos: rel_path_pos + len(url)]
            raw_html_content_url = related_path if related_path.startswith('https://') else f'{"https://"}{domain}/{related_path}'
            slug = related_path.split('/')[-2]
            a = Article(slug=slug, title=str(header), public_date=_time,
                        raw_html_content_url=raw_html_content_url,
                        raw_html_preview=raw.replace(related_path, f'/news/{slug}/'))
            db.session.add(a)
            db.session.commit()
            success_num += 1
        except:
            db.session.rollback()

    return success_num


@celery.task(name="load_articles_page")
@with_appcontext
def load_articles_page(page: int) -> bool:
    """trying to loading full page of preview data"""
    n_fist_pages = MAX_PAGES - page
    page_size = DEFAULT_PAGE_SIZE
    success = 0
    for num in range(n_fist_pages + 1):
        success += commit_preview_raw_data(page + num)
        if success >= page_size:
            break
    return True


@celery.task(name="load_static")
def load_static(query: list[tuple]) -> bool:
    for url, path in query:
        response = requests.get(url)
        with open(path, 'wb') as f:
            f.write(response.content)
    return True


@shared_task
@with_appcontext
def load_new() -> bool:
    commit_preview_raw_data()
    return True
