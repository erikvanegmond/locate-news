import gemAnalysisUtils as analysisUtils
import json

articlesPath = "../Data/articlesFile.txt"

utils = analysisUtils.gemAnalysisUtils("../Data/bevolking.csv", "../Data/gebieden.txt", "../Data/beschrijving.txt", articlesPath)

utils.runAnalysis()

for x in utils.articles:
    utils.articles[x].pop('body', None)
    utils.articles[x].pop('excerpt', None)
    utils.articles[x].pop('tags', None)
    
with open('../Output/articlesData.json', 'w') as outfile:
    json.dump(utils.articles, outfile)

utils.saveLocationInfoToJson('../Output/locationData.json');