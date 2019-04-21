from configparser import ConfigParser
import logging
import praw
import requests


def build_comment_data(comment: praw.reddit.models.Comment):
    return {
        'id': comment.id,
        'body': comment.body,
        'submission_id': comment.link_id,
        'parent_id': comment.parent_id,
        'score': comment.score
    }


def get_config():
    config = ConfigParser()
    config.read('config.properties')
    return config


class RedditCrawler(object):
    __batch_size: int = 100
    __config = get_config()

    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__last_batch = set()
        self.__reddit: praw.Reddit = self.__get_reddit()

    def crawl(self):
        self.__scrape_sub_comments(self.__config['reddit']['subreddit'])

    def __scrape_sub_comments(self, sub_name: str):
        comment_stream = self.__reddit.subreddit(sub_name).stream.comments(skip_existing=True)

        comment_data = list()
        for comment in comment_stream:
            if comment.id in self.last_batch:
                continue

            comment_data.append(build_comment_data(comment))

            if len(comment_data) == self.__batch_size:
                self.__post_comment_batch(comment_data)
                comment_data = list()

    def __get_reddit(self):
        config: dict = self.__config['reddit']
        reddit: praw.Reddit = praw.Reddit(client_id=config['clientId'],
                                          client_secret=config['clientSecret'],
                                          user_agent=config['userAgent'],
                                          username=config['reddit_username'],
                                          password=config['reddit_password'],
                                          read_only=True)
        return reddit

    def __post_comment_batch(self, comment_data: list):
        self.last_batch = set([data['id'] for data in comment_data])

        username = self.__config['django']['django_username']
        password = self.__config['django']['django_password']

        request = requests.post(self.__config['django']['url'],
                                auth=(username, password),
                                data=comment_data,
                                headers={'Content-Type': 'application/json'})

        if request.status_code != 200:
            self.__logger.warning(
                'Comment data POST responded with status code {} for data {}'.format(request.status_code, comment_data))


if __name__ == '__main__':
    crawler = RedditCrawler()
    crawler.crawl()
