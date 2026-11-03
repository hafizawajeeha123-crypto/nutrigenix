import json
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from .models import ChatSession, ChatMessage


SYSTEM_PROMPT = """You are NutriGenix AI — a friendly, expert diet and nutrition assistant 
for Pakistani users. You specialize in:
- Pakistani and South Asian foods (Biryani, Roti, Daal, Karahi, etc.)
- Calorie counting and macro tracking
- Weight loss, weight gain, and maintenance advice
- Diet plans for health conditions: Diabetes, PCOS, Hypertension
- Healthy Pakistani food alternatives and substitutes

Important rules:
- Always respond in English only. Be clear, friendly and professional.
- Be warm, encouraging and supportive
- Give specific, practical advice with Pakistani food examples
- Keep responses concise (3-5 sentences max unless asked for a plan)
- Never give medical diagnoses — always suggest consulting a doctor for medical issues
- If asked about non-diet topics, politely redirect to nutrition/health

Example tone: "Bilkul! Chicken karahi ek acha option hai weight loss ke liye — 
isme protein zyada hoti hai aur aap roti kam karke khayein toh calories control 
mein rehti hain."
"""

@login_required
def chatbot_view(request):
    profile = request.user.profile

    session, _ = ChatSession.objects.get_or_create(
        user=request.user,
        defaults={'title': 'Diet Chat'}
    )

    # Only show last 20 messages
    messages_qs = session.messages.all().order_by('created_at')

    context = {
        'session':            session,
        'messages':           messages_qs,
        'messages_remaining': 999 if profile.is_premium else session.messages_remaining,
        'is_limit_reached':   False if profile.is_premium else session.is_limit_reached,
        'is_premium':         profile.is_premium,
    }
    return render(request, 'chatbot/chatbot.html', context)

@login_required
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        body    = json.loads(request.body)
        message = body.get('message', '').strip()

        if not message:
            return JsonResponse({'error': 'Empty message'}, status=400)

        # Get session
        session, _ = ChatSession.objects.get_or_create(
            user=request.user,
            defaults={'title': message[:50]}
        )

        # Check daily limit
        if session.is_limit_reached:
            return JsonResponse({
                'error': 'Daily limit reached. You have used all 10 free messages for today. Come back tomorrow!',
                'limit_reached': True,
            }, status=429)

        # Save user message
        ChatMessage.objects.create(
            session=session,
            role=ChatMessage.ROLE_USER,
            content=message,
        )

        # Build conversation history for Groq
        history = session.messages.order_by('created_at')
        groq_messages = []
        for msg in history:
            groq_messages.append({
                'role':    msg.role,
                'content': msg.content,
            })

        # Call Groq API
        api_key = settings.GROQ_API_KEY
        if not api_key:
            # Fallback response if no API key
            reply = get_fallback_response(message)
            source = ChatMessage.SOURCE_RULE
        else:
            try:
                response = requests.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type':  'application/json',
                    },
                    json={
                        'model': 'llama-3.1-8b-instant',
                        'messages':    [{'role': 'system', 'content': SYSTEM_PROMPT}] + groq_messages,
                        'max_tokens':  500,
                        'temperature': 0.7,
                    },
                    timeout=15,
                )
                data  = response.json()
                reply = data['choices'][0]['message']['content']
                source = ChatMessage.SOURCE_GROQ

            except Exception:
                reply  = get_fallback_response(message)
                source = ChatMessage.SOURCE_RULE

        # Save assistant reply
        ChatMessage.objects.create(
            session=session,
            role=ChatMessage.ROLE_ASSISTANT,
            content=reply,
            source=source,
        )

        # Increment counter
        session.increment_message_count()

        return JsonResponse({
            'success':           True,
            'reply':             reply,
            'messages_remaining': session.messages_remaining,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def clear_chat(request):
    if request.method == 'POST':
        ChatSession.objects.filter(user=request.user).delete()
    return JsonResponse({'success': True})


def get_fallback_response(message):
    """Simple keyword-based fallback when Groq API is unavailable."""
    message = message.lower()

    if any(w in message for w in ['bmi', 'weight', 'mota', 'patla']):
        return "Aap ka BMI calculate karne ke liye Calculator page use karein. Healthy BMI range 18.5-24.9 hai. Aap apni height aur weight enter karein aur apna result dekhen!"

    if any(w in message for w in ['calorie', 'calories', 'khana', 'diet']):
        return "Pakistani diet mein calories control karne ke liye: roti 1-2 tak limit karein, daal aur sabzi zyada khayein, chicken grilled ya boiled prefer karein, aur meetha kam karein. Aap Food Log mein apni daily calories track kar sakte hain!"

    if any(w in message for w in ['water', 'paani', 'pani']):
        return "Rozana kam az kam 8 glasses (2 litres) paani pina chahiye. Subah uthte hi ek glass paani piyein, aur har meal se pehle bhi. Water Tracker mein aap apna intake log kar sakte hain!"

    if any(w in message for w in ['diabetes', 'sugar', 'diabetic']):
        return "Diabetes mein low glycemic index foods prefer karein: brown rice, whole wheat roti, daal, sabziyaan. Meetha, white rice, aur maida avoid karein. Karela aur methi diabetes ke liye mufeed hain. Doctor se zaroor consult karein!"

    if any(w in message for w in ['protein', 'muscle', 'gym']):
        return "Protein ke achay Pakistani sources: chicken, eggs, daal, dahi, paneer. Gym karne wale rozana 1.6-2.2g protein per kg body weight lein. Har meal mein protein zaroor shamil karein!"

    if any(w in message for w in ['breakfast', 'nashta', 'subah']):
        return "Healthy Pakistani breakfast: 2 boiled eggs + 1 roti + dahi. Ya oatmeal with fruits. Ya paratha ek — lekin makhan kam. Nashta skip mat karein — yeh metabolism ke liye zaroori hai!"

    return "Aap ka sawaal samajh aa gaya! Main aap ki diet aur nutrition mein madad karne ke liye yahan hun. Koi specific food, calorie count, ya diet plan ke baare mein poochh sakte hain. Groq API connect karne ke baad main aur behtar jawab de sakta hun!"