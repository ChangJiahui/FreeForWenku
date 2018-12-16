#! env python3
# coding: utf-8
# Athor: Lz1y
# Blog: www.Lz1y.cn
# TIPS: PDF|PPT只能下载图片
import argparse
import json
import pathlib
import re

import requests


parser = argparse.ArgumentParser()
parser.add_argument('url', help='Target Url,你所需要文档的URL')
parser.add_argument('type', help='Target Type,你所需要文档的的类型(DOC|PPT|TXT|PDF)')
args = parser.parse_args()

url = args.url
type = args.type


def mkdir(path):
    pathlib.Path(path).mkdir(exist_ok=True)


def get_id(url):
    return re.match('.*view/(.*)(.html)?', url).group(1)


def DOC(url):
    # https://wenku.baidu.com/view/7bfacb3c312b3169a451a495.html
    doc_id = get_id(url)
    html = requests.get(url).text
    lists = re.findall('(https.*?0.json.*?)\\\\x22}', html)
    lenth = len(lists) // 2
    new_lists = lists[:lenth]
    y = 0
    fn = f'{doc_id}.txt'
    fp = open(fn, 'w')
    for line in new_lists:
        line = line.replace('\\', '')
        txts = requests.get(line).text
        txtlists = re.findall('"c":"(.*?)".*?"y":(.*?),', txts)
        for txt in txtlists:
            if y != txt[1]:
                y = txt[1]
                fp.write('\n')
            fp.write(txt[0].encode().decode('unicode_escape'))
    print(f'Save to {fn}.')


def TXT(url):
    # https://wenku.baidu.com/view/327ed8b51eb91a37f0115c13.html
    doc_id = get_id(url)
    url = 'https://wenku.baidu.com/api/doc/getdocinfo?' \
          f'callback=json&doc_id={doc_id}'
    text = requests.get(url).text
    text = re.match(r'.*json\((.*)\)', text).group(1)
    data = json.loads(text)
    md5 = data['md5sum']
    pn = data['docInfo']['totalPageNum']
    rsign = data['rsign']
    url = 'https://wkretype.bdimg.com/retype/text/' \
          f'{doc_id}?rn={pn}&type=txt{md5}&rsign={rsign}'
    body = requests.get(url).json()
    fn = f'{doc_id}.txt'
    fp = open(fn, 'w')
    for data in body:
        for parag in data['parags']:
            fp.write(parag['c'])
    print(f'Save to {fn}.')


def PPT(url):
    # https://wenku.baidu.com/view/37bdddf5f90f76c661371a6b.html
    doc_id = get_id(url)
    url = 'https://wenku.baidu.com/browse/getbcsurl?'   \
          f'pn=1&rn=99999&type=ppt&doc_id={doc_id}'
    body = requests.get(url).json()
    mkdir(doc_id)
    for idx, data in enumerate(body):
        img = requests.get(data['zoom']).content
        with open(f'{doc_id}/{idx}.jpg', 'wb') as fp:
            fp.write(img)
    print(f'Save to {doc_id} dir.')


def PDF(url):
    # https://wenku.baidu.com/view/246214f5d15abe23492f4d15
    doc_id = get_id(url)
    html = requests.get(url).text
    # 寻找下载地址
    urls = re.search("WkInfo.htmlUrls = '(.*)'", html).group(1)
    urls = urls.replace(r'\/', '/')     # ?
    urls = urls.encode().decode('unicode_escape')
    urls = json.loads(urls)
    mkdir(doc_id)
    for idx, url in enumerate(urls['png']):
        url = url['pageLoadUrl']
        img = requests.get(url).content
        with open(f'{doc_id}/{idx}.png', 'wb') as fp:
            fp.write(img)
    print(f'Save to {doc_id} dir.')


if __name__ == '__main__':
    eval(type.upper())(url)
