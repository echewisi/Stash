from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from phonenumber_field.modelfields import PhoneNumberField
from .utils import encrypt_data, decrypt_data




class BaseUser(AbstractBaseUser):
    '''
the USER role reprsents the base user of the application. that is, the user that is neither a creator or a dweller of a stash
'''
    Role= (("Creator", "Creator"),  ("Dweller", "Dweller"), ("User", "User"))

    id=  models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)   
    username= models.CharField(max_length= 200, null= False, blank= False, verbose_name= _("UserName"))
    email = models.EmailField(unique=True,  verbose_name= _("Email Address"))
    phonenumber= PhoneNumberField(_("Phone"))
    role= models.CharField(choices= Role, null= False, blank= False) #set this to a default og 'User'
    otp= models.CharField(max_length= 6, unique= True, null= True)
    otp_sent_at= models.DateTimeField(auto_now_add=True, null= True)
    is_superuser= models.BooleanField(default= False)
    is_active= models.BooleanField(default= False)
    is_staff= models.BooleanField(default= False)
    is_verified= models.BooleanField(default= False)
    email_verified = models.BooleanField(default=False)
    reset_token = models.CharField(max_length=200, blank=True, null=True, default= None)
    reset_token_sent_at = models.DateTimeField(null=True, blank=True, auto_now_add= True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD= 'email'
    REQUIRED_FIELDS= ['username']
    objects = CustomUserManager()

    def __str__(self):
        return f'{self.username} {self.email} '



class CreatorUser(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    signing_key = models.CharField(max_length=200, unique=True, blank=False, null=False, )
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username



class Stash(models.Model):
    TYPE_CHOICES = (
        ('Invited', 'Invited'),
        ('Free Roam', 'Free Roam'),
    )

    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    creator = models.ForeignKey('CreatorUser', on_delete=models.CASCADE, related_name='stashes')
    name = models.CharField(max_length=255, verbose_name=_("Stash Name"))
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name=_("Stash Type"))
    content_url = models.URLField(max_length=500, verbose_name=_("Content URL"), blank=True, null=True)
    signing_key = models.CharField(max_length=200, unique=True, blank=False, null=False)
    cover_image = models.ImageField(upload_to='stash_covers/', blank=True, null=True, verbose_name=_("Cover Image"))
    dwellers = models.ManyToManyField('dweller.DwellerUser', related_name='accessible_stashes', blank=True)
    number_of_dwellers = models.PositiveIntegerField(default=0, verbose_name=_("Number of Dwellers"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Stash")
        verbose_name_plural = _("Stashes")

    def __str__(self):
        return f'{self.id} {self.name} by {self.creator.user.username}'


class DecryptionKey(models.Model):
    KEY_TYPE_CHOICES = (
        ('QR Code', 'QR Code'),
        ('URL', 'URL'),
        ('Code', 'Code'),
    )

    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    stash = models.ForeignKey('Stash', on_delete=models.CASCADE, related_name='decryption_keys')
    dweller = models.ForeignKey('dweller.DwellerUser', on_delete=models.CASCADE, related_name='decryption_keys')
    key_type = models.CharField(max_length=10, choices=KEY_TYPE_CHOICES, verbose_name=_("Key Type"))
    key_value = models.CharField(max_length=500, verbose_name=_("Decryption Key"))
    issued_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Used At"))

    class Meta:
        unique_together = ('stash', 'dweller')
        verbose_name = _("Decryption Key")
        verbose_name_plural = _("Decryption Keys")

    def __str__(self):
        return f'{self.id} - {self.stash.name}'
    
    def deactivate(self):
        self.is_active = False
        self.save()

    def generate_encrypted_key(self):
        # Combine signing key, stash ID, and dweller ID for encryption
        return encrypt_data(
            self.stash.signing_key, 
            str(self.stash.id), 
            str(self.dweller.id), 
            key_password="secure_shared_password"  # Or any password used for key derivation
        )

    def validate_decryption_key(self, encrypted_key):
        # Decrypt the received key and validate it
        decrypted_data = decrypt_data(encrypted_key, key_password="secure_shared_password")
        signing_key, stash_id, dweller_id = decrypted_data.split(":")
        return (
            signing_key == self.stash.signing_key and 
            stash_id == str(self.stash.id) and 
            dweller_id == str(self.dweller.id)
        )