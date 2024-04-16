from django.core.management import BaseCommand

from core.models import Question, question_reset_votes


class Command(BaseCommand):
    # provide a list of results of a poll

    def add_arguments(self, parser):
        parser.add_argument('--question_id', type=int, help='question id to calculate votes for', required=True)

    def handle(self, *args, **options):

        question_id = options['question_id']

        # get instance of Question
        question = Question.objects.get(id=question_id)

        # get all Choice instances associated to question:
        choices = question.choice_set.all()

        # sort choices by votes, descending
        choices = sorted(choices, key=lambda x: x.votes, reverse=True)

        # create a dict using choice_text as key and votes as value
        choices = {choice.choice_text: choice.votes for choice in choices}

        # exclude 'ZZZ_USER_DEFINED' choice
        choices.pop('ZZZ_USER_DEFINED', None)

        # consider also choices suggested by users
        user_suggested_choices = question.choicesuggestedbyuser_set.all()
        if user_suggested_choices:
            # sort user suggested choices by votes, descending
            user_suggested_choices = sorted(user_suggested_choices, key=lambda x: x.votes, reverse=True)

            # create a dict using choice_text as key and votes as value
            user_suggested_choices = {choice.choice_text: choice.votes for choice in user_suggested_choices}

        else:
            user_suggested_choices = {}

        # join the two dicts
        choices |= user_suggested_choices

        # sort the dict by votes, descending
        choices = dict(sorted(choices.items(), key=lambda x: x[1], reverse=True))

        # print results
        print(f"Results for question: {question.question_text}")
        for choice, votes in choices.items():
            print(f"{choice}: {votes} votes")

        # send the same results to the admin email


