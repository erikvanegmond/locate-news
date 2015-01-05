import json
import gemAnalysisUtils as gem
import logging
import sys,os

#configure logger
logging.basicConfig(format='%(levelname)s [%(asctime)s] [%(filename)s:%(lineno)s] %(message)s')
logger = logging.getLogger('root')
logger.setLevel(logging.INFO)

json_data=open('../Data/gemGeo.json')

data = json.load(json_data)

utils = gem.gemAnalysisUtils("../Data/bevolking.csv", "../Data/gebieden.txt", "../Data/beschrijving.txt", "../Data/articlesFile.txt")
utils.runAnalysis()



for i,feature in enumerate(data["features"]):
    try:
        propertie = dict(feature["properties"].items() + utils.locationInfo[utils.getGem(feature["properties"]["GM_NAAM"].encode('ascii', 'ignore')).decode('utf-8').encode('ascii', 'ignore')].items())
        if "Fry" in str(propertie):
            print propertie
        data["features"][i]["properties"]=propertie
    except Exception as e:
        logger.error("could not use "+feature["properties"]["GM_NAAM"].encode('ascii', 'ignore'))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)



with open('../Output/data.json', 'w') as outfile:
    json.dump(data, outfile)