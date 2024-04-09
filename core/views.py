from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from .models import Choice, Question


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'core/index.html', context)


def detail(request, question_id):
    return HttpResponse(f"You're looking at question {question_id}.")


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if not question.is_active():
        return HttpResponse("This poll is not active.")

    if request.COOKIES.get(f'has_voted_{question_id}'):
        return HttpResponse("You have already voted in this poll.")

    try:
        # Retrieve the selected choice based on the ID submitted in the POST request.
        # The 'choice' is the name of the input in your form that holds the choice's ID.
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form if the choice is not found.
        return render(request, 'core/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        # Increment the vote count for the selected choice and save.
        selected_choice.votes += 1
        selected_choice.save()

        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        response = HttpResponseRedirect(reverse('core:results', args=(question.id,)))

        # Set the cookie to block re-voting, with expiration at the question's end time.
        response.set_cookie(f'has_voted_{question_id}', 'true', expires=question.end_time)

        return response
