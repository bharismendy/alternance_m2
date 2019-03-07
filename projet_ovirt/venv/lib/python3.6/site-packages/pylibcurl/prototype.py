#-*- coding: utf-8 -*-
from ctypes import *
import const


def writefunction(func):
    def wrap(buf, size, nmemb, stream):
        #print "buffer %s" % buf
        #print "size %s" % size
        #print "nmemb %s" % nmemb
        #print "stream %s" % stream

        actual_size = size * nmemb
        res = func(buf[:actual_size])
        return actual_size
        #return res if res is not None else actual_size
    return const.curl_write_callback(wrap)

headerfunction = writefunction



def readfunction(func):
    def wrap(buf, size, nmemb, stream):
        buf.value = func(size * nmemb)
        return len(buf.value)
    return const.curl_read_callback(wrap)

def ioctlfunction(func):
    raise NotImplementedError

def progressfunction(func):
    def wrap(curl, download_total, downloaded, upload_total, uploaded):
        return func(download_total, downloaded, upload_total, uploaded)
    return const.curl_progress_callback(func)

def debugfunction(func):
    def wrap(curl, type_, data, size, void):
        #print "DEBUG in wrap:"
        #print curl, type_, data, size, void
        func(type_, data[:size])
        return 0
    return const.curl_debug_callback(wrap)

def sockoptfunction(func):
    raise NotImplementedError

def opensocketfunction(func):
    raise NotImplementedError

def seekfunction(func):
    raise NotImplementedError

def ssl_ctx_function(func):
    raise NotImplementedError

def conv_to_network_function(func):
    raise NotImplementedError

def conv_from_network_function(func):
    raise NotImplementedError

def conv_from_utf8_function(func):
    raise NotImplementedError


#### Multi

def socketfunction(func):
    from pylibcurl import Curl

    def wrap(curl, socket, event, userp, socketp):
        func(Curl(curl), socket, event)
        return 0
    return const.curl_socket_callback(wrap)

def timerfunction(func):
    from pylibcurl import Multi

    def wrap(multi, timeout, userp):
        func(Multi(multi), timeout)
        return 0
    return const.curl_multi_timer_callback(wrap)
    
#### Share

def lockfunc(func):
    raise NotImplementedError

def unlockfunc(func):
    raise NotImplementedError

