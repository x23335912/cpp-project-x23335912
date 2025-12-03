from pickle import FALSE
from django.shortcuts import redirect, render
from django.http import HttpResponse
from posApp.models import Category, Products, Sales, salesItems
from django.db.models import Count, Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json, sys
from datetime import date, datetime

# Login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

# Create your views here.
@login_required
def home(request):
    now = datetime.now()
    current_year = now.strftime("%Y")
    current_month = now.strftime("%m")
    current_day = now.strftime("%d")
    categories = len(Category.objects.all())
    products = len(Products.objects.all())
    transaction = len(Sales.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ))
    today_sales = Sales.objects.filter(
        date_added__year=current_year,
        date_added__month = current_month,
        date_added__day = current_day
    ).all()
    total_sales = sum(today_sales.values_list('grand_total',flat=True))
    context = {
        'page_title':'Home',
        'categories' : categories,
        'products' : products,
        'transaction' : transaction,
        'total_sales' : total_sales,
    }
    return render(request, 'posApp/home.html',context)


def about(request):
    context = {
        'page_title':'About',
    }
    return render(request, 'posApp/about.html',context)

#Categories
@login_required
def category(request):
    category_list = Category.objects.all()
    # category_list = {}
    context = {
        'page_title':'Category List',
        'category':category_list,
    }
    return render(request, 'posApp/category.html',context)
@login_required
def manage_category(request):
    category = {}
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            category = Category.objects.filter(id=id).first()
    
    context = {
        'category' : category
    }
    return render(request, 'posApp/manage_category.html',context)

@login_required
def save_category(request):
    data =  request.POST
    resp = {'status':'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0 :
            save_category = Category.objects.filter(id = data['id']).update(name=data['name'], description = data['description'],status = data['status'])
        else:
            save_category = Category(name=data['name'], description = data['description'],status = data['status'])
            save_category.save()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully saved.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_category(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Category.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

# Products
@login_required
def products(request):
    product_list = Products.objects.all()
    context = {
        'page_title':'Product List',
        'products':product_list,
    }
    return render(request, 'posApp/products.html',context)
@login_required
def manage_products(request):
    product = {}
    categories = Category.objects.filter(status = 1).all()
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            product = Products.objects.filter(id=id).first()
    
    context = {
        'product' : product,
        'categories' : categories
    }
    return render(request, 'posApp/manage_product.html',context)
def test(request):
    categories = Category.objects.all()
    context = {
        'categories' : categories
    }
    return render(request, 'posApp/test.html',context)

""" 
@login_required
def save_product(request):
    data =  request.POST
    resp = {'status':'failed'}
    id= ''
    if 'id' in data:
        id = data['id']
    if id.isnumeric() and int(id) > 0:
        check = Products.objects.exclude(id=id).filter(code=data['code']).all()
    else:
        check = Products.objects.filter(code=data['code']).all()
    if len(check) > 0 :
        resp['msg'] = "Product Code Already Exists in the database"
    else:
        category = Category.objects.filter(id = data['category_id']).first()
        try:
            if (data['id']).isnumeric() and int(data['id']) > 0 :
                save_product = Products.objects.filter(id = data['id']).update(code=data['code'], category_id=category, name=data['name'], description = data['description'], price = float(data['price']),image = data['image'],status = data['status'])
            else:
                save_product = Products(code=data['code'], category_id=category, name=data['name'], description = data['description'], price = float(data['price']),image = data['image'],status = data['status'])
                save_product.save()
            resp['status'] = 'success'
            messages.success(request, 'Product Successfully saved.')
        except:
            resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")
 """
""" 

@login_required
def save_product(request):
    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        resp = {'status': 'failed'}
        id = data.get('id', '')

        # Check for existing code
        if id.isnumeric() and int(id) > 0:
            check = Products.objects.exclude(id=id).filter(code=data['code']).all()
        else:
            check = Products.objects.filter(code=data['code']).all()

        if len(check) > 0:
            resp['msg'] = "Product Code Already Exists in the database"
        else:
            category = Category.objects.filter(id=data['category_id']).first()

            try:
                image = files.get('image', None)

                if id.isnumeric() and int(id) > 0:
                    product = Products.objects.get(id=id)
                    product.code = data['code']
                    product.category_id = category
                    product.name = data['name']
                    product.description = data['description']
                    product.price = float(data['price'])
                    product.status = data['status']

                    if image:
                        product.image = image  

                    product.save()

                    # Upload to S3 if image is provided
                    import boto3
                    from botocore.exceptions import NoCredentialsError, PartialCredentialsError

                    bucket_name = "x23344440-s3"
                    if object_name is None:
                        object_name = product.name

                    s3_client = boto3.client('s3', region_name="us-east-1")
                    
                    try:
                        s3_client.upload_fileobj(image, bucket_name, object_name)
                        return True
                    except (NoCredentialsError, PartialCredentialsError) as e:
                        print(f"Credentials error: {e}")
                        return False
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        return False
                    
                else:
                    product = Products(
                        code=data['code'],
                        category_id=category,
                        name=data['name'],
                        description=data['description'],
                        price=float(data['price']),
                        status=data['status']
                    )
                    if image:
                        product.image = image
                    product.save()

                resp['status'] = 'success'
                messages.success(request, 'Product successfully saved.')
            except Exception as e:
                resp['status'] = 'failed'
                resp['msg'] = f"An error occurred: {str(e)}"

        return HttpResponse(json.dumps(resp), content_type="application/json")
 """




@login_required
def save_product(request):
    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        resp = {'status': 'failed'}
        id = data.get('id', '')

        # Check for existing code
        if id.isnumeric() and int(id) > 0:
            check = Products.objects.exclude(id=id).filter(code=data['code']).all()
        else:
            check = Products.objects.filter(code=data['code']).all()

        if check.exists():
            resp['msg'] = "Product Code Already Exists in the database"
        else:
            category = Category.objects.filter(id=data['category_id']).first()

            try:
                image = files.get('image', None)

                if id.isnumeric() and int(id) > 0:
                    product = Products.objects.get(id=id)
                else:
                    product = Products()

                # Update fields
                product.code = data['code']
                product.category_id = category
                product.name = data['name']
                product.description = data['description']
                product.price = float(data['price'])
                product.status = data['status']

                if image:
                    product.image = image  # Save to local media folder
                product.save()

                # Upload image to S3
                if image:
                    
                    import boto3
                    from botocore.exceptions import NoCredentialsError, PartialCredentialsError

                    bucket_name = "cpp-s3-x23335912"
                    object_name = f"products/{image.name}"  

                    s3_client = boto3.client('s3', region_name="us-east-1")

                    try:
                        image.seek(0)
                        s3_client.upload_fileobj(image, bucket_name, object_name)
                    except (NoCredentialsError, PartialCredentialsError) as e:
                        print(f"[S3 Credential Error] {e}")
                    except Exception as e:
                        print(f"[S3 Upload Error] {e}")


                resp['status'] = 'success'
                messages.success(request, 'Product successfully saved.')

            except Exception as e:
                resp['status'] = 'failed'
                resp['msg'] = f"An error occurred: {str(e)}"

        return HttpResponse(json.dumps(resp), content_type="application/json")






@login_required
def delete_product(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Products.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Product Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")
@login_required
def pos(request):
    products = Products.objects.filter(status = 1)
    product_json = []
    for product in products:
        product_json.append({'id':product.id, 'name':product.name, 'price':float(product.price)})
    context = {
        'page_title' : "Point of Sale",
        'products' : products,
        'product_json' : json.dumps(product_json)
    }
    # return HttpResponse('')
    return render(request, 'posApp/pos.html',context)

@login_required
def checkout_modal(request):
    grand_total = 0
    if 'grand_total' in request.GET:
        grand_total = request.GET['grand_total']
    context = {
        'grand_total' : grand_total,
    }
    return render(request, 'posApp/checkout.html',context)



@login_required
def save_pos(request):
    resp = {'status':'failed','msg':''}
    data = request.POST
    pref = datetime.now().year + datetime.now().year
    i = 1
    while True:
        code = '{:0>5}'.format(i)
        i += int(1)
        check = Sales.objects.filter(code = str(pref) + str(code)).all()
        if len(check) <= 0:
            break
    code = str(pref) + str(code)

    try:
        sales = Sales(code=code, sub_total = data['sub_total'], tax = data['tax'], tax_amount = data['tax_amount'], grand_total = data['grand_total'], tendered_amount = data['tendered_amount'], amount_change = data['amount_change']).save()
        sale_id = Sales.objects.last().pk
        i = 0
        for prod in data.getlist('product_id[]'):
            product_id = prod 
            sale = Sales.objects.filter(id=sale_id).first()
            product = Products.objects.filter(id=product_id).first()
            qty = data.getlist('qty[]')[i] 
            price = data.getlist('price[]')[i] 
            total = float(qty) * float(price)
            print({'sale_id' : sale, 'product_id' : product, 'qty' : qty, 'price' : price, 'total' : total})
            salesItems(sale_id = sale, product_id = product, qty = qty, price = price, total = total).save()
            i += int(1)
        resp['status'] = 'success'
        resp['sale_id'] = sale_id
        messages.success(request, "Sale Record has been saved.")
        lambda_result = call_lambda_via_api('New Sale Record Created',f"sale id: {sale_id}, code: {code}, grand total: {data['grand_total']}")
        print("Lambda response:", lambda_result)

    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp),content_type="application/json")




@login_required
def salesList(request):
    sales = Sales.objects.all()
    sale_data = []
    for sale in sales:
        data = {}
        for field in sale._meta.get_fields(include_parents=False):
            if field.related_model is None:
                data[field.name] = getattr(sale,field.name)
        data['items'] = salesItems.objects.filter(sale_id = sale).all()
        data['item_count'] = len(data['items'])
        if 'tax_amount' in data:
            data['tax_amount'] = format(float(data['tax_amount']),'.2f')
        # print(data)
        sale_data.append(data)
    # print(sale_data)
    context = {
        'page_title':'Sales Transactions',
        'sale_data':sale_data,
    }
    # return HttpResponse('')
    return render(request, 'posApp/sales.html',context)


import requests


def call_lambda_via_api(subject, message):
    api_url = "https://0lyjvc22p2.execute-api.us-east-1.amazonaws.com/default/my-lambda-cpp-x23335912"
    headers = {'Content-Type': 'application/json'}

    payload = {
        "subject": subject,
        "message": message
    }

    try:
        res = requests.post(api_url, json=payload, headers=headers)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print("Error calling Lambda:", e)
        return {"error": str(e)}



""" 
@login_required
def receipt(request):
    id = request.GET.get('id')
    sales = Sales.objects.filter(id = id).first()
    transaction = {}
    for field in Sales._meta.get_fields():
        if field.related_model is None:
            transaction[field.name] = getattr(sales,field.name)
    if 'tax_amount' in transaction:
        transaction['tax_amount'] = format(float(transaction['tax_amount']))
    ItemList = salesItems.objects.filter(sale_id = sales).all()
    context = {
        "transaction" : transaction,
        "salesItems" : ItemList
    }
    return render(request, 'posApp/receipt.html',context)
    # return HttpResponse('') """



from invoice_details_lib import get_transaction_date, get_transaction_code, get_current_date



@login_required
def receipt(request):
    id = request.GET.get('id')
    sales = Sales.objects.filter(id=id).first()
    transaction = {}

    for field in Sales._meta.get_fields():
        if field.related_model is None:
            value = getattr(sales, field.name)

            # Format date
            if field.name == 'date_added':
                transaction['date_added'] = get_transaction_code(datetime.now())
            else:
                transaction[field.name] = value

    if 'tax_amount' in transaction:
        transaction['tax_amount'] = format(float(transaction['tax_amount']), ".2f")

    transaction['transaction_code'] = get_transaction_code()

    ItemList = salesItems.objects.filter(sale_id=sales).all()
    context = {
        "transaction": transaction,
        "salesItems": ItemList
    }
    return render(request, 'posApp/receipt.html', context)



@login_required
def delete_sale(request):
    resp = {'status':'failed', 'msg':''}
    id = request.POST.get('id')
    try:
        delete = Sales.objects.filter(id = id).delete()
        resp['status'] = 'success'
        messages.success(request, 'Sale Record has been deleted.')
    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp), content_type='application/json')