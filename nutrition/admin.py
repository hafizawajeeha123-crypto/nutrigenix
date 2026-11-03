from django.contrib import admin
from .models import FoodItem, MealLog, DietPlan, DietPlanMeal, WaterLog, WaterDailySummary

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display  = ('name_en', 'category', 'calories_kcal', 'protein_g', 'carbs_g', 'fat_g', 'is_active')
    list_filter   = ('category', 'meal_type', 'suitable_for_diabetes', 'suitable_for_hypertension', 'is_active')
    search_fields = ('name_en', 'name_ur', 'name_roman_ur')

@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    list_display  = ('user', 'food_item', 'meal_type', 'log_date', 'total_calories')
    list_filter   = ('meal_type', 'log_date')
    search_fields = ('user__username', 'food_item__name_en')

@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display  = ('user', 'title', 'status', 'calorie_target', 'start_date')
    list_filter   = ('status',)

@admin.register(WaterLog)
class WaterLogAdmin(admin.ModelAdmin):
    list_display  = ('user', 'amount_ml', 'log_date')
    list_filter   = ('log_date',)