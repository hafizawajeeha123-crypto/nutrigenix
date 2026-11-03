from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    """
    Extended profile for every registered user.
    Linked 1-to-1 with Django's built-in User model.
    """

    # --- Gender choices ---
    GENDER_MALE   = 'M'
    GENDER_FEMALE = 'F'
    GENDER_OTHER  = 'O'
    GENDER_CHOICES = [
        (GENDER_MALE,   'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER,  'Other'),
    ]

    # --- Activity level choices (used in TDEE calculation) ---
    ACTIVITY_SEDENTARY   = 'sedentary'
    ACTIVITY_LIGHT       = 'light'
    ACTIVITY_MODERATE    = 'moderate'
    ACTIVITY_ACTIVE      = 'active'
    ACTIVITY_VERY_ACTIVE = 'very_active'
    ACTIVITY_CHOICES = [
        (ACTIVITY_SEDENTARY,   'Sedentary (little or no exercise)'),
        (ACTIVITY_LIGHT,       'Lightly active (exercise 1–3 days/week)'),
        (ACTIVITY_MODERATE,    'Moderately active (exercise 3–5 days/week)'),
        (ACTIVITY_ACTIVE,      'Very active (hard exercise 6–7 days/week)'),
        (ACTIVITY_VERY_ACTIVE, 'Extra active (physical job or 2x training)'),
    ]

    # --- Health goal choices ---
    GOAL_LOSE     = 'lose'
    GOAL_MAINTAIN = 'maintain'
    GOAL_GAIN     = 'gain'
    GOAL_CHOICES = [
        (GOAL_LOSE,     'Lose weight'),
        (GOAL_MAINTAIN, 'Maintain weight'),
        (GOAL_GAIN,     'Gain weight'),
    ]

    # --- Health condition choices (multi-select stored as separate BooleanFields) ---
    # See health condition fields below

    # --- Language preference ---
    LANG_EN  = 'en'
    LANG_RU  = 'roman_urdu'
    LANG_UR  = 'ur'
    LANG_CHOICES = [
        (LANG_EN, 'English'),
        (LANG_RU, 'Roman Urdu'),
        (LANG_UR, 'Urdu'),
    ]

    # Core link
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    # Physical data
    age            = models.PositiveSmallIntegerField(
                         validators=[MinValueValidator(5), MaxValueValidator(120)],
                         null=True, blank=True,
                     )
    gender         = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    height_cm      = models.DecimalField(
                         max_digits=5, decimal_places=1,
                         validators=[MinValueValidator(50), MaxValueValidator(250)],
                         null=True, blank=True,
                         help_text='Height in centimetres',
                     )
    weight_kg      = models.DecimalField(
                         max_digits=5, decimal_places=1,
                         validators=[MinValueValidator(10), MaxValueValidator(300)],
                         null=True, blank=True,
                         help_text='Current weight in kilograms',
                     )
    target_weight_kg = models.DecimalField(
                         max_digits=5, decimal_places=1,
                         null=True, blank=True,
                         help_text='Goal weight in kilograms',
                     )

    # Lifestyle
    activity_level = models.CharField(
                         max_length=20,
                         choices=ACTIVITY_CHOICES,
                         default=ACTIVITY_SEDENTARY,
                     )
    health_goal    = models.CharField(
                         max_length=10,
                         choices=GOAL_CHOICES,
                         default=GOAL_MAINTAIN,
    )

    # Calculated fields (updated whenever physical data changes)
    bmi            = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bmr            = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True,
                         help_text='Basal Metabolic Rate (kcal/day)')
    tdee           = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True,
                         help_text='Total Daily Energy Expenditure (kcal/day)')
    daily_calorie_goal = models.PositiveSmallIntegerField(null=True, blank=True,
                         help_text='Adjusted calorie target based on goal')
    
    
    
    
           # Health conditions (separate BooleanFields for easy Django ORM filtering)
    has_diabetes        = models.BooleanField(default=False)
    has_hypertension    = models.BooleanField(default=False)
    has_pcos            = models.BooleanField(default=False)
    has_thyroid_issue   = models.BooleanField(default=False)

    # App settings
    language_preference = models.CharField(
                              max_length=12,
                              choices=LANG_CHOICES,
                              default=LANG_EN,
                          )
    daily_water_goal_ml = models.PositiveSmallIntegerField(
                              default=2000,
                              help_text='Daily water intake target in ml',
                          )
# Premium fields
    is_premium        = models.BooleanField(default=False)
    premium_activated = models.DateTimeField(null=True, blank=True)
    premium_expires   = models.DateTimeField(null=True, blank=True)
    payment_method    = models.CharField(max_length=20, blank=True)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name        = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.user.username} — Profile'

    # ------------------------------------------------------------------
    # Helpers: calculate BMI, BMR, TDEE, and daily calorie goal
    # ------------------------------------------------------------------

    ACTIVITY_MULTIPLIERS = {
        'sedentary':   1.2,
        'light':       1.375,
        'moderate':    1.55,
        'active':      1.725,
        'very_active': 1.9,
    }

    def calculate_bmi(self):
        """BMI = weight(kg) / height(m)²"""
        if self.weight_kg and self.height_cm:
            h = float(self.height_cm) / 100
            return round(float(self.weight_kg) / (h ** 2), 2)
        return None

    def calculate_bmr(self):
        if not all([self.weight_kg, self.height_cm, self.age, self.gender]):
            return None
        w = float(self.weight_kg)
        h = float(self.height_cm)
        a = int(self.age)  # ← yeh fix hai
        if self.gender == self.GENDER_MALE:
            return round(10 * w + 6.25 * h - 5 * a + 5, 2)
        else:
            return round(10 * w + 6.25 * h - 5 * a - 161, 2)
    
    def calculate_tdee(self):
        """TDEE = BMR × activity multiplier"""
        bmr = self.calculate_bmr()
        if bmr is None:
            return None
        multiplier = self.ACTIVITY_MULTIPLIERS.get(self.activity_level, 1.2)
        return round(bmr * multiplier, 2)

    def calculate_daily_calorie_goal(self):
        """
        Adjust TDEE based on health goal:
          Lose weight  → TDEE - 500 kcal (≈ 0.5 kg/week deficit)
          Maintain     → TDEE
          Gain weight  → TDEE + 300 kcal
        """
        tdee = self.calculate_tdee()
        if tdee is None:
            return None
        adjustments = {
            self.GOAL_LOSE:     -500,
            self.GOAL_MAINTAIN: 0,
            self.GOAL_GAIN:     300,
        }
        return int(tdee + adjustments.get(self.health_goal, 0))

    def refresh_calculations(self):
        """Recalculate and save all derived fields."""
        self.bmi               = self.calculate_bmi()
        self.bmr               = self.calculate_bmr()
        self.tdee              = self.calculate_tdee()
        self.daily_calorie_goal = self.calculate_daily_calorie_goal()
        self.save(update_fields=['bmi', 'bmr', 'tdee', 'daily_calorie_goal'])

    @property
    def bmi_category(self):
        """Return a human-readable BMI category."""
        if self.bmi is None:
            return 'Unknown'
        bmi = float(self.bmi)
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal'
        elif bmi < 30:
            return 'Overweight'
        return 'Obese'
    