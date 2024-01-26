from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser, BaseUserManager,Permission, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)#(in default implemenation email can be blank, here we are customizing the EMAIL Authentication that is why we are 
    phone = models.TextField(max_length=20, blank=False, default=0)
    is_verified = models.BooleanField(default=False) 
    first_name = models.CharField(max_length=255,default=None)
    otp = models.CharField(max_length=6, blank=True, null=True)# mentioning the email as unique here we are overriding the parent class functionality)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='customuser_groups',  # Updated related_name
        related_query_name='customuser_group',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='customuser_user_permissions',  # Updated related_name
        related_query_name='customuser_user_permission',
    )


    USERNAME_FIELD = 'email'   # The username filed is used when login the django automatically checks with the field which is mention in USERNAME_FIELD  here dajngo checks with email
    REQUIRED_FIELDS = ['phone','first_name']  # Other than the USERNAME_FIELD (email) which one is required we have to mention here

    objects = CustomUserManager() # USER MANAGER id the default usernmanager
                            # but here we want more spec than the default therefore we created a CUSTOMUSER MANAGER and the  class CUSTOMUSER MANAGER extends the default base user manager 

    def __str__(self):
        return self.email
    
class Task(models.Model):
    user = models.ForeignKey(CustomUser,on_delete = models.CASCADE , null=True,blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True,blank=True)
    complete = models.BooleanField(default = False)
    date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering =['complete']
