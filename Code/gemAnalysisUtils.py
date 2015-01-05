import loadCBSData as ld
import re
import logging
import time
import json
from collections import Counter

#configure logger
logging.basicConfig(format='%(levelname)s [%(asctime)s] [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s')
logger = logging.getLogger('root')
logger.setLevel(logging.INFO)


class gemAnalysisUtils:

    SYNONYM_LOCATION = "../Data/plaatsSynomymen.csv"

    pathToPopulationData = pathToAreas = pathToAreaDescriptions = pathToArticles = ""

    hierarchyDict = {}
    population = {}
    articles = {}
    locationsCounted = {}
    gebiedenDict = {}
    gebiedenNameDict = {}
    locationInfo = {}

    rep = pattern = None

    def __init__(self, pathToPopulationData, pathToAreas, pathToAreaDescriptions, pathToArticles):
        self.pathToPopulationData = pathToPopulationData
        self.pathToAreas = pathToAreas
        self.pathToAreaDescriptions = pathToAreaDescriptions
        self.pathToArticles = pathToArticles
        
        
    def runAnalysis(self):
        gebiedenDict, gebiedenNameDict = ld.loadGebieden(self.pathToAreas)
        self.hierarchyDict = self.loadHierarchyData(gebiedenDict, gebiedenNameDict, self.pathToAreaDescriptions)
        
        populationData = open(self.pathToPopulationData).read().split("\n")
        self.population = {x.split(",")[0].decode('cp1252').encode('ascii', 'ignore'):x.split(",")[1].decode('utf-8').encode('ascii', 'ignore') for x in populationData}

        self.articles = self.loadArticles(self.pathToArticles)

        self.setLocationRegEx(gebiedenDict)
        
        self.locateArticles()

        self.countLocations()

        self.setLocationInfo()

    def locateArticles(self):
        logger.info("Locating articles...")
        for articleID in self.articles:
            locations = self.getLocationsFromText(self.articles[articleID]['title']+self.articles[articleID]['excerpt']+self.articles[articleID]['body'], articleID)
            logger.debug("Found %s in %s", str(locations), articleID)
            self.articles[articleID]['locations'] = locations
        logger.info("Located %d articles", len(self.articles))

    def countLocations(self):
        logger.info("Counting articles...")
        locations = reduce(lambda x,y:x+y,[x['locations'] for x in self.articles.values()])
        self.locationsCounted = Counter(locations)
        logger.info("Counted locations of %d articles ", len(self.articles))

    def setLocationInfo(self):
        logger.info("Setting up location info...")
        self.locationInfo = {x:{} for x in self.population.keys()}
        for location in self.locationInfo:
            self.locationInfo[location]['articleCount'] = self.locationsCounted[location]
            self.locationInfo[location]['population'] = self.population[location]
            self.locationInfo[location]['articles'] = [x for x in self.articles if location in self.articles[x]['locations']]
            self.locationInfo[location]['relativeArticleCount'] = float(self.locationsCounted[location])/int(self.population[location])
        logger.info("Location information setup")

    def loadGebieden(pathToAreas):
        gebiedenDict, gebiedenNameDict = ld.loadGebieden(pathToAreas)

    def loadArticles(self, pathToArticles=None):
        if pathToArticles is None:
            pathToArticles = self.pathToArticles
            
        articles = open(pathToArticles).read().split("\n\n")

        articleDict = {}

        for article in articles:
            lines = article.split("\n")

            articleID = link = title = excerpt = body = date = tags = ""
            for line in lines:
                if line.startswith("articleID:"):
                    articleID = int(line[11:])
                if line.startswith("link:"):
                    link = line[6:]
                if line.startswith("title:"):
                    title = line[7:]
                if line.startswith("excerpt:"):
                    excerpt = line[8:]
                if line.startswith("body:"):
                    body = line[6:]
                if line.startswith("date:"):
                    date = line[6:]
                if line.startswith("tags:"):
                    tags = line[6:]

            articleDict[articleID] = {"link":link,
                                      "title":title,
                                      "excerpt":excerpt,
                                      "body":body,
                                      "date":date,
                                      "tags":tags}

        logger.info("Loaded %d articles", len(articleDict))

        return articleDict

    def loadHierarchyData(self, gebiedenDict, gebiedenNameDict, pathToAreaDescriptions):
        hDict = ld.loadBevKernen(pathToAreaDescriptions, gebiedenNameDict, gebiedenDict)

        synonymen = open(self.SYNONYM_LOCATION).read().split("\n")
        synDict = {syn.split(',')[0].strip(): syn.split(',')[1].strip() for syn in synonymen if len(syn)}

        for syn in synonymen:
            if len(syn):
                hDict[syn.split(',')[0].strip()] = syn.split(',')[1].strip()

        logger.info("Loaded Hierarchy Data")

        return hDict

    def getGem(self, gem):
        if gem in self.hierarchyDict:
            return self.getGem(self.hierarchyDict[gem])
        else:
            return gem.decode("utf-8").encode("ascii","ignore")

    def getLocationsFromText(self, text, articleID):
        text = text.decode("utf-8").encode("ascii","ignore")
        logger.debug("Text before: %s", text)
        try:
            text = self.pattern.sub(lambda m: self.rep[re.escape(m.group(0))], text)
        except KeyError as e:
            logger.error("KeyError: %s in %d", e, articleID)
        logger.debug("Text after: %s", text)
        plaatsenInArtikel = re.findall("(<\[)(.*?)(\]>)", text)
        plaatsenInArtikel = set([self.getGem(x[1]) for x in plaatsenInArtikel])
        return list(plaatsenInArtikel)

    def setLocationRegEx(self, gebiedenDict):
        t = sorted(set([x['name'] for x in gebiedenDict.values()])|set(self.hierarchyDict.keys()), key=lambda x: len(x), reverse=True)

        rep = {x:"<["+x+"]>" for x in t}
        self.rep = dict((re.escape(k), v) for k, v in rep.iteritems())
        self.pattern = re.compile("|".join(t))
        logger.info("Location Regular expression set")

    def getArticlesFromLocation(self, location):
        if location in self.locationInfo:
            return [self.articles[x]['link'] for x in self.locationInfo[location]['articles']]
        else:
            logger.warn("%s is not in locationInfo")

    def saveLocationInfoToJson(self, fname):
        # data = dict(self.locationInfo.items())
        data = [dict([("naam",x)]+self.locationInfo[x].items()) for x in self.locationInfo]
        with open(fname, 'w') as outfile:
            json.dump(data, outfile)