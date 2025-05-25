from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Document
from .serializers import UserSerializer, DocumentSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import os
import json
from django.conf import settings
import fitz  # PyMuPDF for PDF processing
import requests
from django.core.exceptions import ValidationError

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        file = self.request.FILES['file']
        file_type = file.name.split('.')[-1].lower()
        
        # Validate file type
        if file_type not in ['pdf', 'doc', 'docx']:
            raise ValidationError('Unsupported file type. Only PDF, DOC, and DOCX files are allowed.')
        
        # Validate file size (10MB limit)
        if file.size > 10 * 1024 * 1024:
            raise ValidationError('File size cannot exceed 10MB.')

        serializer.save(
            user=self.request.user,
            file_type=file_type,
            size=file.size
        )

    @action(detail=True, methods=['post'])
    def ask(self, request, pk=None):
        document = self.get_object()
        question = request.data.get('question')

        if not question:
            return Response(
                {'error': 'Question is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract text based on file type
        text = ""
        try:
            if document.file_type == 'pdf':
                doc = fitz.open(document.file.path)
                for page in doc:
                    text += page.get_text()
                doc.close()
            else:
                return Response(
                    {'error': 'Question answering is only supported for PDF files'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Configure the request to Gemini API
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                return Response(
                    {'error': 'Gemini API key is not configured'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            try:
                url = 'https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent'
                headers = {
                    'Content-Type': 'application/json',
                }
                
                prompt = f"""Based on the following document excerpt, please answer this question: {question}

Document content:
{text[:5000]}

Please provide a clear and concise answer based only on the information present in the document."""

                payload = {
                    'contents': [{
                        'parts': [{
                            'text': prompt
                        }]
                    }]
                }

                response = requests.post(
                    f'{url}?key={api_key}',
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                print(f"Status Code: {response.status_code}")
                print(f"Response Headers: {response.headers}")
                print(f"Response Text: {response.text[:1000]}")

                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        error_message = error_data.get('error', {}).get('message', 'Unknown error occurred')
                    except ValueError:
                        error_message = response.text or 'No error message available'
                    return Response(
                        {
                            'error': f'Gemini API error: {error_message}',
                            'status_code': response.status_code,
                            'response_headers': dict(response.headers),
                            'response_text': response.text[:1000]  # First 1000 chars of response
                        }, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                try:
                    data = response.json()
                except ValueError:
                    return Response(
                        {
                            'error': 'Invalid JSON response from Gemini API',
                            'response_text': response.text[:1000],  # First 1000 chars of response
                            'status_code': response.status_code,
                            'response_headers': dict(response.headers)
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                if not data.get('candidates'):
                    return Response(
                        {
                            'error': 'No response generated from the AI model',
                            'response_text': response.text[:1000],
                            'status_code': response.status_code,
                            'response_headers': dict(response.headers)
                        }, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                answer = data['candidates'][0]['content']['parts'][0]['text']
                return Response({'answer': answer})

            except requests.exceptions.RequestException as e:
                print(f"Request Exception: {str(e)}")
                return Response(
                    {
                        'error': f'Failed to connect to Gemini API: {str(e)}',
                        'details': {
                            'type': type(e).__name__,
                            'message': str(e)
                        }
                    }, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as e:
                print(f"General Exception: {str(e)}")
                return Response(
                    {
                        'error': f'Error processing response: {str(e)}',
                        'details': {
                            'type': type(e).__name__,
                            'message': str(e)
                        }
                    }, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            return Response(
                {'error': f'Failed to process document: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def list_models(self, request):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return Response(
                {'error': 'Gemini API key is not configured'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            url = 'https://generativelanguage.googleapis.com/v1/models'
            headers = {
                'Content-Type': 'application/json',
            }

            response = requests.get(
                f'{url}?key={api_key}',
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:
                error_data = response.json() if response.text else {'error': 'Unknown error'}
                error_message = error_data.get('error', {}).get('message', 'Unknown error occurred')
                return Response(
                    {'error': f'Gemini API error: {error_message}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response(response.json())

        except requests.exceptions.RequestException as e:
            return Response(
                {
                    'error': f'Failed to connect to Gemini API: {str(e)}',
                    'details': {
                        'type': type(e).__name__,
                        'message': str(e)
                    }
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
