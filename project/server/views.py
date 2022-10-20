from flask import render_template, Blueprint, request
from flask_paginate import Pagination, get_page_parameter

from project.server.models import get_articles
from project.server.tasks import load_article_content, load_articles_page, DEFAULT_PAGE_SIZE

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route('/', methods=["GET"])
def about():
    return render_template('about.html')


@main_blueprint.route('/', methods=["GET"])
def home():
    return render_template('layout.html')


def load_page(page: int, update_articles: bool = False):
    articles = get_articles()
    count = articles.count()
    page_loaded = count >= DEFAULT_PAGE_SIZE * page
    if not page_loaded:
        res = load_articles_page.delay(page)
        if update_articles:
            res.wait()
            articles = get_articles()
            count = articles.count()
    return articles, count


@main_blueprint.route('/news')
def news():
    page = request.args.get(get_page_parameter(), type=int, default=1)  # get current page
    articles, count = load_page(page, update_articles=True)     # load current if not is loaded
    load_page(page + 1)     # preload next page
    page_articles = articles.limit(DEFAULT_PAGE_SIZE).offset((page - 1) * DEFAULT_PAGE_SIZE)
    pagination = Pagination(page=page, total=count, per_page=DEFAULT_PAGE_SIZE, record_name='articles')
    return render_template('articles.html', articles=page_articles, pagination=pagination)


@main_blueprint.route('/news/<slug>/', methods=["GET"])
def render_article(slug: str):
    content = load_article_content.delay(slug).wait()
    return render_template('article.html', raw_html_content=content['raw_html_content'])
