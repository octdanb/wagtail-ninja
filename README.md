<p align="center">
  <a href="https://github.com/falsaform/wagtail-ninja">
    <img src="https://github.com/falsaform/wagtail-ninja/raw/main/.github/wagtail-wagtail_ninja.svg?sanitize=true" alt="A ninja bird" width="80" height="80">
  </a>
</p>

# Wagtail Ninja

[![Build status](https://github.com/torchbox/wagtail-grapple/actions/workflows/ci.yml/badge.svg)](https://github.com/torchbox/wagtail-grapple/actions)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPi](https://img.shields.io/pypi/v/wagtail-wagtail_ninja.svg)](https://pypi.org/project/wagtail-grapple/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/torchbox/wagtail-grapple/main.svg)](https://results.pre-commit.ci/latest/github/torchbox/wagtail-grapple/main)

A library to build GraphQL endpoints easily so you can grapple your Wagtail data from anywhere!

[Explore the docs »](https://wagtail-wagtail_ninja.readthedocs.io/en/latest/) ·
[Report Bug](https://github.com/torchbox/wagtail-grapple/issues) ·
[Request Feature](https://github.com/torchbox/wagtail-grapple/issues)

## About The Project

Headless wagtail is a pain, adding an openapi spec and ninja api should help frontend libraries access wagtail content easier 

No complex serializers need to be written - just add a `wagtail_ninja_fields` list
to your model and away you go (although if you want to go deeper you can!).

### Features

-   Easily create wagtail ninja types by adding a small annotation in your models.
-   Supports traditional Wagtail models:
    -   Pages (including StreamField & Orderables)
    -   Snippets
    -   Images
    -   Documents
    -   Media (via [wagtailmedia](https://pypi.org/project/wagtailmedia/))
    -   Settings
    -   Redirects
    -   Search (on all models)
-   Custom Image & Document model support
-   Pagination support
-   Middleware support

### Built With

This library is an abstraction upon and relies heavily on Ninja, Ninja Extra & Pydantic

## Getting Started

Getting Wagtail Ninja installed is designed to be as simple as possible!

### Prerequisites

```
Python >= 3.8
Wagtail >= 5.2
Django >= 4.2
```

### Installation

Install using pip

```bash
python -m pip install wagtail_ninja
```

Add the following to the `INSTALLED_APPS` list in your Wagtail settings file:

```python
INSTALLED_APPS = [
    # ...
    "wagtail_ninja",
    # ...
]
```

Add the following to the bottom of the same settings file, where each key is the app you want to this library to scan and the value is the prefix you want to give to GraphQL types (you can usually leave this blank):

```python
# Grapple config:
WAGTAIL_NINJA = {
    "APPS": ["home"],
}
```

Add the wagtail ninja URLs to your `urls.py`:

```python
from django.urls import include, path
from wagtail_ninja import urls as wagtail_ninja_urls

# ...
urlpatterns = [
    # ...
    path("api/", include(wagtail_ninja_urls)),
    # ...
]
```

Done! Now you can proceed onto configuring your models to generate GraphQL types that adopt their structure :tada:
_Your Openapi spec and endpoints are available at [http://localhost:8000/api/wagtail_ninja/docs](http://localhost:8000/api/graphql/)_

## Usage

Here is a model configuration for the default page from the Wagtail docs:

```python
# ...
from src.wagtail_ninja.models import GraphQLString, GraphQLStreamfield


class BlogPage(Page):
    author = models.CharField(max_length=255)
    date = models.DateField("Post date")
    body = StreamField(
        [
            ("heading", blocks.CharBlock(classname="full title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ]
    )

    content_panels = Page.content_panels + [
        FieldPanel("author"),
        FieldPanel("date"),
        StreamFieldPanel("body"),
    ]

    # Note these fields below:
    wagtail_ninja_fields = [
        GraphQLString("heading"),
        GraphQLString("date"),
        GraphQLString("author"),
        GraphQLStreamfield("body"),
    ]
```

_For more examples, please refer to the [Documentation](https://wagtail-wagtail_ninja.readthedocs.io/en/latest/)_

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create.
Any contributions [you make](https://github.com/torchbox/wagtail-grapple/graphs/contributors) are **greatly appreciated**.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Local development

-   In the Python environment of your choice, navigate to `tests/`
-   Run `python -m pip install -r requirements.txt`
-   Run `python manage.py migrate`
-   Run server `python manage.py runserver`
-   Run tests `python manage.py test`

#### With Postgres

-   Ensure you have docker and docker compose
-   Run `docker compose up`
-   Run `export DATABASE_URL="postgres://postgres:postgres@localhost/postgres"`
-   In the Python environment of your choice, navigate to `tests/`
-   Run `python -m pip install -r requirements.txt`
-   Run `python manage.py migrate`
-   Run server `python manage.py runserver`
-   Run tests `python manage.py test`

## Compatibility

Wagtail Ninja supports:

-   Python 3.8, 3.9, 3.10 3.11 and 3.12
-   Wagtail >= 5.2

## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- ACKNOWLEDGEMENTS -->

## Inspired by
- wagtail_grapple
