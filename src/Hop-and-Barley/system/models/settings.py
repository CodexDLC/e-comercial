from codex_django.system.mixins.settings import (
    AbstractSiteSettings,
    SiteContactSettingsMixin,
    SiteEmailSettingsMixin,
    SiteGeoSettingsMixin,
    SiteMarketingSettingsMixin,
    SiteSocialSettingsMixin,
    SiteTechnicalSettingsMixin,
)
from django.db import models
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

    company_name = models.CharField(_("Company Name"), max_length=100, blank=True, default="Hop & Barley")
    site_description = models.TextField(_("Site Description"), blank=True)

    class Meta:
        verbose_name = _("Настройки сайта")
        verbose_name_plural = _("Настройки сайта")
