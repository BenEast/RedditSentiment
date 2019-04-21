import logging
import spacy
from typing import Optional
from vaderSentiment import vaderSentiment


class SentimentAnalyzer:
    _analysis_keys = ['neg', 'neu', 'pos', 'compound']
    _output_keys = {'neg': 'negative', 'neu': 'neutral', 'pos': 'positive', 'compound': 'compound'}
    _english = spacy.load('en_core_web_sm')

    def __init__(self):
        self._analyzer = vaderSentiment.SentimentIntensityAnalyzer()
        self._logger = logging.getLogger(self.__class__.__name__)

    def analyze(self, text: str) -> Optional[dict]:
        if not text:
            return

        sentences: list = [str(s) for s in self._english(text).sents]
        sentiments = [self._analyzer.polarity_scores(s) for s in sentences]

        try:
            analysis: dict = self._merge_analysis(sentiments)
        except ValueError as e:
            self._logger.error(e)
            return None

        return analysis

    def _merge_analysis(self, sentiments: list) -> dict:
        if not sentiments:
            raise ValueError('Failed to merge analysis due to invalid sentiments.')

        analysis: dict = self._initialize_analysis()
        for sentiment in sentiments:
            for key in self._analysis_keys:
                analysis[key] += sentiment[key]

        return self._avg_analysis(analysis, len(sentiments))

    def _avg_analysis(self, analysis: dict, count: int) -> dict:
        return {self._output_keys[key]: analysis[key] / count for key in self._analysis_keys}

    def _initialize_analysis(self) -> dict:
        return {key: 0.0 for key in self._analysis_keys}
