from django import forms

from stack import models as sm

class QuestionForm(forms.ModelForm):
	comment = forms.CharField(widget=forms.widgets.Textarea,label="Explanation",help_text="Background about your question")
	def __init__(self,*args,**kwargs):
		super(QuestionForm,self).__init__(*args,**kwargs)
		self.fields['title'].widget.attrs = {'style': 'width:400px;font-size:18px'}

	class Meta:
		model = sm.Question
		exclude = ['comment','slug','accepted_answer','has_answer', 'site']

class AjaxQuestionForm(QuestionForm): # Optional
	def __init__(self,*args,**kwargs):
		super(AjaxQuestionForm,self).__init__(*args,**kwargs)
		from ajax_select import fields as afields

		# The above may fail, obviously, if you don't have ajax select
		self.fields['title'] = afields.AutoCompleteField('question')
		self.fields['title'].widget.attrs.update({'style': 'width:400px;font-size:18px'})
