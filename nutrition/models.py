from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


# ======================================================================
# FOOD ITEM
# ======================================================================

class FoodItem(models.Model):
    """
    Master database of 500+ Pakistani and South Asian foods.
    Admins create entries; users search and read.
    (CRUD: Admin = Create + Read | Users = Read only)
    """

    # --- Category choices ---
    CAT_BREAD        = 'bread'
    CAT_RICE         = 'rice'
    CAT_LENTILS      = 'lentils'
    CAT_MEAT         = 'meat'
    CAT_POULTRY      = 'poultry'
    CAT_SEAFOOD      = 'seafood'
    CAT_DAIRY        = 'dairy'
    CAT_VEGETABLES   = 'vegetables'
    CAT_FRUITS       = 'fruits'
    CAT_SNACKS       = 'snacks'
    CAT_DESSERTS     = 'desserts'
    CAT_BEVERAGES    = 'beverages'
    CAT_CONDIMENTS   = 'condiments'
    CAT_BREAKFAST    = 'breakfast'
    CAT_FAST_FOOD    = 'fast_food'
    CAT_OTHER        = 'other'

    CATEGORY_CHOICES = [
        (CAT_BREAD,      'Bread & Roti'),
        (CAT_RICE,       'Rice Dishes'),
        (CAT_LENTILS,    'Lentils & Daal'),
        (CAT_MEAT,       'Meat (Beef/Mutton/Lamb)'),
        (CAT_POULTRY,    'Poultry (Chicken)'),
        (CAT_SEAFOOD,    'Seafood'),
        (CAT_DAIRY,      'Dairy & Eggs'),
        (CAT_VEGETABLES, 'Vegetables & Sabzi'),
        (CAT_FRUITS,     'Fruits'),
        (CAT_SNACKS,     'Snacks & Street Food'),
        (CAT_DESSERTS,   'Desserts & Mithai'),
        (CAT_BEVERAGES,  'Beverages'),
        (CAT_CONDIMENTS, 'Condiments & Chutneys'),
        (CAT_BREAKFAST,  'Breakfast Items'),
        (CAT_FAST_FOOD,  'Fast Food'),
        (CAT_OTHER,      'Other'),
    ]

    # --- Meal type suitability ---
    MEAL_BREAKFAST = 'breakfast'
    MEAL_LUNCH     = 'lunch'
    MEAL_DINNER    = 'dinner'
    MEAL_SNACK     = 'snack'
    MEAL_ANY       = 'any'
    MEAL_TYPE_CHOICES = [
        (MEAL_BREAKFAST, 'Breakfast'),
        (MEAL_LUNCH,     'Lunch'),
        (MEAL_DINNER,    'Dinner'),
        (MEAL_SNACK,     'Snack'),
        (MEAL_ANY,       'Any meal'),
    ]

    # Basic info
    name_en       = models.CharField(max_length=150, help_text='English name, e.g. Chicken Biryani')
    name_ur       = models.CharField(max_length=150, blank=True, help_text='Urdu name (Nastaliq)')
    name_roman_ur = models.CharField(max_length=150, blank=True, help_text='Roman Urdu name, e.g. Murgh Biryani')
    category      = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CAT_OTHER)
    meal_type     = models.CharField(max_length=15, choices=MEAL_TYPE_CHOICES, default=MEAL_ANY)
    description   = models.TextField(blank=True)

    # Serving info
    serving_size_g   = models.DecimalField(
                           max_digits=6, decimal_places=1,
                           default=100,
                           help_text='Standard serving size in grams',
                       )
    serving_label    = models.CharField(
                           max_length=60, blank=True,
                           help_text='e.g. "1 roti", "1 cup", "1 piece"',
                       )

    # Macronutrients (per serving)
    calories_kcal = models.DecimalField(
                        max_digits=7, decimal_places=1,
                        validators=[MinValueValidator(0)],
                        help_text='Calories per serving (kcal)',
                    )
    protein_g     = models.DecimalField(max_digits=6, decimal_places=1, default=0,
                        validators=[MinValueValidator(0)])
    carbs_g       = models.DecimalField(max_digits=6, decimal_places=1, default=0,
                        validators=[MinValueValidator(0)])
    fat_g         = models.DecimalField(max_digits=6, decimal_places=1, default=0,
                        validators=[MinValueValidator(0)])
    fiber_g       = models.DecimalField(max_digits=6, decimal_places=1, default=0,
                        validators=[MinValueValidator(0)])
    sugar_g       = models.DecimalField(max_digits=6, decimal_places=1, default=0,
                        validators=[MinValueValidator(0)])
    sodium_mg     = models.DecimalField(max_digits=7, decimal_places=1, default=0,
                        validators=[MinValueValidator(0)])

    # Health condition flags (used by the health condition mode filter)
    suitable_for_diabetes     = models.BooleanField(default=True)
    suitable_for_hypertension = models.BooleanField(default=True)
    suitable_for_pcos         = models.BooleanField(default=True)
    is_vegetarian             = models.BooleanField(default=False)
    is_vegan                  = models.BooleanField(default=False)

    # Healthier substitute (self-referential FK)
    healthier_substitute = models.ForeignKey(
                               'self',
                               on_delete=models.SET_NULL,
                               null=True, blank=True,
                               related_name='substituted_by',
                               help_text='A lower-calorie alternative to this food',
                           )

    # Metadata
    is_active  = models.BooleanField(default=True, help_text='Hide from searches without deleting')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Food Item'
        verbose_name_plural = 'Food Items'
        ordering            = ['name_en']
        indexes             = [
            models.Index(fields=['category']),
            models.Index(fields=['meal_type']),
            models.Index(fields=['suitable_for_diabetes']),
            models.Index(fields=['suitable_for_hypertension']),
        ]

    def __str__(self):
        return f'{self.name_en} ({self.calories_kcal} kcal / {self.serving_size_g}g)'

    @property
    def calories_per_100g(self):
        """Useful for comparison across different serving sizes."""
        if self.serving_size_g:
            return round(float(self.calories_kcal) / float(self.serving_size_g) * 100, 1)
        return None

    @property
    def macro_summary(self):
        return {
            'calories': float(self.calories_kcal),
            'protein':  float(self.protein_g),
            'carbs':    float(self.carbs_g),
            'fat':      float(self.fat_g),
        }


# ======================================================================
# MEAL LOG
# ======================================================================

class MealLog(models.Model):
    """
    Records every meal a user logs throughout the day.
    Full CRUD: users can Create, Read, Update, and Delete their entries.
    """

    MEAL_BREAKFAST = 'breakfast'
    MEAL_LUNCH     = 'lunch'
    MEAL_DINNER    = 'dinner'
    MEAL_SNACK     = 'snack'
    MEAL_TYPE_CHOICES = [
        (MEAL_BREAKFAST, 'Breakfast'),
        (MEAL_LUNCH,     'Lunch'),
        (MEAL_DINNER,    'Dinner'),
        (MEAL_SNACK,     'Snack'),
    ]

    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_logs')
    food_item = models.ForeignKey(FoodItem, on_delete=models.PROTECT, related_name='meal_logs')
    meal_type = models.CharField(max_length=15, choices=MEAL_TYPE_CHOICES, default=MEAL_BREAKFAST)
    log_date  = models.DateField(default=timezone.now, help_text='Date this meal was consumed')
    log_time  = models.TimeField(null=True, blank=True, help_text='Optional: time of consumption')

    # How much the user actually ate (may differ from the FoodItem's default serving)
    quantity_servings = models.DecimalField(
                            max_digits=4, decimal_places=1,
                            default=1.0,
                            validators=[MinValueValidator(0.1)],
                            help_text='Number of servings consumed (e.g. 1.5 = 1½ servings)',
                        )

    # Cached calorie total for this log entry (serving × quantity)
    # Stored so the daily total is fast to query without joining FoodItem every time
    total_calories = models.DecimalField(max_digits=7, decimal_places=1, default=0)
    total_protein  = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    total_carbs    = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    total_fat      = models.DecimalField(max_digits=6, decimal_places=1, default=0)

    notes      = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Meal Log'
        verbose_name_plural = 'Meal Logs'
        ordering            = ['-log_date', 'meal_type']
        indexes             = [
            models.Index(fields=['user', 'log_date']),
            models.Index(fields=['user', 'log_date', 'meal_type']),
        ]

    def __str__(self):
        return f'{self.user.username} — {self.food_item.name_en} ({self.log_date})'

    def save(self, *args, **kwargs):
        """Auto-calculate totals before saving."""
        qty = float(self.quantity_servings)
        self.total_calories = round(float(self.food_item.calories_kcal) * qty, 1)
        self.total_protein  = round(float(self.food_item.protein_g)     * qty, 1)
        self.total_carbs    = round(float(self.food_item.carbs_g)        * qty, 1)
        self.total_fat      = round(float(self.food_item.fat_g)          * qty, 1)
        super().save(*args, **kwargs)


# ======================================================================
# DIET PLAN
# ======================================================================

class DietPlan(models.Model):
    """
    A 7-day personalised meal plan generated for a user.
    Full CRUD: users can generate (Create), view (Read), edit meals (Update),
    and delete/regenerate (Delete) their plan.
    """

    STATUS_ACTIVE   = 'active'
    STATUS_DRAFT    = 'draft'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES  = [
        (STATUS_ACTIVE,   'Active'),
        (STATUS_DRAFT,    'Draft'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diet_plans')
    title            = models.CharField(
                           max_length=150,
                           default='My 7-Day Plan',
                           help_text='User-friendly name for this plan',
                       )
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    # Snapshot of the user's goals at generation time
    calorie_target   = models.PositiveSmallIntegerField(help_text='Daily calorie target when plan was generated')
    health_goal      = models.CharField(max_length=10, blank=True)

    # Plan dates
    start_date       = models.DateField(default=timezone.now)
    end_date         = models.DateField(null=True, blank=True, help_text='Automatically set to start_date + 6 days')

    notes            = models.TextField(blank=True, help_text='Optional notes or customisations')
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Diet Plan'
        verbose_name_plural = 'Diet Plans'
        ordering            = ['-created_at']
        indexes             = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f'{self.user.username} — {self.title} (from {self.start_date})'

    def save(self, *args, **kwargs):
        """Auto-set end_date to start_date + 6 days (7-day plan)."""
        if self.start_date and not self.end_date:
            from datetime import timedelta
            self.end_date = self.start_date + timedelta(days=6)
        super().save(*args, **kwargs)

    @property
    def total_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 7


class DietPlanMeal(models.Model):
    """
    A single meal slot within a DietPlan.
    Represents one meal (e.g. Monday Breakfast) with one or more food items.
    """

    DAY_CHOICES = [(i, day) for i, day in enumerate(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], start=1
    )]

    MEAL_BREAKFAST = 'breakfast'
    MEAL_LUNCH     = 'lunch'
    MEAL_DINNER    = 'dinner'
    MEAL_SNACK     = 'snack'
    MEAL_TYPE_CHOICES = [
        (MEAL_BREAKFAST, 'Breakfast'),
        (MEAL_LUNCH,     'Lunch'),
        (MEAL_DINNER,    'Dinner'),
        (MEAL_SNACK,     'Snack'),
    ]

    diet_plan         = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name='meals')
    day_number        = models.PositiveSmallIntegerField(choices=DAY_CHOICES, help_text='1=Monday … 7=Sunday')
    meal_type         = models.CharField(max_length=15, choices=MEAL_TYPE_CHOICES)
    food_item         = models.ForeignKey(FoodItem, on_delete=models.PROTECT)
    quantity_servings = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    notes             = models.CharField(max_length=255, blank=True, help_text='e.g. "skip if not available"')

    class Meta:
        verbose_name        = 'Diet Plan Meal'
        verbose_name_plural = 'Diet Plan Meals'
        ordering            = ['day_number', 'meal_type']
        unique_together     = ['diet_plan', 'day_number', 'meal_type', 'food_item']

    def __str__(self):
        return (
            f'Day {self.day_number} {self.get_meal_type_display()} — '
            f'{self.food_item.name_en} ×{self.quantity_servings}'
        )

    @property
    def calories(self):
        return round(float(self.food_item.calories_kcal) * float(self.quantity_servings), 1)
# ======================================================================
# WATER LOG
# ======================================================================

class WaterLog(models.Model):
    SIZE_SMALL  = 150
    SIZE_MEDIUM = 250
    SIZE_LARGE  = 500
    SIZE_BOTTLE = 1000

    SIZE_CHOICES = [
        (SIZE_SMALL,  'Small glass (150 ml)'),
        (SIZE_MEDIUM, 'Standard glass (250 ml)'),
        (SIZE_LARGE,  'Large bottle / mug (500 ml)'),
        (SIZE_BOTTLE, '1-litre bottle (1000 ml)'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='water_logs')
    log_date   = models.DateField(default=timezone.now)
    logged_at  = models.TimeField(default=timezone.now)
    amount_ml  = models.PositiveSmallIntegerField(default=SIZE_MEDIUM)
    notes      = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Water Log'
        verbose_name_plural = 'Water Logs'
        ordering            = ['-log_date', '-logged_at']
        indexes             = [models.Index(fields=['user', 'log_date'])]

    def __str__(self):
        return f'{self.user.username} — {self.amount_ml} ml on {self.log_date}'


class WaterDailySummary(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='water_summaries')
    date         = models.DateField()
    total_ml     = models.PositiveIntegerField(default=0)
    goal_ml      = models.PositiveSmallIntegerField(default=2000)
    goal_reached = models.BooleanField(default=False)

    class Meta:
        verbose_name        = 'Water Daily Summary'
        verbose_name_plural = 'Water Daily Summaries'
        unique_together     = ['user', 'date']
        ordering            = ['-date']

    def __str__(self):
        return f'{self.user.username} — {self.date} — {self.total_ml} ml'

    @property
    def percentage(self):
        if self.goal_ml:
            return min(round(self.total_ml / self.goal_ml * 100), 100)
        return 0

    @property
    def remaining_ml(self):
        return max(self.goal_ml - self.total_ml, 0)