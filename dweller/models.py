from django.db import models
from django.utils.translation import gettext_lazy as _
from ..creator.models import BaseUser


class Dweller(models.Model):
    """
    The Dweller model represents users who can join and access stashes created by creators.
    """
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    date_joined_stash = models.DateTimeField(auto_now_add=True, verbose_name=_("Date Joined Stash"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        verbose_name = _("Dweller User")
        verbose_name_plural = _("Dweller Users")

    def __str__(self):
        return f'{self.user.id} {self.user.username}'

    @property
    def stashes_joined(self):
        """Returns the number of stashes this user has joined"""
        return self.user.accessible_stashes.count()  # Related name from Stash model
