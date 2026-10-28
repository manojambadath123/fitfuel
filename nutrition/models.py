from django.db import models

# Create your models here.

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal


# =========================================================
# Custom User Model
# =========================================================

class User(AbstractUser):

    phone = models.CharField(max_length=15,unique=True)

    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ["email", "phone"]

    def __str__(self):
        return self.username


# =========================================================
# Profile Model
# =========================================================

class Profile(models.Model):

    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    ACTIVITY_LEVEL_CHOICES = (
        ("sedentary", "Sedentary"),
        ("light", "Lightly Active"),
        ("moderate", "Moderately Active"),
        ("active", "Active"),
        ("very_active", "Very Active"),
    )

    GOAL_CHOICES = (
        ("weight_loss", "Weight Loss"),
        ("maintenance", "Maintenance"),
        ("muscle_gain", "Muscle Gain"),
    )

    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")

    age = models.PositiveIntegerField()

    gender = models.CharField(max_length=20,choices=GENDER_CHOICES)

    height = models.DecimalField(max_digits=5,decimal_places=2,help_text="Height in CM")

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Weight in KG"
    )

    target_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    duration = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True
    )

    activity_level = models.CharField(
        max_length=20,
        choices=ACTIVITY_LEVEL_CHOICES
    )

    goal = models.CharField(
        max_length=20,
        choices=GOAL_CHOICES
    )

    bmi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False
    )

    daily_calorie_goal = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    profile_image = models.ImageField(
        upload_to="profile_images/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        # BMI Calculation
        if self.height and self.weight:

            height_in_meter = Decimal(self.height) / Decimal(100)

            self.bmi = round(
                Decimal(self.weight) / (height_in_meter ** 2),
                2
            )

        # =========================
        # BMR Calculation
        # =========================

        weight = float(self.weight)
        height = float(self.height)
        age = self.age

        if self.gender == "male":

            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5

        else:

            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        # =========================
        # Activity Multiplier
        # =========================

        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }

        tdee = bmr * activity_multipliers.get(
            self.activity_level,
            1.2
        )

        # =========================
        # Goal Adjustment
        # =========================

        
        # maintenance -> no change

        self.daily_calorie_goal = round(tdee)

        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.user.username} Profile"


# =========================================================
# Food Log Model
# =========================================================

class FoodLog(models.Model):

    MEAL_TYPE_CHOICES = (
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="food_logs"
    )

    title = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    image = models.ImageField(
        upload_to="food_logs/",
        null=True,
        blank=True
    )

    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPE_CHOICES
    )

    quantity = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Example: 1 Bowl, 250g"
    )

    calories = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        null=True,
        blank=True
    )

   
    consumed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.meal_type}"



from django.db import models
from django.utils import timezone
from datetime import timedelta


class Subscription(models.Model):

    STATUS_CHOICES = (
        ("active", "Active"),
        ("expired", "Expired"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="membership"
    )

    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=500
    )

    payment_date = models.DateField(
        default=timezone.now
    )

    end_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    payment_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        self.end_date = self.payment_date + timedelta(days=27)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
    

"""
from django.utils import timezone

if request.user.subscription.end_date >= timezone.now().date():
    print("Premium User")
else:
    print("Subscription Expired")

"""