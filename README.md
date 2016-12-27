[![PyPI version](https://badge.fury.io/py/django-rest-secureview.svg)](https://badge.fury.io/py/django-rest-secureview)

# django-rest-secureview

A collection of decorators to enforce conditions on [Django REST Framework](http://www.django-rest-framework.org/) API routes that are accessed by the User. At the moment, it focuses on enforcing specific model keys in POST params, or requiring that a User has a foreign key relation to a model they are accessing. 

## Requirements

1. Python 2 or Python 3
2. Django
3. Django REST Framework

## Usuage

1. Install package

	`pip install django-rest-secureview`

2. Import decorators

	``` python
	from django_rest_secureview import require_owner
	```

3. Decorate ViewSets

	``` python
	from rest_framework.viewsets import ModelViewSet
	from django_rest_secureview import require_params
	
	class ApiEndpoint(ModelViewSet):
	    @require_params(params=['dog', 'cat'])
	    def create(self, request):
	        pass
	```

## Decorators

1. `require_params`: Requires User to submit specific POST params when accessing an endpoint

	``` python
	@require_params(params=['dog', 'cat'])
	def create(self, request):
	    pass
	```

2. `require_owner`: Requires the authenticated User to have a ForeignKey relationship with the model in a detailed view

	``` python
	@require_owner(model=Pet)
	def retrieve(self, request, pk=None):
	    pass
	```

3. `require_owner_with_params`: Requires POST params and a ForeignKey relationship with the authenticated User and the model in a detailed view

	``` python
	@require_owner_with_params(model=Pet, params=['dog', 'cat'])
	def update(self, request, pk=None):
	    pass
	```

## Testing
[Tox](https://tox.testrun.org) should be in your virtual environment in order to run tests. Other dependencies, such as the Django REST Framework will be packaged separately in Tox's virtual testing environment. 

``` sh
./run_tests.sh
```