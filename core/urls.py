from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    # path('<int:question_id>/', views.detail, name='detail'),
    # path('<int:question_id>/results/', views.results, name='results'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),

    path('<str:question_slug>/show-poll-question/', views.show_poll_question, name='show-poll-question'),

    path('<str:question_slug>/success_url/', views.success_url, name='success_url'),

    path('<str:question_slug>/show-survey-question/', views.show_survey_question, name='show-survey-question'),

    path('login/', views.subscriber_login, name='subscriber-login'),
]
