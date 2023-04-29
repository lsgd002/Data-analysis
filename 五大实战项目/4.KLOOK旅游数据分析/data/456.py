from lxml import etree
from urllib import request, parse
from bs4 import BeautifulSoup as BS
import requests
import re
import json
import time

url = r'https://www.klook.com'
headers = {
    'Accept-Language': 'zh_CN',
    # 'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36"
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
}
proxies = {"http": "http:183.129.244.16:11723"}


def get_hot_page(url):
    page = requests.get(url, headers=headers).text
    html = etree.HTML(page)
    page_html = html.xpath("//section//div[@class=' m_bg hot_lazy']/a/@href")
    hot_html = {}
    for i, page_html in enumerate(page_html):
        if i == 0:
            hot_html = [url+page_html]
        else:
            hot_html.append(url+page_html)
    return hot_html


def get_hot_activity(hot_page):
    for i, page in enumerate(hot_page):
        page = requests.get(page, headers=headers).text
        html = etree.HTML(page)
        hot_activity = html.xpath(
            "//div//div[@class='m_justify_list m_radius_box act_card act_card_sm a_sd_move j_activity_item js-item ']/a/@href")
        for j, info in enumerate(hot_activity):
            # print(info)
            if i == 0 and j == 0:
                activity_html = [url+info]
        else:
            activity_html.append(url+info)
    return activity_html


def get_base_infos(activity_html):
    with open(r'C:\Users\wdl\Data-analysis\五大实战项目\kelu.csv', 'w') as f:
        f.write('title,num,before_price,after_price,author,rating,time,evaluate\n')
        for i, html in enumerate(activity_html):
            print(html)
            e_html = requests.get(html, headers=headers).text
            e_html = etree.HTML(e_html)
        try:
            e_html.xpath(
                "//div//div[@class='pagination j_pagination']/a[@class='p_num']")[0].text
        except:
            try:
                int(e_html.xpath(
                    "//div//div[@class='pagination j_pagination']/a[@class='p_num ']")[-1].text.replace(',', ''))
            except:
                num = 1
            else:
                num = int(e_html.xpath(
                    "//div//div[@class='pagination j_pagination']/a[@class='p_num ']")[-1].text.replace(',', ''))
        else:
            num = int(e_html.xpath(
                "//div//div[@class='pagination j_pagination']/a[@class='p_num']")[0].text.replace(',', ''))
            after_price = int(e_html.xpath(
                "//div//p[@class='price']/strong/span")[0].text.replace(',', ''))
        try:
            e_html.xpath("//div//p[@class='price']/del")[0].text
        except:
            before_price = after_price
        else:
            before_price = int(e_html.xpath(
                "//div//p[@class='price']/del")[0].text.replace(',', ''))

        title_page = e_html.xpath("//div//h1[@class='t32']")[0].text
        pattern = re.compile(r'.*/(\d{4,5})-.*', re.I)
        num_page = pattern.match(html).group(1)
        print(num_page)
        for j in range(1, num):
            data = {
                'page': j,
                'limit': '10',
                'translate': '1',
                '_': '1548144348424'
            }
            html = "https://www.klook.com/xos_api/v1/usrcsrv/activities/%s/reviews?page=%d&limit=10&translate=1&_=1548143908771" % (
                num_page, j)
            print(html)
            page = requests.get(html, headers=headers,
                                params=data, proxies=proxies).text
            for k in range(0, 10):
                try:
                    json.loads(page)['result']['item'][k].get('author')
                except:
                    break
                else:
                    author_page = str(json.loads(
                        page)['result']['item'][k]['author']).replace('\'', '')
                    rating_page = int(json.loads(
                        page)['result']['item'][k]['rating'])
                    evaluate_page = str(json.loads(
                        page)['result']['item'][k]['translate_content']).replace('\'', '')
                    time_page = json.loads(page)['result']['item'][k]['date']
                    data = []
                    data.extend([title_page, num_page, before_price, after_price,
                                author_page, rating_page, time_page, evaluate_page])
                    data = ','.join(map(str, data))
                    f.write(data + '\n')
                time.sleep(0.1)


if __name__ == 'main':
    print('即将进行抓取')
    hot_page = get_hot_page(url)
    activity_html = get_hot_activity(hot_page)
    base_infos = get_base_infos(activity_html)
