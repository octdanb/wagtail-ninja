Installation
#############

Basic usage
===========

Add library to an existing Wagtail project:

``pip install wagtail_grapple``

Add the following to the ``INSTALLED_APPS`` list in your Wagtail
settings file:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        "grapple",
        "graphene_django",
        # ...
    ]

Add the following to the bottom of the same settings file where each key
is the app you want to this library to scan and the value is the prefix
you want to give to GraphQL types (you can usually leave this blank):

.. code-block:: python

    # Grapple Config:
    GRAPHENE = {"SCHEMA": "wagtail_ninja.schema.schema"}
    WAGTAIL_NINJA = {
        "APPS": ["home"],
    }

Add the GraphQL URLs to your ``urls.py``:

.. code-block:: python

    from django.urls import path
    from grapple import urls as grapple_urls

    # ...
    urlpatterns = [
        # ...
        path("", include(grapple_urls)),
        # ...
    ]

Done! Now you can proceed onto configuring your models to generate
GraphQL types that adopt their structure.

By default, Grapple uses :doc:`these settings <settings>`.

* **Next Steps**

  * :doc:`examples`
  * :doc:`settings`
  * :doc:`../general-usage/graphql-types`


*Your GraphQL endpoint is available at http://localhost:8000/graphql/*
