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

2. Import decorators and blueprints

	``` python
	from django_rest_secureview.decorators import require
	from django_rest_secureview.blueprints import Params
	```

3. Decorate ViewSets

	``` python
	from rest_framework.viewsets import ModelViewSet
	from django_rest_secureview.decorators import require
	from django_rest_secureview.blueprints import Params
	
	class ApiEndpoint(ModelViewSet):
	    @require(Params, params=['dog', 'cat'])
	    def create(self, request):
	        pass
	```

## Blueprints

Blueprints contain the logic behind the API conditions being enforced. Using the `require` decorator requires a Blueprint at the minimum. The Blueprints supplied by default in this package all expect a certain keyword arguments to compliment them. If you need additional functionality, you can create your own Blueprint (explained below)

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

1. `require`: Accepts a Blueprint detailing API conidtions and an arbitrary number of keyword values. For more information, reference the Blueprint documentation.

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

## Creating Your Own Blueprints

We can create our own Blueprints by extending the ErrorBlueprint abstract class supplied in the blueprints module and implementing an `enforce` method. For convenience, HTTP status codes from the Django REST Framework are available in the class's `http_status` attribute and arguments in the request object are available in the class's `request` attribute.

``` python
from django_rest_secureview.blueprints import ErrorBlueprint

class MyCondition(ErrorBlueprint):
    def enforce(self, params=None):
        # Check who the User is
        user = self.request.user
        # Some rules here
        condition_met = False
        if not condition_met:
	        code = self.http_status.HTTP_400_BAD_REQUEST
            return self.response({"detail":"Whoops something went wrong"}, 
                                 status=code)
```

## Testing

[Tox](https://tox.testrun.org) should be in your virtual environment in order to run tests. Other dependencies, such as the Django REST Framework will be packaged separately in Tox's virtual testing environment. 

``` sh
./run_tests.sh
```