import syslog

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


from anonpoll.settings import DEBUG, TECHNICAL_CONTACT_EMAIL, TECHNICAL_CONTACT
from anonpoll.view_tools import is_private_ip
from .forms import VoteForm
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


def show_poll_question(request, question_slug):
    http_real_ip = request.META.get('HTTP_X_REAL_IP', '')

    if not request.user.is_authenticated or not request.user.is_superuser:
        # Check if the IP is private
        if http_real_ip != '' and not is_private_ip(http_real_ip) and not DEBUG:
            syslog.syslog(syslog.LOG_ERR, f'IP address {http_real_ip} is not private')
            return render(request, 'core/show_generic_message.html',
                          {'message': "403 Forbidden - accesso consentito solo da intranet"}, status=403)

    # get question by slug
    question = get_object_or_404(Question, slug=question_slug)

    print(f"Question: {question}")

    if not question.is_active():
        return HttpResponse("This poll is not active.")

    cookie_name = f'has_voted_{question.ref_token}'

    if request.COOKIES.get(cookie_name):
        return HttpResponse("You have already voted in this poll.")

    if request.method == 'POST':
        form = VoteForm(request.POST, question=question)
        if form.is_valid():
            choice = form.cleaned_data['choice']
            accept_privacy_policy = form.cleaned_data['accept_privacy_policy']

            if accept_privacy_policy == 'yes':
                choice.votes += 1
                choice.save()
                # Redirect to a new URL to show the vote was successful
                return redirect('success_url')  # Replace 'success_url' with your actual success URL
            else:
                # Handle the case where privacy policy is not accepted
                form.add_error('accept_privacy_policy', _('You must accept the privacy policy to participate to the poll.'))
    else:
        form = VoteForm(question=question)

    context = {
        'question': question,
        'form': form,
        'TECHNICAL_CONTACT_EMAIL': TECHNICAL_CONTACT_EMAIL,
        'TECHNICAL_CONTACT': TECHNICAL_CONTACT,
    }
    return render(request, 'core/vote.html', context)









    if request.method == 'POST':
        pass

    context = {
        'question': question,
        'choices': question.get_choices(randomize_choices=True),
    }



    return None