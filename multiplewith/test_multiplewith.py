#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码
from collections import OrderedDict
from contextlib import contextmanager
from io import StringIO
import sys
import unittest
from multiplewith import MultipleWith


class test_context():
    log = StringIO()

    def __init__(self, name, init_exc_value=None, enter_exc_value=None, exit_exc_value=None, exit_return=False):
        self.name = name
        self.init_exc_value = init_exc_value
        self.enter_exc_value = enter_exc_value
        self.exit_exc_value = exit_exc_value
        self.exit_return = exit_return
        test_context.log.write(u'[%s]init\r\n' % self.name)
        if self.init_exc_value:
            raise self.init_exc_value

    def __enter__(self):
        test_context.log.write(u'[%s]enter\r\n' % self.name)
        if self.enter_exc_value:
            raise self.enter_exc_value
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        test_context.log.write(u'[%s]exit(%s,%s,%s)\r\n' % (self.name, exc_type, exc_val, exc_tb))
        if self.exit_return:
            return True
        if self.exit_exc_value:
            raise self.exit_exc_value


class MultipleWithTestCase(unittest.TestCase):
    def setUp(self):
        test_context.log = StringIO()

    def test_list(self):
        with MultipleWith(
                test_context(u'test1'),
                test_context(u'test2'),
                test_context(u'test3'),
                test_context(u'test4'),
        ) as contexts:
            self.assertEqual(test_context.log.getvalue(), u'[test1]init\r\n'
                                                          u'[test2]init\r\n'
                                                          u'[test3]init\r\n'
                                                          u'[test4]init\r\n'
                                                          u'[test1]enter\r\n'
                                                          u'[test2]enter\r\n'
                                                          u'[test3]enter\r\n'
                                                          u'[test4]enter\r\n')
            self.assertEqual(contexts[0].name, u'test1')
            self.assertEqual(contexts[1].name, u'test2')
            self.assertEqual(contexts[2].name, u'test3')
            self.assertEqual(contexts[3].name, u'test4')

        self.assertEqual(test_context.log.getvalue(), u'[test1]init\r\n'
                                                      u'[test2]init\r\n'
                                                      u'[test3]init\r\n'
                                                      u'[test4]init\r\n'
                                                      u'[test1]enter\r\n'
                                                      u'[test2]enter\r\n'
                                                      u'[test3]enter\r\n'
                                                      u'[test4]enter\r\n'
                                                      u'[test4]exit(None,None,None)\r\n'
                                                      u'[test3]exit(None,None,None)\r\n'
                                                      u'[test2]exit(None,None,None)\r\n'
                                                      u'[test1]exit(None,None,None)\r\n')

    def test_list_init_err(self):
        try:
            with MultipleWith(
                    test_context(u'test1'),
                    test_context(u'test2', init_exc_value=Exception('test2_init_exc')),
                    test_context(u'test3'),
                    test_context(u'test4'),
            ) as contexts:
                self.assertTrue(False)
        except:
            self.assertEqual(test_context.log.getvalue(), u'[test1]init\r\n[test2]init\r\n')
        else:
            self.assertTrue(False)

    def test_list_enter_err(self):
        try:
            with MultipleWith(
                    test_context(u'test1'),
                    test_context(u'test2', enter_exc_value=Exception('test2_enter_exc')),
                    test_context(u'test3'),
                    test_context(u'test4'),
            ) as contexts:
                self.assertTrue(False)
        except:
            self.assertIn(u"[test1]init\r\n"
                          u"[test2]init\r\n"
                          u"[test3]init\r\n"
                          u"[test4]init\r\n"
                          u"[test1]enter\r\n"
                          u"[test2]enter\r\n"
                          u"[test1]exit(<type 'exceptions.Exception'>,test2_enter_exc,<", test_context.log.getvalue())
        else:
            self.assertTrue(False)

    def test_list_enter_err2(self):
        try:
            with MultipleWith(
                    test_context(u'test1', exit_return=True),
                    test_context(u'test2', enter_exc_value=Exception('test2_enter_exc')),
                    test_context(u'test3'),
                    test_context(u'test4'),
            ) as contexts:
                self.assertTrue(False, u'test2 enter 时引发了异常，不应该在执行 with 块内的内容。')
        except Exception as e:
            self.assertTrue(False, u"test1 exit_return=True ,不应该在引发异常。但是这个问题目前想不到解决办法。")
        else:
            self.assertTrue(True)
        finally:
            log = test_context.log.getvalue()
            self.assertIn(u"[test1]init\r\n"
                          u"[test2]init\r\n"
                          u"[test3]init\r\n"
                          u"[test4]init\r\n"
                          u"[test1]enter\r\n"
                          u"[test2]enter\r\n"
                          u"[test1]exit(<type 'exceptions.Exception'>,test2_enter_exc,<", log)

    def test_list_exit_err(self):
        try:
            with MultipleWith(
                    test_context(u'test1'),
                    test_context(u'test2', exit_exc_value=Exception('test2_init_exc')),
                    test_context(u'test3'),
                    test_context(u'test4'),
            ) as contexts:
                test_context.log.write(u'with\r\n')
        except:
            log = test_context.log.getvalue()
            self.assertIn(u"[test1]init\r\n"
                          u"[test2]init\r\n"
                          u"[test3]init\r\n"
                          u"[test4]init\r\n"
                          u"[test1]enter\r\n"
                          u"[test2]enter\r\n"
                          u"[test3]enter\r\n"
                          u"[test4]enter\r\n"
                          u"with\r\n"
                          u"[test4]exit(None,None,None)\r\n"
                          u"[test3]exit(None,None,None)\r\n"
                          u"[test2]exit(None,None,None)\r\n"
                          u"[test1]exit(<type 'exceptions.Exception'>,test2_init_exc,", log)
        else:
            self.assertTrue(False)

    def test_list_exit_err2(self):
        try:
            with MultipleWith(
                    test_context(u'test1', exit_return=True),
                    test_context(u'test2', exit_exc_value=Exception('test2_init_exc')),
                    test_context(u'test3'),
                    test_context(u'test4'),
            ) as contexts:
                test_context.log.write(u'with\r\n')
        except:
            self.assertTrue(False, u'test1 存在 exit_return=True ,不应该引发异常')
        else:
            self.assertTrue(True)
        finally:
            log = test_context.log.getvalue()
            self.assertIn(u"[test1]init\r\n"
                          u"[test2]init\r\n"
                          u"[test3]init\r\n"
                          u"[test4]init\r\n"
                          u"[test1]enter\r\n"
                          u"[test2]enter\r\n"
                          u"[test3]enter\r\n"
                          u"[test4]enter\r\n"
                          u"with\r\n"
                          u"[test4]exit(None,None,None)\r\n"
                          u"[test3]exit(None,None,None)\r\n"
                          u"[test2]exit(None,None,None)\r\n"
                          u"[test1]exit(<type 'exceptions.Exception'>,test2_init_exc,", log)

    def test_list_exit_err3(self):
        try:
            with MultipleWith(
                    test_context(u'test1', exit_return=True),
                    test_context(u'test2', exit_exc_value=Exception('test2_init_exc')),
                    test_context(u'test3'),
                    test_context(u'test4', exit_exc_value=Exception('test4_init_exc')),
            ) as contexts:
                test_context.log.write(u'with\r\n')
        except:
            self.assertTrue(False, u'test1 存在 exit_return=True ,不应该引发异常')
        else:
            self.assertTrue(True)
        finally:
            log = test_context.log.getvalue()
            self.assertIn(u"[test1]init\r\n"
                          u"[test2]init\r\n"
                          u"[test3]init\r\n"
                          u"[test4]init\r\n"
                          u"[test1]enter\r\n"
                          u"[test2]enter\r\n"
                          u"[test3]enter\r\n"
                          u"[test4]enter\r\n"
                          u"with\r\n"
                          u"[test4]exit(None,None,None)\r\n", log)

            self.assertIn(u"[test3]exit(<type 'exceptions.Exception'>,test4_init_exc", log)
            self.assertIn(u"[test2]exit(<type 'exceptions.Exception'>,test4_init_exc", log)
            self.assertIn(u"[test1]exit(<type 'exceptions.Exception'>,test2_init_exc", log)

    def test_dict(self):
        with MultipleWith(
                ('test1', test_context(u'test1')),
                ('test2', test_context(u'test2')),
                ('test3', test_context(u'test3')),
                ('test4', test_context(u'test4')),
        ) as contexts:
            self.assertEqual(test_context.log.getvalue(), u'[test1]init\r\n'
                                                          u'[test2]init\r\n'
                                                          u'[test3]init\r\n'
                                                          u'[test4]init\r\n'
                                                          u'[test1]enter\r\n'
                                                          u'[test2]enter\r\n'
                                                          u'[test3]enter\r\n'
                                                          u'[test4]enter\r\n')
            self.assertEqual(contexts['test1'].name, u'test1')
            self.assertEqual(contexts['test2'].name, u'test2')
            self.assertEqual(contexts['test3'].name, u'test3')
            self.assertEqual(contexts['test4'].name, u'test4')

        self.assertEqual(test_context.log.getvalue(), u'[test1]init\r\n'
                                                      u'[test2]init\r\n'
                                                      u'[test3]init\r\n'
                                                      u'[test4]init\r\n'
                                                      u'[test1]enter\r\n'
                                                      u'[test2]enter\r\n'
                                                      u'[test3]enter\r\n'
                                                      u'[test4]enter\r\n'
                                                      u'[test4]exit(None,None,None)\r\n'
                                                      u'[test3]exit(None,None,None)\r\n'
                                                      u'[test2]exit(None,None,None)\r\n'
                                                      u'[test1]exit(None,None,None)\r\n')

    def test_dict2(self):
        with MultipleWith(
                test1=test_context(u'test1'),
                test2=test_context(u'test2'),
                test3=test_context(u'test3'),
                test4=test_context(u'test4'),
        ):
            log = test_context.log.getvalue()
            self.assertIn(u'[test1]init\r\n', log)
            self.assertIn(u'[test2]init\r\n', log)
            self.assertIn(u'[test3]init\r\n', log)
            self.assertIn(u'[test4]init\r\n', log)

            self.assertIn(u'[test1]enter\r\n', log)
            self.assertIn(u'[test2]enter\r\n', log)
            self.assertIn(u'[test3]enter\r\n', log)
            self.assertIn(u'[test4]enter\r\n', log)

            self.assertNotIn(u'[test4]exit', log)
            self.assertNotIn(u'[test3]exit', log)
            self.assertNotIn(u'[test2]exit', log)
            self.assertNotIn(u'[test1]exit', log)

        log = test_context.log.getvalue()
        self.assertIn(u'[test4]exit', log)
        self.assertIn(u'[test3]exit', log)
        self.assertIn(u'[test2]exit', log)
        self.assertIn(u'[test1]exit', log)

    def test_dict_err(self):
        enter_list = []

        try:
            with MultipleWith(
                    test1=test_context(u'test1'),
                    test2=test_context(u'test2'),
                    test3=test_context(u'test3', enter_exc_value=Exception(u'test3_enter_exc_value')),
                    test4=test_context(u'test4'),
            ):
                log = test_context.log.getvalue()
                self.assertIn(u'[test1]init\r\n', log)
                self.assertIn(u'[test2]init\r\n', log)
                self.assertIn(u'[test3]init\r\n', log)
                self.assertIn(u'[test4]init\r\n', log)

                for i in range(1, 5):
                    if u'[test%s]enter\r\n' % i in log:
                        enter_list.append('test%s' % i)

                self.assertNotIn(u'exit', log)
        except:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
        finally:
            log = test_context.log.getvalue()
            for enter in enter_list:
                self.assertIn(u'[%s]exit' % enter)


if __name__ == "__main__":
    unittest.main()
