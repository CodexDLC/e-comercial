from codex_django.system.mixins.settings import (
    AbstractSiteSettings,
    SiteContactSettingsMixin,
    SiteEmailSettingsMixin,
    SiteGeoSettingsMixin,
    SiteMarketingSettingsMixin,
    SiteSocialSettingsMixin,
    SiteTechnicalSettingsMixin,
)
from django.utils.translation import gettext_lazy as _


class SiteSettings(
    AbstractSiteSettings,
    SiteContactSettingsMixin,
    SiteGeoSettingsMixin,
    SiteSocialSettingsMixin,
    SiteMarketingSettingsMixin,
    SiteTechnicalSettingsMixin,
    SiteEmailSettingsMixin,
):
    """
    Global site settings.
    Automatically synchronized with Redis.
    """

    class Meta:
        verbose_name = _("Настройки сайта")
        verbose_name_plural = _("Настройки сайта")
