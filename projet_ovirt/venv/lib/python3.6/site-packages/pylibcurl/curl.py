# -*- coding: utf-8 -*-

from iri2uri import iri2uri


import ctypes
import lib
import const
import prototype
import urllib
from pylibcurl.base import Base

### classes

class Curl(Base):
    
    _CURLOPT_SLIST = ('httpheader', 'http200aliases', 'quote',
            'postquote', 'prequote', 'telnetoptions')


    _CURLINFO_CHAR = ('effective_url', 'content_type', 'private', 'redirect_url',
        'primary_ip', 'ftp_entry_path', 
    )
    _CURLINFO_LONG = ('response_code', 'http_connectcode', 'filetime', 
        'redirect_count', 'header_size', 'request_size', 'ssl_verifyresult', 
        'httpauth_avail', 'proxyauth_avail', 'os_errno', 'num_connects', 'lastsocket',
        'condition_unmet'
    )
    _CURLINFO_DOUBLE = ('total_time', 'namelookup_time', 'connect_time', 'appconnect_time',
        'pretransfer_time', 'starttransfer_time', 'redirect_time', 'size_upload',
        'size_download', 'speed_download', 'speed_upload', 'content_length_download', 
        'content_length_upload',
    )
    _CURLINFO_SLIST = ('ssl_engines', 'cookielist')


    _pointer_type = ctypes.POINTER(const.CURL)
    _lib_init_func = lib.curl_easy_init
    _lib_cleanup_func = lib.curl_easy_cleanup
    
    def __init__(self, url=None, **kwargs):
        self._slist = {}
        self._buff = {}

        if url:
            kwargs['url'] = url

        if kwargs:
            self.setopt(**kwargs)

    
    #def __copy__(self):
    #    obj = super(Curl, self).__copy__()
    #    obj._handle = lib.curl_easy_duphandle(self._handle)
    #    return obj


    
    def __setattr__(self, name, value):
        if name in ('_handle', '_slist', '_buff'):
            object.__setattr__(self, name, value)
        else:
            self.setopt(**{name: value})

    
    def __getattr__(self, name):
        try:
            return self.getinfo(name)
        except ValueError:
            raise AttributeError

    
    def perform(self):
        lib.curl_easy_perform(self._handle)

    
    def reset(self):
        self._clear()
        lib.curl_easy_reset(self._handle)
        

    
    def _clear(self):
        self._buff.clear()

        for k in self._slist:
            lib.curl_slist_free_all(self._slist[k])
        
        self._slist.clear()


    def setopt(self, **kwargs):
        """
            c.setopt(url='http://python.org')
                or
            c.setopt(url='http://python.org', useragent='opera')
        """
        def setopt(name, value):
            option_name  = 'CURLOPT_%s' % name.upper()
            if name.islower() and hasattr(const, option_name):
                option_value = getattr(const, option_name)
                
                if name in self._CURLOPT_SLIST:
                    value = lib.list2pointer_slist(value)
                    if name in self._slist:
                        lib.curl_slist_free_all(self._slist[name])
                        del self._slist[name]
                    else:
                        self._slist[name] = value
                elif hasattr(prototype, name):
                    if callable(value):
                        value = getattr(prototype, name)(value)
                elif name == 'postfields' and isinstance(value, dict):
                    value = urllib.urlencode(value)
                elif name == 'share':
                    value = value._handle
                elif name == 'url' and value:
                    value = iri2uri(value)
                    if isinstance(value, unicode):
                        value = value.encode('utf-8')

                
                # setopt
                lib.curl_easy_setopt(self._handle, option_value, value)
                #print option_name, value
                self._buff[option_name] = value
            else:
                raise ValueError('invalid option name "%s"' % name)

        for k, v in kwargs.items():
            setopt(k, v)

    
    def strerror(self, errornum):
        return lib.curl_easy_strerror(errornum)

    
    def getinfo(self, *args):
        """
            url = c.effective_url
                or
            d = c.getinfo('effective_url', 'response_code') # return dict

            return dict or str|int|float if len(args) == 1
        """
        def getinfo(name):
            option_name = 'CURLINFO_%s' % name.upper()
            if name.islower() and hasattr(const, option_name):
                option_value = getattr(const, option_name)

                if name in self._CURLINFO_CHAR:
                    variable = ctypes.c_char_p()
                elif name in self._CURLINFO_LONG:
                    variable = ctypes.c_long()
                elif name in self._CURLINFO_DOUBLE:
                    variable = ctypes.c_double()
                elif name in self._CURLINFO_SLIST:
                    variable = ctypes.POINTER(const.curl_slist)()
                else:
                    raise ValueError('invalid option name "%s"' % name)

                value = ctypes.byref(variable)
                # getinfo
                lib.curl_easy_getinfo(self._handle, option_value, value)
                
                if name in self._CURLINFO_SLIST:
                    return lib.slist2list(variable.contents)
                else:
                    return variable.value
            else:
                raise ValueError('invalid option name "%s"' % name)

        if len(args) == 1:
            return getinfo(args[0])
        else:
            d = {}
            for name in args:
                d[name] = getinfo(name)
            return d

    

