from stack.models import Question

class QuestionLookup(object):
	def get_query(self,q,request):
		return Question.objects.filter(title__search=q.strip())
	
	def format_item(self,obj):
		return '%s' % obj.get_absolute_url()

	def get_objects(self,ids):
		""" given a list of ids, return the objects ordered as you would like them on the admin page.
		this is for displaying the currently selected items (in the case of a ManyToMany field)
		"""
		return Question.objects.filter(pk__in=ids)
	
	def format_result(self,obj):
		""" a more verbose display, used in the search results display.  may contain html and multi-lines """
		return '<a href=\"%s\">%s</a>' % (obj.get_absolute_url(),obj)


class QuestionHaystackLookup(QuestionLookup):
	def get_query(self,q,request):
		if not q or len(q) < 3:
			return []

		from haystack.query import SearchQuerySet
		return Question.objects.filter(pk__in=[c.pk for c in SearchQuerySet().models(Question).auto_query(q)])
