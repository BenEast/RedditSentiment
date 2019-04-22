import logging
import spacy
from typing import Optional
from vaderSentiment import vaderSentiment


class SentimentAnalyzer(object):
    _analysis_keys = ['neg', 'neu', 'pos', 'compound']
    _output_keys = {'neg': 'negative', 'neu': 'neutral', 'pos': 'positive', 'compound': 'compound'}
    _english = spacy.load('en_core_web_sm')

    def __init__(self):
        self.__analyzer = vaderSentiment.SentimentIntensityAnalyzer()
        self.__logger = logging.getLogger(self.__class__.__name__)

    def analyze(self, text: str) -> Optional[dict]:
        if not text:
            return

        sentences: list = [str(s) for s in self._english(text).sents]
        sentiments = [self.__analyzer.polarity_scores(s) for s in sentences]

        return self.__merge_analysis(sentiments)

    def __merge_analysis(self, sentiments: list) -> dict:
        if not sentiments:
            self.__logger.error('Failed to merge analysis due to invalid sentiments.')

        analysis: dict = self.__initialize_analysis()
        for sentiment in sentiments:
            for key in self._analysis_keys:
                analysis[key] += sentiment[key]

        return self.__avg_analysis(analysis, len(sentiments))

    def __avg_analysis(self, analysis: dict, count: int) -> dict:
        return {self._output_keys[key]: analysis[key] / count for key in self._analysis_keys}

    def __initialize_analysis(self) -> dict:
        return {key: 0.0 for key in self._analysis_keys}
