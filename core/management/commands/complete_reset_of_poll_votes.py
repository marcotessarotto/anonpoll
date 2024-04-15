from django.core.management import BaseCommand

from core.models import Question, question_reset_votes


class Command(BaseCommand):
    #

    def add_arguments(self, parser):
        parser.add_argument('--question_id', type=int, help='question id to reset votes for', required=True)

    def handle(self, *args, **options):

        question_id = options['question_id']

        # get instance of Question
        question = Question.objects.get(id=question_id)

        # reset votes for the given question
        question_reset_votes(question)

        print("Votes reset for question: ", question)
