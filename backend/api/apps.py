from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        import os
        # Only start polling in the main process (not the reloader child)
        if os.environ.get('RUN_MAIN') == 'true':
            from .poll_service import start_polling
            start_polling()
