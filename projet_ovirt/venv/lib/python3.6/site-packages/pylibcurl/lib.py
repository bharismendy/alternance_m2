# -*- coding: utf-8 -*-
from ctypes import util

import ctypes
import const
import os


if os.name == 'nt':
    native = ctypes.cdll.libcurl
else:
    native = ctypes.CDLL(util.find_library('curl'))


def not_implemented(*args, **kwargs):
    raise NotImplementedError


def init_func(native, attr_name, restype=None, errcheck=None):
    func = getattr(native, attr_name, not_implemented)

    if restype:
        func.restype = restype

    if errcheck:
        func.errcheck = errcheck

    return func

# curl_version
curl_version = init_func(native, 'curl_version', restype=ctypes.c_char_p)

# curl_version_info
_curl_version_info = init_func(native, 'curl_version_info',
    restype=ctypes.POINTER(const.curl_version_info_data))

def curl_version_info(ver=const.CURLVERSION_NOW):
    return _curl_version_info(ver).contents



# cmp_version
CURRENT_VERSION_INFO = curl_version_info(const.CURLVERSION_NOW)
CURRENT_VERSION_NUM = CURRENT_VERSION_INFO.version_num
CURRENT_VERSION_MAJOR = CURRENT_VERSION_NUM >> 16
CURRENT_VERSION_MINOR = (CURRENT_VERSION_NUM ^ CURRENT_VERSION_MAJOR << 16) >> 8
CURRENT_VERSION_PATCH = CURRENT_VERSION_NUM ^ CURRENT_VERSION_MAJOR << 16 ^ CURRENT_VERSION_MINOR << 8

def cmp_version(major, minor, patch): 
    return cmp(CURRENT_VERSION_MAJOR, major)\
        or cmp(CURRENT_VERSION_MINOR, minor)\
        or cmp(CURRENT_VERSION_PATCH, patch)

def curl_easy_errcheck(result, func, args):
    from pylibcurl.exceptions import CurlError

    if (isinstance(result, int) and result != const.CURLE_OK) or result is None:
        raise CurlError(result)

    return result
    
curl_easy_cleanup = init_func(native, 'curl_easy_cleanup')

# curl_easy_duphandle
curl_easy_duphandle = init_func(native, 'curl_easy_duphandle', 
    errcheck=curl_easy_errcheck)

# curl_easy_escape
curl_easy_escape = init_func(native, 'curl_easy_escape', 
    errcheck=curl_easy_errcheck)

# curl_easy_getinfo
curl_easy_getinfo = init_func(native, 'curl_easy_getinfo',
    errcheck=curl_easy_errcheck)

# curl_easy_init
curl_easy_init = init_func(native, 'curl_easy_init',
    restype=ctypes.POINTER(ctypes.c_void_p), errcheck=curl_easy_errcheck)


# curl_easy_pause
curl_easy_pause = init_func(native, 'curl_easy_pause',
    errcheck=curl_easy_errcheck)

# curl_easy_perform
curl_easy_perform = init_func(native, 'curl_easy_perform',
    errcheck=curl_easy_errcheck)

# curl_easy_recv
curl_easy_recv = init_func(native, 'curl_easy_recv',
    errcheck=curl_easy_errcheck)


curl_easy_reset = init_func(native, 'curl_easy_reset')

# curl_easy_send
curl_easy_send = init_func(native, 'curl_easy_send',
    errcheck=curl_easy_errcheck)

# curl_easy_setopt
curl_easy_setopt = init_func(native, 'curl_easy_setopt',
    errcheck=curl_easy_errcheck)

# curl_easy_strerror
curl_easy_strerror = init_func(native, 'curl_easy_strerror',
    restype=ctypes.c_char_p)


# curl_easy_unescape
curl_easy_unescape = init_func(native, 'curl_easy_unescape',
    errcheck=curl_easy_errcheck)

#curl_escape (deprecated, do not use)
curl_formadd = init_func(native, 'curl_formadd')
curl_formfree = init_func(native, 'curl_formfree')
curl_formget = init_func(native, 'curl_formget')
curl_free = init_func(native, 'curl_free')

curl_getdate = init_func(native, 'curl_getdate')
#curl_getenv (deprecated, do not use)

curl_global_cleanup = init_func(native, 'curl_global_cleanup')
curl_global_init = init_func(native, 'curl_global_init')
curl_global_init_mem = init_func(native, 'curl_global_init_mem')

#curl_mprintf (deprecated, do not use)

def curl_multi_errcheck(result, func, args):
    from pylibcurl.exceptions import MultiError

    if (isinstance(result, int) and result not in (const.CURLM_OK, const.CURLM_CALL_MULTI_PERFORM)) or result is None:
        raise MultiError(result)

    return result
    

# curl_multi_add_handle
curl_multi_add_handle = init_func(native, 'curl_multi_add_handle',
    errcheck=curl_multi_errcheck)

# curl_multi_assign
curl_multi_assign = init_func(native, 'curl_multi_assign',
    errcheck=curl_multi_errcheck)

# curl_multi_cleanup
curl_multi_cleanup = init_func(native, 'curl_multi_cleanup',
    errcheck=curl_multi_errcheck)

# curl_multi_fdset
curl_multi_fdset = init_func(native, 'curl_multi_fdset',
    errcheck=curl_multi_errcheck)

class curl_msg(object):
    def __init__(self, msg):
        self.__msg = msg

    def __getattr__(self, name):
        return getattr(self.__msg, name)

    @property
    def easy_handle(self):
        return self.__msg.easy_handle.contents.value

    def __repr__(self):
        return super(curl_msg, self).__repr__()
        
# info_read
_curl_multi_info_read = init_func(native, 'curl_multi_info_read',
    restype=ctypes.POINTER(const.CURLMsg),
    errcheck=curl_multi_errcheck)

def curl_multi_info_read(handle):
    number = ctypes.c_int()
    msg = _curl_multi_info_read(handle, ctypes.byref(number))
    if msg:
        return curl_msg(msg.contents), number.value


# curl_multi_init
curl_multi_init = init_func(native, 'curl_multi_init',
    restype=ctypes.POINTER(ctypes.c_void_p),
    errcheck=curl_multi_errcheck)

# curl_multi_perform
curl_multi_perform = init_func(native, 'curl_multi_perform',
    errcheck=curl_multi_errcheck)

# curl_multi_remove_handle
curl_multi_remove_handle = init_func(native, 'curl_multi_remove_handle',
    errcheck=curl_multi_errcheck)

# curl_multi_setopt
curl_multi_setopt = init_func(native, 'curl_multi_setopt',
    errcheck=curl_multi_errcheck)

# curl_multi_socket_action
curl_multi_socket_action = init_func(native, 'curl_multi_socket_action',
    errcheck=curl_multi_errcheck)

curl_multi_strerror = init_func(native, 'curl_multi_strerror',
    restype=ctypes.c_char_p)

# curl_multi_timeout 
curl_multi_timeout = init_func(native, 'curl_multi_timeout',
    errcheck=curl_multi_errcheck)


# Share

def curl_share_errcheck(result, func, args):
    from pylibcurl.exceptions import ShareError

    if (isinstance(result, int) and result != const.CURLSHE_OK) or result is None:
        raise ShareError(result)
        
    return result

# curl_share_cleanup 
curl_share_cleanup = init_func(native, 'curl_share_cleanup',
    errcheck=curl_share_errcheck)

# curl_share_init
curl_share_init = init_func(native, 'curl_share_init',
    restype=ctypes.POINTER(ctypes.c_void_p),
    errcheck=curl_share_errcheck)

# curl_share_setopt
curl_share_setopt = init_func(native, 'curl_share_setopt',
    errcheck=curl_share_errcheck)

# curl_share_strerror
curl_share_strerror = init_func(native, 'curl_share_strerror',
    restype=ctypes.c_char_p)





curl_slist_append = init_func(native, 'curl_slist_append')
curl_slist_free_all = init_func(native, 'curl_slist_free_all')

#curl_strequal (deprecated, do not use)
#curl_strnequal (deprecated, do not use)
#curl_unescape (deprecated, do not use)



def slist2list(obj):
    _list = []

    while obj:
        if obj.data:
            _list.append(obj.data)
        try:
            obj = obj.next.contents
        except ValueError:
            break
        
    return _list


def list2slist(_list):
    slist = const.curl_slist()
    nlist = slist
    for i in xrange(len(_list)):
        nlist.data = _list[i]
        if i < len(_list) - 1:
            nlist.next = ctypes.pointer(const.curl_slist())
            nlist = nlist.next.contents

    return slist

def list2pointer_slist(_list):
    slist = None
    for v in _list:
        slist = native.curl_slist_append(slist, v)

    return slist

    


