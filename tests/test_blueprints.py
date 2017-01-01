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

from django_rest_secureview.view_rules import *
from . mocks import MockRequest, MockModelManager

class ViewRulesTest(unittest.TestCase):

    def test_it_can_compare_param_keys(self):
        """
        Confirms that the params in the POST request match
        the specified params for the endpoint
        """
        request = MockRequest(QueryDict('dog=1&cat=2'))
        view_rule = Params([request], None)
        
        check_1 = view_rule.errors_found({'params':['cat', 'dog']})
        check_2 = view_rule.errors_found({'params':['cat', 'mouse']})

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

        view_rule_1 = Owner([request_1], {'pk':1})
        view_rule_2 = Owner([request_2], {'pk':1})

        check_1 = view_rule_1.errors_found({'model': model})
        check_2 = view_rule_2.errors_found({'model': model})

        self.assertFalse(check_1[0])
        self.assertEqual(check_2[1].data['detail'], 'Unauthorized access')

    def test_it_can_check_model_relations_and_params(self):
        """
        Confirms Owner and Params logic are called together
        """
        request = MockRequest(QueryDict('dog=1&cat=2'))
        model = MockModelManager()
        view_rule = OwnerParams([request], {'pk':1})
        view_rule.enforce_params = MagicMock(return_value=None)
        view_rule.enforce_owner = MagicMock(return_value=None)
        
        params = {'model': model, 'params':['cat', 'dog']}
        check = view_rule.errors_found(params)

        view_rule.enforce_params.assert_called_with(params)
        view_rule.enforce_owner.assert_called_with(params)
        self.assertFalse(check[0])

    def test_it_can_raise_value_error_for_response(self):
        """
        Custom implementations of ViewRule.enforce should return a Response
        type object or None.
        """
        class CustomRule(ViewRule):
            def enforce(self, params=None):
                return 1

        request = MockRequest()
        view_rule = CustomRule([request], {'pk':2})
        with self.assertRaises(ValueError):
            view_rule.errors_found()

if __name__ == '__main__':
    unittest.main()





