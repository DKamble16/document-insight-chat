# converts a list of values into a list of orm models that match field value
# usage: v.am.string.to.models(User, field='id')
def models(model, validate=True, field='id'):
    def validator(v, accept=None, reject=None):
        # ensure we have a list
        if not isinstance(v, list):
            reject('expected_model_list')

        # find objects with where model field is in v (list of values)
        fields = {}
        fields[f'{field}__in'] = v

        # accept a model or query set
        if hasattr(model, 'objects'):
            objects = model.objects.filter(**fields).all()
        else:
            objects = model.filter(**fields).all()

        # validate every v was converted into a model
        if validate and {str(id) for id in v} != {str(getattr(o, field)) for o in objects}:
            reject(f'expected_every_model_exists')

        # return objects
        return objects
    return validator
models.dynamic = True
