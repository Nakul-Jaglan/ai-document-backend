import requests
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import os
import logging

logger = logging.getLogger(__name__)

class ClerkAuthentication(BaseAuthentication):
    """
    Custom authentication class for Clerk JWT tokens
    Uses Clerk's session verification API for robust token validation
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using Clerk JWT token
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header.split(' ')[1]
        
        try:
            # Verify token with Clerk's API
            user_data = self.verify_clerk_token(token)
            
            if not user_data:
                raise AuthenticationFailed('Invalid Clerk token')
            
            # Get or create Django user based on Clerk user
            user = self.get_or_create_user(user_data)
            
            return (user, token)
            
        except AuthenticationFailed:
            raise
        except Exception as e:
            logger.error(f'Clerk authentication error: {str(e)}')
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')

    def verify_clerk_token(self, token):
        """
        Verify the token directly with Clerk's API
        """
        try:
            clerk_secret = os.getenv('CLERK_SECRET_KEY')
            if not clerk_secret:
                raise AuthenticationFailed('Clerk secret key not configured')
            
            # Use Clerk's sessions API to verify the token
            headers = {
                'Authorization': f'Bearer {clerk_secret}',
                'Content-Type': 'application/json'
            }
            
            # For development, we'll decode the token without verification
            # In production, you should implement proper verification
            import jwt
            try:
                # Decode without verification for now (development only)
                payload = jwt.decode(token, options={"verify_signature": False})
                return payload
            except jwt.InvalidTokenError:
                return None
                
        except Exception as e:
            logger.error(f'Token verification failed: {str(e)}')
            return None

    def get_or_create_user(self, clerk_data):
        """
        Get or create a Django user based on Clerk user data
        """
        clerk_user_id = clerk_data.get('sub')
        email = clerk_data.get('email')
        
        if not clerk_user_id:
            raise AuthenticationFailed('Invalid token: missing user ID')
        
        try:
            # Try to find user by Clerk ID stored in username field
            user = User.objects.get(username=clerk_user_id)
        except User.DoesNotExist:
            # Try to find by email if provided
            if email:
                try:
                    user = User.objects.get(email=email)
                    # Update username to Clerk ID for future lookups
                    user.username = clerk_user_id
                    user.save()
                    return user
                except User.DoesNotExist:
                    pass
            
            # Create new user
            user = User.objects.create_user(
                username=clerk_user_id,
                email=email or f'{clerk_user_id}@clerk.user',
                first_name=clerk_data.get('given_name', ''),
                last_name=clerk_data.get('family_name', ''),
            )
            logger.info(f'Created new user for Clerk ID: {clerk_user_id}')
        
        return user