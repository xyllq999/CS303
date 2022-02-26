from django.conf.urls import patterns, url
from stack.views import QuestionList

urlpatterns = patterns(
    'stack.views',
    url('^$', 'home', name="stack_question_home"),
    url('^all/$', QuestionList.as_view(), name="stack_question_list"),
    url('^add/$', 'add', name="stack_question_add"),
    url('^preview/$', 'preview', name="stack_question_preview"),

    url('^(?P<slug>[^/]+)/$', 'detail', name="stack_question_detail"),
    url('^(?P<slug>[^/]+)/accepted-answer/(?P<comment>[^/]+)/$', 'accepted_answer', name="stack_accepted_answer"),
)
