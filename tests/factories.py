import factory
import wagtail_factories
from faker import Faker
from testapp.models import DifferentPage, ExamplePage

fake = Faker()


class ExamplePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ExamplePage

    title = factory.Faker("sentence")
    body = factory.LazyFunction(lambda: "\n".join(fake.paragraphs()))


class DifferentPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = DifferentPage

    body = factory.LazyFunction(lambda: "\n".join(fake.paragraphs()))
