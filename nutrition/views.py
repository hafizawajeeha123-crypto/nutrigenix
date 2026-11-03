from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Q
from django.db import models
from django.http import JsonResponse
from .models import MealLog, WaterLog, DietPlan, DietPlanMeal, FoodItem
import json
import random
@login_required
def dashboard_view(request):
    today = timezone.now().date()
    profile = request.user.profile

    # Today's meal logs
    meal_logs = MealLog.objects.filter(
        user=request.user,
        log_date=today
    ).select_related('food_item').order_by('meal_type')

    # Today's calories consumed
    calories_consumed = meal_logs.aggregate(
        total=Sum('total_calories')
    )['total'] or 0

    # Today's water intake
    water_consumed = WaterLog.objects.filter(
        user=request.user,
        log_date=today
    ).aggregate(total=Sum('amount_ml'))['total'] or 0

    # Calorie goal
    calorie_goal = profile.daily_calorie_goal or 2000
    water_goal   = profile.daily_water_goal_ml or 2000

    # Progress percentages (max 100)
    calorie_percent = min(int((float(calories_consumed) / calorie_goal) * 100), 100)
    water_percent   = min(int((water_consumed / water_goal) * 100), 100)

    # Calories remaining
    calories_remaining = max(calorie_goal - int(float(calories_consumed)), 0)

    # Meals grouped by type
    breakfast = meal_logs.filter(meal_type='breakfast')
    lunch     = meal_logs.filter(meal_type='lunch')
    dinner    = meal_logs.filter(meal_type='dinner')
    snacks    = meal_logs.filter(meal_type='snack')

    context = {
        'profile':             profile,
        'today':               today,
        'calories_consumed':   int(float(calories_consumed)),
        'calorie_goal':        calorie_goal,
        'calorie_percent':     calorie_percent,
        'calories_remaining':  calories_remaining,
        'water_consumed':      water_consumed,
        'water_goal':          water_goal,
        'water_percent':       water_percent,
        'breakfast':           breakfast,
        'lunch':               lunch,
        'dinner':              dinner,
        'snacks':              snacks,
        'bmi':                 profile.bmi,
        'bmi_category':        profile.bmi_category,
        'tdee':                profile.tdee,
    }
    return render(request, 'nutrition/dashboard.html', context)
@login_required
def food_log_view(request):
    today = timezone.now().date()

    meal_logs = MealLog.objects.filter(
        user=request.user,
        log_date=today
    ).select_related('food_item').order_by('meal_type')

    total_calories = meal_logs.aggregate(t=Sum('total_calories'))['t'] or 0
    calorie_goal   = request.user.profile.daily_calorie_goal or 2000

    context = {
        'meal_logs':       meal_logs,
        'total_calories':  int(float(total_calories)),
        'calorie_goal':    calorie_goal,
        'today':           today,
        'meal_types':      ['breakfast', 'lunch', 'dinner', 'snack'],
    }
    return render(request, 'nutrition/food_log.html', context)

@login_required
def food_search_api(request):
    query     = request.GET.get('q', '').strip()
    condition = request.GET.get('condition', '')

    foods = FoodItem.objects.filter(is_active=True)

    if query and len(query) >= 2:
        from django.db.models import Q
        foods = foods.filter(
            Q(name_en__icontains=query) |
            Q(name_roman_ur__icontains=query) |
            Q(category__icontains=query)
        )
    elif not query:
        # Return all foods if no query
        foods = foods[:20]

    if condition == 'diabetes':
        foods = foods.filter(suitable_for_diabetes=True)
    elif condition == 'hypertension':
        foods = foods.filter(suitable_for_hypertension=True)
    elif condition == 'pcos':
        foods = foods.filter(suitable_for_pcos=True)

    foods = foods[:20]

    data = [{
        'id':         f.id,
        'name':       f.name_en,
        'name_roman': f.name_roman_ur,
        'calories':   float(f.calories_kcal),
        'protein':    float(f.protein_g),
        'carbs':      float(f.carbs_g),
        'fat':        float(f.fat_g),
        'serving':    f.serving_label or f'{f.serving_size_g}g',
        'category':   f.get_category_display(),
    } for f in foods]

    return JsonResponse({'foods': data})

@login_required
def add_meal_log(request):
    """AJAX endpoint — logs a meal."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        body      = json.loads(request.body)
        food_id   = body.get('food_id')
        meal_type = body.get('meal_type', 'breakfast')
        quantity  = float(body.get('quantity', 1.0))

        food = get_object_or_404(FoodItem, id=food_id, is_active=True)

        log = MealLog.objects.create(
            user              = request.user,
            food_item         = food,
            meal_type         = meal_type,
            log_date          = timezone.now().date(),
            quantity_servings = quantity,
        )

        return JsonResponse({
            'success':   True,
            'log_id':    log.id,
            'food_name': food.name_en,
            'calories':  float(log.total_calories),
            'meal_type': meal_type,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def delete_meal_log(request, log_id):
    """Delete a meal log entry."""
    log = get_object_or_404(MealLog, id=log_id, user=request.user)
    log.delete()
    return JsonResponse({'success': True, 'log_id': log_id})

@login_required
def calculator_view(request):
    profile = request.user.profile
    result  = None

    if request.method == 'POST':
        # Save to profile
        profile.age            = request.POST.get('age')
        profile.gender         = request.POST.get('gender')
        profile.height_cm      = request.POST.get('height_cm')
        profile.weight_kg      = request.POST.get('weight_kg')
        profile.activity_level = request.POST.get('activity_level')
        profile.health_goal    = request.POST.get('health_goal')
        profile.save()
        profile.refresh_calculations()

        result = {
            'bmi':          profile.bmi,
            'bmi_category': profile.bmi_category,
            'bmr':          profile.bmr,
            'tdee':         profile.tdee,
            'calorie_goal': profile.daily_calorie_goal,
        }

    context = {
        'profile': profile,
        'result':  result,
    }
    return render(request, 'nutrition/calculator.html', context)
@login_required
def water_tracker_view(request):
    today   = timezone.now().date()
    profile = request.user.profile

    water_logs = WaterLog.objects.filter(
        user=request.user,
        log_date=today
    ).order_by('-logged_at')

    total_ml  = water_logs.aggregate(t=Sum('amount_ml'))['t'] or 0
    goal_ml   = profile.daily_water_goal_ml or 2000
    percent   = min(int((total_ml / goal_ml) * 100), 100)
    remaining = max(goal_ml - total_ml, 0)

    context = {
        'water_logs': water_logs,
        'total_ml':   total_ml,
        'goal_ml':    goal_ml,
        'percent':    percent,
        'remaining':  remaining,
        'today':      today,
    }
    return render(request, 'nutrition/water_tracker.html', context)

@login_required
def water_tracker_view(request):
    today   = timezone.now().date()
    profile = request.user.profile

    water_logs = WaterLog.objects.filter(
        user=request.user,
        log_date=today
    ).order_by('-logged_at')

    total_ml  = water_logs.aggregate(t=Sum('amount_ml'))['t'] or 0
    goal_ml   = profile.daily_water_goal_ml or 2000
    percent   = min(int((total_ml / goal_ml) * 100), 100)
    remaining = max(goal_ml - total_ml, 0)

    context = {
        'water_logs': water_logs,
        'total_ml':   total_ml,
        'goal_ml':    goal_ml,
        'percent':    percent,
        'remaining':  remaining,
        'today':      today,
    }
    return render(request, 'nutrition/water_tracker.html', context)


@login_required
def add_water_log(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        body      = json.loads(request.body)
        amount_ml = int(body.get('amount_ml', 250))
        notes     = body.get('notes', '')

        log = WaterLog.objects.create(
            user      = request.user,
            amount_ml = amount_ml,
            notes     = notes,
            log_date  = timezone.now().date(),
            logged_at = timezone.now().time(),
        )

        # Recalculate total
        today     = timezone.now().date()
        total_ml  = WaterLog.objects.filter(
            user=request.user, log_date=today
        ).aggregate(t=Sum('amount_ml'))['t'] or 0
        goal_ml   = request.user.profile.daily_water_goal_ml or 2000
        percent   = min(int((total_ml / goal_ml) * 100), 100)

        return JsonResponse({
            'success':  True,
            'log_id':   log.id,
            'amount':   amount_ml,
            'total_ml': total_ml,
            'goal_ml':  goal_ml,
            'percent':  percent,
            'remaining': max(goal_ml - total_ml, 0),
            'time':     log.logged_at.strftime('%I:%M %p'),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def delete_water_log(request, log_id):
    log = get_object_or_404(WaterLog, id=log_id, user=request.user)
    log.delete()

    today    = timezone.now().date()
    total_ml = WaterLog.objects.filter(
        user=request.user, log_date=today
    ).aggregate(t=Sum('amount_ml'))['t'] or 0
    goal_ml  = request.user.profile.daily_water_goal_ml or 2000
    percent  = min(int((total_ml / goal_ml) * 100), 100)

    return JsonResponse({
        'success':  True,
        'total_ml': total_ml,
        'percent':  percent,
        'remaining': max(goal_ml - total_ml, 0),
    })

@login_required
def diet_plan_view(request):
    profile = request.user.profile

    # Get active plan if exists
    active_plan = DietPlan.objects.filter(
        user=request.user,
        status='active'
    ).prefetch_related('meals__food_item').first()

    context = {
        'profile':     profile,
        'active_plan': active_plan,
        'days':        range(1, 8),
        'meal_types':  ['breakfast', 'lunch', 'dinner', 'snack'],
    }
    return render(request, 'nutrition/diet_plan.html', context)


import random
from datetime import timedelta


@login_required
def diet_plan_view(request):
    profile = request.user.profile

    # Get active plan if exists
    active_plan = DietPlan.objects.filter(
        user=request.user,
        status='active'
    ).prefetch_related('meals__food_item').first()

    context = {
        'profile':     profile,
        'active_plan': active_plan,
        'days':        range(1, 8),
        'meal_types':  ['breakfast', 'lunch', 'dinner', 'snack'],
    }
    return render(request, 'nutrition/diet_plan.html', context)


@login_required
def generate_diet_plan(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    profile      = request.user.profile
    calorie_goal = profile.daily_calorie_goal or 2000

    # Archive old plans
    DietPlan.objects.filter(user=request.user, status='active').update(status='archived')

    # Create new plan
    plan = DietPlan.objects.create(
        user           = request.user,
        title          = f'7-Day Plan — {timezone.now().strftime("%b %d, %Y")}',
        status         = 'active',
        calorie_target = calorie_goal,
        health_goal    = profile.health_goal,
        start_date     = timezone.now().date(),
    )

    # Calorie distribution per meal
    # Breakfast 25%, Lunch 35%, Dinner 30%, Snack 10%
    meal_calories = {
        'breakfast': int(calorie_goal * 0.25),
        'lunch':     int(calorie_goal * 0.35),
        'dinner':    int(calorie_goal * 0.30),
        'snack':     int(calorie_goal * 0.10),
    }

    # Build food filter based on health conditions
    def get_foods(meal_type, target_cal):
        foods = FoodItem.objects.filter(is_active=True)

        if meal_type != 'any':
            foods = foods.filter(
                models.Q(meal_type=meal_type) | models.Q(meal_type='any')
            )

        if profile.has_diabetes:
            foods = foods.filter(suitable_for_diabetes=True)
        if profile.has_hypertension:
            foods = foods.filter(suitable_for_hypertension=True)
        if profile.has_pcos:
            foods = foods.filter(suitable_for_pcos=True)

        foods = list(foods)
        if not foods:
            foods = list(FoodItem.objects.filter(is_active=True))

        return foods

    DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    for day_num in range(1, 8):
        for meal_type, target_cal in meal_calories.items():
            foods = get_foods(meal_type, target_cal)
            if not foods:
                continue

            food     = random.choice(foods)
            cal_per  = float(food.calories_kcal)
            quantity = round(target_cal / cal_per, 1) if cal_per > 0 else 1.0
            quantity = max(0.5, min(quantity, 3.0))  # keep between 0.5 and 3

            DietPlanMeal.objects.get_or_create(
                diet_plan         = plan,
                day_number        = day_num,
                meal_type         = meal_type,
                food_item         = food,
                defaults={
                    'quantity_servings': quantity,
                    'notes': f'Day {day_num} — {DAY_NAMES[day_num-1]}',
                }
            )

    return JsonResponse({'success': True, 'plan_id': plan.id})


@login_required
def delete_diet_plan(request):
    if request.method == 'POST':
        DietPlan.objects.filter(user=request.user, status='active').update(status='archived')
    return JsonResponse({'success': True})