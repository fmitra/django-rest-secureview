""" 
ViewSet decorator to impose conditions enforced by
the ViewRules
"""
from functools import wraps


def require(ViewRule, **params):
    """
    Decorator function checks if all conditions are met.
    If no errors are found, it will return the ViewSet

    :param ViewRule: ViewRule template containing an enforce method
    :type ViewRule: Class inheriting from ViewRule
    """
    def wrapper(viewset):
        @wraps(viewset)
        def require(*request_args, **request_kwargs):
            view_rule = ViewRule(request_args, request_kwargs)
            failed = view_rule.errors_found(params)
            if failed[0]: return failed[1]
            return viewset(*request_args, **request_kwargs)
        return require
    return wrapper

