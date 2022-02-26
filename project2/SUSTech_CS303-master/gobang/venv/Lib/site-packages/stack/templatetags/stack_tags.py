from django import template
from django.template.loader import render_to_string
from django.db.models import Count
# This next import is available at http://github.com/subsume/django-comment-plus
from comments_plus.templatetags import comments_plus_tags as tt

from stack import models as sm

register = template.Library()

class KarmaCommentListNode(tt.KarmaCommentListNode):
    """Insert a list of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
	question_pk = self.get_target_ctype_pk(context)
	question = sm.Question.objects.get(pk=question_pk[1])
        return list(qs.exclude(pk=question.comment_id).annotate(Count('karma')))

def get_answer_list(parser, token):
    return KarmaCommentListNode.handle_token(parser, token)

register.tag(get_answer_list)

class RenderCommentStageNode(tt.RenderCommentStageNode):
    def render(self, context):
        template_search_list = [
            "stack/answer_stage.html"
        ]
	return super(RenderCommentStageNode,self).render(context,template_search_list=template_search_list)

def render_answer_stage(parser, token):
	return RenderCommentStageNode.handle_token(parser, token)

register.tag(render_answer_stage)
