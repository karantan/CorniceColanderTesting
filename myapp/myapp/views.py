""" Cornice fruit resources."""
from cornice.resource import resource
from cornice.resource import view
from cornice.validators import colander_body_validator

import colander


@colander.deferred
def deferred_name(node, kw):
    """Only 'banana' fruit is allowed."""
    request = kw['request']

    def validator(node, name):
        if name != 'banana':
            request.errors.add('body', name=name, description='Wrong fruit.')

    return validator


@colander.deferred
def deferred_blacklisted_words(node, kw):
    request = kw['request']

    def validator(node, description):
        if description in ['xxx', 'foo', 'bar']:
            request.errors.add(
                'body',
                name=description,
                description='These words are not allowed.',
            )

    return validator


@colander.deferred
def deferred_description(node, kw):
    request = kw['request']

    def validator(node, description):
        if description == '/':
            request.errors.add(
                'body', name=description, description='Invalid description.')

    return colander.All(
        validator,
        deferred_blacklisted_words(node, kw),
    )


class DescriptionSchema(colander.Schema):
    title = colander.SchemaNode(
        colander.String(),
        title='Title',
        description='Fruit description - title',
        missing=None,
    )
    body = colander.SchemaNode(
        colander.String(),
        title='Description',
        description='Fruit description - body',
        preparer=lambda x: x.lower() if x else x,
        validator=deferred_description,
        missing=None,
    )


class FruitSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title='Title',
        description='Fruit name',
        validator=deferred_name,
    )
    info = DescriptionSchema(missing=None)

    # Alternatively, instead of using a `deferred` validator, we can do:
    # def validator(self, node, cstruct):
    #     request = self.bindings['request']
    #     if cstruct['name'] != 'banana':
    #         request.errors.add('body', description='Wrong fruit.')
    #         # Error can be raised without `request` but we just want to prove
    #         # that we have the "real" `request`
    #         # self.raise_invalid('Wrong fruit.')


def body_validator(request, **kwargs):
    schema = FruitSchema()
    kwargs['schema'] = schema.bind(request=request)
    return colander_body_validator(request, **kwargs)


# dummy DBs
FRUITS = {
    '1': {'name': 'apple', 'description': 'sweet, edible fruit'},
    '2': {'name': 'orange', 'description': 'member of the citrus family'},
}


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
    traverse='/{fruit_id}',
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
        """Add fruit to `FRUITS`.

        If you want flatten result from `self.request`:
        BUT then you need to handle `.deserialize` exceptions yourself

        Example:

        .. code-block:: python

            schema = FruitSchema().bind(request=self.request)

            try:
                appstruct = schema.deserialize(self.request.validated)
            except colander.Invalid as err:
                errors = err.asdict()
                for attribute in errors:
                    self.request.errors.add(
                        'url', name=attribute, description=errors.get(attribute))
                return self.request

            FRUITS[str(len(FRUITS) + 1)] = schema.flatten(appstruct)
        """  # noqa

        FRUITS[str(len(FRUITS) + 1)] = self.request.validated
        self.request.response.status_code = 201
        self.request.response.headers['Location'] = self.request.route_path(
            'fruit_service', fruit_id=len(FRUITS))

        return FRUITS[str(len(FRUITS))]
