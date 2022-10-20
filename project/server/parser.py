import re

from bs4 import BeautifulSoup

from project.server.utils import format_datetime, get_datetime, get_response, upload_local_images, edit_img_block


def parse_meta(url: str) -> tuple[list, list, list, list, list]:
    r = get_response(url)
    if not r:
        return
    soup = BeautifulSoup(r, 'html.parser')
    headers = [x.h3.contents[0] for x in soup.findAll(class_=re.compile('card-big__title')) if x.h3]
    article_urls = [a.find('a')['href'] for a in soup.findAll(class_='parts-page__item')]
    post_time = [get_datetime(x.contents[0]) for x in soup.findAll(class_='card-big__date')]
    raw_preview_html = soup.findAll(class_='parts-page__item')
    for i, time_block in enumerate(soup.findAll(class_='card-big__date')):
        time_block.string = format_datetime(post_time[i])
    query = upload_local_images(soup.findAll(class_='card-big__image'))
    return headers, raw_preview_html, article_urls, post_time, query


def parse_content(url: str) -> tuple[str, list]:
    r = get_response(url)
    if not r:
        return
    soup = BeautifulSoup(r, 'html.parser')
    content = soup.find('div', class_='topic-body _article')

    similar_content = soup.findAll(class_=re.compile('box-inline-topic'))  # delete similar content block
    for similar in similar_content:
        if similar:
            similar.clear()

    [x.replace_with('') for x in soup.findAll('svg')]  # delete all svg
    box_galleries = soup.findAll(class_=re.compile('box-gallery'))
    changed_blocks = []
    for box_gallery in box_galleries:
        tag = soup.new_tag("section",
                           attrs={'id': "image-carousel", 'class': "splide", 'aria-label': "Beautiful Images"})
        div_tag = soup.new_tag("div", attrs={'class': "splide__track"})
        ul_tag = soup.new_tag("ul", attrs={'class': "splide__list"})
        for x in box_gallery.findChildren('img', class_=re.compile('box-gallery__image')):
            li_tag = soup.new_tag("li", attrs={'class': "splide__slide"})
            img_tag = soup.new_tag("img", src=x['data-src'])
            changed_blocks.append(edit_img_block(img_tag))
            li_tag.contents.append(img_tag)
            ul_tag.contents.append(li_tag)
        div_tag.contents.append(ul_tag)
        tag.contents.append(div_tag)
        box_gallery.replace_with(tag)

    if not content:
        content = soup.find('div', class_='topic-page__container')
    query = changed_blocks + upload_local_images(soup.findAll('img'))
    return str(content), query
