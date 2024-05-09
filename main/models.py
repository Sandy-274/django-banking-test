from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, primary_key=True)
    date_created = models.DateTimeField(default=timezone.now)
    dob = models.DateField(blank=True)
    is_active = models.BooleanField(default=True)
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    

    def __str__(self):
        return self.email

    def has_usable_password(self):
        return True

    @property
    def is_staff(self):
        return False

    @property
    def is_superuser(self):
        return False


class AccountInfo(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    account_number=models.BigIntegerField(primary_key=True)
    username=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    account_holder_name = models.CharField(max_length=50,default='')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,default='')
    pan_number = models.CharField(max_length=10,unique=True,null=True)
    aadhar_number = models.CharField(max_length=12,unique=True,null=True)
    amount=models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    
    def __str__(self):
        return self.account_holder_name

    
class Transaction(models.Model):
    account_number=models.ForeignKey(AccountInfo,on_delete=models.CASCADE)
    transaction_type=models.CharField(max_length=3)
    description=models.CharField(max_length=100)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    balance=models.DecimalField(max_digits=10,decimal_places=2)
    timestamp=models.DateTimeField(auto_now_add=True)