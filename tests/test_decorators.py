import unittest

from django.http import QueryDict
from django.conf import settings

# We need to configure Django settings before importing SecureView
# because we are running this test set outside of Django
try:
    settings.configure()
except RuntimeError:
    pass

from django_rest_secureview.decorators import require
from django_rest_secureview.view_rules import Params, Owner, OwnerParams
from . mocks import * 


class DecoratorsTest(unittest.TestCase):

    def test_it_should_require_user_defiend_params(self):
        """
        Request object should contain specific params
        to go through. If params are not provided, a Response
        object is returned
        """
        view = MockView().list_view
        request = MockRequest(QueryDict('dog=1&cat=2'))

        response_1 = require(Params, params=['dog', 'cat'])(view)(request)
        response_2 = require(Params, params=['dog', 'mouse'])(view)(request)

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

        response_1 = require(Owner, model=model)(view)(request_1, pk=1)
        # This should fail because a new user is being associated with the request
        response_2 = require(Owner, model=model)(view)(request_2, pk=1)

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

        response_1 = require(OwnerParams, 
                             model=model, 
                             params=['cat', 'dog'])(view)(request_1, pk=1)
        
        response_2 = require(OwnerParams, 
                             model=model, 
                             params=['cat', 'dog'])(view)(request_2, pk=1)

        response_3 = require(OwnerParams, 
                             model=model, 
                             params=['cat', 'dog'])(view)(request_3, pk=1)

        self.assertIsNone(response_1)
        self.assertEqual(response_2.data, {"detail":"Missing keys cat, dog"})
        self.assertEqual(response_3.data, {"detail":"Unauthorized access"})


if __name__ == '__main__':
    unittest.main()
