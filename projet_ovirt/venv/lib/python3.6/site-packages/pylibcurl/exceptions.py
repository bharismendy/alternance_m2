#coding=utf8

import lib

class Error(Exception):
    def __init__(self, code):
        self.code = code

class CurlError(Error):
    def __str__(self):
        return '#%s %s' % (self.code, lib.curl_easy_strerror(self.code))


class MultiError(Error):
    def __str__(self):
        return '#%s %s' % (self.code, lib.curl_multi_strerror(self.code))


class ShareError(Error):
    def __str__(self):
        return '#%s %s' % (self.code, lib.curl_share_strerror(self.code))

