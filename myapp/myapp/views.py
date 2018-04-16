""" Cornice fruit resources."""
from cornice.resource import resource
from cornice.resource import view
from cornice.validators import colander_body_validator

import colander


@colander.deferred
def deferred_title_validator(node, kw):
    request = kw['request']


class FruitAddSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title='Title',
        description='Fruit name',
        validator=deferred_title_validator,
    )

FruitPOSTSchema = FruitAddSchema().clone()

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

    @view(
        schema=FruitPOSTSchema,
        validators=(colander_body_validator,)
    )
    def collection_post(self):
        """Add fruit to `FRUITS`."""
        return self.request.validated['name']
