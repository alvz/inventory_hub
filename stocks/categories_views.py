from django.contrib import messages
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from stocks.forms import BatchUpdateForm, CategoryForm
from stocks.models import Category, Stock
from utils.tools import capwords


def index(request):
    categories = Category.objects.all()

    data = {
        'categories': categories,
    }

    return render_to_response(
        'stocks/categories/index.html',
        data,
        context_instance=RequestContext(request),
    )


def create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created')
    else:
        form = CategoryForm()

    data = {
        'form': form,
    }

    return render_to_response(
        'stocks/categories/create.html',
        data,
        context_instance=RequestContext(request),
    )


def update(request, category_id):
    category = get_object_or_404(Category, pk=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated')
    else:
        form = CategoryForm(instance=category)

    data = {
        'category': category,
        'form': form,
    }

    return render_to_response(
        'stocks/categories/update.html',
        data,
        context_instance=RequestContext(request),
    )


def delete(request):
    category_id = int(request.POST.get('entry_id', 0))
    try:
        category = Category.objects.get(pk=category_id)
        category.delete()
        messages.success(request, 'Category deleted')
    except Category.DoesNotExist:
        messages.error(request, 'Category with id %i does not exist' % category_id)
    data = reverse('stocks:categories:index')
    return HttpResponse(data, mimetype="application/javascript")


def add_ajax(request):
    new_category = request.POST.get('new_category', '')
    new_category = capwords(new_category)
    if new_category:
        Category.objects.get_or_create(name=new_category)

    data = {
        'categories': Category.objects.order_by('name'),
        'new_category': new_category,
    }

    return render_to_response(
        'stocks/categories/all.html',
        data,
        context_instance=RequestContext(request),
    )


def inventory(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    q = request.GET.get('q', '')
    stock_list = Stock.objects.filter(category=category)
    stock_list = stock_list.filter(
        Q(description__icontains=q) |
        Q(item_code__icontains=q)
    )

    paginator = Paginator(stock_list, 20)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        stocks = paginator.page(page)
    except (EmptyPage, InvalidPage):
        stocks = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = BatchUpdateForm(request.POST)
        if form.is_valid():
            print request.POST.getlist('checked-stocks')
            print form.cleaned_data['retail_price']
    else:
        form = BatchUpdateForm()   

    data = {
        'category': category,
        'form': form,
        'q': q,
        'stocks': stocks,
    }

    return render_to_response(
        'stocks/categories/inventory.html',
        data,
        context_instance=RequestContext(request),
    )
