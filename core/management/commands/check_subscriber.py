import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Check if a subscriber with the given matricola and email exists.'
    # ./manage.py check_subscriber 123456 test@example.com http://localhost:8000/registrazione/check-subscriber/

    def add_arguments(self, parser):
        parser.add_argument('matricola', type=str, help='Matricola of the subscriber')
        parser.add_argument('email', type=str, help='Email of the subscriber')
        parser.add_argument('url', type=str, help='URL of the web service')

    def handle(self, *args, **kwargs):
        matricola = kwargs['matricola']
        email = kwargs['email']
        url = kwargs['url']

        # url = 'http://your_domain.com/check-subscriber/'  # Replace with the actual URL of your web service
        params = {'matricola': matricola, 'email': email}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            exists = data.get('exists', False)
            if exists:
                self.stdout.write(
                    self.style.SUCCESS(f'Subscriber with matricola {matricola} and email {email} exists.'))
            else:
                self.stdout.write(
                    self.style.WARNING(f'Subscriber with matricola {matricola} and email {email} does not exist.'))
        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(f'Error calling CheckSubscriberView: {e}'))
