#coding=utf8

import ctypes
import lib
import const
import prototype

from pylibcurl.base import Base

### classes

class Multi(Base):
    _pointer_type = ctypes.POINTER(const.CURLM)
    _lib_init_func = lib.curl_multi_init
    _lib_cleanup_func = lib.curl_multi_cleanup


    def __init__(self, **kwargs):
        self._handles = set()
        self._callbacks = {}

        if kwargs:
            self.setopt(**kwargs)

    def __setattr__(self, name, value):
        try:
            self.setopt(**{name: value})
        except ValueError:
            object.__setattr__(self, name, value)

    def _clear(self):
        self._handles.clear()
        self._callbacks.clear()

    def add_handle(self, curl):
        lib.curl_multi_add_handle(self._handle, curl._handle)
        self._handles.add(curl)

    def remove_handle(self, curl):
        lib.curl_multi_remove_handle(self._handle, curl._handle)
        self._handles.remove(curl)

    def assign(self, socket, callback):
        raise NotImplementedError

    def fdset(self):
        raise NotImplementedError

    def perform(self):
        running_handles = ctypes.c_int()
        code = lib.curl_multi_perform(self._handle, ctypes.byref(running_handles))
        return code, running_handles.value

    def socket_action(self, socket, event):
        running_handles = ctypes.c_int()
        code = lib.curl_multi_socket_action(self._handle, socket, event, ctypes.byref(running_handles))
        return code, running_handles.value
        
    def info_read(self):
        """
            return tuple(msg, number_in_queue)
                or
            return None
        """
        return lib.curl_multi_info_read(self._handle)


    def setopt(self, **kwargs):
        """
            c.pipelning = 1
                or
            c.setopt(pipelining=1)
                or
            c.setopt(pipelining=1, maxconnects=10)
        """
        def setopt(name, value):
            option_name  = 'CURLMOPT_%s' % name.upper()
            if name.islower() and hasattr(const, option_name):
                option_value = getattr(const, option_name)
                
                if hasattr(prototype, name):
                    if callable(value):
                        value = getattr(prototype, name)(value)
                        self._callbacks[name] = value
                    else:
                        self._callbacks[name] = None

                lib.curl_multi_setopt(self._handle, option_value, value)
            else:
                raise ValueError('invalid option name "%s"' % name)

        for k, v in kwargs.items():
            setopt(k, v)

    def strerror(self, errornum):
        return lib.curl_multi_strerror(errornum)

    def timeout(self):
        time_out = ctypes.c_long()
        lib.curl_multi_timeout(self._handle, ctypes.byref(time_out))
        return time_out.value


