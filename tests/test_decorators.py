import unittest

# py27 vs py34 compatibility 
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from django.http import QueryDict
from django.conf import settings

# We need to configure Django settings before importing SecureView
# because we are running this test set outside of Django
settings.configure()
from django_rest_secureview.decorators import *


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


class SecureViewTest(unittest.TestCase):

    def test_it_should_require_user_defiend_params(self):
        """
        Request object should contain specific params
        to go through. If params are not provided, a Response
        object is returned
        """
        view = MockView().list_view
        request = MockRequest(QueryDict('dog=1&cat=2'))

        response_1 = require_params(params=['dog', 'cat'])(view)(request)
        response_2 = require_params(params=['dog', 'mouse'])(view)(request)

        self.assertIsNone(response_1)
        self.assertEqual("Response", response_2.__class__.__name__)
        self.assertEqual(response_2.data, {"detail": "Missing keys mouse"})

    def test_it_should_require_foreignkey_between_user_and_model(self):
        """
        Request object should contain an authenticated User and a 
        model. If a foregin key relation is not available between
        the User and the model, a Response object is returned
        """
        NewUser = MagicMock()
        view = MockView().retrieve_view
        request_1 = MockRequest()
        request_2 = MockRequest(user=NewUser)

        model = MockModelManager()

        response_1 = require_owner(model=model)(view)(request_1, pk=1)
        # This should fail because a new user is being associated with the request
        response_2 = require_owner(model=model)(view)(request_2, pk=1)

        self.assertIsNone(response_1)
        self.assertEqual(response_2.__class__.__name__, "Response")
        self.assertEqual(response_2.data, {"detail":"Unauthorized access"})

    def test_it_should_require_foreignkey_relation_and_params(self):
        """
        Request object should contain both an authenticated User 
        and a model, as well as a list of user supplied params
        """
        NewUser = MagicMock()
        view = MockView().retrieve_view
        request_1 = MockRequest(QueryDict('dog=1&cat=2'))
        request_2 = MockRequest(QueryDict('mouse=1&rabbit=2'))
        request_3 = MockRequest(data=QueryDict('dog=1&cat=2'), user=NewUser)
        model = MockModelManager()

        response_1 = (require_owner_with_params(model=model, 
                                                params=['dog', 'cat'])
                                                (view)(request_1, pk=1))

        response_2 = (require_owner_with_params(model=model, 
                                                params=['dog', 'cat'])
                                                (view)(request_2, pk=1))

        response_3 = (require_owner_with_params(model=model, 
                                                params=['dog', 'cat'])
                                                (view)(request_3, pk=1))
        self.assertIsNone(response_1)
        self.assertEqual(response_2.data, {"detail":"Missing keys dog, cat"})
        self.assertEqual(response_3.data, {"detail":"Unauthorized access"})


if __name__ == '__main__':
    unittest.main()
