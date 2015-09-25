#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码
import sys
from collections import OrderedDict



class MultipleWith:
    def __init__(self,*args,**kwargs):
        u""" 可以接受的类型

        # 可以保证顺序，前面的处于外侧，后面的处于内测。
        with multiplewith(open('/path1','wb'),open('/path2','wb')) as file_list:
            file_list[1].write(file_list[0].read())

        # 由于 python dict 限制，无法保证顺序。
        with multiplewith(file1=open('/path1','wb'),file2=open('/path2','wb')) as file_dict:
            file_dict['file1'].write(file_dict.file2.read())

        ordered_dict = OrderedDict((
                                    ('A', 1),
                                    ('B', 2),
                                    ('C', 3)
                                    ))
        # OrderedDict 的用法，可保证顺序。
        with multiplewith(ordered_dict.items()):
            file_dict['file1'].write(file_dict.file2.read())

        # 效果同上，可以保证顺序
        with multiplewith(('file1',open('/path1','wb')),('file2',open('/path2','wb'))):
            file_dict['file1'].write(file_dict.file2.read())
        """
        if args and not kwargs:
            if isinstance(args[0],(list,tuple)):
                kwargs = OrderedDict(args)
                args = None
            else:
                self._contexts = []
                for c in args:
                    self._contexts.append(c)
                return
        if not args and kwargs:
            if isinstance(kwargs,OrderedDict):
                self._contexts = kwargs
            else:
                self._contexts = OrderedDict(kwargs)
        else:
            raise ValueError()

    def __enter__(self):
        u""" 进入 with 块 """
        self.__exit_list = []
        exc_type, exc_val, exc_tb = None,None,None

        if isinstance(self._contexts,(list,tuple)):
            # list 类型
            res = []
            for c in self._contexts:
                try:
                    t = c.__enter__()
                except:
                    # 如果出现异常，那么反向调用 __exit__
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    self.__exit(exc_type, exc_value, exc_traceback,True)
                    #TODO: 正常 with嵌套这里应该是直接退出 with 块，并且异常被捕获并抛弃了。
                    #TODO: 但是目前没有想到什么办法可以不引发异常退出 with 块。
                    raise Exception()

                self.__exit_list.append(c)
                res.append(t)
            return res

        elif isinstance(self._contexts,(dict,OrderedDict)):
            # dict
            res = {}
            for k,v in self._contexts.iteritems():
                try:
                    t = v.__enter__()
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    self.__exit(exc_type, exc_value, exc_traceback,True)
                    #TODO: 正常 with嵌套这里应该是直接退出 with 块，并且异常被捕获并抛弃了。
                    #TODO: 但是目前没有想到什么办法可以不引发异常退出 with 块。
                    raise Exception()

                self.__exit_list.append(v)
                res[k]=t
            return res

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.__exit(exc_type, exc_val, exc_tb,False)


    def __exit(self, exc_type, exc_val, exc_tb,is_raise):
        u""" 反向 exit

    is_raise 是否抛出异常(如果是 __exit__ 引发的异常，会强制抛出)
          """
        #  python 2 exit 抛出异常会被丢弃，python 3 会正常抛出with块。
        self.__exit_list.reverse()

        for _exit in self.__exit_list:
            res = False
            try:
                res = _exit.__exit__(exc_type, exc_val, exc_tb)
            except:
                is_raise = True
                _exc_type, _exc_val, _exc_traceback = sys.exc_info()
                _exc_val.__context__ = exc_val

                exc_type, exc_val, exc_tb = _exc_type, _exc_val, _exc_traceback
            if res:
                exc_type, exc_val, exc_tb = None,None,None

        if exc_val:
            if is_raise:
                raise exc_val
            else:
                return False
        else:
            return True

