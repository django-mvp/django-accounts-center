"""The template filters this package registers."""

from django.template import Context, Template

from dac.templatetags.dac import app_is_installed


class TestAppIsInstalled:
    """A card for a separately installable app has to tell "this project does
    not have that app" from "you have nothing there yet", and it is a template
    block with no view behind it, so it asks from the template."""

    def test_true_for_an_installed_app(self):
        assert app_is_installed("allauth.mfa") is True

    def test_false_for_an_app_that_is_not_installed(self):
        assert app_is_installed("allauth.headless") is False

    def test_reads_as_a_filter_in_a_condition(self):
        template = Template(
            '{% load dac %}{% if "allauth.mfa"|app_is_installed %}yes{% else %}no{% endif %}'
            '{% if "allauth.headless"|app_is_installed %}yes{% else %}no{% endif %}'
        )
        assert template.render(Context({})) == "yesno"
