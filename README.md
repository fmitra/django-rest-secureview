[![PyPI version](https://badge.fury.io/py/django-rest-secureview.svg)](https://badge.fury.io/py/django-rest-secureview)
[![Build Status](https://travis-ci.org/fmitra/django-rest-secureview.svg?branch=master)](https://travis-ci.org/fmitra/django-rest-secureview)


# django-rest-secureview

A collection of decorators to enforce conditions on [Django REST Framework](http://www.django-rest-framework.org/) API routes that are accessed by the User. At the moment, it focuses on enforcing specific model keys in POST params, or requiring that a User has a foreign key relation to a model they are accessing. 

## Requirements

1. Python 2 or Python 3
2. Django
3. Django REST Framework

## Usuage

1. Install package

	`pip install django-rest-secureview`

2. Import decorators and viewset rules

	``` python
	from django_rest_secureview.decorators import require
	from django_rest_secureview.view_rules import Params
	```

3. Decorate ViewSets

	``` python
	from rest_framework.viewsets import ModelViewSet
	from django_rest_secureview.decorators import require
	from django_rest_secureview.view_rule import Params
	
	class ApiEndpoint(ModelViewSet):
	    @require(Params, params=['dog', 'cat'])
	    def create(self, request):
	        pass
	```

## ViewRules

ViewRules contain the logic behind the API conditions being enforced. Using the `require` decorator requires a ViewRule at the minimum. The default ViewRules in this package all expect a certain keyword arguments to compliment them. If you need additional functionality, you can create your own ViewRule (explained below)

1. `Params`: Requires specific POST params to be submitted in reqeusts
  * kwargs: `params` list
  * Usuage: `@require(Params, params=['animal', 'name'])`

2. `Owner`: Requires authenticated User to have a foreign key relationship with the requested Model instance in a detailed endpint 
	* kwargs: `model` Django Model
	* Usuage: `@require(Owner, model=Pet)`
	* Note: This only works in detailed endpoints using the default `pk` attribute 

3. `OwnerParams`: Combinds both `Params` and `Owner` conditions
	* kwargs: `model` Django Model, `params` list
	* Usuage: `@require(Owner, model=Pet, params=['animal'])`
	* Note: This only works in detailed endpoints using the default `pk` attribute 

## Decorators

1. `require`: Accepts a ViewRule detailing API conditions and an arbitrary number of keyword values. For more information, reference the ViewRule documentation.

	``` python
	# Expects an animal and name param to be provided in the POST request
	@require(Params, params=['animal', 'name'])
	def create(self, request):
	    pass

	# Expects the accessing User to have a foreign key relation to 
	# the Pet model
	@require(Owner, model=Pet)
	def retrieve(self, request, pk=None):
	    pass
	
	# Expects the accessing User to have a foreign key relation to 
	# the Pet model as well as name and color values in the POST params
	@require_owner(OwnerParams, model=Pet, params=['name', 'color'])
	def update(self, request, pk=None):
	    pass
	```

## Creating Your Own ViewRules

We can create our own ViewRules by extending the ViewRule abstract class supplied in the view_rules module and implementing an `enforce` method. For convenience, HTTP status codes from the Django REST Framework are available in the class's `status` attribute and arguments in the request object are available in the class's `request` attribute.

All ViewRules are expected to have an `enforce` method that returns a JSON-serializable response if specific conditions are not met. If conditions are not met, the ViewSet will deliver this response instead of the response defined within the ViewSet's action method. 

More status codes: [REST Framework Status Codes](http://www.django-rest-framework.org/api-guide/status-codes/)

``` python
from django_rest_secureview.view_rules import ViewRule

class MyCondition(ViewRule):
    def enforce(self, params=None):
        # Check who the User is if necessary
        # user = self.request.user
        # Some rules here
        condition_met = False
        if not condition_met:
	        code = self.status.HTTP_400_BAD_REQUEST
	        notice = {"detail":"Whoops something went wrong"}
            return self.response(data=notice, status=code)
```

## Testing

[Tox](https://tox.testrun.org) should be in your virtual environment in order to run tests. Other dependencies, such as the Django REST Framework will be packaged separately in Tox's virtual testing environment. 

``` sh
./run_tests.sh
```