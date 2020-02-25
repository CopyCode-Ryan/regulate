import requests
from lxml import etree
import json
import fcntl
import hashlib
import os
import threading

class GraduateSpider:
    def __init__(self):
        self.provinceName = 'province.txt'
        self.provinceUrl = 'https://souky.eol.cn/api/newapi/func_11kytj'
        self.url = "https://souky.eol.cn/api/newapi/func_11kytj?province={}&flag={}&tj_speciality={}&Mypage={}"
        self.headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}
        self.province_list = self.provinces()
        pass

    def parseUrl(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    def run(self):
        for province in self.province_list:
            if province != '':
                print(province, "start::")
                t = threading.Thread(target=self.getList, args=(province,))
                t.start()
                #process = multiprocessing.Process(target=self.getList, args=(province,))
                #process.start()
    
    def getList(self, province):
        next_url = self.url.format(province,'','','')
        items = list()
        while next_url is not None:
            content = self.parseUrl(next_url)
            #print(content)
            html = etree.HTML(content)
            pages = html.xpath("//div[@class='page']")
            self.parseContent(content)
            item = self.parseContent(content)
            for page in pages:
                next_url = self.provinceUrl + page.xpath("//a[@class='pageBtn next']/@href")[0] if len(page.xpath("//a[@class='pageBtn next']/@href")) > 0 else None
                if next_url is not None:
                    break
            if item is not None:
                items.extend(item)
        if len(items) > 0 :
            self.cacheData(province, items)
        print("%s end." % province)
        
    def cacheData(self, name,items):
        m = hashlib.md5()
        m.update(name.encode())
        fileName = m.hexdigest() + '.txt'
        with open(fileName, 'w') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(json.dumps(items, ensure_ascii=False, indent=2))
            fcntl.flock(f, fcntl.LOCK_UN)

    def parseContent(self, content):
        html = etree.HTML(content)
        table = html.xpath("//div[@class='table']")[0]
        trs = table.xpath("//tr[@class='dataRow']")
        label = ["name", "title", "type", "detail"]
        items = list()
        for tr in trs:
            tds = tr.xpath("./td")
            if len(tds) > 1: 
                item = {"name": '', "title": '', "type": '', "detail": ''}
                i = 0
                for td in tds:
                    text = ''
                    if td.text == '暂无结果':
                        item = None
                        break
                    if len(td.xpath("./a/@href"))>0:
                        text = td.xpath("./a/@href")[0]
                    else:
                        text = td.text
                    if i == 0:
                        item['name'] = text
                    elif i == 1:
                        item['title'] = text
                    elif i == 2:
                        item['type'] = text
                    elif i == 3:
                        item['detail'] = text
                    i += 1
                if item is not None:
                    items.append(item)
        return items

    def provinces(self):
        if os.path.exists(self.provinceName):
            with open(self.provinceName, 'r') as f:
                content = f.read()
                p = json.loads(content)
                f.close()
                return p
        else:
            provinceHtml = self.parseUrl(self.provinceUrl)
            items = self.getProvince(provinceHtml)
            self.saveProvince(items)
            return items

    def getProvince(self, provinceHtml):
        html = etree.HTML(provinceHtml)
        province = html.xpath("//select[@name='province']")
        item = {}
        for p in province:
            item = p.xpath("./option/@value")
        return item
        
    def saveProvince(self, provinces): 
        with open(self.provinceName, "w") as f:
            f.write(json.dumps(provinces, ensure_ascii=False, indent=2))

    def charts(self):
        while True:
            if threading.activeCount() == 1:
                break
        province = self.provinces()
        jsons = list()
        for p in province:
            m = hashlib.md5()
            m.update(p.encode())
            fileName = m.hexdigest() + '.txt'
            try:
                 with open(fileName, 'r') as f:
                    content = f.read()
                    f.close()
                    items =  json.loads(content)
                    item = {"name": p, "value":len(items), "selected": 'true', "items": items}
                    jsons.append(item)
            except Exception as e:
                pass
        with open("data.js", 'w') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write("var data = " + json.dumps(jsons, ensure_ascii=False, indent=2))
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()
        pass
def main():
    spider = GraduateSpider()
    spider.run()
    spider.charts()

if __name__ == "__main__":
    main()