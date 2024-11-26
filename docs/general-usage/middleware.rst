Middleware
==========

You can use ``middleware`` to affect the evaluation of fields in your schema.

A middleware is any object or function that responds to ``resolve(next_middleware, *args).``

You can read more about middleware on the `Graphene docs <https://docs.graphene-python.org/en/latest/execution/middleware/>`_.

You must enable the GrappleMiddleware for grapple's field level middleware to work.

GrappleMiddleware
-----------------
.. module:: wagtail_ninja.middleware
.. class:: GrappleMiddleware(object)

.. code-block:: python

    # settings.py
    GRAPHENE = {
        # ...
        "MIDDLEWARE": ["wagtail_ninja.middleware.GrappleMiddleware"],
    }


Examples
--------


Authenticated Middleware
^^^^^^^^^^^^^^^^^^^^^^^^
.. module:: wagtail_ninja.middleware
.. class:: IsAuthenticatedMiddleware(object)

This middleware only continues evaluation if the request is authenticated.

.. code-block:: python

    class IsAuthenticatedMiddleware(object):
        def resolve(self, next, root, info, **args):
            if not info.context.user.is_authenticated:
                return None
            return next(root, info, **args)


Anonymous Middleware
^^^^^^^^^^^^^^^^^^^^
.. module:: wagtail_ninja.middleware
.. class:: IsAnonymousMiddleware(object)

This middleware only continues evaluation if the request is **not** authenticated.

.. code-block:: python

    class IsAnonymousMiddleware(object):
        def resolve(self, next, root, info, **args):
            if not info.context.user.is_anonymous:
                return None
            return next(root, info, **args)
