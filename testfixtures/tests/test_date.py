#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\testfixtures\tests\test_date.py
from datetime import date as d
from time import strptime
from testfixtures import ShouldRaise, test_date, replace, compare
from testfixtures.tests import sample1, sample2
from unittest import TestCase

class TestDate(TestCase):

    @replace('datetime.date', test_date())
    def test_today(self):
        from datetime import date
        compare(date.today(), d(2001, 1, 1))
        compare(date.today(), d(2001, 1, 2))
        compare(date.today(), d(2001, 1, 4))

    @replace('datetime.date', test_date(2001, 2, 3))
    def test_today_supplied(self):
        from datetime import date
        compare(date.today(), d(2001, 2, 3))

    @replace('datetime.date', test_date(year=2001, month=2, day=3))
    def test_today_all_kw(self):
        from datetime import date
        compare(date.today(), d(2001, 2, 3))

    @replace('datetime.date', test_date(None))
    def test_today_sequence(self, t):
        t.add(2002, 1, 1)
        t.add(2002, 1, 2)
        t.add(2002, 1, 3)
        from datetime import date
        compare(date.today(), d(2002, 1, 1))
        compare(date.today(), d(2002, 1, 2))
        compare(date.today(), d(2002, 1, 3))

    @replace('datetime.date', test_date(None))
    def test_today_requested_longer_than_supplied(self, t):
        t.add(2002, 1, 1)
        t.add(2002, 1, 2)
        from datetime import date
        compare(date.today(), d(2002, 1, 1))
        compare(date.today(), d(2002, 1, 2))
        compare(date.today(), d(2002, 1, 3))
        compare(date.today(), d(2002, 1, 5))

    @replace('datetime.date', test_date(None))
    def test_add_date_supplied(self):
        from datetime import date
        date.add(d(2001, 1, 2))
        date.add(date(2001, 1, 3))
        compare(date.today(), d(2001, 1, 2))
        compare(date.today(), d(2001, 1, 3))

    @replace('datetime.date', test_date(strict=True))
    def test_call(self, t):
        compare(t(2002, 1, 2), d(2002, 1, 2))
        from datetime import date
        dt = date(2003, 2, 1)
        self.failIf(dt.__class__ is d)
        compare(dt, d(2003, 2, 1))

    def test_gotcha_import(self):

        @replace('datetime.date', test_date())
        def test_something():
            from datetime import date
            compare(date.today(), d(2001, 1, 1))
            compare(sample1.str_today_1(), '2001-01-02')

        with ShouldRaise(AssertionError) as s:
            test_something()
        j, dt1, j, dt2, j = s.raised.args[0].split("'")
        dt1 = strptime(dt1, '%Y-%m-%d')
        compare(dt2, '2001-01-02')

        @replace('testfixtures.tests.sample1.date', test_date())
        def test_something():
            compare(sample1.str_today_1(), '2001-01-01')

        test_something()

    def test_gotcha_import_and_obtain(self):

        @replace('testfixtures.tests.sample1.date', test_date())
        def test_something():
            compare(sample1.str_today_2(), '2001-01-01')

        with ShouldRaise(AssertionError) as s:
            test_something()
        j, dt1, j, dt2, j = s.raised.args[0].split("'")
        dt1 = strptime(dt1, '%Y-%m-%d')
        compare(dt2, '2001-01-01')

        @replace('testfixtures.tests.sample1.today', test_date().today)
        def test_something():
            compare(sample1.str_today_2(), '2001-01-01')

        test_something()

    def test_import_and_obtain_with_lists(self):
        t = test_date(None)
        t.add(2002, 1, 1)
        t.add(2002, 1, 2)
        from testfixtures import Replacer
        r = Replacer()
        r.replace('testfixtures.tests.sample1.today', t.today)
        try:
            compare(sample1.str_today_2(), '2002-01-01')
            compare(sample1.str_today_2(), '2002-01-02')
        finally:
            r.restore()

    @replace('datetime.date', test_date())
    def test_repr(self):
        from datetime import date
        compare(repr(date), "<class 'testfixtures.tdatetime.tdate'>")

    @replace('datetime.date', test_date(delta=2))
    def test_delta(self):
        from datetime import date
        compare(date.today(), d(2001, 1, 1))
        compare(date.today(), d(2001, 1, 3))
        compare(date.today(), d(2001, 1, 5))

    @replace('datetime.date', test_date(delta_type='weeks'))
    def test_delta_type(self):
        from datetime import date
        compare(date.today(), d(2001, 1, 1))
        compare(date.today(), d(2001, 1, 8))
        compare(date.today(), d(2001, 1, 22))

    @replace('datetime.date', test_date(None))
    def test_set(self):
        from datetime import date
        date.set(2001, 1, 2)
        compare(date.today(), d(2001, 1, 2))
        date.set(2002, 1, 1)
        compare(date.today(), d(2002, 1, 1))
        compare(date.today(), d(2002, 1, 3))

    @replace('datetime.date', test_date(None))
    def test_set_date_supplied(self):
        from datetime import date
        date.set(d(2001, 1, 2))
        compare(date.today(), d(2001, 1, 2))
        date.set(date(2001, 1, 3))
        compare(date.today(), d(2001, 1, 3))

    @replace('datetime.date', test_date(None))
    def test_set_kw(self):
        from datetime import date
        date.set(year=2001, month=1, day=2)
        compare(date.today(), d(2001, 1, 2))

    @replace('datetime.date', test_date(None))
    def test_add_kw(self, t):
        t.add(year=2002, month=1, day=1)
        from datetime import date
        compare(date.today(), d(2002, 1, 1))

    @replace('datetime.date', test_date(strict=True))
    def test_isinstance_strict_true(self):
        from datetime import date
        to_check = []
        to_check.append(date(1999, 1, 1))
        to_check.append(date.today())
        date.set(2001, 1, 2)
        to_check.append(date.today())
        date.add(2001, 1, 3)
        to_check.append(date.today())
        to_check.append(date.today())
        date.set(date(2001, 1, 4))
        to_check.append(date.today())
        date.add(date(2001, 1, 5))
        to_check.append(date.today())
        to_check.append(date.today())
        date.set(d(2001, 1, 4))
        to_check.append(date.today())
        date.add(d(2001, 1, 5))
        to_check.append(date.today())
        to_check.append(date.today())
        for inst in to_check:
            self.failUnless(isinstance(inst, date), inst)
            self.failUnless(inst.__class__ is date, inst)
            self.failUnless(isinstance(inst, d), inst)
            self.failIf(inst.__class__ is d, inst)

    @replace('datetime.date', test_date())
    def test_isinstance_default(self):
        from datetime import date
        to_check = []
        to_check.append(date(1999, 1, 1))
        to_check.append(date.today())
        date.set(2001, 1, 2)
        to_check.append(date.today())
        date.add(2001, 1, 3)
        to_check.append(date.today())
        to_check.append(date.today())
        date.set(date(2001, 1, 4))
        to_check.append(date.today())
        date.add(date(2001, 1, 5))
        to_check.append(date.today())
        to_check.append(date.today())
        date.set(d(2001, 1, 4))
        to_check.append(date.today())
        date.add(d(2001, 1, 5))
        to_check.append(date.today())
        to_check.append(date.today())
        for inst in to_check:
            self.failIf(isinstance(inst, date), inst)
            self.failIf(inst.__class__ is date, inst)
            self.failUnless(isinstance(inst, d), inst)
            self.failUnless(inst.__class__ is d, inst)
