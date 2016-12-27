""" 
Enforce API requirements
"""

from functools import wraps

from rest_framework import status
from rest_framework.response import Response


class FailCheck(object):
    """
    Determines whether API conditions were met prior to accessing
    a ViewSet. 
    
    Returns a failing Response object if conditions are not met
    (ex. 401, 400 status). If conditions are met, it will return
    a boolean, False, indicating there are no failures. 
    """
    @classmethod
    def enforce_params(cls, keys, func_args, func_kwargs):
        """ 
        Require specific params to be submitted in POST requests 
        
        :param keys: Valid keys to compare against POST submissions
        :type keys: list
        :returns: False if conditions are met or failing (400, 401, 404) Response object
        :rtype: False
        :rtype: Response
        """
        missing_keys = []
        valid_keys = keys
        # Check the request object from the decorated viewset
        # for POST params
        submitted_keys = func_args[0].request.data.keys()
        for key in valid_keys:
            if key not in submitted_keys:
                missing_keys.append(key)

        if any(missing_keys):
            all_errors = 'Missing keys '+', '.join(missing_keys)
            data = {'detail':all_errors}
            code = status.HTTP_400_BAD_REQUEST
            return Response(data=data, status=code)
        else:
            return False

    @classmethod
    def enforce_owner(cls, model, func_args, func_kwargs):
        """ 
        Requires authenticated User to have a ForeignKey relationship
        with the requested model instance 

        :param model: Model instance to query to confirm User ownership
        :type model: Model
        :returns: False if conditions are met or failing (400, 401, 404) Response object
        :rtype: False
        :rtype: Response
        """
        try:
            model = model.objects.get(id=func_kwargs['pk'])
        except model.DoesNotExist:
            return Response(data={'detail':'Not found'}, status=status.HTTP_404_NOT_FOUND)

        code = status.HTTP_401_UNAUTHORIZED
        data = {'detail': 'Unauthorized access'}
        user = func_args[0].request.user
        if not user.is_authenticated():
            return Response(data=data, status=code)

        test_attrs = [f.name for f in model._meta.get_fields()]
        model_attrs = [getattr(model, f.name, None) for f in model._meta.get_fields()]
        if user not in model_attrs:
            return Response(data=data, status=code)

        return False


def require_params(params):
    """ 
    Decorator method used to enforce POST param requirements
    
    :param params: Valid paramss to compare against POST submissions
    :type params: list
    :returns: (400, 401, 404) Response object if conditions are not met
    :rtype: Response
    """
    def wrapper(func):
        @wraps(func)
        def require(*args, **kwargs):
            failed = FailCheck.enforce_params(params, args, kwargs)
            if failed: return failed
            return func(*args, **kwargs)
        return require
    return wrapper

def require_owner(model):
    """ 
    Decorator method used to enforce a foreign key relationship
    between a model and an authenticated User

    :param model: model instance to query to confirm User ownership
    :type model: Model
    :returns: (400, 401, 404) Response object if conditions are not met
    :rtype: Response
    """
    def wrapper(func):
        @wraps(func)
        def require(*args, **kwargs):
            # Ensure user is super user or author of the model
            if 'pk' in kwargs:
                failed = FailCheck.enforce_owner(model, args, kwargs)
                if failed: return failed
            return func(*args, **kwargs)
        return require
    return wrapper

def require_owner_with_params(model, params):
    """
    Decorator method used to enforce POST param requirements,
    and a foreign key relationship between a model and an authenticated
    User
    
    :param params: List of string names for expected POST params
    :param model: Model to evaluate for a foreign key relationship
    :type params: list
    :type model: Model
    :returns: (400, 401, 404) Response object if conditions are not met
    :rtype: Response
    """
    def wrapper(func):
        @wraps(func)
        def require(*args, **kwargs):
            failed = FailCheck.enforce_params(params, args, kwargs)
            if failed: return failed
            # Ensure user is super user or author of the model
            if 'pk' in kwargs:
                failed = FailCheck.enforce_owner(model, args, kwargs)
                if failed: return failed
            return func(*args, **kwargs)
        return require
    return wrapper
