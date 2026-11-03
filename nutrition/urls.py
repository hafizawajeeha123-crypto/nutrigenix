from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    path('dashboard/',                               views.dashboard_view,     name='dashboard'),
    path('nutrition/food-log/',                      views.food_log_view,      name='food_log'),
    path('nutrition/calculator/',                    views.calculator_view,    name='calculator'),
    path('nutrition/water/',                         views.water_tracker_view, name='water'),
    path('nutrition/diet-plan/',                     views.diet_plan_view,     name='diet_plan'),
    path('nutrition/api/food-search/',               views.food_search_api,    name='food_search'),
    path('nutrition/api/add-meal/',                  views.add_meal_log,       name='add_meal'),
    path('nutrition/api/delete-meal/<int:log_id>/',  views.delete_meal_log,    name='delete_meal'),
    path('nutrition/api/add-water/',                 views.add_water_log,      name='add_water'),
    path('nutrition/api/delete-water/<int:log_id>/', views.delete_water_log,   name='delete_water'),
    path('nutrition/api/generate-plan/',             views.generate_diet_plan, name='generate_plan'),
    path('nutrition/api/delete-plan/',               views.delete_diet_plan,   name='delete_plan'),
]