import hashlib
from typing import Optional

import validators
import bs4
import requests

from datetime import datetime, date, time
from flask import url_for

RU_MONTH_VALUES = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}
RU_MONTH_KEYS = {value: key for key, value in RU_MONTH_VALUES.items()}


def format_datetime(dt: datetime) -> str:
    return f'{dt.strftime("%H:%M")}, {dt.day} {RU_MONTH_KEYS[dt.month]} {dt.year}'


def int_value_from_ru_month(date_str: str) -> str:
    for k, v in RU_MONTH_VALUES.items():
        date_str = date_str.replace(k, str(v))
    return date_str


def get_datetime(datetime_like_obj: str) -> datetime:
    try:
        date_obj = datetime.strptime(int_value_from_ru_month(datetime_like_obj), '%H:%M, %d %m %Y')
    except ValueError:
        date_obj = datetime.combine(date.today(), time.fromisoformat(datetime_like_obj))
    return date_obj


def get_response(url: str) -> str:
    r = requests.get(url)
    if r.status_code != 200:
        return False
    return r.text


def get_generated_filepath(url: str) -> tuple[str, str]:
    filename = f'{hashlib.md5(url.encode()).hexdigest()}.{url.split(".")[-1]}'
    path = f"project/client/static/imgs/{filename}"
    return filename, path


def edit_img_block(block: bs4.element.Tag) -> Optional[tuple[str, str]]:
    try:
        url = block['src']
        if validators.url(url):
            filename, path = get_generated_filepath(url)
            block['src'] = url_for('static', filename=f'imgs/{filename}')
            return url, path
    except:
        pass


def upload_local_images(img_blocks: bs4.element.ResultSet) -> list[tuple[str, str]]:
    result = []
    for block in img_blocks:
        block_info = edit_img_block(block)
        if block_info is not None:
            result.append(block_info)
    return result

