from django.core.management.base import BaseCommand
from core.models import User, ConsumerProfile, MerchantProfile, AgentProfile

class Command(BaseCommand):
    help = 'Create missing profiles for existing users based on their user_type.'

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            if user.user_type == 'consumer' and not hasattr(user, 'consumer_profile'):
                ConsumerProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created ConsumerProfile for user {user.username}'))
            elif user.user_type == 'merchant' and not hasattr(user, 'merchant_profile'):
                MerchantProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created MerchantProfile for user {user.username}'))
            elif user.user_type == 'agent' and not hasattr(user, 'agent_profile'):
                AgentProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created AgentProfile for user {user.username}'))