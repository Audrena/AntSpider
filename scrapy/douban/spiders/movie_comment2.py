#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 23:41:38 2019

@author: liudiwei
"""

import json
import random
import string

import douban.database as db
from douban.items import Comment

from scrapy import Request, Spider

cursor = db.connection.cursor()


class MovieCommentSpider(Spider):
    name = 'movie_comment2'
    allowed_domains = ['movie.douban.com']
    sql = 'SELECT douban_id FROM movies WHERE douban_id NOT IN \
           (SELECT douban_id FROM comments GROUP BY douban_id) ORDER BY douban_id'
    cursor.execute(sql)
    movies = cursor.fetchall()
    random.shuffle(movies)
    start_urls = {
        str(i['douban_id']): ('https://m.douban.com/rexxar/api/v2/movie/%s/interests?count=5&order_by=hot' % i['douban_id']) for i in movies
    }

    def start_requests(self):
        for (key, url) in self.start_urls.items():
            headers = {
                'Referer': 'https://m.douban.com/movie/subject/%s/comments' % key
            }
            bid = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(11))
            cookies = {
                'bid': bid,
                'dont_redirect': True,
                'handle_httpstatus_list': [302],
            }
            yield Request(url, headers=headers, cookies=cookies,meta={'main_url':url})

    def parse(self, response):
        main_url = response.meta['main_url']
        response_url = response.url
        print("##### main_url:", main_url)
        print("##### response_url: ", response_url)
        if 302 == response.status:
            print("movie.comment.response.302.url: ",response.url)
        else:
            douban_id = main_url.split('/')[7]
            print("#####comment.douban_id:", douban_id)
            items = json.loads(response.body)['interests']
            for item in items:
                comment = Comment()
                comment['douban_id'] = douban_id
                comment['douban_comment_id'] = item['id']
                comment['douban_user_nickname'] = item['user']['name']
                comment['douban_user_avatar'] = item['user']['avatar']
                comment['douban_user_url'] = item['user']['url']
                comment['content'] = item['comment']
                comment['votes'] = item['vote_count']
                yield comment

    def second_parse(self,response):
        """print user-agent"""
        print("\nChange User-Agent: ", response.request.headers['User-Agent'])

