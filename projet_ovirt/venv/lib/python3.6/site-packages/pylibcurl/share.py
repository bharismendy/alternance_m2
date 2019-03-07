#coding=utf8

import ctypes
import lib
import const
import prototype

from pylibcurl.base import Base


class Share(Base):
    _pointer_type = ctypes.POINTER(ctypes.c_void_p)
    _lib_init_func = lib.curl_share_init
    _lib_cleanup_func = lib.curl_share_cleanup


    def __init__(self, **kwargs):
        self._callbacks = {}
        
        if kwargs:
            self.setopt(**kwargs)


    def __setattr__(self, name, value):
        try:
            self.setopt(**{name: value})
        except ValueError:
            object.__setattr__(self, name, value)


    def setopt(self, **kwargs):
        """
        """
        def setopt(name, value):
            option_name  = 'CURLSHOPT_%s' % name.upper()
            if name.islower() and hasattr(const, option_name):
                option_value = getattr(const, option_name)
                
                if hasattr(prototype, name):
                    value = getattr(prototype, name)(value)
                    self._callbacks[name] = value
                
                lib.curl_share_setopt(self._handle, option_value, value)
            else:
                raise ValueError('invalid option name "%s"' % name)

        for k, v in kwargs.items():
            setopt(k, v)
    
    def strerror(self, errornum):
        return lib.curl_share_strerror(errornum)

    def _clear(self):
        self._callbacks.clear()


        

