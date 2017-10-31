import json
import connexion
import functools
import jsonschema

class FormJsonRequestBodyValidator(connexion.decorators.validation.RequestBodyValidator):
	def __init__(self, *args, **kwargs):
		super(FormJsonRequestBodyValidator, self).__init__(*args, **kwargs)

	def __call__(self, function):
		super_wrapper = super(FormJsonRequestBodyValidator, self).__call__(function)

		@functools.wraps(function)
		def wrapper(request):
			if not request.json and request.form != {}:
				for k,v in request.form.lists():
					try:
						request.json = json.loads(k)
						request.body = json.dumps(request.json)
						request.form = {}
						break
					except:
						# parsing error
						request.json = None
						request.body = k
						request.form = {}

			return super_wrapper(request)

		return wrapper
