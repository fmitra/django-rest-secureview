""" 
ViewSet decorator to impose conditions enforced by
the Blueprints
"""
from functools import wraps


def require(Blueprint, **params):
    """
    Decorator function checks if all conditions are met.
    If no errors are found, it will return the ViewSet

    :param Blueprint: Blueprint template containing an enforce method
    :type Blueprint: Class inheriting from ErrorBlueprint
    """
    def wrapper(viewset):
        @wraps(viewset)
        def require(*request_args, **request_kwargs):
            blueprint = Blueprint(request_args, request_kwargs)
            failed = blueprint.errors_found(params)
            if failed[0]: return failed[1]
            return viewset(*request_args, **request_kwargs)
        return require
    return wrapper

