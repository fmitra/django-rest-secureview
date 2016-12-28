"""
Blueprints impose specific API conditons via their enforce method.
A Blueprint's goal is to ensure a User meets specific conditions 
when accessing an API endpoint (ex. were POST params submitted in 
the request?). If the conditions were not properly met, they should
return a failing HTTP status code. 

We can think of Blueprints as "Error Blueprints" because they only
return if the conditions were not met. If a Blueprint does not return,
we can expect that all conditions were met and the User may be 
transitioned to the ViewSet
"""
import abc
import six

from rest_framework import status
from rest_framework.response import Response


@six.add_metaclass(abc.ABCMeta)
class ErrorBlueprint(object):
    """
    Blueprint template for internal third party extenion.

    Imposes API restrictions prior to accessing a ViewSet via the
    enforce method.
    """
    http_status = status
    response = Response
    error_status = False

    def __init__(self, request_args, request_kwargs=None):
        """
        Ensures all inheriting classes have access to parameters
        passed via the HTTP Request such as POST parameters, model
        pk value, and User authentication information
        """
        self.request = request_args[0].request
        self.pk = request_kwargs

    @abc.abstractmethod
    def enforce(self, params=None):
        """
        Enforce specific conditions on an API endpoint. If conditions are
        not met, it will return a failing HTTP status code (ex. 401)

        :param params: User defined params to check for failing conditions
        :type params: dict
        :returns: Failing (400, 401, 404) Response object if conditions are not met
        :rtype: Response
        """
        pass

    def errors_found(self, params=None):
        """
        Returns a Response object with a failing HTTP status code (ex. 401)
        if API conditions were not met by the User.
        """
        error_status = self.enforce(params)
        return error_status


class Params(ErrorBlueprint):
    """ 
    Require specific POST params to be submitted in requests
    """
    def enforce_params(self, params):
        """
        :param params: List of expected POST params
        :type params: dict['params'] = list()
        """
        missing_keys = []
        valid_keys = params['params']
        submitted_keys = self.request.data.keys()
        for key in valid_keys:
            if key not in submitted_keys:
                missing_keys.append(key)

        if any(missing_keys):
            all_errors = 'Missing keys '+', '.join(missing_keys)
            data = {'detail':all_errors}
            code = self.http_status.HTTP_400_BAD_REQUEST
            return self.response(data=data, status=code)

    def enforce(self, params):
        return self.enforce_params(params)


class Owner(ErrorBlueprint):
    """
    Requires authenticated User to have a foreign key relationship
    with the requested model instance
    """
    def enforce_owner(self, params):
        """
        :param params: Model affiliated with User
        :type params: dict['model'] = Model
        """
        try:
            model = params['model'].objects.get(id=self.pk['pk'])
        except model.DoesNotExist:
            return self.response(data={'detail':'Not found'}, 
                                 status=self.http_status.HTTP_404_NOT_FOUND)

        code = self.http_status.HTTP_401_UNAUTHORIZED
        user = self.request.user
        data = {'detail': 'Unauthorized access'}
        if not user.is_authenticated():
            return self.response(data=data, status=code)

        test_attrs = [f.name for f in model._meta.get_fields()]
        model_attrs = [getattr(model, f.name, None) for f in model._meta.get_fields()]
        if user not in model_attrs:
            return self.response(data=data, status=code)

    def enforce(self, params):
        return self.enforce_owner(params)


class OwnerParams(Params, Owner):
    """
    Requires authenticated User to have a foreign key relationship with 
    the requested model instance and specific POST params to be submitted
    in the reqeust
    """
    def enforce(self, params):
        param_check = self.enforce_params(params)
        if param_check: return param_check

        owner_check = self.enforce_owner(params)
        if owner_check: return owner_check

