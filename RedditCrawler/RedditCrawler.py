from configparser import ConfigParser
import json
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
    __batch_size: int = 10
    __config = get_config()
    __post_comments_path: str = '/subreddits/{}/comments'

    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__logger.setLevel(20)
        self.__last_batch = set()
        self.__reddit: praw.Reddit = self.__get_reddit()

    def crawl(self):
        self.__scrape_sub_comments(self.__config['reddit']['subreddit'])

    def __scrape_sub_comments(self, sub_name: str):
        comment_stream = self.__reddit.subreddit(sub_name).stream.comments(skip_existing=True)

        comment_data = list()
        for comment in comment_stream:
            if comment.id in self.__last_batch:
                continue

            comment_data.append(build_comment_data(comment))

            print('Retrieved comments: {}'.format(len(comment_data)))

            if len(comment_data) == self.__batch_size:
                self.__post_comment_batch(comment_data, sub_name)
                comment_data = list()

    def __get_reddit(self):
        config: dict = self.__config['reddit']
        reddit: praw.Reddit = praw.Reddit(client_id=config['clientId'],
                                          client_secret=config['clientSecret'],
                                          user_agent=config['userAgent'],
                                          username=config['redditUser'],
                                          password=config['redditPass'],
                                          read_only=True)
        return reddit

    def __post_comment_batch(self, comment_data: list, subreddit: str):
        self.__last_batch = set([data['id'] for data in comment_data])

        username = self.__config['django']['djangoUser']
        password = self.__config['django']['djangoPass']

        r = requests.post(self.__config['django']['url'] + self.__post_comments_path.format(subreddit),
                          auth=(username, password),
                          json=json.dumps(comment_data))

        if r.status_code != 200:
            self.__logger.warning(
                'Comment data POST responded with status code {} for data {}'.format(r.status_code, comment_data))


if __name__ == '__main__':
    crawler = RedditCrawler()
    crawler.crawl()
