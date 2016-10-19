#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\chardet\sjisprober.py
import sys
from .mbcharsetprober import MultiByteCharSetProber
from .codingstatemachine import CodingStateMachine
from .chardistribution import SJISDistributionAnalysis
from .jpcntx import SJISContextAnalysis
from .mbcssm import SJISSMModel
from . import constants

class SJISProber(MultiByteCharSetProber):

    def __init__(self):
        MultiByteCharSetProber.__init__(self)
        self._mCodingSM = CodingStateMachine(SJISSMModel)
        self._mDistributionAnalyzer = SJISDistributionAnalysis()
        self._mContextAnalyzer = SJISContextAnalysis()
        self.reset()

    def reset(self):
        MultiByteCharSetProber.reset(self)
        self._mContextAnalyzer.reset()

    def get_charset_name(self):
        return self._mContextAnalyzer.get_charset_name()

    def feed(self, aBuf):
        aLen = len(aBuf)
        for i in range(0, aLen):
            codingState = self._mCodingSM.next_state(aBuf[i])
            if codingState == constants.eError:
                if constants._debug:
                    sys.stderr.write(self.get_charset_name() + ' prober hit error at byte ' + str(i) + '\n')
                self._mState = constants.eNotMe
                break
            elif codingState == constants.eItsMe:
                self._mState = constants.eFoundIt
                break
            elif codingState == constants.eStart:
                charLen = self._mCodingSM.get_current_charlen()
                if i == 0:
                    self._mLastChar[1] = aBuf[0]
                    self._mContextAnalyzer.feed(self._mLastChar[2 - charLen:], charLen)
                    self._mDistributionAnalyzer.feed(self._mLastChar, charLen)
                else:
                    self._mContextAnalyzer.feed(aBuf[i + 1 - charLen:i + 3 - charLen], charLen)
                    self._mDistributionAnalyzer.feed(aBuf[i - 1:i + 1], charLen)

        self._mLastChar[0] = aBuf[aLen - 1]
        if self.get_state() == constants.eDetecting and self._mContextAnalyzer.got_enough_data():
            if self.get_confidence() > constants.SHORTCUT_THRESHOLD:
                self._mState = constants.eFoundIt
        return self.get_state()

    def get_confidence(self):
        contxtCf = self._mContextAnalyzer.get_confidence()
        distribCf = self._mDistributionAnalyzer.get_confidence()
        return max(contxtCf, distribCf)
