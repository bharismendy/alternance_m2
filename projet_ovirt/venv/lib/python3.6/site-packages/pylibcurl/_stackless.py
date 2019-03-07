#coding:utf8

import stackless
import select
import time
import curl, multi, share, const, exceptions


_ch = stackless.channel()
_ch.preference = -1
_tasklet = None

def start(kill=False, *args, **kwargs):
    global _tasklet
    if not _tasklet or kill:
        try:
            _tasklet.kill()
        except:
            pass
        _tasklet = stackless.tasklet(run)(*args, **kwargs)

def run(maxconnects=10, select_timeout=0):
    sockets = set()

    def _socket_cb(socket, event):
        #print 'socket: ', socket, 'event: ', event
        if event == const.CURL_POLL_REMOVE:
            sockets.remove(socket)
        else:
            sockets.add(socket)

    m = multi.Multi(
        socketfunction=_socket_cb, 
        maxconnects=maxconnects,
        #pipelining=1
    )
    
    running = 0
    while 1:
        if not running:
            #print 'wait curl'
            #print 'multi channel balance: %s' % _ch.balance
            m.add_handle(_ch.receive()) # block until send
            #print 'add curl'

        # non blocking channel
        while len(m._handles) < maxconnects and _ch.balance > 0:
            #print 'multi channel balance: %s' % _ch.balance
            m.add_handle(_ch.receive())
            #print 'add curl'

        if not running:
            code, running = m.socket_action(const.CURL_SOCKET_TIMEOUT, 0)
        else:
            r, w, e = select.select(sockets, sockets, sockets, select_timeout)
            for socks in [r, w, e]:
                if socks == r:
                    event = const.CURL_CSELECT_IN
                elif socks == w:
                    event = const.CURL_CSELECT_OUT
                else:
                    event = const.CURL_CSELECT_ERR

                for s in socks:
                    code = const.CURLM_CALL_MULTI_SOCKET
                    while code == const.CURLM_CALL_MULTI_SOCKET:
                        code, running = m.socket_action(s, event)
            
            while 1:
                info = m.info_read()
                if info:
                    curl = info[0].easy_handle
                    code = info[0].data.result
                    m.remove_handle(curl)
                    #print 'count in queue msg: %s' % info[1]
                    #print 'curl channel balance: %s' % curl._channel.balance
                    #print 'send msg to %s' % curl
                    if code != const.CURLE_OK:
                        curl._channel.send_exception(exceptions.CurlError, code)
                    else:
                        curl._channel.send(1) # unblock
                else:
                    break

        if stackless.getruncount() > 1:
            stackless.schedule() # switch
        else:
            time.sleep(0.01)


class Curl(curl.Curl):

    def perform(self):
        start() # start multi curl if not started
        self._channel = stackless.channel()
        self._channel.preference = 1
        _ch.send(self)
        self._channel.receive() # block until request complete or exception on this curl



