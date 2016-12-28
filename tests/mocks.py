# py27 vs py34 compatibility 
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


MockUser = MagicMock()
MockUser.is_authenticated = MagicMock(return_value=True)

class MockModelAttr(object):
    def __init__(self, attr, value):
        self._name = attr
        self.attr = value

    @property
    def name(self):
        return self._name


class MockModel(object):
    """ Model should have an attribute referencing the User """
    _attr_1 = MockModelAttr('attr_1', 2)
    _attr_2 = MockModelAttr('attr_2', "Harry Potter")
    _attr_3 = MockModelAttr('attr_3', "Fiction")
    _attr_4 = MockModelAttr('attr_4', MockUser)

    _meta = MagicMock()
    _meta.get_fields = MagicMock(return_value=[_attr_1, _attr_2, _attr_3, _attr_4])

    attr_1 = _attr_1.attr
    attr_2 = _attr_2.attr
    attr_3 = _attr_3.attr
    attr_4 = _attr_4.attr


class MockModelManager(object):
    objects = MagicMock()
    objects.get = MagicMock(return_value=MockModel)


class MockRequest(object):
    """ Request objects are expected to contain user and data attributes """
    def __init__(self, data=None, user=MockUser):
        self.request = MagicMock()
        self.request.user = user
        if data is not None:
            self.request.data = data


class MockView(object):
    """ DJRF ViewSets take a request param and an optional pk param """
    def list_view(self, request):
        pass

    def retrieve_view(self, request, pk):
        pass

        