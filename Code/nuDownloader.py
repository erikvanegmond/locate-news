from lxml import html
import requests
import re
import logging
import sys, os

#configure logger
logging.basicConfig(format='%(levelname)s [%(asctime)s] [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s')
logger = logging.getLogger('root')
logger.setLevel(logging.INFO)

class NuDownloader:

    SECTIONS = [ "algemeen",
                 "binnenland",
                 "buitenland",
                 "politiek",
                 "economie",
                 "geldzaken",
                 "ondernemen",
                 "beurs",
                 "sport",
                 "tech",
                 "internet",
                 "mobiel",
                 "gadgets",
                 "games",
                 "entertainment",
                 "achterklap",
                 "film",
                 "muziek",
                 "boek",
                 "media",
                 "overig",
                 "opmerkelijk"
                 "wetenschap",
                 "gezondheid",
                 "lifestyle",
                 "auto",
                 "regio",
                 "amsterdam",
                 "utrecht",
                 "groningen",
                 "rotterdam",
                 "den-haag",
                 "salland",
                 "weekend"]


    def __init__(self):
        self.downloadLinks("linksFile.txt", 1000, "binnenland")
        self.downloadArticles("linksFile.txt", "articlesFile.txt")
        

    def downloadArticles(self, linksFilePath, outputFilePath):

        with open(linksFilePath) as f:
            content = f.readlines()

        outputFile = open(outputFilePath, "w")

        for n, link in enumerate(content):
            if not len(link.strip()):
                break
            link = link.split(",")
            title = link[1].strip()
            link = link[0].strip()

            excerpt, body, date, articleID, tags = self.getArticle(link)
            
            outputFile.write("articleID: "+articleID+"\n")
            outputFile.write("link: "+link+"\n")
            outputFile.write("title: "+title+"\n")
            outputFile.write("excerpt: "+excerpt+"\n")
            outputFile.write("body: "+body+"\n")
            outputFile.write("date: "+date+"\n")
            outputFile.write("tags: "+",".join(tags)+"\n")
            outputFile.write("\n")

            logger.info("[%i/%i] Downloaded %s",n+1, len(content), link)

        outputFile.close()

    def getArticle(self, link):

        url = "http://www.nu.nl"+link

        while True:
            try:

                page = self.getPage(url)
                text = page.text
                tree = html.fromstring(text)
                # title = tree.xpath('//div[@class="title"]/h1[@class="fluid"]/text()')[0].encode('utf-8').strip()
                excerpt = tree.xpath('//div[@class="block-content"]/div[@class="item-excerpt"]/text()')[0].encode('utf-8').strip()
                body = " ".join([p.encode('utf-8').strip() for p in tree.xpath('//div[@class="block article body "]/div[@class="block-wrapper"]/div[@class="block-content"]/p/text()')])
                date = tree.xpath('//span[@class="published"]/span[@class="small"]/text()')[0].encode('utf-8').strip()
                articleID = link.split("/")[2]
                tags = [x.encode('ascii','ignore') for x in tree.xpath('//a[@class="trackevent"]/span/text()')]
            except IndexError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                logger.warn(e)
                # logger.info(text)
                print 'Retry Index'
                continue
            break

        return excerpt, body, date, articleID, tags

    def getPage(self, url):
        while True:
            try:
                page = requests.get(url)
            except requests.exceptions.ConnectionError:
                print "Retry connection "+url
                continue
            break
        return page

    def downloadLinks(self, fname, numberOfLinks=20, section=""):
        if section not in self.SECTIONS:
            logger.warn("%s is not a known section, you might not get any results!", section)
        pattern = r'"([A-Za-z0-9_\./\\-]*)"'

        outputFile = open(fname, "w")
        downloadCounter = 0

        for n in range(0,numberOfLinks+1,20):
            limit = '20' if n + 20 <= numberOfLinks else str(numberOfLinks - n)
            page = requests.get('http://www.nu.nl/block/json/articlelist?section='+section+'&limit='+limit+'&offset='+str(n))

            text = page.text.replace('\\\"','\"')
            tree = html.fromstring(text)
            links = tree.xpath('//li/a/@href')
            titles = tree.xpath('//span[@class="title"]/text()')

            linkTitles = [link+',"'+titles[i]+'"' for i, link in enumerate(links)]
            article = "\n".join(linkTitles)+"\n";

            if len(article.strip()):
                outputFile.write("\n".join(linkTitles)+"\n")
                downloadCounter += int(limit)
                logger.info('Downloaded %i links', downloadCounter)
            else:
                logger.info("No more links found")
                break;

        if len(section):
            logger.info("Downloaded %d links from %s, saved in %s", downloadCounter, section, fname)
        else:
            logger.info("Downloaded %d links, saved in %s", downloadCounter, fname)

        outputFile.close()


n = NuDownloader()