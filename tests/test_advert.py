from django.test import RequestFactory, override_settings
from test_grapple import BaseWagtailNinjaTestWithIntrospection
from testapp.factories import AdvertFactory


class AdvertTest(BaseWagtailNinjaTestWithIntrospection):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.richtext_sample = (
            f'Text with a \'link\' to <a linktype="page" id="{cls.home.id}">Home</a>'
        )
        cls.richtext_sample_rendered = (
            f"Text with a 'link' to <a href=\"{cls.home.url}\">Home</a>"
        )
        cls.advert = AdvertFactory(
            rich_text=cls.richtext_sample, extra_rich_text=cls.richtext_sample
        )

    def setUp(self):
        super().setUp()
        self.request = RequestFactory()

    def validate_advert(self, advert):
        # Check all the fields
        self.assertTrue(isinstance(advert["id"], str))
        self.assertTrue(isinstance(advert["url"], str))
        self.assertTrue(isinstance(advert["text"], str))

    def test_advert_all_query(self):
        query = """
        {
           adverts {
                id
                url
                text
            }
        }
        """
        executed = self.client.execute(query, context_value=self.request)
        advert = executed["data"]["adverts"][0]

        # Check all the fields
        self.validate_advert(advert)

    def test_advert_single_query(self):
        query = """
        query($url: String) {
           advert(url: $url) {
                id
                url
                text
            }
        }
        """
        executed = self.client.execute(
            query, variables={"url": self.advert.url}, context_value=self.request
        )
        advert = executed["data"]["advert"]

        # Check all the fields
        self.validate_advert(advert)

    def test_advert_all_query_required(self):
        adverts_query = list(
            filter(
                lambda x: x["name"] == "adverts",
                self.introspect_schema_for_available_queries(),
            )
        )[0]
        adverts_query_type = adverts_query["type"]["ofType"]

        self.assertEqual(adverts_query["type"]["kind"], "NON_NULL")
        self.assertEqual(adverts_query_type["kind"], "LIST")
        self.assertEqual(adverts_query_type["ofType"]["kind"], "NON_NULL")
        self.assertEqual(adverts_query_type["ofType"]["ofType"]["kind"], "OBJECT")
        self.assertEqual(adverts_query_type["ofType"]["ofType"]["name"], "Advert")

    def test_advert_single_query_required(self):
        advert_query = list(
            filter(
                lambda x: x["name"] == "advert",
                self.introspect_schema_for_available_queries(),
            )
        )[0]
        advert_query_type = advert_query["type"]["ofType"]

        self.assertEqual(advert_query["type"]["kind"], "NON_NULL")
        self.assertEqual(advert_query_type["kind"], "OBJECT")
        self.assertEqual(advert_query_type["name"], "Advert")

    def test_advert_single_query_rich_text(self):
        query = """
        query($url: String) {
           advert(url: $url) {
                richText
                stringRichText
                extraRichText
            }
        }
        """
        executed = self.client.execute(
            query, variables={"url": self.advert.url}, context_value=self.request
        )
        advert = executed["data"]["advert"]

        # Field declared with GraphQLRichText
        self.assertEqual(advert["richText"], self.richtext_sample_rendered)

        # Declared with GraphQLString, custom field source
        self.assertEqual(advert["stringRichText"], self.richtext_sample_rendered)

        # Declared with GraphQLString, default field source
        self.assertEqual(advert["extraRichText"], self.richtext_sample_rendered)

        with override_settings(WAGTAIL_NINJA={"RICHTEXT_FORMAT": "raw"}):
            executed = self.client.execute(
                query, variables={"url": self.advert.url}, context_value=self.request
            )
            advert = executed["data"]["advert"]
            self.assertEqual(advert["richText"], self.richtext_sample)
            self.assertEqual(advert["stringRichText"], self.richtext_sample)
            self.assertEqual(advert["extraRichText"], self.richtext_sample)
