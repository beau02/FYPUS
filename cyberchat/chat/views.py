from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ChatHistory, Threat, UserProfile
from django.http import JsonResponse
from datetime import datetime
from django.utils.timezone import now
import openai
from django.conf import settings
from .utils import monitor_system, detect_threat, generate_recommendation


# Set up your OpenAI API key
openai.api_key = 'your-openai-api-key-here'

# Registration View
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard View (with chat history and threat detection data)
@login_required
def dashboard(request):
    user = request.user

    # Fetch threats and chat history
    threats = Threat.objects.filter(user=user).order_by('-detection_time')[:10]  # <-- Change ThreatDetection to Threat
    chat_history = ChatHistory.objects.filter(user=user).order_by('-timestamp')[:10]

    # Calculate threat level
    threat_count = threats.count()
    if threat_count == 0:
        threat_level = "Low"
    elif threat_count < 5:
        threat_level = "Moderate"
    else:
        threat_level = "High"

    # Prepare context for the dashboard
    context = {
        'threats': threats,
        'chat_history': chat_history,
        'threat_level': threat_level,
        'threat_count': threat_count,
    }

    return render(request, 'dashboard.html', context)

# Chatbot View (Handles user input and OpenAI responses)
def chatbot(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'No message provided.'}, status=400)

        user = request.user if request.user.is_authenticated else None

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ]
            )
            bot_response = response['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error during OpenAI API call: {e}")
            return JsonResponse({'error': 'OpenAI API error.'}, status=500)

        if user:
            try:
                ChatHistory.objects.create(
                    user=user,
                    message=user_message,
                    response=bot_response,
                    timestamp=now()
                )
            except Exception as e:
                print(f"Error saving chat history: {e}")

        return JsonResponse({'response': bot_response})

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

# Chat View (Render chat interface page)
@login_required
def chat_view(request):
    chat_history = ChatHistory.objects.filter(user=request.user).order_by('-timestamp')[:10]
    return render(request, 'chat.html', {'chat_history': chat_history})

# Monitor and Detect View (System monitoring and threat detection)
@login_required
def monitor_and_detect_view(request):
    user = request.user
    context = {}

    if request.method == 'POST':
        try:
            # Get system data
            system_data = monitor_system()
            
            # Detect threats using AI
            threat_description = detect_threat(system_data)
            
            # Generate recommendations
            recommendation = generate_recommendation(threat_description)
            
            # Save the threat detection
            threat = Threat.objects.create(
                user=user,
                threat_type="System Analysis",
                details=threat_description,
                recommendation=recommendation
            )

            context['monitoring_results'] = system_data
            context['detected_threat'] = threat
            messages.success(request, "Monitoring completed successfully.")
            
        except Exception as e:
            messages.error(request, f"Error during monitoring: {str(e)}")
    
    return render(request, 'monitor.html', context)

def analyze_message_for_threat(message):
    # Send message to ChatGPT for threat analysis
    openai.api_key = settings.OPENAI_API_KEY
    prompt = (
        "You are a cybersecurity assistant. Analyze the following message for threats. "
        "If you detect a threat, respond with the threat type (e.g., Phishing, Malware, Unauthorized Access) "
        "and a brief explanation. If no threat, respond with 'No threat detected.'\n\n"
        f"Message: {message}\n"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0
    )
    return response['choices'][0]['message']['content']
