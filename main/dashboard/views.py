from django.shortcuts import render, redirect
from main import models
from main.funcs import staff_required
from itertools import chain
from django.db.models import Q
from datetime import datetime

@staff_required 
def index(request):
    context = {}
    return render(request, 'dashboard/index.html', context)

# ---------- CATEGORY ----------

@staff_required 
def category_list(request):
    queryset = models.Category.objects.all()
    context = {
        'queryset':queryset
        }
    return render(request, 'dashboard/category/list.html', context)

@staff_required 
def category_create(request):
    if request.method == 'POST':
        models.Category.objects.create(
            name = request.POST['name']
        )
        return redirect('dashboard:category_list')
    return render(request, 'dashboard/category/create.html')

@staff_required 
def category_update(request, code):
    queryset = models.Category.objects.get(code=code)
    queryset.name = request.POST['name']
    queryset.save()
    return redirect('dashboard:category_list')

@staff_required 
def category_delete(request, code):
    queryset = models.Category.objects.get(code=code)
    queryset.delete()
    return redirect('dashboard:category_list')

# ---------- PRODUCT ----------

@staff_required 
def product_list(request):
    categories = models.Category.objects.all()
    category_code = request.GET.get('category_code')
    queryset = models.Product.objects.all()
    filter_items = {}
    for key, value in request.GET.items():
        if key == 'category_code' and value == '0':
            continue
        if value:
            if key == 'start_date':
                key = 'date__gte'
            elif key == 'end_date':
                key = 'date__lte'
            elif key == 'category_code':
                key = 'category__code'
            elif key == 'name':
                key = 'name__icontains'
            elif key == 'price':
                key = 'price__lte'
            elif key == 'is_discount':
                key = 'discount_price__isnull'
                filter_items[key] = False
                continue
            filter_items[key] = value
    queryset = models.Product.objects.filter(**filter_items)
    context = {
          'queryset':queryset,
          'categories':categories,
          'category_code':category_code,
    }
    return render(request, 'dashboard/product/list.html', context)

@staff_required 
def product_detail(request, code):
    queryset = models.Product.objects.get(code=code)
    images = models.ProductImg.objects.filter(product=queryset)
    reviews = models.Review.objects.filter(product=queryset)
    videos = models.ProductVideo.objects.filter(product=queryset)
    context = {
          'queryset':queryset,
          'images':images,
          'reviews':reviews,
          'videos':videos
    }
    return render(request, 'dashboard/product/detail.html', context)
    
@staff_required 
def product_create(request):
    categorys = models.Category.objects.all()
    context = {'categorys':categorys}
    if request.method == 'POST':
        delivery = True if request.POST.get('delivery') else False
        product = models.Product.objects.create(
            category_id = request.POST.get('category_id'),
            name = request.POST.get('name'),
            body = request.POST.get('body'),
            price = request.POST.get('price'),
            banner_img = request.FILES.get('banner_img'),
            quantity = request.POST.get('quantity'),
            delivery = delivery
        )
    if request.FILES.getlist('product_img'):
        for img in request.FILES.getlist('product_img'):
            models.ProductImg.objects.create(
                product = product,
                img = img
        )
    if request.FILES.getlist('product_video'):
        for video in request.FILES.getlist('product_video'):
            models.ProductVideo.objects.create(
                product = product,
                video = video
        )
        return redirect('dashboard:product_list')
    return render(request, 'dashboard/product/create.html', context)

@staff_required 
def product_update(request, code):
    images = models.ProductImg.objects.filter(product__code=code)
    videos = models.ProductVideo.objects.filter(product__code=code)
    categories = models.Category.objects.all()
    product = models.Product.objects.get(code=code)

    if request.method == 'POST':
        if request.FILES.get('banner_img'):
            product.banner_img = request.FILES.get('banner_img')
        delivery = True if request.POST.get('delivery') else False
        product.category_code = request.POST.get('category_code')
        product.name = request.POST.get('name')
        product.body = request.POST.get('body')
        product.price = request.POST.get('price') 
        product.delivery = delivery
        product.save()
    
    if request.FILES.getlist('product_img'):
        for img in request.FILES.getlist('product_img'):
            models.ProductImg.objects.create(
                product = product,
                img = img
        )
    if request.FILES.getlist('product_video'):
        for video in request.FILES.getlist('product_video'):
            models.ProductVideo.objects.create(
                product = product,
                video = video
        )
        return redirect('dashboard:product_update',product.code)
    
    context = {
          'images':images,
          'videos':videos,
          'categories':categories,
          'product':product
    }
    return render(request,'dashboard/product/update.html',context=context)

@staff_required 
def product_delete(request, code):
    product = models.Product.objects.get(code=code)
    product.delete()
    return redirect('dashboard:product_list')

@staff_required 
def product_img_delete(request, id):
    product_img = models.ProductImg.objects.get(id=id)
    product_img.delete()
    return redirect('dashboard:product_list')

@staff_required 
def product_video_delete(request, id):
    product_video = models.ProductVideo.objects.get(id=id)
    product_video.delete()
    return redirect('dashboard:product_update',product_video.product_id)

# ---------- ENTER PRODUCT ----------

@staff_required 
def create_enter_product(request):
    products = models.Product.objects.all()
    if request.method == 'POST':
        product = models.Product.objects.get(code=request.POST['code'])
        quantity = request.POST['quantity']
        models.EnterProduct.objects.create(
            product=product,
            quantity=int(quantity),
        )
        return redirect('dashboard:list_enter_product')
    context = {
        'products':products
    }
    return render(request, 'dashboard/enter_product/create.html', context)

@staff_required 
def list_enter_product(request):
    queryset = models.EnterProduct.objects.all()
    context = {
        'queryset':queryset
    }
    return render(request, 'dashboard/enter_product/list.html', context)

@staff_required 
def detail_enter_product(request, code):
    queryset = models.EnterProduct.objects.filter(product__code=code)
    context = {
        'queryset':queryset
    }
    return render(request, 'dashboard/enter_product/detail.html', context)

@staff_required 
def update_enter_product(request, code):
    enter_product = models.EnterProduct.objects.get(code=code)
    products = models.Product.objects.all()
    context = {
        'enter_product':enter_product,
        'products':products
    }
    if request.method == 'POST':
        enter_product.quantity = request.POST.get('quantity') 
        enter_product.date = request.POST.get('date') 
        enter_product.save()
    return render(request, 'dashboard/enter_product/update.html', context)
    
@staff_required 
def delete_enter_product(request, code):
    enter_product = models.EnterProduct.objects.get(code=code)
    enter_product.delete()
    return redirect('dashboard:list_enter_product')    

# ---------- PRODUCT HISTORY ----------

@staff_required 
def product_history(request, code):
    enters = models.EnterProduct.objects.filter(product__code=code)
    outs = models.CartProduct.objects.filter(product__code=code, cart__status=4)
    queryset = list(chain(enters, outs))
    queryset.sort(key=lambda x:x.date, reverse=True)
    result_queryset = []
    for query in queryset:
        try:
            models.EnterProduct.objects.get(code=query.code)
            query.is_enter = True
        except:
            query.is_enter = False
        result_queryset.append(query)
    
    
    return True


