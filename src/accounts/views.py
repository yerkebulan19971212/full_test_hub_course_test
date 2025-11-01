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
    # domain = request.build_absolute_uri('/').rstrip('/')
    domain = "https://api.testhub.kz/"
    auth_url = f"{domain}/api/v1/telegram-auth/"
    
    context = {
        'bot_username': bot_username,
        'auth_url': auth_url,
    }
    
    return render(request, 'accounts/telegram_login.html', context)


@csrf_exempt
def telegram_auth_callback(request):
    """
    Handle Telegram Web App authentication
    Validates initData from Telegram Mini App and creates/authenticates user
    """
    import json
    
    # Get Telegram bot token from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    if not bot_token:
        return JsonResponse({
            'success': False,
            'error': 'Telegram bot token not configured'
        }, status=500)
    
    try:
        # Parse JSON body
        body = json.loads(request.body.decode('utf-8'))
        init_data = body.get('initData', '')
        init_data_unsafe = body.get('initDataUnsafe', {})
        
        if not init_data:
            return JsonResponse({
                'success': False,
                'error': 'No initData provided'
            }, status=400)
        
        # Verify Telegram Web App data
        if not verify_telegram_web_app_data(init_data, bot_token):
            return JsonResponse({
                'success': False,
                'error': 'Invalid authentication data'
            }, status=403)
        
        # Get user data from initDataUnsafe
        user_data = init_data_unsafe.get('user', {})
        
        if not user_data:
            return JsonResponse({
                'success': False,
                'error': 'No user data provided'
            }, status=400)
        
        # Extract user information
        telegram_id = str(user_data.get('id', ''))
        username = user_data.get('username', f'telegram_{telegram_id}')
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        language_code = user_data.get('language_code', 'ru')
        
        # Get or create user
        user = User.objects.filter(username=username).first()
        
        if not user:
            # Create new user
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            # You can add telegram_id and other fields to user profile if needed
            # user.telegram_id = telegram_id
            # user.language_code = language_code
            # user.save()
        else:
            # Update existing user info
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Return success response with tokens
        response_data = {
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'telegram_id': telegram_id,
            }
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def verify_telegram_web_app_data(init_data, bot_token):
    """
    Verify Telegram Web App initData
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    try:
        # Parse initData string into dict
        parsed_data = dict(item.split('=', 1) for item in init_data.split('&'))
        
        # Extract hash
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            return False
        
        # Create data check string (sorted keys)
        data_check_arr = [f'{key}={value}' for key, value in sorted(parsed_data.items())]
        data_check_string = '\n'.join(data_check_arr)
        
        # Create secret key using HMAC-SHA256 with "WebAppData" constant
        secret_key = hmac.new(
            'WebAppData'.encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return calculated_hash == received_hash
    except Exception as e:
        print(f"Error verifying Telegram Web App data: {e}")
        return False


def verify_telegram_authentication(auth_data, bot_token):
    """
    Verify that the authentication data is from Telegram Login Widget
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
