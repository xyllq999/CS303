from django.contrib import admin
from stack import models as sm

def title_snippet(obj):
	return obj.title[:30]

def user(obj):
	return obj.comment.user

class QuestionAdmin(admin.ModelAdmin):
	list_display = [title_snippet,user]
	raw_id_fields = ['comment','accepted_answer']

admin.site.register(sm.Question,QuestionAdmin)
