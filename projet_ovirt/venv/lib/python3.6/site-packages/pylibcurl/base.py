# coding: utf-8
#
import ctypes
import weakref

_registry = weakref.WeakValueDictionary()

def _key(obj):
    return ctypes.addressof(obj.contents)

class Meta(type):
    
    def __call__(cls, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], cls._pointer_type):
            key = _key(args[0])
            obj = _registry[key]
        else:
            obj = cls.__new__(cls, *args, **kwargs)
            if getattr(obj, '__class__', None) == cls:
                obj._handle = cls._lib_init_func()
                key = _key(obj._handle)
                _registry[key] = obj
                obj.__init__(*args, **kwargs)
            
        return obj

class Base(object):
    __metaclass__ = Meta

    def __hash__(self):
        return ctypes.addressof(self._handle.contents)


    def __eq__(self, other):
        return self.__class__ == other.__class__ and hash(self) == hash(other)
    
    def __del__(self):
        if getattr(self, 'close', None):
            self.close()

    def close(self):
        if self._handle:
            self._clear()
            self._lib_cleanup_func(self._handle)
            self._handle = None

        

