from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from markdownx.utils import markdownify
from ..models import *
from django.template import Template
from django.utils.http import urlencode

register = template.Library()


def static_for_db_record(text):
    """
    Convert /static/ and /media/ to {% static %} and {% media %}.
    Useful for URLs stored in db record.
    """
    if "/static/" in text:
        text = text.split("/static/")
        text = settings.STATIC_URL.join(text)
    if "/media/" in text:
        text = text.split("/media/")
        text = settings.MEDIA_URL.join(text)
    return text


@register.simple_tag
def html_bloc(nom):
    try:
        b = Bloc.objects.get(nom=nom)
        content = b.contenu
        # check for static or media and replace with actual values
        content = static_for_db_record(content)
        return mark_safe(content)
    except:
        return ''


@register.filter_function
def markdown(content):
    return markdownify(content)


@register.simple_tag(takes_context=True)
def templatize(context, content):
    # Replace /static/ and /media/ in URLs
    content = static_for_db_record(content)
    return Template('{% load contenu_tags %}' + content).render(context)


@register.simple_tag(takes_context=True)
def soustraire(context, a, b):
    return str(round(a - b, 2)).replace('.', ',')


@register.simple_tag(takes_context=True)
def filter_params(context, key, value):
    params = {}
    for k in context.request.GET:
        params[k] = context.request.GET.get(k)
    params[key] = value
    return urlencode(params)


@register.simple_tag(takes_context=True)
def filter_params_form(context, ignore):
    ignore = ignore.split(',')
    params = ''
    for k in context.request.GET:
        if k not in ignore:
            params += '<input type="hidden" name="%s" value="%s" />' % (k, context.request.GET.get(k))
    return params


@register.inclusion_tag('contenu/tags/footer_actu.html')
def footer_actu():
    return {'actus': Actualite.objects.order_by('-date')[:3]}
