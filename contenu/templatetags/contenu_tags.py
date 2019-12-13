from django import template
from django.utils.datetime_safe import datetime
from django.utils.safestring import mark_safe
from markdownx.utils import markdownify
from ..models import *
from django.shortcuts import render
from django.template import Template, Context
from django.utils.http import urlencode

register = template.Library()


@register.simple_tag
def html_bloc(nom):
    try:
        b = Bloc.objects.get(nom=nom)
        return mark_safe(b.contenu)
    except:
        return ''

@register.filter_function
def markdown(input):
    return markdownify(input)

@register.simple_tag(takes_context=True)
def templatize(context, input):
    return Template('{% load contenu_tags %}' + input).render(context)

@register.simple_tag(takes_context=True)
def soustraire(context, a, b):
    return unicode(round(a - b, 2)).replace('.', ',')


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
        if not k in ignore:
            params += '<input type="hidden" name="%s" value="%s" />' % (k, context.request.GET.get(k))
    return params

@register.inclusion_tag('contenu/tags/footer_actu.html')
def footer_actu():
    return {'actus' : Actualite.objects.order_by('-date')[:3]}
