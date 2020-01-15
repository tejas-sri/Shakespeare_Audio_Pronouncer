import requests
import json
from collections import OrderedDict
import re

def getResponse(word):
  response = requests.get("https://www.dictionaryapi.com/api/v3/references/collegiate/json/" + word + "?key=f3721975-0ebb-4fbe-89d6-0135cd51b27c")
  return response.json()

def removeBrackets(word1, word):
  word = list(word)
  if ")" in word and "(" in word:
    #print("yes")
    for i in range(min(len(word), len(word1))):
      if word[i] == "(":
        #print("yes")
        if word1[i] != word[i + 1]:
          word[i], word[i + 1], word[i + 2] = "", "", ""
          break
        elif word1[i] == word[i + 1]:
          word[i] = ""
          word[i + 2] = ""
          break
  word = "".join(word)
  #print(word)
  return word
  
class SonnetPhonetics:
  def __init__(self, sonnet):
    self.sonnet = sonnet
    self.consvowl = "bcdfghjklmnpqrstvwxzŋ͟ʃʧʤʒðθaeiouy"

  def transformSonnet(self):
    brokenSonnet = self.sonnet.split("\n")
    listOfTuples = [self.transformLine(brokenSonnet[k]) for k in range(len(brokenSonnet))]
    return tuple([[listOfTuples[1][k][t] for k in range(len(listOfTuples))]) for t in range(2)]), tuple(["\n".join([listOfTuples[1][k][t] for k in range(len(listOfTuples))]) for t in range(2)])
  
  def transformLine(self, line):
    brokenLine = line.split()
    punc = ""
    if brokenLine[-1][-1] not in self.consvowl:
      punc = brokenLine[-1][-1]
      brokenLine = brokenLine[:-1] + [brokenLine[-1][:-1]]
    listOfTuples = [self.transformWord(brokenLine[k]) for k in range(len(brokenLine))]
    return tuple([[listOfTuples[k][t] for k in range(len(brokenLine))]) + punc for t in range(2)]), tuple([" ".join([listOfTuples[k][t] for k in range(len(brokenLine))]) + punc for t in range(2)])
  
  #produces the Shakespearean IPA of every word
  def transformWord(self, word):
    new = word[:]
    change = False
    while True:
      response = requests.get("https://www.dictionaryapi.com/api/v3/references/collegiate/json/" + word + "?key=f3721975-0ebb-4fbe-89d6-0135cd51b27c")
      response = response.json()
      if isinstance(response[0], str):
        change = True
        if word[-3:] == "eth":
          if isinstance(getResponse(word[:-2]), str):
            word = word[:-2]
          else:
            word = word[:-3]
        if word[-3:] == "est":
          if isinstance(getResponse(word[:-2]), str):
            word = word[:-2]
          else:
            word = word[:-3]

      elif 'prs' not in response[0]["hwi"].keys():
        change = True
        word = response[0]["hwi"]["hw"]
      else:
        phon = self.WordPhonetics((response[0]["hwi"]['prs'][0]['mw']).split("-"), ((response[0]["hwi"]["hw"]).split("*")))
        break
    print(phon.mot, phon.son)
    m = "-".join(phon.mot)
    n = "-".join(phon.son)
    #print(phon.newSon())


    if m.count("-") == n.count("-"):
      for i in range(len(phon.son)):
        if phon.son[i][-1] == "(":
          phon.son[i] = phon.son[i].replace("(", "")
          phon.son[i + 1] = phon.son[i + 1].replace(")", "")
          phon.son[i] = phon.son[i][1:]
          phon.son[i + 1] = phon.son[i][-1] + phon.son[i + 1][:]

        elif phon.son[i][0] == ")":
          phon.son[i] = phon.son[i].replace(")", "")
          phon.son[i - 1] = phon.son[i - 1].replace("(", "")
          phon.son[i - 1] = phon.son[i - 1][:] + phon.son[i][0] 
          phon.son[i] = phon.son[i][1:]

    elif m.count("-") < n.count("-"):
      for i in range(len(phon.son)):
        if phon.son[i][-1] == "(":
          phon.son[i] = phon.son[i].replace("(", "")
          phon.son[i + 1] = phon.son[i + 1].replace(phon.son[i + 1][:phon.son[i + 1].index(")") + 1], "")
        elif phon.son[i][-1] == ")":
          phon.son[i] = phon.son[i].replace(")", "")
          phon.son[i - 1] = phon.son[i - 1].replace(phon.son[i - 1][phon.son[i + 1].index("("):], "")
    #print(phon.son)
    #print(phon.mot, phon.son)

    for i in range(len(phon.son)):
      phon.son[i] = removeBrackets(phon.mot[i], phon.son[i])

    #print(phon.newSon())
    verbs = {"ed": "'d",
            "ies":"z",
            "est": "est",
            "st": "st",
            "eth":"eth",
            "th": "th",
            "s": "z",
            "es": "z",
            "ing": "iŋ",
            }
    #ADD AS MANY VOWEL SOUNDS AS YOU CAN HERE what voelws
    vowels = list("aeiouəēīōȯüu̇āy")
    if change:
      if new[-2:] in ["ed", "es"]:
        phon.son[-1] = list(phon.son[-1])
        phon.son[-1].append(verbs[new[-2:]])
        phon.son[-1] = "".join(phon.son[-1])

        phon.mot[-1] = list(phon.mot[-1])
        phon.mot[-1].append(new[-2:])
        phon.mot[-1] = "".join(phon.mot[-1])

      elif new[-1:] in ["s"]:
        phon.son[-1] = list(phon.son[-1])
        phon.son[-1].append(verbs[new[-1:]])
        phon.son[-1] = "".join(phon.son[-1])

        phon.mot[-1] = list(phon.mot[-1])
        phon.mot[-1].append(new[-1:])
        phon.mot[-1] = "".join(phon.mot[-1])

      else:
        newSyl = ""
        newerSyl = ""
        if len(phon.mot) == 1:
          for i in range(len(phon.son[0]) - 1, 0, -1):
            if phon.son[0][i] in vowels:
              newerSyl += (phon.son[0][i + 1:])
              newSon = phon.son[0][:i + 1]

          for i in range(len(phon.mot[0]) - 1, 0, -1):
            if phon.mot[0][i] in vowels:
              newSyl += (phon.mot[0][i + 1:])
              newMot = phon.mot[0][:i + 1]
              print(i)


        if new[-3:] in ["ies", "est", "eth", "ing"]:
          newSyl += verbs[new[-3:]]
          newerSyl += new[-3:]

        elif new[-2:] in ["th", "st"]:
          newSyl += verbs[new[-2:]]
          newerSyl += new[-2:]     
        
        phon.mot[0] = newMot
        phon.son[0] = newSon
        phon.mot.append(newSyl)
        phon.son.append(newerSyl)

    #print(phon.mot, phon.son)
      
    m = "-".join(phon.mot)
    n = "-".join(phon.son)
    #print(phon.newSon())


    if m.count("-") == n.count("-"):
      for i in range(len(phon.son)):
        if phon.son[i][-1] == "(":
          phon.son[i] = phon.son[i].replace("(", "")
          phon.son[i + 1] = phon.son[i + 1].replace(")", "")
        elif phon.son[i][0] == ")":
          phon.son[i] = phon.son[i].replace(")", "")
          phon.son[i - 1] = phon.son[i - 1].replace("(", "")
    elif m.count("-") < n.count("-"):
      for i in range(len(phon.son)):
        if phon.son[i][-1] == "(":
          phon.son[i] = phon.son[i].replace("(", "")
          phon.son[i + 1] = phon.son[i + 1].replace(phon.son[i + 1][:phon.son[i + 1].index(")") + 1], "")
        elif phon.son[i][-1] == ")":
          phon.son[i] = phon.son[i].replace(")", "")
          phon.son[i - 1] = phon.son[i - 1].replace(phon.son[i - 1][phon.son[i + 1].index("("):], "")
    #print(phon.son)
    #change x to ks
    n = list("-".join(phon.mot))
    for i in range(len(n)):
      if n[i] == "x":
        if n[i + 1] == "-":
          n[i] = "k"
          n[i + 1] = "-"
          n.insert(i + 2, "s")
        else:
          n[i] = "ks"
    phon.mot = "".join(n).split("-")
    
    print(phon.newSon())

    return phon.newSon()
  def eSpeakPhonetics(self):
    transformed = self.transformSonnet()[1]
    correspondence = {
      "ɐ": "3", "ɑ": "A", "ɒ": "0",
      "b": "b",
      "d": "d",
      "ʤ": "dZ",
      "e": "e", "ɛ": "E",
      "ɪ": "I",
      "ŋ": "N",
      "ɔ": "O",
      "r": "R",
      "ɹ": "r",
      "ʃ": "S",
      "ʧ": "tS",
      "θ": "T",
      "ð": "D",
      "ɤ": "V",
      "ʊ": "U",
      "ʒ": "Z",
      "ə": "@",
      "ː": ":",
      "ˈ": "'",
      "ˌ": ",",
    }
    for key in list(correspondence.keys()):
      transformed.replace(key, correspondence[key])
    
    return transformed

  #the class for generating the Shakespearean IPA of every word
  class WordPhonetics:
    def __init__(self, son, mot): 
      self.son = son
      self.mot = [mot[k].lower() for k in range(len(mot))]

      self.cons = "bcdfghjklmnpqrstvwxzŋ͟ʃʧʤʒðθ"
      self.vowl = "aeiouy"
      self.stress = "ˌˈ%"

      self.vowelchange = { #vowel correspondences
        #single vowel
        "a": {"a":"a", "ā":"ɛː", "ä":"ɑː", "ə":"ə"},
        "e": {"e":"e", "ē":"iː", "ə":"ə"},
        "i": {"i":"ɪ", "ī":"əɪ", "ə":"ə"},
        "o": {"ä":"ɒ", "ō": "oː", "ȯ":"ɔː", "ə":["ə","ɤ"], "ü":"uː"},
        "u": {"ə":["ə","ɤ"], "yü":"juː", "ü":"uː", "yu̇":"jʊ", "yə":"jʊ", "u̇":"ʊ"},
        "y": {"i":"ɪ", "ī":"əɪ", "ē":"əɪ"},
        #-w
        "aw": {"ȯ":"ɔː"},
        "ew": {"yü":"juː", "ü":"juː"},
        "ow": {"ō":"oː", "au̇":"ǝʊ"},
        "awe": {"ȯ":"ɔː"},
        "ewe": {"yü":"juː", "yü":"juː"},
        "owe": {"ō":"oː", "au̇":"ǝʊ"},
        #-r
        "ar": {"är":"ɑːɹ", "ər":"əɹ", "er":"ar"},
        "air": {"er":"ɛːɹ"},
        "aur": {"ȯr":"ɔːɹ"},
        "are": {"er":"ɛːɹ", "är":"ɑ:ɹ"},
        "er": {"ər":["əɹ","ɐːɹ"], "er":"er"},
        "ear": {"ir":"iːɹ", "er":"ɛːɹ", "ər":"ɐːɹ"},
        "eare": {"ir":"iːɹ", "er":"ɛːɹ", "ər":"ɐːɹ"},
        "eer": {"ir": "iːɹ"},
        "eur": {"ər":"əɹ"},
        "ere": {"ir": "iːɹ"},
        "ir": {"ər":["əɹ","ɐːɹ"]},
        "ier": {"ir":"iːɹ"},
        "ire": {"īr":"ǝɪɹ"},
        "or": {"ȯr":"ɔːɹ", "ər":"əɹ"},
        "oar": {"ȯr":"ɔːɹ"},
        "oor": {"ȯr":"ɔːɹ", "u̇r":"oːɹ"},
        "our": {"au̇r":"oːɹ", "ȯr":"oːɹ", "u̇r":"uːɹ", "ər":"əɹ"},
        "ore": {"ȯr":"ɔːɹ"},
        "ur": {"ər":["əɹ","ɐːɹ"], "yu̇r":"juːɹ", "u̇r":"uːɹ"},
        "ure": {"yu̇r":"juːɹ", "u̇r":"uːɹ"},
        "yr": {"ər":["əɹ","ɐːɹ"], "ir":"iːɹ"},
        "yre": {"īr":"ǝɪɹ"},
        #other double/triple vowels
        "ai": {"ā":"ɛː"},
        "au": {"ȯ":"ɔː"},
        "ay": {"ā":"ɛː"},
        "ea": {"e":"e", "ē":"eː"},
        "ee": {"ē":"iː"},
        "ei": {"ā":"ɛː"},
        "eu": {"yü":"juː", "ü":"juː"},
        "ey": {"ā":"ɛː"},
        "eye": {"ī":"əɪ"},
        "ie": {"ē":"iː", "ī":"əɪ"},
        "ieu": {"yü":"juː"},
        "oa": {"ō":"oː"},
        "oe": {"ō":"oː"},
        "oi": {"ȯi":"əɪ"},
        "oo": {"ə":"ɤ", "u̇":"ʊ", "ü":"uː"},
        "ou": {"au̇":"ǝʊ", "ü":"uː", "ō":"oː", "ə":"ə"},
        "oy": {"ȯi":"əɪ"},
        #u, y
        "ua": {"wa":"wa", "wā":"wɛː", "wä":"wɑː", "wə": "wə"},
        "ue": {"we":"we", "wē":"wiː", "wə":"wə"},
        "ui": {"wi":"wɪ", "wī":"wəɪ"},
        "uo": {"wo":"wɒ", "wō": "woː", "wȯ":"wɔː", "wə":"wɤ", "wü":"wuː"},
        "uu": {"wə":"wɤ", "wyü":"wjuː", "wü":"wuː"},
        "uy": {"wi":"wɪ", "wī":"wəɪ", "wē":"wəɪ"},
        "ya": {"ya":"ja", "yā":"jɛː", "yä":"jɑː", "yə": "jə"},
        "ye": {"ī":"əɪ", "ye":"je", "yē":"jiː", "yə":"jə"},
        "yi": {"yi":"jɪ", "yī":"jəɪ"},
        "yo": {"yo":"jɒ", "yō": "joː", "yȯ":"jɔː", "yə":"jɤ", "yü":"juː"},
        "yu": {"yə":"jɤ", "yyü":"jjuː", "yü":"juː"},
        "yy": {"yi":"jɪ", "yī":"jəɪ", "yē":"jəɪ"},
      }

      self.conschange = { #consonnat correspondences
        "sh": "ʃ",
        "ch": "ʧ",
        "j": "ʤ",
        "zh": "ʒ",
        "t͟h": "ð",
        "th": "θ",
        "h": "",
        "y": "j"
      }
    
      self.exception = { #exceptions
        "to": ("tuː", "tuː"),
        "at": ("at", "at"),
        "will": ("wɪl", "wɪl"),
        "shall": ("ʃal", "ʃal"),
        "wary": ("ˈwɛːrǝɪ", "wˈɛːr&ǝɪ"),
        "warily": ("ˈwɛːrɪlǝɪ", "wˈɛːr%ɪlǝɪ"),
        "Mary": ("ˈmɛːrǝɪ", "mˈɛːr%ǝɪ"),
        "library": ("ˈlǝɪbrǝˌrǝɪ", "lˈǝɪbr%ǝrˌǝɪ")
      }

    def splitVowCon(self, syl): #splits a syllable into vowel and consonant groups (-r is considered a roticization of the vowel) e.g. "board" --> ["b", "oar","d"]
      splited = []
      change = False
      comb = ""
      for k in range(len(syl)):
        if change:
          splited.append(comb)
          comb = ""
        
        comb += syl[k]

        if k < len(syl) - 1: #decide whether or not a consonant | vowel boundary has occurred
          change = (syl[k+1] in self.stress) or (syl[k] not in self.stress and (((k == 0 or (k == 1 and syl[k] in self.stress)) and (syl[k] == "y") and (syl[k+1] not in self.cons)) or ((syl[k] in self.cons) and (syl[k+1] not in self.cons) and ((k+1) != len(syl)-1 or syl[-1] != "e" or len(splited) == 0)) or (((syl[k] not in self.cons) or ((syl[k] in "rw") and (syl[k-1] not in self.cons))) and (syl[k+1] in self.cons) and (syl[k+1] not in "rw"))))
      
      splited.append(comb)

      return splited

    def wordToSyl(self, word, Sound): #produces correct syllable divisions of word that matches that of the phonetics in case the Merriam Webster division is incorrect (e.g. "asleep", "ə-ˈslēp" --> ["a", "sleep"])
      sound = []
      #split word into vowel and consonant groups (in vowels and consonants arrays)
      vowels = []
      consonants = []
      comb = ""
      Type = "Cons"
      for k in range(len(word)):
        if (Type == "Vowl") != (word[k] in self.vowl):
          if Type == "Cons":
            consonants.append(comb)
            Type = "Vowl"
          else:
            vowels.append(comb)
            Type = "Cons"
          comb = ""
        comb += word[k]
      
      if word[k] in self.vowl:
        vowels.append(comb)
      else:
        consonants.append(comb)
      
      if len(consonants) == len(vowels):
        consonants.append("")

      print("Split:", word, consonants, vowels)
      #split consonant clusters and regroup with vowels
      for k in range(len(Sound)):
        sound.append(self.son[k].replace(self.stress[0], "").replace(self.stress[1], ""))
      
      #possible consonant correspondences between Merriam Webster phonetics and actual spelling
      conschange = {
        "ch": ["ch", "t"],
        "j": ["g", "j", "d"],
        "zh": ["g", "z", "j"],
        "t͟h": ["th"],
        "sh": ["sh","s"],
        "k": ["c","k","ch"],
        "f": ["f", "gh"],
        "ks": ["ks", "x"],
        "gz": ["gz", "x"],
        "z": ["z", "x"]
      }
      spellings = list(conschange.values())
      conschanges = [{
        "ch": ch,
        "j": j,
        "zh": zh,
        "t͟h": the,
        "sh": sh,
        "k": k,
        "f": f,
        "ks": ks,
        "gz": gz,
        "z": z
      } for ch in spellings[0] for j in spellings[1] for zh in spellings[2] for the in spellings[3] for sh in spellings[4] for k in spellings[5] for f in spellings[6] for ks in spellings[7] for gz in spellings[8] for z in spellings[9]]
      
      splited = [] #the word split into its syllables correctly
      lastCons = consonants[0]
      
      for k in range(1,len(consonants)-1):
        syllable = lastCons + vowels[k-1]
        nextCons = consonants[k]
        if sound[k-1][-1] not in self.cons: #syllable boundary between a vowel and consonant e.g. a-sleep
          lastCons = nextCons
        if sound[k][0] not in self.cons: #syllable boundary between a consonant and a vowel e.g. ant-eater
          syllable += nextCons
          lastCons = ""
        else: #syllable 
          for actConschange in conschanges:
            try:
              ind = nextCons.index(sound[k-1][-1]+sound[k][0]) + 1
              break
            except:
              pass
          try:
            syllable += nextCons[:ind]
            lastCons = nextCons[ind:]
          except:
            print("Error: Failure in breaking consonant cluster.")
        
        splited.append(syllable)
      
      splited.append(lastCons + vowels[-1] + consonants[-1])
      #print(splited)
      return splited

    def newSyl(self, syl, pron):
      new = []
      #change le to el; swap superscript schwa symbol
      if syl[0] in self.cons and syl[1:] == "le":
        oldSyl = [syl[0], "e", "l"]
      else:
        oldSyl = self.splitVowCon(syl)
      oldPron = self.splitVowCon(pron.replace("ᵊ", "ə"))
      print(oldSyl, oldPron)
      if len(oldSyl) == len(oldPron) or (len(oldSyl) == len(oldPron) + 1 and oldSyl[-1] == "gh"):
        #t, s, c palatized to sh sound
        if len(syl) >= 4 and syl[0:2] in ["ti", "si", "ci"] and syl[-1] in ["n", "l", "s"]:
          vowel = "ɑ" if syl[-2:] == "al" else "ə"
          new = ["s", "ɪ" + vowel, syl[-1]]
        else:
          for k in range(min(len(oldSyl), len(oldPron))):
            #generate cosonant phonetics
            if oldSyl[k][0] in self.cons or (k == 0 and oldSyl[0] == "y"): #palatized t to ch
              newCons = oldPron[k]
              if newCons[-2:] == "ch" and oldSyl[-1] == "t":
                newCons = newCons[:2] + "t"
              else: #general phonetic symbol changes
                for key in list(self.conschange.keys()):
                  newCons = newCons.replace(key, self.conschange[key])
              new.append(newCons)
            
            #generate vowel phonetics
            else:
              try:
                if oldPron[k][0] in self.stress:
                  new.append(oldPron[k][0]+self.vowelchange[oldSyl[k]][oldPron[k][1:]])
                else:
                  newVow = self.vowelchange[oldSyl[k]][oldPron[k]]
                  if type(newVow) == str:
                    new.append(newVow)
                  else:
                    if pron[0] in self.stress:
                      new.append(newVow[1])
                    else:
                      new.append(newVow[0])
              except:
                curKeySpl = list(self.vowelchange.keys())[0]
                curKeyPro = list(self.vowelchange[curKeySpl].keys())[0]
                curScore = 0
                for keySpl in list(self.vowelchange.keys()):
                  for keyPro in list(self.vowelchange[keySpl].keys()):
                    score = 0
                    try:
                      firstInd = keySpl.index(oldSyl[k])
                      for i in range(min(len(keySyl)-firstInd, len(oldSyl))):
                        if keySyl[firstInd+i] == oldSyl[k][i]:
                          score += 1
                        else:
                          break
                    except:
                      pass
                    
                    try:
                      firstInd = keyPro.index(oldPron[k])
                      for i in range(min(len(keyPro)-firstInd, len(oldPron))):
                        if keyPro[firstInd+i] == oldPron[k][i]:
                          score += 1
                        else:
                          break
                    except:
                      break

                    if score > curScore:
                      curKeySpl = keySpl
                      curKeyPro = keyPro

                new.append(self.vowelchange[curKeySpl][curKeyPro])

        newSyllable = ""
        for let in new:
          newSyllable += let          
        return new, newSyllable
      else:
        print("Warning: Inconsistent phoneme number")
        return "Warning: Inconsistent phoneme number"  
    
    def newSon(self): #Shakespearean pronunciation of word
      print(self.mot)
      if "".join(self.mot) in self.exception.keys():
        return self.exception["".join(self.mot)]

      if len(self.mot) != len(self.son):
        self.mot = self.wordToSyl("".join(self.mot), self.son)
      
      if len(self.mot) == len(self.son):
        IPN = True #IPN = inconsistent phoneme number
        trials = 0
        maxIt = 5
        while IPN and trials < maxIt:
          IPN = False
          length = min(len(self.mot), len(self.son))
          new = ([], [])
          for k in range(length):
            if k < length - 1:
              if self.mot[k][-1] == self.mot[k+1][0]:
                mot = self.mot[k][:-1]
              else:
                mot = self.mot[k]
            else:
              mot = self.mot[k]
            newSyllable = self.newSyl(mot, self.son[k])

            if newSyllable == "Warning: Inconsistent phoneme number":
              self.mot = self.wordToSyl("".join(self.mot), self.son)
              IPN = True
              break
            else:
              new[0].append(newSyllable[0])
              if len(newSyllable[1]) >= 2:
                if newSyllable[1][1] in self.cons:
                  if newSyllable[1][0] == self.stress[0]:
                    new[1].append([newSyllable[0][0][1:], self.stress[0] + newSyllable[0][1]] + newSyllable[0][2:])
                  elif newSyllable[1][0] == self.stress[1]:
                    new[1].append([newSyllable[0][0][1:], self.stress[1] + newSyllable[0][1]] + newSyllable[0][2:])
                  else:
                    #new[1].append([newSyllable[0][0], "%"+newSyllable[0][1]] + newSyllable[0][2:])
                    new[1].append(newSyllable[0])
                else:
                  if newSyllable[1][0] in self.cons:
                    #new[1].append([newSyllable[0][0], "%"+newSyllable[0][1]] + newSyllable[0][2:])
                    new[1].append(newSyllable[0])
                  else:                    
                    #new[1].append(["%"+newSyllable[0][0]] + newSyllable[0][2:])
                    new[1].append(newSyllable[0])
              else:
                #new[1].append(["%"+newSyllable[0][0]] + newSyllable[0][2:])
                new[1].append(newSyllable[0])
            
          trials += 1

          if trials == maxIt - 1:
            print("Fatal error occurred.")
        
        for t in range(2):
          for i in range(len(new[t])-1):
            if new[t][i][-1][-1] == "ɹ" and new[t][i+1][0][0] not in self.cons + self.stress:
              new[t][i][-1] = new[t][i][-1][:-1]
              new[t][i+1][0] = "r" + new[t][i+1][0]
        
        #print("NEW", new)
        newSound = tuple(["".join(["".join(syllable) for syllable in new[t]]) for t in range(2)])
        return newSound
      else:
        return "Error: Inconsistent syllable number."


sonnet_phonetics = SonnetPhonetics("Shall I compare thee to a summer’s day?\nThou art more lovely and more temperate.")
print(sonnet_phonetics.transformSonnet()[1])
