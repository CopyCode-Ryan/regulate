# -*- coding: UTF-8 -*-

import requests
from lxml import etree
import threading
import json
import time


class RegulateSpider:

    regulates = list()

    def __init__(self, provinces, codes, url=None, headers=None):
        if url is not None:
            self.url = url
        else:
            self.url = "https://souky.eol.cn/api/newapi/func_11kytj"
        if headers is not None:
            self.headers = headers
        else:
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}
        self.codes = codes
        self.provinces = provinces

    def parseUrl(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    def run(self):
        for i in range(len(self.provinces)):
            province = self.provinces[i]
            code = self.codes[i]
            if province != '':
                t = threading.Thread(target=self.spider, args=(province, code,))
                print(province, "start:")
                t.start()
                time.sleep(0.5)

    def spider(self, province, code):
        nextUrl = self.url + "?province=" + province
        items = list()
        while nextUrl is not None:
            content = self.parseUrl(nextUrl)
            item = self.cleanData(content, province, code)
            if item is not None:
                items.extend(item)
            nextUrl = self.parseNext(content)
        RegulateSpider.regulates.extend(items)
        #print(RegulateSpider.regulates)
        print(province, code, items)

    def cleanData(self, content, province, code):
        html = etree.HTML(content)
        table = html.xpath("//div[@class='table']")[0]
        trs = table.xpath("//tr[@class='dataRow']")
        items = list()
        for tr in trs:
            tds = tr.xpath("./td")
            if len(tds) > 1:
                item = {"area": province, "area_code": str(code), "school_name": '', "majors": '', "school_type": '',
                        "school_detail": ''}
                i = 0
                for td in tds:
                    text = ''
                    if td.text == '暂无结果':
                        item = None
                        break
                    if len(td.xpath("./a/@href")) > 0:
                        text = td.xpath("./a/@href")[0]
                    else:
                        text = td.text
                    if i == 0:
                        item['school_name'] = text
                    elif i == 1:
                        item['majors'] = text
                    elif i == 2:
                        item['school_type'] = text
                    elif i == 3:
                        item['school_detail'] = text
                    i += 1
                if item is not None:
                    items.append(item)
        return items

    def parseNext(self, content):
        html = etree.HTML(content)
        pages = html.xpath("//div[@class='page']")
        for page in pages:
            next_url = self.url + page.xpath("//a[@class='pageBtn next']/@href")[
                0] if len(page.xpath("//a[@class='pageBtn next']/@href")) > 0 else None
            if next_url is not None:
                return next_url
        return None


province_list = [
    "北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江", "上海", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南", "广东",
    "广西", "海南", "重庆", "四川", "贵州", "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆", "香港", "澳门"]
province_code = [
    110000, 120000, 130000, 140000, 150000, 210000, 220000, 230000, 310000, 320000, 330000, 340000, 350000, 360000,
    370000,
    410000, 420000, 430000, 440000, 450000, 460000, 500000, 510000, 520000, 530000, 540000, 610000, 620000, 630000,
    640000,
    650000, 810000, 820000]


def update_data(url):
    while True:
        thread_num = len(threading.enumerate())
        print(thread_num)
        if thread_num <= 1:
            break
    if len(RegulateSpider.regulates) > 0:
        header = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=header, data=json.dumps(RegulateSpider.regulates))
        print(response.content.decode())


def main():
    spider = RegulateSpider(provinces=province_list, codes=province_code)
    spider.run()
    update_data("https://graduate.xiaoyelive.com/api/v1.0/district/school-majors")
    pass


if __name__ == "__main__":
    main()
