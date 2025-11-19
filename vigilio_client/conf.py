"""
Configuration settings for Vigilio Client Django App

Add these settings to your Django project's settings.py:

# Vigilio gRPC Client Settings
VIGILIO_GRPC_HOST = '127.0.0.1:50051'  # gRPC server host and port
VIGILIO_GRPC_SECURE = False  # Use secure connection (SSL/TLS)
VIGILIO_GRPC_CREDENTIALS_PATH = None  # Path to SSL credentials if secure=True
"""

from django.conf import settings


def get_vigilio_setting(name, default=None):
    """Helper to get Vigilio settings with defaults"""
    return getattr(settings, f'VIGILIO_{name}', default)


# Default configuration
DEFAULTS = {
    'GRPC_HOST': '127.0.0.1:50051',
    'GRPC_SECURE': False,
    'GRPC_CREDENTIALS_PATH': None,
}