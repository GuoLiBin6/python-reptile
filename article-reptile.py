#!/usr/bin/python
# coding=utf-8

# 公众号文章爬虫脚本 来源：知乎文章
# 打包python可执行文件，执行 pyinstaller article-reptile.py，将 dist 中 article-reptile 目录替换到根目录，其他无关文件删除
# 有python环境，可在根目录执行 python article-reptile.py
# 没有python环境，可在根目录执行 ./article-reptile/article-reptile

import requests
import re
import os
import time
import fileinput
import sys
from bs4 import BeautifulSoup

# 多色输出
def color_print(str, type):
    if (type == 'success'):
        print("\033[32m" + str + "\033[0m")
    elif (type == 'danger'):
        print("\033[31m" + str + "\033[0m")
    elif (type == 'warning'):
        print("\033[33m" + str + "\033[0m")
    else:
        print(str)

# 获取文档
def get_remote_html():
    # url = 'https://zhuanlan.zhihu.com/p/619085442'
    url = input("请输入知乎文章地址：")
    req = requests.get(url)
    req.encoding = 'utf-8'
    html = req.text
    domSoup = BeautifulSoup(html, 'html.parser')  # 用BeautifulSoup解析
    return domSoup

# 解析dom
def get_parsed_dom(domObj):
    ret = {'type': '', 'class': ''}
    name = domObj.name
    text = domObj.getText()
    # 普通文字
    if name == 'p' and text and not text.startswith('GitHub') and not text.startswith('官网地址'):
        ret['type'] = 'p'
        ret['class'] = 'article-text'
        ret['text'] = text
    # 一级标题
    if name == 'h1' and text:
        ret['type'] = 'h1'
        ret['class'] = 'article-title mb-3 mt-2'
        ret['text'] = text
    # 二级标题
    elif name == 'h2' and text:
        ret['type'] = 'h1'
        ret['class'] = 'article-h1 mb-3'
        ret['text'] = text
    # 三级标题
    elif name == 'h3' and text:
        ret['type'] = 'h2'
        ret['class'] = 'article-h2 mb-3'
        ret['text'] = text
    elif name == 'img':
        # print(domObj)
        imgRegx = re.compile(r'img.*src="(.*?)"')  # 正则表达式匹配图片
        imgUrls = re.findall(imgRegx, str(domObj))
        for i, picUrl in enumerate(imgUrls):
            if picUrl.startswith('http'):
                ret['type'] = 'img'
                ret['class'] = 'article-img w-100 mb-3'
                ret['text'] = picUrl
    elif name == 'li' and text:
        ret['type'] = 'li'
        ret['text'] = text
        ret['class'] = 'article-li mb-3'
    elif name == 'a' and text:
        ret['type'] = 'a'
        ret['text'] = text
        ret['href'] = domObj.attrs['href']
        ret['class'] = 'article-link mb-3'
    return ret

# 获取文档内容
def get_html_info(domSoup):
    htmlInfo = {
        'title': '',
        'content': []
    }
    # 获得文章结构
    # 标题
    title = domSoup.find(attrs={"class": "Post-Title"})
    titleDom = get_parsed_dom(title)
    htmlInfo['content'].append(titleDom)
    title = title.get_text()
    if (title):
        htmlInfo['title'] = title
        color_print('成功爬取文章：' + title, 'success')
    # 内容
    content = domSoup.find(attrs={"class": "RichText"})
    for i, child in enumerate(content.descendants):
        parseDom = get_parsed_dom(child)
        if (parseDom['type']):
            htmlInfo['content'].append(parseDom)

    return htmlInfo

# 写入文件
def write_file(htmlInfo):
    # 时间
    localtime = time.localtime(time.time())
    month = time.strftime("%Y%m", localtime)
    day = time.strftime("%Y%m%d", localtime)

    # article目录
    articleDir = os.getcwd() + '/src/article'

    # 序号
    htmls = os.listdir(articleDir + '/html')
    htmlNum = len(htmls)
    sortId = str(htmlNum + 1)
    color_print('文章序号：' + sortId, 'success')

    # 文章Id
    has = 0
    for i, filename in enumerate(htmls):  # 判断是否已经有同名文件
        if filename == day + '.html':
            has = 1
    articleId = day
    if (has == 1):
        articleId = input("\033[32m请输入文章编号：\033[0m")
    color_print('文章ID：' + articleId, 'success')

    # 修改 config.js
    configPath = articleDir + '/config.js'
    for line in fileinput.FileInput(configPath, inplace=1):
        lineList = []
        if 'defaultArticleId' in line:
            lineList.append("  defaultArticleId: '" + articleId + "',\n")
        elif 'articleList' in line:
            lineList.append(line)
            lineList.append("      {\n")
            lineList.append("        sortId: " + sortId + ",\n")
            lineList.append("        id: '" + articleId + "',\n")
            lineList.append("        title: '" + htmlInfo['title'] + "',\n")
            lineList.append("      },\n")
        else:
            lineList.append(line)
        sys.stdout.write(''.join(lineList))

    # 修改默认文章
    htmlLines = []
    htmlLines.append('<!DOCTYPE html>\n')
    htmlLines.append('<html lang="en">\n')
    htmlLines.append('@require(\'../lib/app/components/head.html\')\n')
    htmlLines.append('<title>了解云计算_开源融合云_云联壹云</title>\n')
    htmlLines.append('<meta name="keywords" content="云计算">\n')
    htmlLines.append('<meta name="description" content="云联壹云-云计算">\n')
    htmlLines.append('@require(\'../lib/app/components/head2.html\')\n')
    htmlLines.append('\n')
    htmlLines.append('<body id="version-body">\n')
    htmlLines.append('  @require(\'../lib/app/components/header.html\')\n')
    htmlLines.append('\n')
    htmlLines.append('  <div class="article-dom py-5 mt-2" id="article-dom">\n')
    htmlLines.append('    <div class="container">\n')
    htmlLines.append('        <div class="article-wrapper">\n')
    htmlLines.append('            <!-- 文章内容 -->\n')
    htmlLines.append('            <div id="article-content" class="article-content" data-id="' + articleId + '">\n')
    htmlLines.append('              <!-- \n')
    htmlLines.append('                <h1 class="mb-3 mt-2 article-title"></h1>\n')
    htmlLines.append('                <img src="https://pic4.zhimg.com/v2-b5d1f2d2699f8b13acb3e2d5690c062f_b.jpg" class="article-img w-70 mb-3" alt="">\n')
    htmlLines.append('                <h1 class="mb-3 article-h1"></h1>\n')
    htmlLines.append('                <h2 class="mb-3 article-h2"></h1>\n')
    htmlLines.append('                <p class="article-text"></p>\n')
    htmlLines.append('               -->\n')
    # 文章正文
    hN = 1
    for i, line in enumerate(htmlInfo['content']):
        if line['type'] == 'img':
            htmlLines.append('              <' + line['type'] + ' class="' + line['class'] + '" src="' + line['text'] + '" />\n')
        elif line['class'].startswith('article-h'):
            htmlLines.append('              <' + line['type'] + ' class="' + line['class'] + '" id="h-' + str(hN) + '">' + line['text'] + '</' + line['type'] + '>\n')
            hN += 1
        elif line['type'] == 'a':
            htmlLines.append('              <' + line['type'] + ' class="' + line['class'] + '" href="' + line['href'] + '">' + line['text'] + '</' + line['type'] + '>\n')
        else:
            htmlLines.append('              <' + line['type'] + ' class="' + line['class'] + '">' + line['text'] + '</' + line['type'] + '>\n')
    htmlLines.append('            </div>\n')
    htmlLines.append('            <div id="article-sidepage" class="article-sidepage">\n')
    # 判断是否包含目录
    hNum = 0
    for i, line in enumerate(htmlInfo['content']):
        if 'article-h1' in line['class']:
            hNum += 1
    if hNum > 0:
        htmlLines.append('              <div class="article-catalogue">\n')
        htmlLines.append('                <div class="sidepage-title">目录</div>\n')
        htmlLines.append('                <div class="catalogue-list" id="article-catalogue-list">\n')
        htmlLines.append('                </div>\n')
        htmlLines.append('              </div>\n')
    else:
        htmlLines.append('              <!-- <div class="article-catalogue">\n')
        htmlLines.append('                <div class="sidepage-title">目录</div>\n')
        htmlLines.append('                <div class="catalogue-list" id="article-catalogue-list">\n')
        htmlLines.append('                </div>\n')
        htmlLines.append('              </div> -->\n')
    htmlLines.append('              <div class="article-others">\n')
    htmlLines.append('                <div class="sidepage-title">其它</div>\n')
    htmlLines.append('                <div class="other-article-list" id="article-other-list">\n')
    htmlLines.append('                  <!-- <div class="other-article-item" data-id=""></div> -->\n')
    htmlLines.append('                </div>\n')
    htmlLines.append('              </div>\n')
    htmlLines.append('            </div>\n')
    htmlLines.append('        </div>\n')
    htmlLines.append('    </div>\n')
    htmlLines.append('  </div>\n')
    htmlLines.append('  @require(\'../lib/app/components/contact.html\')\n')
    htmlLines.append('  @require(\'../lib/app/components/footer.html\')\n')
    htmlLines.append('</body>')
    htmlLines.append('</html>')

    indexHtml = open(articleDir + '/index.html', 'w', encoding='utf-8')
    indexHtml.truncate()
    indexHtml.write(''.join(htmlLines))
    indexHtml.close()

    # 新增文章
    newHtmlLines = []
    for i, line in enumerate(htmlLines):
        if ('../' in line):
            line = line.replace('../', '../../')
        newHtmlLines.append(line)

    newHtml = open(articleDir + '/html/' + articleId +
                   '.html', 'w', encoding='utf-8')
    newHtml.truncate()
    newHtml.write(''.join(newHtmlLines))
    newHtml.close()

# 主程序
def main():
    domSoup = get_remote_html()
    htmlInfo = get_html_info(domSoup)
    write_file(htmlInfo)


main()
