from django.shortcuts import render, get_object_or_404

from .models import *
from django.core.urlresolvers import reverse
# Create your views here.


def actu_liste(request):
    actus = Actualite.objects.order_by('-date')
    actu_par_page = 6
    page_courante = int(request.GET.get('p', 1))
    pagination = []
    if actus.count() > actu_par_page:
        nb_pages = actus.count() / actu_par_page
        if actus.count() % actu_par_page > 0:
            nb_pages += 1
        pagination = range(1, nb_pages + 1)

    return render(request, 'actu/liste.html', {
        'actus' : actus[(page_courante - 1) * actu_par_page : page_courante * actu_par_page],
        'pagination' : pagination,
        'page_courante' : page_courante,
    })

def actu_detail(request, actu_url):
    return render(request, 'actu/detail.html', {
        'actu' : get_object_or_404(Actualite, url=actu_url),
    })


def page_detail(request, page_adresse):
    return render(request, 'contenu/page.html', {
        'page' : get_object_or_404(Page, adresse=page_adresse),
    })


def sitemap(request):
    urls = []
    for actu in Actualite.objects.all():
        urls.append(reverse('actu-detail', args=[actu.url]))
    for page in Page.objects.all():
        urls.append(reverse('page-detail', args=[page.adresse]))
    return render(request, 'sitemap.xml', {
        'urls' : urls,
    })
