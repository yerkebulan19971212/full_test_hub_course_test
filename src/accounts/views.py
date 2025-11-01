import hashlib
import hmac
import os
from urllib.parse import urlencode

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def telegram_login_page(request):
    """
    Render the Telegram login page
    """
    # Get bot username from environment or settings
    bot_username = os.getenv('TELEGRAM_BOT_USERNAME', 'testup1bot')
    
    # Construct the auth URL
    domain = request.build_absolute_uri('/').rstrip('/')
    auth_url = f"{domain}/api/v1/telegram-auth/"
    
    context = {
        'bot_username': bot_username,
        'auth_url': auth_url,
    }
    
    return render(request, 'accounts/telegram_login.html', context)


@csrf_exempt
def telegram_auth_callback(request):
    """
    Handle Telegram authentication callback
    Validates the data from Telegram and creates/authenticates user
    """
    # Get Telegram bot token from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    if not bot_token:
        return JsonResponse({
            'error': 'Telegram bot token not configured'
        }, status=500)
    
    # Get data from request
    auth_data = {}
    for key in ['id', 'first_name', 'last_name', 'username', 'photo_url', 'auth_date', 'hash']:
        value = request.GET.get(key)
        if value:
            auth_data[key] = value
    
    # Verify Telegram authentication
    if not verify_telegram_authentication(auth_data, bot_token):
        return redirect('/api/v1/telegram-login/?error=Invalid authentication data')
    
    # Get or create user
    telegram_id = auth_data.get('id')
    username = auth_data.get('username', f'telegram_{telegram_id}')
    first_name = auth_data.get('first_name', '')
    last_name = auth_data.get('last_name', '')
    photo_url = auth_data.get('photo_url', '')
    
    try:
        # Try to find user by telegram_id (you may need to add this field to your User model)
        user = User.objects.filter(username=username).first()
        
        if not user:
            # Create new user
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            # You can add telegram_id and photo_url to user profile if needed
            # user.telegram_id = telegram_id
            # user.telegram_photo = photo_url
            # user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Return success response with tokens
        # You can redirect to frontend with tokens or return JSON
        response_data = {
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }
        
        # Option 1: Return JSON response
        return JsonResponse(response_data)
        
        # Option 2: Redirect to frontend with tokens in URL (less secure)
        # frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        # redirect_url = f"{frontend_url}/auth/callback?{urlencode({'access': access_token, 'refresh': refresh_token})}"
        # return redirect(redirect_url)
        
    except Exception as e:
        return redirect(f'/api/v1/telegram-login/?error={str(e)}')


def verify_telegram_authentication(auth_data, bot_token):
    """
    Verify that the authentication data is from Telegram
    https://core.telegram.org/widgets/login#checking-authorization
    """
    check_hash = auth_data.get('hash')
    if not check_hash:
        return False
    
    # Create data check string
    auth_data_copy = auth_data.copy()
    del auth_data_copy['hash']
    
    data_check_arr = [f'{key}={value}' for key, value in sorted(auth_data_copy.items())]
    data_check_string = '\n'.join(data_check_arr)
    
    # Create secret key
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    
    # Calculate hash
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return calculated_hash == check_hash
