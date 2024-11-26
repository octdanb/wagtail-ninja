import unittest

from pydoc import locate
from unittest.mock import patch

import wagtail_factories

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import RequestFactory, TestCase, override_settings
from graphene.test import Client
from testapp.factories import AdvertFactory, BlogPageFactory, PersonFactory
from testapp.models import GlobalSocialMediaSettings, HomePage, SocialMediaSettings
from wagtail.documents import get_document_model
from wagtail.models import Page, Site
from wagtailmedia.models import get_media_model

from wagtail_ninja.registry import RegistryItem
from wagtail_ninja.schema import create_schema


SCHEMA = locate(settings.GRAPHENE["SCHEMA"])
MIDDLEWARE_OBJECTS = [
    locate(middleware) for middleware in settings.GRAPHENE["MIDDLEWARE"]
]
MIDDLEWARE = [item() if isinstance(item, type) else item for item in MIDDLEWARE_OBJECTS]


class BaseWagtailNinjaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.first()

    def setUp(self):
        self.client = Client(SCHEMA, middleware=MIDDLEWARE)


class BaseWagtailNinjaTestWithIntrospection(BaseWagtailNinjaTest):
    def introspect_schema_for_available_queries(self):
        query = """
        query availableQueries {
          __schema {
            queryType {
              fields{
                name
                type {
                  kind
                  ofType {
                    name
                    kind
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                        }
                    }
                  }
                }
              }
            }
          }
        }
        """
        return self.client.execute(query)["data"]["__schema"]["queryType"]["fields"]

    def introspect_schema_by_type(self, object_type: str):
        """
        Introspect the schema for a given type name.
        """
        query = """
        query schemaByType ($type: String!) {
            __type(name: $type) {
                name
                fields {
                    name
                    type {
                        name
                        kind
                    }
                    args {
                        name
                        type {
                            name
                            kind
                        }
                        description
                    }
                }
                interfaces {
                    name
                }
            }
        }
        """
        return self.client.execute(query, variables={"type": object_type})


class PagesTest(BaseWagtailNinjaTest):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.blog_post = BlogPageFactory(parent=self.home)

        self.site_different_hostname = wagtail_factories.SiteFactory(
            hostname="wagtail-ninja-hook.localhost",
            site_name="Wagtail Ninja test site (different hostname)",
        )

        self.site_different_hostname_different_port = wagtail_factories.SiteFactory(
            hostname="wagtail-ninja-hook.localhost",
            port=8000,
            site_name="Wagtail Ninja site (different hostname/port)",
        )

    def test_pages(self):
        query = """
        {
            pages {
                id
                title
                contentType
                pageType
            }
        }
        """

        executed = self.client.execute(query)

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["pages"]), list)
        self.assertEqual(type(executed["data"]["pages"][0]), dict)

        pages_data = executed["data"]["pages"]
        self.assertEqual(pages_data[0]["contentType"], "testapp.HomePage")
        self.assertEqual(pages_data[0]["pageType"], "HomePage")
        self.assertEqual(pages_data[1]["contentType"], "testapp.BlogPage")
        self.assertEqual(pages_data[1]["pageType"], "BlogPage")

        pages = Page.objects.filter(depth__gt=1)
        self.assertEqual(len(executed["data"]["pages"]), pages.count())

    @override_settings(WAGTAIL_NINJA={"PAGE_SIZE": 1, "MAX_PAGE_SIZE": 1})
    def test_pages_limit(self):
        query = """
        {
            pages(limit: 5) {
                id
                title
                contentType
                pageType
            }
        }
        """

        executed = self.client.execute(query)

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["pages"]), list)
        self.assertEqual(type(executed["data"]["pages"][0]), dict)

        pages_data = executed["data"]["pages"]
        self.assertEqual(pages_data[0]["contentType"], "testapp.HomePage")
        self.assertEqual(pages_data[0]["pageType"], "HomePage")
        self.assertEqual(len(executed["data"]["pages"]), 1)

    def test_pages_in_site(self):
        query = """
        {
            pages(inSite: true) {
                title
                contentType
                pageType
            }
        }
        """

        request = self.factory.get("/")
        executed = self.client.execute(query, context_value=request)

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["pages"]), list)
        self.assertEqual(type(executed["data"]["pages"][0]), dict)

        site = Site.find_for_request(request)
        pages = Page.objects.in_site(site).live().public().filter(depth__gt=1)

        self.assertEqual(len(executed["data"]["pages"]), pages.count())

    def test_pages_site(self):
        site = Site.objects.get(is_default_site=True)

        query = """
        query($site: String) {
            pages(site: $site) {
                title
                contentType
                pageType
            }
        }
        """

        request = self.factory.get("/")
        executed = self.client.execute(
            query,
            context_value=request,
            variables={
                "site": site.hostname,
            },
        )

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["pages"]), list)
        self.assertEqual(type(executed["data"]["pages"][0]), dict)

        pages = Page.objects.in_site(site).live().public().filter(depth__gt=1)

        self.assertEqual(len(executed["data"]["pages"]), pages.count())

    def test_pages_site_returns_empty_list_when_no_site_found(
        self,
    ):
        query = """
        query($site: String) {
            pages(site: $site) {
                title
                contentType
                pageType
            }
        }
        """

        executed = self.client.execute(query, variables={"site": "does.not.exist"})

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["pages"]), list)
        self.assertEqual(len(executed["data"]["pages"]), 0)

    def test_pages_site_errors_when_multiple_sites_match_hostname_and_port_unspecified(
        self,
    ):
        query = """
        query($site: String) {
            pages(site: $site) {
                title
                contentType
                pageType
            }
        }
        """

        executed = self.client.execute(
            query, variables={"site": self.site_different_hostname.hostname}
        )

        self.assertEqual(
            executed,
            {
                "errors": [
                    {
                        "message": (
                            f"Your filter `site={self.site_different_hostname.hostname}` returned "
                            "multiple sites. Try including a port number to disambiguate "
                            f"(e.g. `site={self.site_different_hostname.hostname}:8000`)."
                        ),
                        "locations": [{"line": 3, "column": 13}],
                        "path": ["pages"],
                    }
                ],
                "data": None,
            },
        )

    def test_pages_site_with_different_port(self):
        query = """
        query($site: String) {
            pages(site: $site) {
                title
                contentType
                pageType
            }
        }
        """

        executed = self.client.execute(
            query,
            variables={"site": f"{self.site_different_hostname.hostname}:8000"},
        )

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["pages"]), list)

        pages = (
            Page.objects.in_site(self.site_different_hostname)
            .live()
            .public()
            .filter(depth__gt=1)
        )

        self.assertEqual(len(executed["data"]["pages"]), pages.count())

    def test_pages_site_and_in_site_cannot_be_used_together(
        self,
    ):
        query = """
        query($site: String) {
            pages(site: $site, inSite: true) {
                title
                contentType
                pageType
            }
        }
        """

        executed = self.client.execute(
            query, variables={"site": self.site_different_hostname.hostname}
        )

        self.assertEqual(
            executed,
            {
                "errors": [
                    {
                        "message": "The 'site' and 'in_site' filters cannot be used at "
                        "the same time.",
                        "locations": [{"line": 3, "column": 13}],
                        "path": ["pages"],
                    }
                ],
                "data": None,
            },
        )

    def test_pages_content_type_filter(self):
        query = """
        query($content_type: String) {
            pages(contentType: $content_type) {
                id
                title
                contentType
                pageType
            }
        }
        """

        results = self.client.execute(
            query, variables={"content_type": "testapp.HomePage"}
        )
        data = results["data"]["pages"]
        self.assertEqual(len(data), 1)
        self.assertEqual(int(data[0]["id"]), self.home.id)

        another_post = BlogPageFactory(parent=self.home)
        results = self.client.execute(
            query, variables={"content_type": "testapp.BlogPage"}
        )
        data = results["data"]["pages"]
        self.assertEqual(len(data), 2)
        self.assertListEqual(
            [int(p["id"]) for p in data], [self.blog_post.id, another_post.id]
        )

        results = self.client.execute(
            query, variables={"content_type": "testapp.HomePage,testapp.BlogPage"}
        )
        data = results["data"]["pages"]
        self.assertEqual(len(data), 3)
        self.assertListEqual(
            [int(p["id"]) for p in data],
            [self.home.id, self.blog_post.id, another_post.id],
        )

        results = self.client.execute(
            query, variables={"content_type": "bogus.ContentType"}
        )
        self.assertListEqual(results["data"]["pages"], [])

    def test_page(self):
        query = """
        query($id: ID) {
            page(id: $id) {
                contentType
                parent {
                    contentType
                }
            }
        }
        """

        executed = self.client.execute(query, variables={"id": self.blog_post.id})

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["page"]), dict)

        page_data = executed["data"]["page"]
        self.assertEqual(page_data["contentType"], "testapp.BlogPage")
        self.assertEqual(page_data["parent"]["contentType"], "testapp.HomePage")

    def test_pages_ancestor_filter(self):
        p1_1 = BlogPageFactory(slug="D1-1", parent=self.home)
        p1_1_1 = BlogPageFactory(slug="D1-1-1", parent=p1_1)
        BlogPageFactory(slug="D1-1-1-1", parent=p1_1_1)
        BlogPageFactory(slug="D1-1-1-2", parent=p1_1_1)
        p1_1_2 = BlogPageFactory(slug="D1-1-2", parent=p1_1)
        BlogPageFactory(slug="D1-1-2-1", parent=p1_1_2)
        BlogPageFactory(slug="D1-1-2-2", parent=p1_1_2)
        p1_2 = BlogPageFactory(slug="D1-2", parent=self.home)
        p1_2_1 = BlogPageFactory(slug="D1-2-1", parent=p1_2)
        BlogPageFactory(slug="D1-2-1-1", parent=p1_2_1)
        BlogPageFactory(slug="D1-2-1-2", parent=p1_2_1)
        p1_2_2 = BlogPageFactory(slug="D1-2-2", parent=p1_2)
        BlogPageFactory(slug="D1-2-2-1", parent=p1_2_2)
        BlogPageFactory(slug="D1-2-2-2", parent=p1_2_2)

        query = """
        query($ancestor: ID) {
            pages(ancestor: $ancestor) {
                id
                urlPath
                depth
                live
                contentType
                pageType
            }
        }
        """

        executed = self.client.execute(query, variables={"ancestor": p1_2.id})
        page_data = executed["data"].get("pages")
        self.assertEqual(len(page_data), 6)
        for page in page_data:
            self.assertTrue(page["urlPath"].startswith(p1_2.url_path))

    def test_pages_parent_filter(self):
        p1_1 = BlogPageFactory(slug="D1-1", parent=self.home)
        p1_1_1 = BlogPageFactory(slug="D1-1-1", parent=p1_1)
        BlogPageFactory(slug="D1-1-1-1", parent=p1_1_1)
        BlogPageFactory(slug="D1-1-1-2", parent=p1_1_1)
        p1_1_2 = BlogPageFactory(slug="D1-1-2", parent=p1_1)
        BlogPageFactory(slug="D1-1-2-1", parent=p1_1_2)
        BlogPageFactory(slug="D1-1-2-2", parent=p1_1_2)
        p1_2 = BlogPageFactory(slug="D1-2", parent=self.home)
        p1_2_1 = BlogPageFactory(slug="D1-2-1", parent=p1_2)
        BlogPageFactory(slug="D1-2-1-1", parent=p1_2_1)
        BlogPageFactory(slug="D1-2-1-2", parent=p1_2_1)
        p1_2_2 = BlogPageFactory(slug="D1-2-2", parent=p1_2)
        BlogPageFactory(slug="D1-2-2-1", parent=p1_2_2)
        BlogPageFactory(slug="D1-2-2-2", parent=p1_2_2)

        query = """
        query($parent: ID) {
            pages(parent: $parent) {
                id
                urlPath
                depth
                live
                contentType
                pageType
            }
        }
        """

        executed = self.client.execute(query, variables={"parent": p1_2.id})
        page_data = executed["data"].get("pages")

        self.assertEqual(len(page_data), 2)
        for page in page_data:
            self.assertTrue(page["urlPath"].startswith(p1_2.url_path))
            self.assertEqual(page["depth"], p1_2.depth + 1)


class PagesSearchTest(BaseWagtailNinjaTest):
    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.first()
        BlogPageFactory(
            title="Alpha",
            body=[("heading", "Sigma")],
            parent=cls.home,
            show_in_menus=True,
        )
        BlogPageFactory(
            title="Alpha Alpha", body=[("heading", "Sigma Sigma")], parent=cls.home
        )
        BlogPageFactory(
            title="Alpha Beta", body=[("heading", "Sigma Theta")], parent=cls.home
        )
        BlogPageFactory(
            title="Alpha Gamma", body=[("heading", "Sigma Delta")], parent=cls.home
        )
        BlogPageFactory(title="Beta", body=[("heading", "Theta")], parent=cls.home)
        BlogPageFactory(
            title="Beta Alpha", body=[("heading", "Theta Sigma")], parent=cls.home
        )
        BlogPageFactory(
            title="Beta Beta", body=[("heading", "Theta Theta")], parent=cls.home
        )
        BlogPageFactory(
            title="Beta Gamma", body=[("heading", "Theta Delta")], parent=cls.home
        )
        BlogPageFactory(title="Gamma", body=[("heading", "Delta")], parent=cls.home)
        BlogPageFactory(
            title="Gamma Alpha", body=[("heading", "Delta Sigma")], parent=cls.home
        )
        BlogPageFactory(
            title="Gamma Beta", body=[("heading", "Delta Theta")], parent=cls.home
        )
        BlogPageFactory(
            title="Gamma Gamma", body=[("heading", "Delta Delta")], parent=cls.home
        )

    @unittest.skipIf(
        connection.vendor != "sqlite",
        "sqlite doesn't support annotating scores, so search results order will be in the order of defintion",
    )
    def test_searchQuery_order_by_relevance_sqlite(self):
        query = """
        query($searchQuery: String, $order: String) {
            pages(searchQuery: $searchQuery, order: $order) {
                title
                searchScore
            }
        }
        """

        executed = self.client.execute(query, variables={"searchQuery": "Alpha"})
        page_data = executed["data"].get("pages")
        self.assertEqual(len(page_data), 6)
        self.assertEqual(page_data[0]["title"], "Alpha")
        self.assertEqual(page_data[0]["searchScore"], None)
        self.assertEqual(page_data[1]["title"], "Alpha Alpha")
        self.assertEqual(page_data[1]["searchScore"], None)
        self.assertEqual(page_data[2]["title"], "Alpha Beta")
        self.assertEqual(page_data[2]["searchScore"], None)
        self.assertEqual(page_data[3]["title"], "Alpha Gamma")
        self.assertEqual(page_data[3]["searchScore"], None)
        self.assertEqual(page_data[4]["title"], "Beta Alpha")
        self.assertEqual(page_data[4]["searchScore"], None)
        self.assertEqual(page_data[5]["title"], "Gamma Alpha")
        self.assertEqual(page_data[5]["searchScore"], None)

    @unittest.skipIf(
        connection.vendor == "sqlite",
        "non-sqlite database backends should support annotating search score, so results should be orderd by score by default",
    )
    def test_searchQuery_order_by_relevance(self):
        query = """
        query($searchQuery: String, $order: String) {
            pages(searchQuery: $searchQuery, order: $order) {
                title
                searchScore
            }
        }
        """
        executed = self.client.execute(query, variables={"searchQuery": "Alpha"})
        page_data = executed["data"].get("pages")
        self.assertEqual(len(page_data), 6)
        self.assertEqual(page_data[0]["title"], "Alpha Alpha")
        self.assertEqual(page_data[0]["searchScore"], 0.23700128495693207)
        self.assertEqual(page_data[1]["title"], "Alpha")
        self.assertEqual(page_data[1]["searchScore"], 0.18960101902484894)
        self.assertEqual(page_data[2]["title"], "Gamma Alpha")
        self.assertEqual(page_data[2]["searchScore"], 0.11060059443116188)
        self.assertEqual(page_data[3]["title"], "Beta Alpha")
        self.assertEqual(page_data[3]["searchScore"], 0.11060059443116188)
        self.assertEqual(page_data[4]["title"], "Alpha Gamma")
        self.assertEqual(page_data[4]["searchScore"], 0.11060059443116188)
        self.assertEqual(page_data[5]["title"], "Alpha Beta")
        self.assertEqual(page_data[5]["searchScore"], 0.10533389945824942)

    def test_explicit_order(self):
        query = """
        query($searchQuery: String, $order: String) {
            pages(searchQuery: $searchQuery, order: $order) {
                title
            }
        }
        """
        executed = self.client.execute(
            query, variables={"searchQuery": "Gamma", "order": "-title"}
        )
        page_data = executed["data"].get("pages")
        self.assertEqual(len(page_data), 6)
        self.assertEqual(page_data[0]["title"], "Gamma Gamma")
        self.assertEqual(page_data[1]["title"], "Gamma Beta")
        self.assertEqual(page_data[2]["title"], "Gamma Alpha")
        self.assertEqual(page_data[3]["title"], "Gamma")
        self.assertEqual(page_data[4]["title"], "Beta Gamma")
        self.assertEqual(page_data[5]["title"], "Alpha Gamma")

    def test_search_in_menus(self):
        query = """
        query($searchQuery: String, $inMenu: Boolean) {
            pages(searchQuery: $searchQuery, inMenu: $inMenu) {
                title
            }
        }
        """
        executed = self.client.execute(query, variables={"inMenu": True})
        page_data = executed["data"].get("pages")
        self.assertEqual(len(page_data), 1)
        self.assertEqual(page_data[0]["title"], "Alpha")

    def test_search_not_in_menus(self):
        query = """
        query($searchQuery: String, $inMenu: Boolean) {
            pages(searchQuery: $searchQuery, inMenu: $inMenu, limit: 100) {
                title
            }
        }
        """
        executed = self.client.execute(query, variables={"inMenu": False})
        page_data = executed["data"].get("pages")
        self.assertEqual(len(page_data), 12)  # 11 blog pages + home page

    def test_search_operator_default(self):
        """default operator is and"""
        query = """
        query($searchQuery: String) {
            pages(searchQuery: $searchQuery) {
                title
                searchScore
            }
        }
        """
        executed = self.client.execute(query, variables={"searchQuery": "Alpha Beta"})
        page_data = executed["data"].get("pages")
        self.assertEqual(len(page_data), 2)
        self.assertEqual(page_data[0]["title"], "Alpha Beta")
        self.assertEqual(page_data[1]["title"], "Beta Alpha")

    def test_search_operator_and(self):
        query = """
        query($searchQuery: String, $searchOperator: SearchOperatorEnum) {
            pages(searchQuery: $searchQuery, searchOperator: $searchOperator) {
                title
                searchScore
            }
        }
        """
        executed = self.client.execute(
            query, variables={"searchQuery": "Alpha Beta", "searchOperator": "AND"}
        )
        page_data = executed["data"].get("pages")
        self.assertEqual(len(page_data), 2)
        self.assertEqual(page_data[0]["title"], "Alpha Beta")
        self.assertEqual(page_data[1]["title"], "Beta Alpha")

    def test_search_operator_or(self):
        query = """
        query($searchQuery: String, $searchOperator: SearchOperatorEnum) {
            pages(searchQuery: $searchQuery, searchOperator: $searchOperator) {
                title
                searchScore
            }
        }
        """
        executed = self.client.execute(
            query, variables={"searchQuery": "Alpha Beta", "searchOperator": "OR"}
        )
        page_data = executed["data"].get("pages")
        self.assertEqual(len(page_data), 10)
        self.assertEqual(page_data[0]["title"], "Alpha")
        self.assertEqual(page_data[1]["title"], "Alpha Alpha")
        self.assertEqual(page_data[2]["title"], "Alpha Beta")
        self.assertEqual(page_data[3]["title"], "Alpha Gamma")
        self.assertEqual(page_data[4]["title"], "Beta")
        self.assertEqual(page_data[5]["title"], "Beta Alpha")
        self.assertEqual(page_data[6]["title"], "Beta Beta")
        self.assertEqual(page_data[7]["title"], "Beta Gamma")
        self.assertEqual(page_data[8]["title"], "Gamma Alpha")
        self.assertEqual(page_data[9]["title"], "Gamma Beta")


class PageUrlPathTest(BaseWagtailNinjaTest):
    def _query_by_path(self, path, *, in_site=False):
        query = """
        query($urlPath: String, $inSite: Boolean) {
            page(urlPath: $urlPath, inSite: $inSite) {
                id
                url
            }
        }
        """

        executed = self.client.execute(
            query, variables={"urlPath": path, "inSite": in_site}
        )
        return executed["data"].get("page")

    def test_page_url_path_filter(self):
        home_child = BlogPageFactory(slug="child", parent=self.home)
        parent = BlogPageFactory(slug="parent", parent=self.home)

        child = BlogPageFactory(slug="child", parent=parent)

        page_data = self._query_by_path("/parent/child/")
        self.assertEqual(int(page_data["id"]), child.id)

        # query without trailing slash
        page_data = self._query_by_path("/parent/child")
        self.assertEqual(int(page_data["id"]), child.id)

        # we have two pages with the same slug, however /home/child will
        # be returned first because of its position in the tree
        page_data = self._query_by_path("/child")
        self.assertEqual(int(page_data["id"]), home_child.id)

        page_data = self._query_by_path("/")
        self.assertEqual(int(page_data["id"]), self.home.id)

        page_data = self._query_by_path("foo/bar")
        self.assertIsNone(page_data)

    def test_with_multisite(self):
        home_child = BlogPageFactory(slug="child", parent=self.home)

        another_home = HomePage.objects.create(
            title="Another home", slug="another-home", path="00010002", depth=2
        )
        another_site = wagtail_factories.SiteFactory(
            site_name="Another site", root_page=another_home
        )
        another_child = BlogPageFactory(slug="child", parent=another_home)

        # with multiple sites, only the first one will be returned
        page_data = self._query_by_path("/child/")
        self.assertEqual(int(page_data["id"]), home_child.id)

        with patch(
            "wagtail.models.Site.find_for_request",
            return_value=another_site,
        ):
            page_data = self._query_by_path("/child/", in_site=True)
            self.assertEqual(int(page_data["id"]), another_child.id)

            page_data = self._query_by_path("/child", in_site=True)
            self.assertEqual(int(page_data["id"]), another_child.id)


class SitesTest(TestCase):
    def setUp(self):
        self.site = wagtail_factories.SiteFactory(
            hostname="wagtail_ninja.localhost", site_name="Grapple test site"
        )

        self.site_different_hostname = wagtail_factories.SiteFactory(
            hostname="wagtail_ninja-hook.localhost",
            site_name="Grapple test site (different hostname)",
        )

        self.site_different_hostname_different_port = wagtail_factories.SiteFactory(
            hostname="wagtail_ninja-hook.localhost",
            port=8000,
            site_name="Grapple test site (different hostname/port)",
        )

        self.client = Client(SCHEMA)
        self.home = HomePage.objects.first()

    def test_sites(self):
        query = """
        {
            sites {
                siteName
                hostname
                port
                isDefaultSite
                rootPage {
                    title
                }
                pages {
                    title
                }
            }
        }
        """

        executed = self.client.execute(query)

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["sites"]), list)
        self.assertEqual(len(executed["data"]["sites"]), Site.objects.count())

    def test_site(self):
        query = """
        query($hostname: String) {
            site(hostname: $hostname) {
                siteName
                pages {
                    title
                }
            }
        }
        """

        executed = self.client.execute(
            query, variables={"hostname": self.site.hostname}
        )

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["site"]), dict)
        self.assertEqual(type(executed["data"]["site"]["pages"]), list)

        self.assertEqual(executed["data"]["site"]["siteName"], "Grapple test site")

        pages = Page.objects.in_site(self.site)

        self.assertEqual(len(executed["data"]["site"]["pages"]), pages.count())
        self.assertNotEqual(
            len(executed["data"]["site"]["pages"]), Page.objects.count()
        )

    def test_site_returns_none_when_no_site_found(
        self,
    ):
        query = """
        query($hostname: String) {
            site(hostname: $hostname) {
                siteName
            }
        }
        """

        executed = self.client.execute(query, variables={"hostname": "does.not.exist"})

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["site"]), type(None))
        self.assertEqual(executed["data"]["site"], None)

    def test_site_errors_when_multiple_sites_match_hostname_and_port_unspecified(
        self,
    ):
        query = """
        query($hostname: String) {
            site(hostname: $hostname) {
                siteName
            }
        }
        """

        executed = self.client.execute(
            query, variables={"hostname": self.site_different_hostname.hostname}
        )

        self.assertEqual(
            executed,
            {
                "errors": [
                    {
                        "message": (
                            f"Your filter `hostname={self.site_different_hostname.hostname}` returned "
                            "multiple sites. Try including a port number to disambiguate "
                            f"(e.g. `hostname={self.site_different_hostname.hostname}:8000`)."
                        ),
                        "locations": [{"line": 3, "column": 13}],
                        "path": ["site"],
                    }
                ],
                "data": {"site": None},
            },
        )

    def test_site_with_different_port(self):
        query = """
        query($hostname: String) {
            site(hostname: $hostname) {
                siteName
            }
        }
        """

        executed = self.client.execute(
            query,
            variables={"hostname": self.site_different_hostname.hostname + ":8000"},
        )

        self.assertEqual(
            executed["data"]["site"]["siteName"],
            "Grapple test site (different hostname/port)",
        )

    def test_site_pages_content_type_filter(self):
        query = """
        query($hostname: String $content_type: String) {
            site(hostname: $hostname) {
                siteName
                pages(contentType: $content_type) {
                    title
                    contentType
                }
            }
        }
        """
        # wagtail_ninja test site root page
        results = self.client.execute(
            query,
            variables={
                "hostname": self.site.hostname,
                "content_type": "wagtailcore.Page",
            },
        )
        data = results["data"]["site"]["pages"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], self.site.root_page.title)

        # Shouldn't return any data
        results = self.client.execute(
            query,
            variables={
                "hostname": self.site.hostname,
                "content_type": "testapp.HomePage",
            },
        )
        data = results["data"]["site"]["pages"]
        self.assertEqual(len(data), 0)

        # localhost root page
        results = self.client.execute(
            query,
            variables={
                "hostname": self.home.get_site().hostname,
                "content_type": "testapp.HomePage",
            },
        )
        data = results["data"]["site"]["pages"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["contentType"], "testapp.HomePage")
        self.assertEqual(data[0]["title"], self.home.title)

        # Blog page under wagtail_ninja test site
        blog = BlogPageFactory(
            parent=self.site.root_page, title="post on wagtail_ninja test site"
        )
        results = self.client.execute(
            query,
            variables={
                "hostname": self.site.hostname,
                "content_type": "testapp.BlogPage",
            },
        )
        data = results["data"]["site"]["pages"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["contentType"], "testapp.BlogPage")
        self.assertEqual(data[0]["title"], blog.title)

        # Blog page under localhost
        blog = BlogPageFactory(parent=self.home, title="blog on localhost")
        results = self.client.execute(
            query,
            variables={
                "hostname": self.home.get_site().hostname,
                "content_type": "testapp.BlogPage",
            },
        )
        data = results["data"]["site"]["pages"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["contentType"], "testapp.BlogPage")
        self.assertEqual(data[0]["title"], blog.title)

    def test_site_page_slug_filter(self):
        query = """
        query($hostname: String $slug: String) {
            site(hostname: $hostname) {
                siteName
                page(slug: $slug) {
                    title
                }
            }
        }
        """
        # Blog page under wagtail_ninja test site
        blog = BlogPageFactory(
            parent=self.site.root_page,
            title="post on wagtail_ninja test site",
            slug="blog-page-1",
        )
        # wagtail_ninja test SiteObjectType page field
        results = self.client.execute(
            query,
            variables={
                "hostname": self.site.hostname,
                "slug": blog.slug,
            },
        )
        data = results["data"]["site"]["page"]
        self.assertIsNotNone(data)
        self.assertEqual(data["title"], blog.title)
        # Shouldn't return any data
        results = self.client.execute(
            query,
            variables={
                "hostname": self.site.hostname,
                "slug": "not-a-page-slug",
            },
        )
        data = results["data"]["site"]["page"]
        self.assertIsNone(data)

        # Blog page under localhost
        blog = BlogPageFactory(
            parent=self.home, title="blog on localhost", slug="blog-page-2"
        )
        results = self.client.execute(
            query,
            variables={
                "hostname": self.home.get_site().hostname,
                "slug": blog.slug,
            },
        )
        data = results["data"]["site"]["page"]
        self.assertIsNotNone(data)
        self.assertEqual(data["title"], blog.title)

    def test_site_page_url_path_filter(self):
        # These additional sites prevent the .relative_url() call below from returning a relative URL
        # They're not needed for this particular test
        self.site_different_hostname.delete()
        self.site_different_hostname_different_port.delete()

        query = """
        query($hostname: String $urlPath: String) {
            site(hostname: $hostname) {
                siteName
                page(urlPath: $urlPath) {
                    title
                }
            }
        }
        """
        # Blog page under wagtail_ninja test site
        blog = BlogPageFactory(
            parent=self.site.root_page,
            title="post on wagtail_ninja test site",
            slug="blog-page-1",
        )
        results = self.client.execute(
            query,
            variables={
                "hostname": self.site.hostname,
                "urlPath": blog.relative_url(current_site=self.site),
            },
        )
        data = results["data"]["site"]["page"]
        self.assertIsNotNone(data)
        self.assertEqual(data["title"], blog.title)
        # Shouldn't return any data
        results = self.client.execute(
            query,
            variables={
                "hostname": self.site.hostname,
                "urlPath": "/not-a-page-slug",
            },
        )
        data = results["data"]["site"]["page"]
        self.assertIsNone(data)

        # Blog page under localhost
        blog = BlogPageFactory(
            parent=self.home, title="blog on localhost", slug="blog-page-2"
        )
        results = self.client.execute(
            query,
            variables={
                "hostname": self.home.get_site().hostname,
                "urlPath": blog.relative_url(current_site=self.home.get_site()),
            },
        )
        data = results["data"]["site"]["page"]
        self.assertIsNotNone(data)
        self.assertEqual(data["title"], blog.title)

    def test_site_page_content_type_filter(self):
        query = """
        query($hostname: String $slug: String $content_type: String) {
            site(hostname: $hostname) {
                siteName
                page(slug: $slug, contentType: $content_type) {
                    title
                }
            }
        }
        """
        # Blog page under wagtail_ninjawagtail_ninja test site
        blog = BlogPageFactory(
            parent=self.site.root_page, title="post on wagtail_ninja test site"
        )
        results = self.client.execute(
            query,
            variables={
                "hostname": self.site.hostname,
                "slug": blog.slug,
                "content_type": "testapp.BlogPage",
            },
        )
        data = results["data"]["site"]["page"]
        self.assertIsNotNone(data)
        self.assertEqual(data["title"], blog.title)
        # Shouldn't return any data
        results = self.client.execute(
            query,
            variables={
                "hostname": self.site.hostname,
                "slug": blog.slug,
                "content_type": "testapp.HomePage",
            },
        )
        data = results["data"]["site"]["page"]
        self.assertIsNone(data)


@override_settings(WAGTAIL_NINJA={"AUTO_CAMELCASE": False})
class DisableAutoCamelCaseTest(TestCase):
    def setUp(self):
        schema = create_schema()
        self.client = Client(schema)

    def test_disable_auto_camel_case(self):
        query = """
        {
            pages {
                title
                url_path
            }
        }
        """
        executed = self.client.execute(query)

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["pages"]), list)
        self.assertEqual(type(executed["data"]["pages"][0]), dict)
        self.assertEqual(type(executed["data"]["pages"][0]["title"]), str)
        self.assertEqual(type(executed["data"]["pages"][0]["url_path"]), str)

        # note: not using .all() as the pages query returns all pages with a depth > 1. Wagtail will normally have
        # only one page at depth 1 (RootPage). everything else lives under it.
        pages = Page.objects.filter(depth__gt=1)

        self.assertEqual(len(executed["data"]["pages"]), pages.count())


class DocumentsTest(BaseWagtailNinjaTest):
    def setUp(self):
        super().setUp()
        self.document_model = get_document_model()
        self.assertEqual(self.document_model.objects.all().count(), 0)

        uploaded_file = SimpleUploadedFile("example.txt", b"Hello world!")
        self.example_document = self.document_model(
            title="Example File", file=uploaded_file
        )
        self.example_document.full_clean()
        self.example_document.save()
        self.example_document.get_file_hash()
        self.example_document.get_file_size()
        self.assertEqual(self.document_model.objects.all().count(), 1)

    def test_properties_on_saved_example_document(self):
        example_doc = self.document_model.objects.first()

        self.assertEqual(example_doc.id, 1)
        self.assertEqual(example_doc.title, "Example File")
        with example_doc.open_file() as file:
            file.seek(0)
            self.assertEqual(file.readline(), b"Hello world!")

        self.assertNotEqual(example_doc.file_hash, "")
        self.assertNotEqual(example_doc.file_size, None)

    def test_query_documents_id(self):
        query = """
        {
            documents {
                id
                customDocumentProperty
            }
        }
        """

        executed = self.client.execute(query)

        documents = self.document_model.objects.all()

        self.assertEqual(len(executed["data"]["documents"]), documents.count())
        self.assertEqual(
            executed["data"]["documents"][0]["id"], str(self.example_document.id)
        )
        self.assertEqual(
            executed["data"]["documents"][0]["customDocumentProperty"],
            "Document Model!",
        )

    def test_query_file_field(self):
        query = """
        {
            documents {
                id
                file
            }
        }
        """

        executed = self.client.execute(query)

        self.assertEqual(
            executed["data"]["documents"][0]["file"], self.example_document.file.name
        )

    def test_query_file_hash_field(self):
        query = """
        {
            documents {
                id
                fileHash
            }
        }
        """

        executed = self.client.execute(query)

        self.assertEqual(
            executed["data"]["documents"][0]["fileHash"],
            self.example_document.file_hash,
        )

    def test_query_file_size_field(self):
        query = """
        {
            documents {
                id
                fileSize
            }
        }
        """

        executed = self.client.execute(query)

        self.assertEqual(
            executed["data"]["documents"][0]["fileSize"],
            self.example_document.file_size,
        )

    def test_query_url_field_with_default_document_serve_method(self):
        query = """
        {
            documents {
                id
                url
            }
        }
        """

        executed = self.client.execute(query)

        self.assertEqual(
            executed["data"]["documents"][0]["url"],
            "http://localhost:8000" + self.example_document.url,
        )

    def test_query_url_field_with_direct_document_serve_method(self):
        serve_method_at_test_start = settings.WAGTAILDOCS_SERVE_METHOD
        settings.WAGTAILDOCS_SERVE_METHOD = "direct"
        query = """
        {
            documents {
                id
                url
            }
        }
        """

        executed = self.client.execute(query)

        self.assertEqual(
            executed["data"]["documents"][0]["url"],
            "http://localhost:8000" + self.example_document.file.url,
        )
        settings.WAGTAILDOCS_SERVE_METHOD = serve_method_at_test_start

    def tearDown(self):
        self.example_document.file.delete()


class MediaTest(BaseWagtailNinjaTest):
    def setUp(self):
        super().setUp()

        self.media_model = get_media_model()
        self.assertEqual(self.media_model.objects.all().count(), 0)

        uploaded_file = SimpleUploadedFile("example.mp4", b"")
        self.media_item = self.media_model(
            title="Example Media File", file=uploaded_file, duration=0, type="video"
        )
        self.media_item.full_clean()
        self.media_item.save()
        self.assertEqual(self.media_model.objects.all().count(), 1)

    def test_properties_on_saved_example_media(self):
        media_item = self.media_model.objects.first()

        self.assertEqual(media_item.id, 1)
        self.assertEqual(media_item.title, "Example Media File")

    def test_query_media_id(self):
        query = """
        {
            media {
                id
            }
        }
        """

        executed = self.client.execute(query)

        media = self.media_model.objects.all()

        self.assertEqual(len(executed["data"]["media"]), media.count())
        self.assertEqual(executed["data"]["media"][0]["id"], str(self.media_item.id))

    def test_query_file_field(self):
        query = """
        {
            media {
                id
                file
            }
        }
        """

        executed = self.client.execute(query)

        self.assertEqual(
            executed["data"]["media"][0]["file"], self.media_item.file.name
        )

    def tearDown(self):
        self.media_item.file.delete()


class SettingsTest(BaseWagtailNinjaTest):
    def setUp(self):
        super().setUp()

        self.site_a = Site.objects.get()
        self.site_a.hostname = "a"
        self.site_a.save()

        self.site_b = Site.objects.create(
            hostname="b", port=80, root_page_id=self.site_a.root_page_id
        )

        self.site_a_settings = SocialMediaSettings.objects.create(
            site=self.site_a,
            facebook="https://facebook.com/site-a",
            instagram="site-a",
            trip_advisor="https://tripadvisor.com/site-a",
            youtube="https://youtube.com/site-a",
        )

        self.site_b_settings = SocialMediaSettings.objects.create(
            site=self.site_b,
            facebook="https://facebook.com/site-b",
            instagram="site-b",
            trip_advisor="https://tripadvisor.com/site-b",
            youtube="https://youtube.com/site-b",
        )

        self.global_settings = GlobalSocialMediaSettings.objects.create(
            facebook="https://facebook.com/global",
            instagram="global",
            trip_advisor="https://tripadvisor.com/global",
            youtube="https://youtube.com/global",
        )

    def test_query_single_setting(self):
        # This only works if there is a single Site, so let's make that true.
        self.site_b.delete()
        self.site_b_settings.delete()

        query = """
        {
            setting(name: "SocialMediaSettings") {
                ... on SocialMediaSettings {
                    facebook
                    instagram
                    tripAdvisor
                    youtube
                }
            }
        }
        """

        response = self.client.execute(query)

        self.assertEqual(
            response,
            {
                "data": {
                    "setting": {
                        "facebook": "https://facebook.com/site-a",
                        "instagram": "site-a",
                        "tripAdvisor": "https://tripadvisor.com/site-a",
                        "youtube": "https://youtube.com/site-a",
                    }
                }
            },
        )

    def test_query_single_setting_with_site_filter(self):
        query = """
        {
            setting(site: "b", name: "SocialMediaSettings") {
                ... on SocialMediaSettings {
                    facebook
                    instagram
                    tripAdvisor
                    youtube
                }
            }
        }
        """

        response = self.client.execute(query)

        self.assertEqual(
            response,
            {
                "data": {
                    "setting": {
                        "facebook": "https://facebook.com/site-b",
                        "instagram": "site-b",
                        "tripAdvisor": "https://tripadvisor.com/site-b",
                        "youtube": "https://youtube.com/site-b",
                    }
                }
            },
        )

    def test_query_single_setting_with_site_filter_clashing_port(self):
        # Create another site with the hostname "b" but a different port
        self.site_b_8080 = Site.objects.create(
            hostname="b", port=8080, root_page_id=self.site_a.root_page_id
        )

        query = """
        {
            setting(site: "b", name: "SocialMediaSettings") {
                ... on SocialMediaSettings {
                    facebook
                    instagram
                    tripAdvisor
                    youtube
                }
            }
        }
        """

        response = self.client.execute(query)

        self.assertEqual(
            response,
            {
                "errors": [
                    {
                        "message": (
                            f"Your filter `site={self.site_b.hostname}` returned "
                            "multiple sites. Try including a port number to disambiguate "
                            f"(e.g. `site={self.site_b.hostname}:8000`)."
                        ),
                        "locations": [{"line": 3, "column": 13}],
                        "path": ["setting"],
                    }
                ],
                "data": {"setting": None},
            },
        )

    def test_query_single_setting_with_site_filter_with_port(self):
        # Create another site with the hostname "b" but a different port
        self.site_b_8080 = Site.objects.create(
            hostname="b", port=8080, root_page_id=self.site_a.root_page_id
        )

        query = """
        {
            setting(site: "b:80", name: "SocialMediaSettings") {
                ... on SocialMediaSettings {
                    facebook
                    instagram
                    tripAdvisor
                    youtube
                }
            }
        }
        """

        response = self.client.execute(query)

        self.assertEqual(
            response,
            {
                "data": {
                    "setting": {
                        "facebook": "https://facebook.com/site-b",
                        "instagram": "site-b",
                        "tripAdvisor": "https://tripadvisor.com/site-b",
                        "youtube": "https://youtube.com/site-b",
                    }
                }
            },
        )

    def test_query_site_settings(self):
        query = """
        {
            settings(name: "SocialMediaSettings") {
                ... on SocialMediaSettings {
                    facebook
                    instagram
                    tripAdvisor
                    youtube
                }
            }
        }
        """

        response = self.client.execute(query)

        self.assertEqual(
            response,
            {
                "data": {
                    "settings": [
                        {
                            "facebook": "https://facebook.com/site-a",
                            "instagram": "site-a",
                            "tripAdvisor": "https://tripadvisor.com/site-a",
                            "youtube": "https://youtube.com/site-a",
                        },
                        {
                            "facebook": "https://facebook.com/site-b",
                            "instagram": "site-b",
                            "tripAdvisor": "https://tripadvisor.com/site-b",
                            "youtube": "https://youtube.com/site-b",
                        },
                    ]
                }
            },
        )

    def test_query_all_settings(self):
        query = """
        {
            settings {
                ... on SocialMediaSettings {
                    facebook
                    instagram
                    tripAdvisor
                    youtube
                }
                ... on GlobalSocialMediaSettings {
                    facebook
                    instagram
                    tripAdvisor
                    youtube
                }
            }
        }
        """

        response = self.client.execute(query)

        self.assertEqual(
            response,
            {
                "data": {
                    "settings": [
                        {
                            "facebook": "https://facebook.com/site-a",
                            "instagram": "site-a",
                            "tripAdvisor": "https://tripadvisor.com/site-a",
                            "youtube": "https://youtube.com/site-a",
                        },
                        {
                            "facebook": "https://facebook.com/site-b",
                            "instagram": "site-b",
                            "tripAdvisor": "https://tripadvisor.com/site-b",
                            "youtube": "https://youtube.com/site-b",
                        },
                        {
                            "facebook": "https://facebook.com/global",
                            "instagram": "global",
                            "tripAdvisor": "https://tripadvisor.com/global",
                            "youtube": "https://youtube.com/global",
                        },
                    ]
                }
            },
        )

    def test_query_all_settings_with_site_filter(self):
        query = """
        {
            settings(site: "b") {
                ... on SocialMediaSettings {
                    facebook
                    instagram
                    tripAdvisor
                    youtube
                }
                ... on GlobalSocialMediaSettings {
                    facebook
                    instagram
                    tripAdvisor
                    youtube
                }
            }
        }
        """

        response = self.client.execute(query)

        # Should return site-specific settings for site b and global settings
        self.assertEqual(
            response,
            {
                "data": {
                    "settings": [
                        {
                            "facebook": "https://facebook.com/site-b",
                            "instagram": "site-b",
                            "tripAdvisor": "https://tripadvisor.com/site-b",
                            "youtube": "https://youtube.com/site-b",
                        },
                        {
                            "facebook": "https://facebook.com/global",
                            "instagram": "global",
                            "tripAdvisor": "https://tripadvisor.com/global",
                            "youtube": "https://youtube.com/global",
                        },
                    ]
                }
            },
        )

    def test_query_single_setting_without_site_filter_and_multiple_sites(self):
        # Create another site so that querying for `SocialMediaSettings` is
        # ambiguous (i.e. which site should we be returning
        # `SocialMediaSettings` for?)
        wagtail_factories.SiteFactory()

        query = """
        {
            setting(name: "SocialMediaSettings") {
                ... on SocialMediaSettings {
                    facebook
                    instagram
                    tripAdvisor
                    youtube
                }
            }
        }
        """

        response = self.client.execute(query)

        self.assertEqual(
            response,
            {
                "errors": [
                    {
                        "message": (
                            "There are multiple `SocialMediaSettings` instances - "
                            "please include a `site` filter to disambiguate "
                            "(e.g. `setting(name: 'SocialMediaSettings', site='example.com')`."
                        ),
                        "locations": [{"column": 13, "line": 3}],
                        "path": ["setting"],
                    }
                ],
                "data": {"setting": None},
            },
        )


class SnippetsTest(BaseWagtailNinjaTest):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.advert = AdvertFactory()
        self.person = PersonFactory()

    def test_snippets(self):
        """
        Query for snippets of different schemas, they should all be returned in
        the same response.
        """

        query = """
        {
            snippets {
                snippetType
                contentType
            }
        }
        """

        executed = self.client.execute(query)

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["snippets"]), list)
        self.assertEqual(len(executed["data"]["snippets"]), 2)
        self.assertEqual(type(executed["data"]["snippets"][0]), dict)

        snippets_data = sorted(
            executed["data"]["snippets"], key=lambda s: s["snippetType"]
        )
        self.assertEqual(snippets_data[0]["snippetType"], "Advert")
        self.assertEqual(snippets_data[0]["contentType"], "testapp.Advert")
        self.assertEqual(snippets_data[1]["snippetType"], "Person")
        self.assertEqual(snippets_data[1]["contentType"], "testapp.Person")

    def test_no_snippet_classes_registered(self):
        """
        If there are no registered snippet classes, the snippets query should
        still work, and return nothing.
        """

        query = """
        {
            snippets {
                snippetType
                contentType
            }
        }
        """

        with patch("wagtail_ninja.registry.registry.snippets", RegistryItem()):
            executed = self.client.execute(query)

        self.assertEqual(type(executed["data"]), dict)
        self.assertEqual(type(executed["data"]["snippets"]), list)
        self.assertEqual(len(executed["data"]["snippets"]), 0)
