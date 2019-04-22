from datetime import datetime
import json

import pytz
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework import authentication, permissions

from service.SentimentAnalyzer import SentimentAnalyzer
from service.sentiment.models import Comment, CommentSentiment, SubredditSentiment


class PostCommentsView(APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    subreddit_url_kwarg = 'subreddit'

    sentiment_analyzer = SentimentAnalyzer()

    total_compound = 0.0
    total_negative = 0.0
    total_neutral = 0.0
    total_positive = 0.0

    def post(self, request, **kwargs):
        if not request.data:
            return Response({'message': 'No request data provided.'}, status=HTTP_400_BAD_REQUEST)

        self.__reset_totals()

        count: int = 0
        request_data: dict = json.loads(request.data)

        for data in request_data:
            if not Comment.objects.filter(comment_id=data['id']).exists():
                self.__process_comment_data(data)
                count += 1

        sub_name, sub_id = kwargs.get(self.subreddit_url_kwarg).split('|')

        sub_sentiment, _ = SubredditSentiment.objects.get_or_create(subreddit_id=sub_id, subreddit_name=sub_name)
        count += sub_sentiment.count

        sub_sentiment.negative = ((sub_sentiment.negative * sub_sentiment.count) + self.total_negative) / count
        sub_sentiment.neutral = ((sub_sentiment.neutral * sub_sentiment.count) + self.total_neutral) / count
        sub_sentiment.positive = ((sub_sentiment.positive * sub_sentiment.count) + self.total_positive) / count
        sub_sentiment.compound = ((sub_sentiment.compound * sub_sentiment.count) + self.total_compound) / count
        sub_sentiment.count = count
        sub_sentiment.save()

        return Response(status=HTTP_200_OK)

    def __process_comment_data(self, data: dict):
        comment = Comment()
        comment.comment_id = data['id']
        comment.submission_id = data['submission_id']
        comment.subreddit_id = data['subreddit_id']
        comment.subreddit_name = data['subreddit_name']
        comment.parent_id = data['parent_id']
        comment.score = data['score']
        comment.body = data['body']
        comment.created_utc = datetime.fromisoformat(data['created_utc']).astimezone(pytz.UTC)
        comment.is_distinguished = data['is_distinguished']
        comment.save()

        analysis: dict = self.sentiment_analyzer.analyze(data['body'])

        sentiment = CommentSentiment()
        sentiment.comment = comment
        sentiment.compound = analysis['compound']
        sentiment.negative = analysis['negative']
        sentiment.neutral = analysis['neutral']
        sentiment.positive = analysis['positive']
        sentiment.save()

        self.total_compound += analysis['compound']
        self.total_negative += analysis['negative']
        self.total_neutral += analysis['neutral']
        self.total_positive += analysis['positive']

    def __reset_totals(self):
        self.total_compound = 0.0
        self.total_negative = 0.0
        self.total_neutral = 0.0
        self.total_positive = 0.0
