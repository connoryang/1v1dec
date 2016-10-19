#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\diffMerge\wordDiffer.py


class WordDiffer:

    def __init__(self):
        self.addTag = '<a>%s</a>'
        self.remTag = '<r>%s</r>'

    def createJoinedString(self, afterSplit, beforeSplit):
        joined = ''
        for index, word in enumerate(beforeSplit):
            if index < len(afterSplit):
                if afterSplit[index] == word:
                    if joined == '':
                        joined = word
                    else:
                        joined += ' ' + word

        return joined

    def findAdds(self, afterSplit, before):
        for word in afterSplit:
            if word not in before:
                self.result += ' ' + self.addTag % word

    def findRemoves(self, after, beforeSplit):
        for word in beforeSplit:
            if word not in after:
                self.result += ' ' + self.remTag % word

    def diff(self, before, after):
        self.result = ''
        if before != after:
            beforeSplit = before.split()
            afterSplit = after.split()
            self.result = self.createJoinedString(afterSplit, beforeSplit)
            self.findAdds(afterSplit, before)
            self.findRemoves(after, beforeSplit)

    def getStringWithChanges(self):
        return self.result

    def setAddTag(self, tag):
        self.addTag = tag

    def setRemTag(self, tag):
        self.remTag = tag
