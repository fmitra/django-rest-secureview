# py27 vs py34 compatibility 
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

import unittest

from django.http import QueryDict
from django.conf import settings

# We need to configure Django settings before importing SecureView
# because we are running this test set outside of Django
try:
    settings.configure()
except RuntimeError:
    pass

from django_rest_secureview.view_rules import Params, Owner, OwnerParams
from . mocks import MockRequest, MockModelManager

class ViewRulesTest(unittest.TestCase):

    def test_it_can_compare_param_keys(self):
        """
        Confirms that the params in the POST request match
        the specified params for the endpoint
        """
        request = MockRequest(QueryDict('dog=1&cat=2'))
        blueprint = Params([request], None)
        
        check_1 = blueprint.errors_found({'params':['cat', 'dog']})
        check_2 = blueprint.errors_found({'params':['cat', 'mouse']})

        self.assertFalse(check_1[0])
        self.assertEqual(check_2[1].data['detail'], 'Missing keys mouse')

    def test_it_can_check_model_relations(self):
        """
        Confirms that User is present in one of the Model's attributes
        """
        NewUser = MagicMock()
        request_1 = MockRequest()
        request_2 = MockRequest(user=NewUser)
        model = MockModelManager()

        blueprint_1 = Owner([request_1], {'pk':1})
        blueprint_2 = Owner([request_2], {'pk':1})

        check_1 = blueprint_1.errors_found({'model': model})
        check_2 = blueprint_2.errors_found({'model': model})

        self.assertFalse(check_1[0])
        self.assertEqual(check_2[1].data['detail'], 'Unauthorized access')

    def test_it_can_check_model_relations_and_params(self):
        """
        Confirms Owner and Params logic are called together
        """
        request = MockRequest(QueryDict('dog=1&cat=2'))
        model = MockModelManager()
        blueprint = OwnerParams([request], {'pk':1})
        blueprint.enforce_params = MagicMock(return_value=None)
        blueprint.enforce_owner = MagicMock(return_value=None)
        
        params = {'model': model, 'params':['cat', 'dog']}
        check = blueprint.errors_found(params)

        blueprint.enforce_params.assert_called_with(params)
        blueprint.enforce_owner.assert_called_with(params)
        self.assertFalse(check[0])


if __name__ == '__main__':
    unittest.main()





