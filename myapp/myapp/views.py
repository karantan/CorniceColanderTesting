""" Cornice fruit resources."""
from cornice.resource import resource
from cornice.resource import view
from cornice.validators import colander_body_validator

import colander


class FruitAddSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title='Title',
        description='Fruit name',
    )

    def validator(self, node, cstruct):
        request = self.bindings['request']
        if cstruct['name'] != 'banana':
            request.errors.add('body', description='Wrong fruit.')
            # Error can be raised without `request` but we just want to prove
            # that we have the "real" `request`
            # self.raise_invalid('Wrong fruit.')


def binded_schema(request):
    FruitPOSTSchema = FruitAddSchema()
    FruitPOSTSchema = FruitPOSTSchema.bind(request=request)
    schema = FruitPOSTSchema
    return schema


def body_validator(request, **kwargs):
    kwargs['schema'] = binded_schema(request)
    return colander_body_validator(request, **kwargs)


# dummy DBs
FRUITS = {'1': {'name': 'apple'}, '2': {'name': 'orange'}}


class FruitFactory(object):

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        return FRUITS[key]


@resource(
    collection_path='/fruits/',
    collection_factory=FruitFactory,
    collection_traverse='',
    path='/fruits/{fruit_id}/',
    factory=FruitFactory,
    name='fruit_service',
    traverse='/{fruit_id}'
)
class Fruit(object):

    def __init__(self, request, context):
        self.request = request
        self.context = context

    def collection_get(self):
        """Get all fruits."""
        return {'fruits': list(FRUITS.keys())}

    @view(renderer='json')
    def get(self):
        """Get fruit from `FRUITS`."""
        return self.context

    @view(validators=(body_validator,))
    def collection_post(self):
        """Add fruit to `FRUITS`."""
        FRUITS[str(len(FRUITS) + 1)] = {'name': self.request.validated['name']}
        return FRUITS[str(len(FRUITS))]
