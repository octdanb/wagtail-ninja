Settings
========

The Wagtail Ninja configuration is contained inside a single Django setting - ``WAGTAIL_NINJA``.

For example, your project's ``settings.py`` file might include something like this:

.. code-block:: python

    # settings.py
    WAGTAIL_NINJA = {
        "APPS": ["home"],
        "ADD_SEARCH_HIT": True,
        # ...
    }


Accessing settings
------------------

To access any Wagtail Ninja setting in your code, use the ``grapple_settings`` object. For example.

.. code-block:: python

    from wagtail_ninja.settings import grapple_settings

    print(grapple_settings.APPS)

The ``grapple_settings`` object will check for any user-defined settings, and otherwise fall back to
the default values.


API Reference
-------------


Grapple settings
^^^^^^^^^^^^^^^^

``APPS``
********

A list/tuple of the apps that Grapple will scan for models to generate GraphQL types that adopt their structure.

Default: ``[]``


``AUTO_CAMELCASE``
******************

By default, all field and argument names will be converted from `snake_case` to `camelCase`.
To disable this behavior, set the ``WAGTAIL_NINJA['AUTO_CAMELCASE']`` setting to `False`.

Default: ``True``


Renditions settings
^^^^^^^^^^^^^^^^^^^

``ALLOWED_IMAGE_FILTERS``
*************************

To prevent arbitrary renditions from being generated, set ``WAGTAIL_NINJA['ALLOWED_IMAGE_FILTERS']`` in
your settings to a `list` or `tuple` of allowed filters. Read more about generating renditions in the Wagtail docs
(`Generating renditions in Python <https://docs.wagtail.io/en/stable/advanced_topics/images/renditions.html#generating-renditions-in-python>`_ and
`How to use images in templates <https://docs.wagtail.io/en/stable/topics/images.html#how-to-use-images-in-templates>`_)

Default: ``None``

Example:

.. code-block:: python

    # settings.py
    WAGTAIL_NINJA = {
        # ...
        "ALLOWED_IMAGE_FILTERS": [
            "width-1000",
            "fill-300x150|jpegquality-60",
            "width-700|format-webp",
        ]
    }

Note that the ``srcSet`` attribute on ``ImageObjectType`` generates ``width-*`` filters, so if in use
consider adding the relevant filters to the allowed list.


.. _rich text settings:

Rich text settings
^^^^^^^^^^^^^^^^^^

``RICHTEXT_FORMAT``
*******************

Controls the ``RichText`` field and the ``RichTextBlock`` StreamField block output. Read more about the Wagtail
rich text data format in the Wagtail docs (`Rich text internals <https://docs.wagtail.io/en/stable/extending/rich_text_internals.html#data-format>`_).
Set to ``raw`` to return the database representation.

Note: the ``RichTextBlock`` ``rawValue`` output will always be the database representation.

Default: ``html``

Search settings
^^^^^^^^^^^^^^^

``ADD_SEARCH_HIT``
******************

When set to ``True``, Grapple will log search queries so that Wagtail can suggest promoted results.

Default: ``False``


Pagination settings
^^^^^^^^^^^^^^^^^^^

``PAGE_SIZE``
**************

Used as default for both the ``limit`` argument for ``QuerySetList`` and the ``perPage`` argument for ``PaginatedQuerySet``.

Default: ``10``


``MAX_PAGE_SIZE``
*****************

Limit the maximum number of items that ``QuerySetList`` and ``PaginatedQuerySet`` types return.

Default: ``100``


Wagtail model interfaces
^^^^^^^^^^^^^^^^^^^^^^^^

.. _page interface setting:

``PAGE_INTERFACE``
******************

Used to construct the schema for Wagtail Page-derived models. It can be overridden to provide a custom interface for all
page models.

Default: ``wagtail_ninja.types.interfaces.PageInterface``


.. _snippet interface setting:

``SNIPPET_INTERFACE``
*********************

Used to construct the schema for Wagtail snippet models. It can be overridden to provide a custom interface for all
snippet models.

Default: ``wagtail_ninja.types.interfaces.SnippetInterface``
