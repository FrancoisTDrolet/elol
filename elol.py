__author__ = 'FrancoisTDrolet@gmail.com'
import math
import random

class Modifier:
    def __init__(self,name,tags = None):
        self.name = name
        self.delta = 0.0
        self.tags = tags

class Game:
    def __init__(self,elo ,result,modifiers = None):
        self.result = result
        self.modifiers = modifiers
        self.elo = elo

class Universe:
    def __init__(self):
        self.modifiers = {}
        self.games = []
        self.alpha = 1.0/400.0
        self.elo = 1650.0

    def buildClassicElo(self):
        for game in self.games:
            result = game.result
            heroElo = self.elo
            for modifier in game.modifiers:
                heroElo += modifier.delta
            expected = 1.0/(1.0+math.exp((game.elo-heroElo)*self.alpha))
            diff = (result - expected)*32.0/(len(game.modifiers)+1)
            for modifier in game.modifiers:
                modifier.delta += diff
                self.elo += diff

    def predictedElo(self,tags):
        elo = self.elo
        for tag in tags:
            elo+= self.modifiers[tag].delta
        return elo

    def alphaStep(self):
        randomTest = random.choice([-0.001,0.001])
        previousProb = self.overAllProbability()
        self.alpha+=randomTest
        newProb = self.overAllProbability()
        if newProb<previousProb:
            self.alpha-=randomTest

    def optStep(self):
        randomModifier = random.choice(self.modifiers.values())
        randomTest = random.choice([-1,1])
        previousProb = self.overAllProbability()
        randomModifier.delta+=randomTest
        newProb = self.overAllProbability()
        if newProb<previousProb:
            randomModifier.delta-=randomTest

    def populateBaseModifiers(self):
        self.modifiers["jun"] = Modifier("jun",["position"])
        self.modifiers["sup"] = Modifier("sup",["position"])
        self.modifiers["top"] = Modifier("top",["position"])
        self.modifiers["mid"] = Modifier("mid",["position"])
        self.modifiers["adc"] = Modifier("adc",["position"])

        self.modifiers["isRankedTrue"] = Modifier("isRankedTrue",["isRanked"])
        self.modifiers["isRankedFalse"] = Modifier("isRankedFalse",["isRanked"])

        self.modifiers["isTeamTrue"] = Modifier("isTeamTrue",["isTeam"])
        self.modifiers["isTeamFalse"] = Modifier("isTeamFalse",["isTeam"])

    def buildFromFile(self,filename):
        file = open(filename)
        for line in file.readlines():
            data = line.split(",")
            if data[0]=="Date":
                continue
            if data[6] == "":
                continue

            newModifiers = []

            if not(self.modifiers.has_key(data[4])):
                self.modifiers[data[4]] = Modifier("data[4]",["champion"])

            newModifiers.append(self.modifiers[data[4]])

            newModifiers.append(self.modifiers[data[5]])

            if data[8] == "1":
                newModifiers.append(self.modifiers["isRankedTrue"])
            if data[8] == "0":
                newModifiers.append(self.modifiers["isRankedFalse"])

            if data[9] == "1":
                newModifiers.append(self.modifiers["isTeamTrue"])

            if data[9] == "0":
                newModifiers.append(self.modifiers["isTeamFalse"])

            if data[11] != "":
                if not(self.modifiers.has_key(data[11])):
                    self.modifiers[data[11]] = Modifier("data[11]",["nOfGames"])
                newModifiers.append(self.modifiers[data[11]])

            self.games.append(Game(int(data[6]),int(data[7]),newModifiers))

        file.close()

    def resultProbability(self,game):
        heroElo = self.elo
        for modifier in game.modifiers:
            heroElo += modifier.delta

        gameElo = game.elo

        return 1.0/(1.0+math.exp((gameElo-heroElo)*self.alpha*(2.0*game.result-1)))

    def overAllProbability(self):
        p=1.0
        for game in self.games:
            p*=self.resultProbability(game)

        return p

######

u = Universe()
u.populateBaseModifiers()
u.buildFromFile("data.csv")
u.buildClassicElo()



