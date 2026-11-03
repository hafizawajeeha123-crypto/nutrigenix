from django.core.management.base import BaseCommand
from nutrition.models import FoodItem

FOODS = [
    # (name_en, name_roman_ur, category, meal_type, serving_size_g, serving_label, calories, protein, carbs, fat, fiber, diabetes, hypertension, pcos)
    ("Chicken Biryani","Murgh Biryani","rice","lunch",250,"1 plate",350,22,45,8,2,True,False,True),
    ("Beef Biryani","Gosht Biryani","rice","dinner",250,"1 plate",420,25,48,12,2,False,False,False),
    ("Plain Roti","Sada Roti","bread","any",30,"1 roti",80,3,16,1,2,True,True,True),
    ("Butter Roti","Makhan Roti","bread","any",35,"1 roti",120,3,16,5,2,False,False,False),
    ("Naan","Naan","bread","any",80,"1 naan",260,8,50,4,2,False,False,False),
    ("Paratha","Paratha","bread","breakfast",60,"1 paratha",200,4,28,9,2,False,False,False),
    ("Aloo Paratha","Aloo Paratha","bread","breakfast",120,"1 paratha",280,6,42,10,3,False,False,False),
    ("Daal Chawal","Daal Chawal","lentils","lunch",300,"1 plate",380,18,65,5,8,True,True,True),
    ("Daal Makhani","Daal Makhani","lentils","dinner",200,"1 cup",220,12,28,7,6,True,False,True),
    ("Masoor Daal","Masoor Daal","lentils","lunch",200,"1 cup",180,14,30,2,8,True,True,True),
    ("Chana Daal","Chana Daal","lentils","lunch",200,"1 cup",210,13,35,3,9,True,True,True),
    ("Moong Daal","Moong Daal","lentils","lunch",200,"1 cup",160,12,28,1,8,True,True,True),
    ("Chicken Karahi","Murgh Karahi","poultry","dinner",250,"1 serving",310,32,8,18,1,True,False,True),
    ("Chicken Curry","Murgh Salan","poultry","dinner",200,"1 cup",260,28,10,14,2,True,False,True),
    ("Chicken Tikka","Murgh Tikka","poultry","dinner",150,"3 pieces",220,30,4,10,0,True,True,True),
    ("Tandoori Chicken","Tandoori Murgh","poultry","dinner",180,"2 pieces",240,32,6,10,0,True,True,True),
    ("Beef Karahi","Gosht Karahi","meat","dinner",250,"1 serving",380,30,8,26,1,False,False,False),
    ("Mutton Karahi","Mutton Karahi","meat","dinner",250,"1 serving",400,28,6,30,1,False,False,False),
    ("Nihari","Nihari","meat","breakfast",250,"1 bowl",420,30,15,28,2,False,False,False),
    ("Haleem","Haleem","meat","lunch",200,"1 bowl",280,22,25,10,4,True,False,True),
    ("Keema","Qeema","meat","lunch",150,"1 serving",290,24,8,18,2,False,False,False),
    ("Seekh Kabab","Seekh Kabab","meat","dinner",100,"2 pieces",220,20,6,14,1,False,False,False),
    ("Shami Kabab","Shami Kabab","meat","dinner",80,"2 pieces",180,14,12,9,2,False,False,False),
    ("Boiled Egg","Ubla Anda","dairy","breakfast",50,"1 egg",78,6,1,5,0,True,True,True),
    ("Fried Egg","Tala Anda","dairy","breakfast",60,"1 egg",120,6,1,10,0,True,False,True),
    ("Omelette","Omelette","dairy","breakfast",100,"1 omelette",180,12,2,14,0,True,False,True),
    ("Doodh (Milk)","Doodh","dairy","any",240,"1 glass",150,8,12,8,0,True,False,False),
    ("Dahi (Yogurt)","Dahi","dairy","any",200,"1 cup",120,8,14,5,0,True,True,True),
    ("Lassi (Sweet)","Meethi Lassi","beverages","any",300,"1 glass",220,7,38,5,0,False,False,False),
    ("Lassi (Salted)","Namkeen Lassi","beverages","any",300,"1 glass",130,7,15,5,0,True,True,True),
    ("Aloo Gosht","Aloo Gosht","meat","lunch",250,"1 serving",360,24,22,20,3,False,False,False),
    ("Aloo Ki Sabzi","Aloo Ki Sabzi","vegetables","lunch",150,"1 cup",140,3,28,4,3,False,True,False),
    ("Bhindi (Okra)","Bhindi","vegetables","lunch",150,"1 cup",90,3,16,3,4,True,True,True),
    ("Palak (Spinach)","Palak","vegetables","lunch",150,"1 cup",70,5,10,2,4,True,True,True),
    ("Palak Paneer","Palak Paneer","vegetables","dinner",200,"1 cup",240,12,14,16,4,True,False,True),
    ("Karela (Bitter Gourd)","Karela","vegetables","lunch",100,"1 cup",35,2,7,1,3,True,True,True),
    ("Baingan (Brinjal)","Baingan Ka Bharta","vegetables","dinner",150,"1 cup",120,3,18,5,4,True,True,True),
    ("Mixed Vegetables","Mix Sabzi","vegetables","lunch",150,"1 cup",100,4,18,3,5,True,True,True),
    ("Apple","Seb","fruits","snack",150,"1 medium",80,0,21,0,4,True,True,True),
    ("Banana","Kela","fruits","snack",120,"1 medium",105,1,27,0,3,False,True,False),
    ("Mango","Aam","fruits","snack",150,"1 cup",100,1,25,1,3,False,True,False),
    ("Guava","Amrood","fruits","snack",100,"1 medium",68,3,14,1,5,True,True,True),
    ("Orange","Narangi","fruits","snack",130,"1 medium",62,1,15,0,3,True,True,True),
    ("Watermelon","Tarbuz","fruits","snack",200,"1 slice",60,1,15,0,1,True,True,True),
    ("Samosa","Samosa","snacks","snack",60,"1 piece",150,4,18,7,2,False,False,False),
    ("Pakora","Pakora","snacks","snack",60,"4 pieces",180,5,20,9,2,False,False,False),
    ("Chaat","Chaat","snacks","snack",150,"1 plate",200,6,35,5,4,False,False,False),
    ("Pani Puri","Gol Gappay","snacks","snack",100,"6 pieces",180,4,32,5,3,False,False,False),
    ("White Rice","Chawal","rice","lunch",200,"1 cup cooked",260,5,56,0,1,False,True,False),
    ("Brown Rice","Brown Chawal","rice","lunch",200,"1 cup cooked",220,5,46,2,4,True,True,True),
    ("Khichdi","Khichdi","rice","lunch",200,"1 bowl",220,8,40,4,4,True,True,True),
    ("Kheer","Kheer","desserts","snack",150,"1 cup",250,6,42,7,0,False,False,False),
    ("Gulab Jamun","Gulab Jamun","desserts","snack",60,"2 pieces",180,3,35,5,0,False,False,False),
    ("Sohan Halwa","Sohan Halwa","desserts","snack",50,"1 piece",200,3,30,9,1,False,False,False),
    ("Green Tea","Sabz Chai","beverages","any",240,"1 cup",2,0,0,0,0,True,True,True),
    ("Chai (Tea)","Doodh Patti Chai","beverages","breakfast",200,"1 cup",60,2,8,3,0,False,False,False),
    ("Rooh Afza","Rooh Afza","beverages","any",240,"1 glass",120,0,30,0,0,False,False,False),
]


class Command(BaseCommand):
    help = 'Import 55 Pakistani food items into the database'

    def handle(self, *args, **kwargs):
        created = 0
        skipped = 0

        for food in FOODS:
            (name_en, name_roman_ur, category, meal_type,
             serving_size_g, serving_label, calories,
             protein, carbs, fat, fiber,
             diabetes, hypertension, pcos) = food

            obj, was_created = FoodItem.objects.get_or_create(
                name_en=name_en,
                defaults={
                    'name_roman_ur':            name_roman_ur,
                    'category':                 category,
                    'meal_type':                meal_type,
                    'serving_size_g':           serving_size_g,
                    'serving_label':            serving_label,
                    'calories_kcal':            calories,
                    'protein_g':                protein,
                    'carbs_g':                  carbs,
                    'fat_g':                    fat,
                    'fiber_g':                  fiber,
                    'suitable_for_diabetes':    diabetes,
                    'suitable_for_hypertension':hypertension,
                    'suitable_for_pcos':        pcos,
                    'is_active':                True,
                }
            )

            if was_created:
                created += 1
                self.stdout.write(f'  ✓ {name_en}')
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {created} foods added, {skipped} already existed.'
        ))