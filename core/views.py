import locale
import syslog
from datetime import date

import pytz
import requests
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from anonpoll.email_utils import my_send_email
from anonpoll.settings import DEBUG, TECHNICAL_CONTACT_EMAIL, TECHNICAL_CONTACT, CHECK_SUBSCRIBER_WS_URL, SUBJECT_EMAIL, \
    FROM_EMAIL, DEBUG_EMAIL, EMAIL_HOST
from anonpoll.view_tools import is_private_ip
from .forms import VoteForm, SubscriberLoginForm, make_named_survey_form
from .logic import create_event_log, create_subscriber_if_not_exits
from .models import Choice, Question, ChoiceVote, ChoiceSuggestedByUser, ChoiceVoteSuggestedByUser, EventLog, \
    NamedSurvey, NamedSurveyResponse, NamedSurveyQuestion, NamedSurveyAnswer, Subscriber


def index(request):
    latest_question_list = Question.objects.all()  # order_by('-pub_date')[:5]
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

    if not question.is_active():
        return HttpResponse(_("This poll is not active."))

    cookie_name = f'has_voted_{question.ref_token}'

    if request.COOKIES.get(cookie_name):
        return HttpResponse(_("You have already voted in this poll."))

    if request.method == 'POST':
        form = VoteForm(request.POST, question=question)
        if form.is_valid():
            choice = form.cleaned_data['choice']
            accept_privacy_policy = form.cleaned_data['accept_privacy_policy']
            text_choice = form.cleaned_data.get('text_choice', None)

            print(f"form.cleaned_data: {form.cleaned_data}")

            if accept_privacy_policy == 'yes':

                if choice.is_choice_text_user_defined():
                    # If the user's choice is a user-defined choice, lookup for an instance with the same choice_text
                    # and question, if it exists, increment the votes, otherwise create a new instance
                    user_choice = ChoiceSuggestedByUser.objects.filter(
                        question=question,
                        choice_text=text_choice,
                    ).first()

                    if user_choice is None:
                        user_choice = ChoiceSuggestedByUser(
                            question=question,
                            choice_text=text_choice,
                            votes=1,
                        )
                    else:
                        user_choice.votes += 1

                    user_choice.save()

                    new_vote = ChoiceVoteSuggestedByUser(
                        question=question,
                        choice=user_choice,
                    )
                    new_vote.save()

                else:
                    choice.votes += 1
                    choice.save()

                    # Create a new ChoiceVote instance
                    new_vote = ChoiceVote(
                        question=question,
                        choice=choice,
                    )

                    new_vote.save()

                # Always return an HttpResponseRedirect after successfully dealing
                # with POST data. This prevents data from being posted twice if a
                # user hits the Back button.
                response = HttpResponseRedirect(reverse('core:success_url', args=(question_slug,)))

                if not DEBUG:
                    # Set the cookie to block re-voting, with expiration at the question's end time.
                    response.set_cookie(cookie_name, 'true', expires=question.end_time)

                return response
            else:
                # Handle the case where privacy policy is not accepted
                form.add_error('accept_privacy_policy',
                               _('You must accept the privacy policy to participate to the poll.'))
    else:
        form = VoteForm(question=question)

    context = {
        'question': question,
        'form': form,
        'TECHNICAL_CONTACT_EMAIL': TECHNICAL_CONTACT_EMAIL,
        'TECHNICAL_CONTACT': TECHNICAL_CONTACT,
    }
    return render(request, 'core/vote.html', context)


def success_url(request, question_slug):
    http_real_ip = request.META.get('HTTP_X_REAL_IP', '')

    if not request.user.is_authenticated or not request.user.is_superuser:
        # Check if the IP is private
        if http_real_ip != '' and not is_private_ip(http_real_ip) and not DEBUG:
            syslog.syslog(syslog.LOG_ERR, f'IP address {http_real_ip} is not private')
            return render(request, 'core/show_generic_message.html',
                          {'message': "403 Forbidden - accesso consentito solo da intranet"}, status=403)

    # get question by slug
    question = get_object_or_404(Question, slug=question_slug)

    if not question.is_active():
        return HttpResponse("This poll is not active.")

    # Get the current date and time
    # current_datetime = timezone.now()

    # Set the locale to Italian
    locale.setlocale(locale.LC_TIME, 'it_IT.utf8')
    rome_tz = pytz.timezone("Europe/Rome")

    if timezone.is_naive(question.end_time):
        # If start_date is naive, make it aware using Europe/Rome timezone
        end_date_aware = timezone.make_aware(question.end_time, rome_tz)
    else:
        # If start_date is already aware, just ensure it's using Europe/Rome timezone
        end_date_aware = question.end_time.astimezone(rome_tz)  # <====

    # Format the date in a common Italian format
    formatted_date = end_date_aware.strftime("%d %B %Y, %H:%M")
    print(formatted_date)

    context = {
        'question': question,
        'TECHNICAL_CONTACT_EMAIL': TECHNICAL_CONTACT_EMAIL,
        'TECHNICAL_CONTACT': TECHNICAL_CONTACT,
        'end_date': formatted_date,
    }

    return render(request, 'core/thanks_poll_participation.html', context)


__subscriber_dict = {}


def show_survey_question(request, question_slug):
    http_real_ip = request.META.get('HTTP_X_REAL_IP', '')

    if not request.user.is_authenticated or not request.user.is_superuser:
        # Check if the IP is private
        if http_real_ip != '' and not is_private_ip(http_real_ip) and not DEBUG:
            syslog.syslog(syslog.LOG_ERR, f'IP address {http_real_ip} is not private')
            return render(request, 'core/show_generic_message.html',
                          {'message': "403 Forbidden - accesso consentito solo da intranet"}, status=403)

    # check request.session['subscriber_id'] and retrieve the subscriber instance
    subscriber_id = request.session.get('subscriber_id')
    if subscriber_id:
        # subscriber = Subscriber.objects.get(id=subscriber_id)
        pass
    else:
        # send email to admin
        # redirect to login page
        return redirect('subscriber-login')

    return None


def subscriber_login(request, question_slug):
    # get ip address from request META
    http_real_ip = request.META.get('HTTP_X_REAL_IP', '')

    # Check if the IP is private
    if http_real_ip != '' and not is_private_ip(http_real_ip) and not DEBUG:
        syslog.syslog(syslog.LOG_ERR, f'IP address {http_real_ip} is not private')
        return render(request, 'show_message.html', {'message': "403 Forbidden - accesso consentito solo da intranet"},
                      status=403)

    # check existence of NamedSurvey instance with the given slug
    named_survey = get_object_or_404(NamedSurvey, slug=question_slug)
    if named_survey is None:
        return render(request, 'show_message.html', {'message': "404 Not Found - survey non trovato"}, status=404)

    if request.method == 'POST':
        form = SubscriberLoginForm(request.POST)
        if form.is_valid():
            matricola = form.cleaned_data['matricola']
            email = form.cleaned_data['email']

            params = {'matricola': matricola, 'email': email}

            url = CHECK_SUBSCRIBER_WS_URL

            try:
                response = requests.get(url, params=params)
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()
                exists = data.get('exists', False)
                if exists:
                    subscriber = data.get('subscriber', {})

                    create_event_log(
                        event_type=EventLog.LOGIN_SUCCESS,
                        event_title="Subscriber login success",
                        event_data=f"matricola: {matricola} email: {email} http_real_ip: {http_real_ip}",
                    )

                    subscriber = create_subscriber_if_not_exits(
                        email=subscriber.get('email', ''),
                        name=subscriber.get('name', ''),
                        surname=subscriber.get('surname', ''),
                        matricola=subscriber.get('matricola', ''),
                    )

                    # login(request, user, backend=AUTHENTICATION_BACKENDS[0])

                    # Simulate login by saving subscriber's ID in session (example)
                    request.session['subscriber_id'] = subscriber.id
                    request.session['question_slug'] = question_slug

                    # Reverse the URL with the slug parameter
                    url = reverse('core:post-authenticated-survey', kwargs={'question_slug': question_slug})

                    return redirect(url)

                else:

                    create_event_log(
                        event_type=EventLog.LOGIN_FAILED,
                        event_title="Subscriber login failed",
                        event_data=f"matricola: {matricola} email: {email} http_real_ip: {http_real_ip}",
                    )

                    messages.error(request, 'errore: matricola o email non validi')

            except requests.RequestException as e:
                # self.stderr.write(self.style.ERROR(f'Error calling CheckSubscriberView: {e}'))

                create_event_log(
                    event_type=EventLog.LOGIN_FAILED,
                    event_title="Subscriber login failed",
                    event_data=f"matricola: {matricola} email: {email} http_real_ip: {http_real_ip} error: {e}",
                )

                messages.error(request, 'errore: matricola o email non validi')

    else:
        form = SubscriberLoginForm()

    context = {
        'APPLICATION_TITLE': '-',
        'TECHNICAL_CONTACT_EMAIL': TECHNICAL_CONTACT_EMAIL,
        'TECHNICAL_CONTACT': TECHNICAL_CONTACT,
        'form': form,
        # 'question_slug': question_slug,
    }

    return render(request, 'subscribers/login.html', context)


def post_authenticated_survey(request, question_slug):

    # get ip address from request META
    http_real_ip = request.META.get('HTTP_X_REAL_IP', '')

    # Check if the IP is private
    if http_real_ip != '' and not is_private_ip(http_real_ip) and not DEBUG:
        syslog.syslog(syslog.LOG_ERR, f'IP address {http_real_ip} is not private')
        return render(request, 'show_message.html', {'message': "403 Forbidden - accesso consentito solo da intranet"},
                      status=403)

    survey = get_object_or_404(NamedSurvey, slug=question_slug)
    if not survey.is_active():
        return HttpResponse("This named survey is not currently active.", status=403)

    # check http session for subscriber_id
    subscriber_id = request.session.get('subscriber_id')
    if subscriber_id is None:
        url = reverse('core:subscriber-login', kwargs={'question_slug': question_slug})
        return redirect(url)

    PollForm = make_named_survey_form(survey)
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            response = NamedSurveyResponse(survey=survey)
            response.save()
            for field in form.cleaned_data:
                question_id = field.split('_')[1]
                question = get_object_or_404(NamedSurveyQuestion, id=question_id)
                text = form.cleaned_data[field]
                NamedSurveyAnswer.objects.create(response=response, question=question, text=text)

            # prepare a summary of the submitted data by user
            summary = []
            for field in form.cleaned_data:
                question_id = field.split('_')[1]
                question = get_object_or_404(NamedSurveyQuestion, id=question_id)
                text = form.cleaned_data[field]
                summary.append(f"{question.text}: {text}")

            # send an email to the user with the summary
            # get Subscriber istance using subscriber_id
            subscriber = get_object_or_404(Subscriber, id=subscriber_id)

            message_subject = f'Riepilogo delle tue risposte al sondaggio "{survey.title}"'
            message_body = f'Ciao {subscriber.name},<br><br>'
            message_body += f'grazie per aver partecipato alla nostra indagine.<br><br>'
            message_body += 'Ecco il riepilogo delle tue risposte:<br><br>'
            message_body += '<br>'.join(summary)

            # add data to the http session
            request.session['survey_summary'] = summary
            request.session['survey_id'] = survey.id
            request.session['message_body'] = message_body
            request.session['message_subject'] = message_subject

            if DEBUG:
                print(f"debug mode: fake sending email to {subscriber.email}")
                print(f"message: {message_body}  (debug mode)")
            else:
                my_send_email(
                    FROM_EMAIL,
                    [subscriber.email],
                    message_subject,
                    message_body,
                    bcc_addresses=[DEBUG_EMAIL],
                    attachments=None,
                    email_host=EMAIL_HOST
                )

            create_event_log(
                event_type=EventLog.EMAIL_SENT,
                event_title=message_subject,
                event_data=f"subscriber: {subscriber} email: {subscriber.email} {message_body}",
                event_target=subscriber.email,
            )

            success_url = reverse('core:authenticated-survey-success-url', args=(survey.slug,))
            return redirect(success_url)
    else:
        form = PollForm()

    return render(request, 'named_polls/poll_form.html', {'form': form, 'survey': survey})


def authenticated_survey_successl_url(request, question_slug):
    message_body = request.session.get('message_body')

    context = {
        'APPLICATION_TITLE': '-',
        'TECHNICAL_CONTACT_EMAIL': TECHNICAL_CONTACT_EMAIL,
        'TECHNICAL_CONTACT': TECHNICAL_CONTACT,
        'message_body': message_body,
        # 'form': form,
        # 'question_slug': question_slug,
    }

    return render(request, 'named_polls/thanks_poll_participation.html', context)