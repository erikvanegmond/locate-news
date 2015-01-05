import json, csv

def fixBeschrijvingen(inputFile, output):
    lines = open(inputFile).read().split('\n')
    outputFile = open(output, "w")

    for i,line in enumerate(lines):

        if i+1 < len(lines) and lines[i+1][:2] == "- " and lines[i+2][:3] != "..." and lines[i+2][:2] != "- ":
            line = line+lines[i+1]
            lines[i+1]=""
            outputFile.write(line+"\n")
        elif i+1 < len(lines) and lines[i][:2] == "- " and lines[i+1][:2] == "- ":
            line = lines[i]+lines[i+1]
            lines[i+1]=""
            outputFile.write(line+"\n")

        elif line and line != ".":

            if line[:3] != "...":
                line = line.replace("...","\n...")
            if line[:2] != "- ":
                line = line.replace("- ", "\n- ")
            
            if line[:13] != "Wijziging per":
                line = line.replace("Wijziging per", "\nWijziging per")
            if line[:25] != "Provinciale wijziging per":
                line = line.replace("Provinciale wijziging per", "\nProvinciale wijziging per")
            if line[:18] != "Grenswijziging per":
                line = line.replace("Grenswijziging per", "\nGrenswijziging per")
            if line[:12] != "Ontstaan per":
                line = line.replace("Ontstaan per", "\nOntstaan per")
            if line[:13] != "Opgeheven per":
                line = line.replace("Opgeheven per", "\nOpgeheven per")
            if line[:18] != "Naamswijziging per":
                line = line.replace("Naamswijziging per", "\nNaamswijziging per")
            if line[:25] != "Gemeentelijke herindeling":
                line = line.replace("Gemeentelijke herindeling", "\nGemeentelijke herindeling")
            if line[:10] != "Begindatum":
                line = line.replace("Begindatum", "\nBegindatum")
            
            if ",oude naam:" in line:
                line = line.replace(",oude naam:", ",\noude naam:")
            if ",nieuwe naam:" in line:
                line = line.replace(",nieuwe naam:", ",\nnieuwe naam:")

            if "inwoners." in line:
                line = line.replace("inwoners.","inwoners")
            if line[-1] == ".":
                line = line[:-1]


            # line = line.replace(",",",\n")
            outputFile.write(line+"\n")
        else:
            if "Begindatum" in lines[i-1] and (line == "." or (i+1 < len(lines) and lines[i+1])):
                outputFile.write("\n")

    outputFile.close()

def loadDataDictFromTXT(fileName, gebiedenNameDict):
    f = open(fileName).read()
    cities = f.strip().split('\n\n')
    dataDict = {}
    year = 0

    #if we shoud add new lines to the current city dict
    #changes when a new section is found
    addToCityDict = False

    for city in cities:
        lines = city.split("\n")
        name = lines[0].decode("utf-8").encode("ascii","ignore")
        cityDict = {'name':name}
        addToCityDict = False

        for i, line in enumerate(lines):
            if line[:18] == "Naamswijziging per":
                if line[25:29] not in cityDict:
                    cityDict[line[25:29]] = {}
                newName = getNameChange(lines[i+1])
                if newName:
                    cityDict[line[25:29]]["nameChange"]=newName

            if line[:13] == "Wijziging per":
                if "ontvangen van" in line:
                    addToCityDict = True
                    year = line[20:24]
                    if year not in cityDict:
                        cityDict[year] = {}
                        cityDict[year]["changes"] = []
                else:
                    addToCityDict = False


            if line[:25] == "Provinciale wijziging per":
                addToCityDict = False

            if line[:18] == "Grenswijziging per":
                if "ontvangen van" in line:
                    addToCityDict = True
                    year = line[25:29]
                    if year not in cityDict:
                        cityDict[year] = {}
                        cityDict[year]["changes"] = []
                else:
                    addToCityDict = False

            if line[:12] == "Ontstaan per":
                if "ontvangen van" in line:
                    addToCityDict = True
                    year = line[19:23]
                    if year not in cityDict:
                        cityDict[year] = {}
                        cityDict[year]["changes"] = []
                else:
                    addToCityDict = False
                

            if line[:29] == "Gemeentelijke herindeling per":
                if "ontvangen van" in line:
                    addToCityDict = True
                    year = line[36:40]
                    if year not in cityDict:
                        cityDict[year] = {}
                        cityDict[year]["changes"] = []
                else:
                    addToCityDict = False

            if addToCityDict and line[:2]=="- " and "changes" in cityDict[year]:
                t = [getCode(line)]+getChangedProperties(lines[i+1])
                c = cityDict[year]["changes"]
                c.append(t)

        
        if name in gebiedenNameDict:
            code = gebiedenNameDict[name]
            dataDict[code] = cityDict
        else:
            print "else ", name
            dataDict[name] = cityDict

    return dataDict

def loadDataListFromTXT(fileName, gebiedenNameDict, gebiedenDict):
    f = open(fileName).read()
    cities = f.strip().split('\n\n')
    dataList = []
    year = 0

    #if we shoud add new lines to the current city dict
    #changes when a new section is found
    addToCityDict = False

    for city in cities:
        lines = city.split("\n")
        name = lines[0].decode("utf-8").encode("ascii","ignore")

        if name in gebiedenNameDict:
            province = gebiedenDict[gebiedenNameDict[name]]['provincie']
            code = gebiedenNameDict[name]
            cityObj = City(code, name, province)
            begin = int(gebiedenDict[gebiedenNameDict[name]]['begin'][:4])
            eind = int(gebiedenDict[gebiedenNameDict[name]]['eind'][:4]) if len(gebiedenDict[gebiedenNameDict[name]]['eind']) else 2014
            cityObj.setPeriod(begin,eind)
            
        else:
            #print "skip "+name
            continue

        cityList = [name]
        cityDict = {'name':name}
        addToCityDict = False

        changeType = ""
        for i, line in enumerate(lines):
            if line[:18] == "Naamswijziging per":
                changeType = "Naamswijziging"

                if line[25:29] not in cityDict:
                    cityDict[line[25:29]] = {}
                newName = getNameChange(lines[i+1])
                if newName:
                    cityDict[line[25:29]]["nameChange"]=newName

            if line[:13] == "Wijziging per":
                changeType = "Wijziging"
                if "ontvangen van" in line:
                    addToCityDict = True
                    year = line[20:24]
                    # if year not in cityDict:
                    #     cityDict[year] = {}
                    #     cityDict[year]["changes"] = []
                else:
                    addToCityDict = False


            if line[:25] == "Provinciale wijziging per":
                changeType = "Provinciale wijziging"
                addToCityDict = False

            if line[:18] == "Grenswijziging per":
                changeType = "Grenswijziging"
                if "ontvangen van" in line:
                    addToCityDict = True
                    year = line[25:29]
                    # if year not in cityDict:
                    #     cityDict[year] = {}
                    #     cityDict[year]["changes"] = []
                else:
                    addToCityDict = False

            if line[:12] == "Ontstaan per":
                changeType = "Ontstaan"
                if "ontvangen van" in line:
                    addToCityDict = True
                    year = line[19:23]
                    # if year not in cityDict:
                    #     cityDict[year] = {}
                    #     cityDict[year]["changes"] = []
                else:
                    addToCityDict = False
                

            if line[:29] == "Gemeentelijke herindeling per":
                changeType = "Gemeentelijke herindeling"
                if "ontvangen van" in line:
                    addToCityDict = True
                    year = line[36:40]
                    # if year not in cityDict:
                    #     cityDict[year] = {}
                    #     cityDict[year]["changes"] = []
                else:
                    addToCityDict = False


            if addToCityDict and line[:2]=="- ":
                change = Change(year,changeType, getCode(line), getChangedProperties(lines[i+1]))
                cityObj.addChange( change )
                # t = [getCode(line)]+getChangedProperties(lines[i+1])
                # c = cityDict[year]["changes"]
                # c.append(t)

        if cityObj:
            dataList.append(cityObj)

    return dataList

def loadBevKernen(fileName, gebiedenNameDict, gebiedenDict):
    f = open(fileName).read()
    cities = f.strip().split('\n\n')
    dataList = []
    year = 0

    #if we shoud add new lines to the current city dict
    #changes when a new section is found
    addToCityDict = False

    for city in cities:
        lines = city.split("\n")
        name = lines[0].decode("utf-8").encode("ascii","ignore")

        if name in gebiedenNameDict:
            province = gebiedenDict[gebiedenNameDict[name]]['provincie']
            code = gebiedenNameDict[name]
            cityObj = City(code, name, province)
            begin = int(gebiedenDict[gebiedenNameDict[name]]['begin'][:4])
            eind = int(gebiedenDict[gebiedenNameDict[name]]['eind'][:4]) if len(gebiedenDict[gebiedenNameDict[name]]['eind']) else 2014
            cityObj.setPeriod(begin,eind)
            
        else:
            #print "skip "+name
            continue

        cityList = [name]
        cityDict = {'name':name}
        addToCityDict = False
        save = False

        changeType = ""
        for i, line in enumerate(lines):
            if line[:18] == "Naamswijziging per":
                changeType = "Opgeheven"
                save = True

                if line[25:29] not in cityDict:
                    cityDict[line[25:29]] = {}
                newName = getNameChange(lines[i+1])
                if newName and newName in gebiedenDict:
                    change = Change(1,changeType, newName, [1,1,1])
                    cityObj.addChange(change)
                    #cityDict[line[25:29]]["nameChange"]=newName

            if line[:13] == "Opgeheven per":
                changeType = "Opgeheven"
                if "overgegaan naar" in line and line[20:24]>1940:
                    addToCityDict = True
                    save = True
                else:
                    addToCityDict =False

            if line[:13] == "Wijziging per":
                changeType = "Wijziging"
                if "ontvangen van" in line:
                    addToCityDict = True
                    year = line[20:24]
                else:
                    addToCityDict = False


            if line[:25] == "Provinciale wijziging per":
                changeType = "Provinciale wijziging"
                addToCityDict = False

            if line[:18] == "Grenswijziging per":
                changeType = "Grenswijziging"
                if "ontvangen van" in line:
                    addToCityDict = True
                    year = line[25:29]
                else:
                    addToCityDict = False

            if line[:12] == "Ontstaan per":
                changeType = "Ontstaan"
                if "ontvangen van" in line:
                    addToCityDict = True
                    year = line[19:23]
                    # if year not in cityDict:
                    #     cityDict[year] = {}
                    #     cityDict[year]["changes"] = []
                else:
                    addToCityDict = False
                

            if line[:29] == "Gemeentelijke herindeling per":
                changeType = "Gemeentelijke herindeling"
                if "ontvangen van" in line:
                    addToCityDict = True
                    year = line[36:40]
                    # if year not in cityDict:
                    #     cityDict[year] = {}
                    #     cityDict[year]["changes"] = []
                else:
                    addToCityDict = False


            if addToCityDict and line[:2]=="- ":
                change = Change(year,changeType, getCode(line), getChangedProperties(lines[i+1]))
                cityObj.addChange( change )
                # t = [getCode(line)]+getChangedProperties(lines[i+1])
                # c = cityDict[year]["changes"]
                # c.append(t)

        if cityObj and save:
            dataList.append(cityObj)
            save = False

    hierarchieDict = {}
    for city in dataList:
        newCities = [x for x in city.getChanges() if x.changeType=="Opgeheven"]
        if len(newCities):
            newCity = max(newCities, key=lambda x: x.people).fromCode
            if newCity in gebiedenDict:
                hierarchieDict[city.getName()] = gebiedenDict[newCity]['name']

        # for change in city.getChanges():
        #     print change
                
        # newName = [x for x in city.getChanges() if x.changeType=="nameChange"]
        # print newName
 
    return hierarchieDict

def getNameChange(line):
    if "nieuwe naam" in line:
        code = getCode(line)
        return code
    return 0

#gets the properties of the change, hectare/woningen and inwoners in a list
def getChangedProperties(line):
    change = []
    split = line.split()
    if "hectare" in split:
        change.append(int(split[split.index("hectare")-1]))
    else:
        change.append(0)

    if "inwoners" in split:
        change.append(int(split[split.index("inwoners")-1]))
    elif "inwoner" in split:
        change.append(1)
    else:
        change.append(0)

    if "woningen" in split:
        change.append(int(split[split.index("woningen")-1]))
    elif "woning" in split:
        change.append(1)
    else:
        change.append(0)


    return change

def getCode(line):
    leftbracket = line.index('(')+1
    rightbracket = line.index(')')
    code = line[leftbracket:rightbracket]
    if len(code) is not 6:
        secondcode = line[rightbracket+1:]
        leftbracket = secondcode.index('(')+1
        rightbracket = secondcode.index(')')
        code = secondcode[leftbracket:rightbracket]

    return code

def loadGebieden(fileName):
    gebieden = open(fileName).read().replace("\"","").split("\n")
    # gebieden = csv.reader(open(file),delimiter=';')

    del gebieden[0]

    gebiedenDict = {}
    gebiedenNameDict = {}

    for gebied in gebieden:
        gebied = gebied.split(";")
        name = gebied[0].decode("utf-8").encode("ascii","ignore")
        
        if len(gebied[2]) and int(gebied[2][6:11])>1940 or not len(gebied[2]):
            gebiedenDict[gebied[3]] = {'name':name,"begin":gebied[6],"eind":gebied[7], "provincie":gebied[4]}
            gebiedenNameDict[name] = gebied[3]

    return gebiedenDict, gebiedenNameDict

def prettyPrint(data, level=0):
    print "pretty!"
    # print type(data)
    children = None
    properties = None
    if type(data) == list:
        for d in data:
            prettyPrint(d, level+1)
    elif type(data) == dict:
        if "children" in data:
            children = data.pop("children")

        if "properties" in data:
            properties = data.pop("properties")

        if "GMC" in data:
            print getSpaces(level),data["GMC"],
        
        if properties:
            if "children" in properties:
                child = properties.pop("children")
                print printProperties(properties)
                prettyPrint(child, level+1)
            else:
                print printProperties(properties)
        
        if children:
            prettyPrint(children, level+1)
    
    elif type(data) == unicode:
        print getSpaces(level),data

def printProperties(properties):
    return properties

def getSpaces(numSpaces):
    return " "*numSpaces

class City(object):
    """docstring for City"""

    province = ""
    name = ""
    code = ""
    period = []
    # changeList = []

    def __init__(self, code, name, province):
        self.province = province
        self.code = code
        self.name = name
        self.changeList = []

    def addChange(self, change):
        self.changeList.append(change)

    def pprint(self):
        print self
        for change in self.changeList:
            print getSpaces(4),change

    def getName(self):
        return self.name

    def getProvince(self):
        return self.province

    def getCode(self):
        return self.code

    def getChanges(self):
        return self.changeList

    def getPeriod(self):
        return self.period

    def setPeriod(self, begin, eind):
        self.period = [begin, eind]

    def __repr__(self):
        return "City()"
    def __str__(self):
        return self.code+" "+self.name+" "+self.province

class Change(object):
    """docstring for Change"""

    year = 0
    changeType = ""
    fromCode = ""
    area = 0
    people = 0
    houses = 0

    def __init__(self, year, changeType, fromCode, changes):
        self.year = year
        self.changeType = changeType
        self.fromCode = fromCode
        self.area = changes[0]
        self.people = changes[1]
        self.houses = changes[2]


    def __repr__(self):
        return "Change()"
    def __str__(self):
        return self.changeType+" in "+str(self.year)+" van "+self.fromCode+": "+str(self.area)+" "+str(self.people)+" "+str(self.houses)

