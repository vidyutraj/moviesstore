from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Reset location popup for testing - clears session storage flag'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                'Location popup reset for testing!\n'
                'To see the popup again:\n'
                '1. Open browser Developer Tools (F12)\n'
                '2. Go to Application/Storage tab\n'
                '3. Delete "locationPopupShown" from Session Storage\n'
                '4. Refresh the page\n\n'
                'OR use incognito/private browsing mode.\n\n'
                'The popup will appear when you visit any page while logged in.'
            )
        )
