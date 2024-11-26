Model Types
===========
What do we mean when we say types? In a Grapple context, a type is a descriptor
function that instructs Grapple what type a Django model field is represented by
in GraphQL.

The field types below are simple to use and all work in the same way.
We created a number of built-in types for general use, but you can create your own
using `Graphene <https://github.com/graphql-python/graphene/>`_ (Grapple's underlying library)
and take advantage of Grapple's generic ``GraphQLField`` type.


GraphQLField
-------------
.. module:: wagtail_ninja.models
.. class:: GraphQLField(field_name: str, field_type: type = None, required=None, **kwargs)

    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: field_type (type)

        A Grapple model type such as ``GraphQLString`` or ``GraphQLBoolean``.

    .. attribute:: required (bool=None)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.

    .. attribute:: kwargs

        Useful keyword arguments:

        * ``description`` (string)
            A description of the type to show in the GraphiQL browser.

        * ``deprecation_reason`` (string)
            Provide a deprecation reason for the Field, will also show in the GraphiQL browser.

        * ``source`` (string)
            You can pass a source string that is an attribute or method on the
            class itself.

            If used within a `StreamField`, the method will receive all values
            from the instance via the `values` kwarg, e.g.:

            .. code-block:: python

                class SomeStructBlock(blocks.StructBlock):
                    text = blocks.CharBlock()

                    graphql_fields = [
                        GraphQLField(
                            field_name="some_name",
                            field_type=graphene.String,
                            source="some_method",
                        )
                    ]

                    def some_method(self, values: Dict[str, Any] = None) -> Optional[str]:
                        return values.get("text") if values else None


GraphQLString
-------------
.. module:: wagtail_ninja.models
.. class:: GraphQLString(field_name, required=False, **kwargs)

    A basic field type is string. Commonly used for CharField, TextField,
    UrlField or any other Django field that returns a string as it's value.

    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: required (bool=False)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.

    .. attribute:: kwargs

        Useful keyword arguments:

        * ``description`` (string)
            A description of the type to show in the GraphiQL browser.

        * ``deprecation_reason`` (string)
            Provide a deprecation reason for the Field, will also show in the GraphiQL browser.

        * ``source`` (string)
            You can pass a source string that is an attribute or method on the
            class itself.

            If used within a `StreamField`, the method will receive all values
            from the instance via the `values` kwarg, e.g.:

            .. code-block:: python

                class SomeStructBlock(blocks.StructBlock):
                    text = blocks.CharBlock()

                    graphql_fields = [
                        GraphQLString(
                            field_name="some_name",
                            source="some_method",
                        )
                    ]

                    def some_method(self, values: Dict[str, Any] = None) -> Optional[str]:
                        return values.get("text") if values else None

    In your models.py:

    .. code-block:: python

        from wagtail_ninja.types import GraphQLString


        class BlogPage(Page):
            author = models.CharField(max_length=255)

            graphql_fields = [
                GraphQLString("author"),
            ]


    Example query:

    ::

        query {
            page(slug: "example-blog-page") {
                author
            }
        }


GraphQLCollection
-----------------
.. module:: wagtail_ninja.models
.. class:: GraphQLCollection(nested_type, field_name, *args, is_queryset=False, is_paginated_queryset=False, required=False, item_required=False, **kwargs)

    A field type that wraps another model type in a list. Best suited for referencing Orderables (i.e. ForeignKey lists).

    .. attribute:: nested_type

        A Grapple model type such as ``GraphQLString`` or ``GraphQLForeignKey``.

    .. attribute:: field_name (str)

        The name of the class property used in your model definition.

    .. attribute:: *args

        Any positional arguments that you want to pass on to the nested type.

    .. attribute:: is_queryset (bool=False)

        This sets the arguments ``id``, ``limit``, ``offset``, ``search_query``, and ``order`` on the field.

    .. attribute:: is_paginated_queryset (bool=False)

        This sets the arguments ``id``, ``page``, ``per_page``, ``search_query``, and ``order`` on the field.

        Also sets the return value as an extended PaginatedType (example below).

    .. attribute:: required (bool=False)

        Represents the list as non-nullable in the schema. This promises the client that an array will be returned.

    .. attribute:: item_required (bool=False)

        Represents the fields in the list as non-nullable in the schema. This promises the client that the array items won't be null.

    .. attribute:: **kwargs

        Any keyword arguments that you want to pass on to the nested type.

        One keyword argument that is more powerful with Collections is the ``source`` argument. With ``GraphQLCollection``,
        You can pass a source string that is multiple layers deep and Grapple will handle the querying for you through
        multiple models (example below).

    In your models.py:

    .. code-block:: python

        from wagtail_ninja.types import GraphQLString


        class BlogPage(Page):
            author = models.CharField(max_length=255)

            def paginated_related_links(self, info, **kwargs):
                return resolve_paginated_queryset(self.related_links.all(), info, **kwargs)

            graphql_fields = [
                # Basic reference to Orderable model
                GraphQLCollection(
                    GraphQLForeignKey, "related_links", "home.BlogPageRelatedLink"
                ),
                # Will return an array of just the url from each link
                GraphQLCollection(GraphQLString, "related_urls", source="related_links.url"),
                # Reference to Orderable model with pagination
                GraphQLCollection(
                    GraphQLForeignKey,
                    "paginated_related_links",
                    "home.BlogPageRelatedLink",
                    is_paginated_queryset=True,
                ),
            ]

    Example query:

    ::

        query {
            page(slug: "example-blog-page") {
                relatedUrls
                relatedLinks {
                    name
                }
                paginatedRelatedLinks {
                    items {
                        name
                    }
                    pagination {
                        total
                        count
                        perPage
                        currentPage
                        prevPage
                        nextPage
                        totalPages
                    }
                }
            }
        }


GraphQLInt
----------
.. module:: wagtail_ninja.models
.. class:: GraphQLInt(field_name, required=False, **kwargs)

    Used to serialize integer-based Django fields such as ``IntegerField``
    or ``PositiveSmallIntegerField``.

    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: required (bool=False)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.

    .. attribute:: kwargs

        Useful keyword arguments:

        * ``description`` (string)
            A description of the type to show in the GraphiQL browser.

        * ``deprecation_reason`` (string)
            Provide a deprecation reason for the Field, will also show in the GraphiQL browser.

        * ``source`` (string)
            You can pass a source string that is an attribute or method on the
            class itself.

            If used within a `StreamField`, the method will receive all values
            from the instance via the `values` kwarg, e.g.:

            .. code-block:: python

                class SomeStructBlock(blocks.StructBlock):
                    integer = blocks.IntegerBlock()

                    graphql_fields = [
                        GraphQLInt(
                            field_name="some_name",
                            source="some_method",
                        )
                    ]

                    def some_method(self, values: Dict[str, Any] = None) -> Optional[int]:
                        return values.get("integer") if values else None


GraphQLFloat
------------
.. module:: wagtail_ninja.models
.. class:: GraphQLFloat(field_name, required=False, **kwargs)

    Like ``GraphQLInt``, this field is used to serialize ``Float`` and ``Decimal`` fields.

    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: required (bool=False)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.

    .. attribute:: kwargs

        Useful keyword arguments:

        * ``description`` (string)
            A description of the type to show in the GraphiQL browser.

        * ``deprecation_reason`` (string)
            Provide a deprecation reason for the Field, will also show in the GraphiQL browser.

        * ``source`` (string)
            You can pass a source string that is an attribute or method on the
            class itself.

            If used within a `StreamField`, the method will receive all values
            from the instance via the `values` kwarg, e.g.:

            .. code-block:: python

                class SomeStructBlock(blocks.StructBlock):
                    float = blocks.FloatBlock()

                    graphql_fields = [
                        GraphQLFloat(
                            field_name="some_name",
                            source="some_method",
                        )
                    ]

                    def some_method(self, values: Dict[str, Any] = None) -> Optional[float]:
                        return values.get("decimal") if values else None


GraphQLBoolean
--------------
.. module:: wagtail_ninja.models
.. class:: GraphQLBoolean(field_name, required=False, **kwargs)

    Used to serialize ``Boolean`` fields.

    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: required (bool=False)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.

    .. attribute:: kwargs

        Useful keyword arguments:

        * ``description`` (string)
            A description of the type to show in the GraphiQL browser.

        * ``deprecation_reason`` (string)
            Provide a deprecation reason for the Field, will also show in the GraphiQL browser.

        * ``source`` (string)
            You can pass a source string that is an attribute or method on the
            class itself.

            If used within a `StreamField`, the method will receive all values
            from the instance via the `values` kwarg, e.g.:

            .. code-block:: python

                class SomeStructBlock(blocks.StructBlock):
                    text = blocks.CharBlock()

                    graphql_fields = [
                        GraphQLBoolean(
                            field_name="some_name",
                            source="some_method",
                        )
                    ]

                    def some_method(self, values: Dict[str, Any] = None) -> Optional[bool]:
                        return bool(values.get("text")) if values else None


GraphQLStreamfield
------------------
.. module:: wagtail_ninja.models
.. class:: GraphQLStreamfield(field_name, **kwargs)

    This field type supports all built-in ``Streamfield`` blocks. It also supports
    custom blocks built using ``StructBlock`` and the like.

    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: required (bool=False)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.

    .. attribute:: kwargs

        Keyword arguments to pass to the field type definition. Notably:

        * is_list (bool=True)
            Defaults to True to indicate a list of blocks. Set this to false when the nested ``StructBlock``s
            do not return a value.

        e.g.

    .. code-block:: python

        @register_streamfield_block
        class ButtonBlock(blocks.StructBlock):
            button_text = blocks.CharBlock(required=True, max_length=50, label="Text")
            button_link = blocks.CharBlock(required=True, max_length=255, label="Link")

            graphql_fields = [GraphQLString("button_text"), GraphQLString("button_link")]


        @register_streamfield_block
        class TextAndButtonsBlock(blocks.StructBlock):
            text = blocks.TextBlock()
            buttons = blocks.ListBlock(ButtonBlock())
            mainbutton = ButtonBlock()

            graphql_fields = [
                GraphQLString("text"),
                GraphQLImage("image"),
                GraphQLStreamfield("buttons"),
                GraphQLStreamfield(
                    "mainbutton", is_list=False
                ),  # this is a direct StructBlock, not a list of sub-blocks
            ]


        @register_paginated_query_field("blog_page")
        class BlogPage(Page):
            body = StreamField(
                [
                    ("text_and_buttons", TextAndButtonsBlock()),
                ]
            )

            graphql_fields = [GraphQLStreamfield("body")]

    ::

        # Example query, based on the above
        {
            blogPage(id: 123) {
                body {
                    ... on TextAndButtonsBlock {
                        mainbutton {
                            ... on ButtonBlock {
                                buttonText
                                buttonLink
                            }
                        }
                        buttons {
                            ... on ButtonBlock {
                                buttonText
                                buttonLink
                            }
                        }
                    }
                }
            }
        }


GraphQLSnippet
--------------
.. module:: wagtail_ninja.models
.. class:: GraphQLSnippet(field_name, snippet_model, required=False)

    ``GraphQLSnippet`` is a little bit more complicated; You first need to define
    a ``graphql_field`` list on your snippet like you do your page. Then you need
    to reference the snippet in the field type function.

    Your snippet values are then available through a sub-selection query on the
    field name.

    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: snippet_model (str)

        String which defines the location of the snippet model.

    .. attribute:: required (bool=False)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.


    In your models.py:

    .. code-block:: python

        class BookPage(Page):
            advert = models.ForeignKey(
                "demo.Advert",
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name="+",
            )

            graphql_fields = [
                GraphQLSnippet("advert", "demo.Advert"),
            ]

            content_panels = Page.content_panels + [
                SnippetChooserPanel("advert"),
            ]


        @register_snippet
        class Advert(models.Model):
            url = models.URLField(null=True, blank=True)
            text = models.CharField(max_length=255)

            graphql_fields = [
                GraphQLString("url"),
                GraphQLString("text"),
            ]

            panels = [
                FieldPanel("url"),
                FieldPanel("text"),
            ]

            def __str__(self):
                return self.text


    ::

        # Example query
        {
            page(slug: "some-blog-page") {
                advert {
                    url
                    text
                }
            }
        }


GraphQLForeignKey
-----------------
.. module:: wagtail_ninja.models
.. class:: GraphQLForeignKey(field_name, content_type, required=False)

    ``GraphQLForeignKey`` is similar to ``GraphQLSnippet`` in that you pass a
    ``field_name`` and ``content_type``. You can also specify that the field
    is a list (for example when using ``Orderable``). For foreign keys to ``wagtailcore.Page``, use ``GraphQLPage``.

    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: content_type (str)

        String which defines the location of the model you are referencing. You can also pass the model class itself.

    .. attribute:: required (bool=False)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.

    .. code-block:: python

        class BookPage(Page):
            advert = models.ForeignKey(
                "demo.Advert",
                null=True,
                blank=True,
                on_delete=models.SET_NULL,
                related_name="+",
            )

            graphql_fields = [
                GraphQLSnippet("advert", "demo.Advert"),
            ]

            content_panels = Page.content_panels + [
                SnippetChooserPanel("advert"),
            ]


GraphQLImage
------------

.. module:: wagtail_ninja.models
.. class:: GraphQLImage(field_name, required=False)

    Use this field type to serialize the core Wagtail or your custom Image model.

    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: required (bool=False)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.

    .. attribute:: kwargs

        Useful keyword arguments:

        * ``description`` (string)
            A description of the type to show in the GraphiQL browser.

        * ``deprecation_reason`` (string)
            Provide a deprecation reason for the Field, will also show in the GraphiQL browser.


GraphQLDocument
---------------

.. module:: wagtail_ninja.models
.. class:: GraphQLDocument(field_name, required=False)

    Use this field type to serialize the core Wagtail or your custom Document model.

    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: required (bool=False)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.

    .. attribute:: kwargs

        Useful keyword arguments:

        * ``description`` (string)
            A description of the type to show in the GraphiQL browser.

        * ``deprecation_reason`` (string)
            Provide a deprecation reason for the Field, will also show in the GraphiQL browser.


GraphQLPage
-----------

.. module:: wagtail_ninja.models
.. class:: GraphQLPage(field_name: str, **kwargs)

    Use this field type to serialize a relationship to a Wagtail Page or Page-derived model. The resulting type
    is the generic Wagtail Page type. A useful type for foreign keys that are not limited to a single, custom Page
    model, registered with Grapple.


    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: required (bool=False)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.

    .. attribute:: kwargs

        Useful keyword arguments:

        * ``description`` (string)
            A description of the type to show in the GraphiQL browser.

        * ``deprecation_reason`` (string)
            Provide a deprecation reason for the Field, will also show in the GraphiQL browser.

        * ``source`` (string)
            You can pass a source string that is an attribute or method on the
            model itself. It can also be several layers deep and Grapple will
            handle the querying for you through multiple models.


GraphQLTag
-----------

.. module:: wagtail_ninja.models
.. class:: GraphQLTag(field_name: str, **kwargs)

    Use this field type to serialize a ``ClusterTaggableManager`` field.


    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: required (bool=False)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.

    .. attribute:: kwargs

        Useful keyword arguments:

        * ``description`` (string)
            A description of the type to show in the GraphiQL browser.

        * ``deprecation_reason`` (string)
            Provide a deprecation reason for the Field, will also show in the GraphiQL browser.



GraphQLRichText
---------------
.. module:: wagtail_ninja.models
.. class:: GraphQLRichText(field_name, required=False, **kwargs)

    Use this field type to serialize ``RichTextField`` and ``RichTextBlock`` values. If your :ref:`RICHTEXT_FORMAT<rich text settings>` setting is ``"html"``, the stored value will be transformed from the internal representation to proper html. If set to ``"raw"``, the raw internal representation will be returned.

    .. attribute:: field_name (str)

        This is the name of the class property used in your model definition.

    .. attribute:: required (bool=False)

        Represents the field as non-nullable in the schema. This promises the client that it will have a value returned.

    .. attribute:: kwargs

        Useful keyword arguments:

        * ``description`` (string)
            A description of the type to show in the GraphiQL browser.

        * ``deprecation_reason`` (string)
            Provide a deprecation reason for the Field, will also show in the GraphiQL browser.

        * ``source`` (string)
            You can pass a source string that is an attribute or method on the
            class itself.
