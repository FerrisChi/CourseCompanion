from django.db import models

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class MyUser(AbstractUser):
    # use _ to mark strings for translation
    phone_number = models.CharField(_("Phone number"), max_length=15, blank=True, null=True)
    address = models.TextField(_("Address"), blank=True, null=True)
    profile_picture = models.ImageField(_("Profile picture"), upload_to="profile_pictures/", blank=True, null=True)
    profile = models.TextField(_("Profile"), blank=True, null=True)
    class Meta:
        verbose_name = _("MyUser")
        verbose_name_plural = _("MyUsers")

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "phone_number": self.phone_number,
            "address": self.address,
            "profile": self.profile,
        }
    
    def __json__(self):
        return self.to_json()

class UserFile(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="user_files/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("UserFile")
        verbose_name_plural = _("UserFiles")

    def __str__(self):
        return self.user.username + " - " + self.file.name