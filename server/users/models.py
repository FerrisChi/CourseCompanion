from django.db import models

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class MyUser(AbstractUser):
    # use _ to mark strings for translation
    
    phone_number = models.CharField(_("Phone number"), max_length=15, blank=True, null=True)
    address = models.TextField(_("Address"), blank=True, null=True)
    profile_picture = models.ImageField(_("Profile picture"), upload_to="profile_pictures/", blank=True, null=True)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
