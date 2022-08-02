from django.shortcuts import render,redirect
from .models import User,Product,Wishlist,Cart,Transaction
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse
# Create your views here.

def validate_signup(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__iexact=email).exists()
	}
	return JsonResponse(data)

def initiate_payment(request):
	user=User.objects.get(email=request.session['email'])
	try:
		amount = int(request.POST['amount'])
	except:
		return render(request, 'cart.html', context={'error': 'Wrong Accound Details or amount'})

	transaction = Transaction.objects.create(made_by=user,amount=amount)
	transaction.save()
	merchant_key = settings.PAYTM_SECRET_KEY

	params = (
		('MID', settings.PAYTM_MERCHANT_ID),
		('ORDER_ID', str(transaction.order_id)),
		('CUST_ID', str("karan.shah11395@gmail.com")),
		('TXN_AMOUNT', str(transaction.amount)),
		('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
		('WEBSITE', settings.PAYTM_WEBSITE),
    # ('EMAIL', request.user.email),
    # ('MOBILE_N0', '9911223388'),
    ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
    ('CALLBACK_URL', 'http://localhost:8000/callback/'),
    # ('PAYMENT_MODE_ONLY', 'NO'),
    )

	paytm_params = dict(params)
	checksum = generate_checksum(paytm_params, merchant_key)

	transaction.checksum = checksum
	transaction.save()
	carts=Cart.objects.filter(user=user)
	for i in carts:
		i.status="paid"
		i.save()
	paytm_params['CHECKSUMHASH'] = checksum
	print('SENT: ', checksum)
	return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)

def index(request):
	products=Product.objects.all()
	return render(request,'index.html',{'products':products})

def seller_index(request):
	products=Product.objects.all()
	return render(request,'seller_index.html',{'products':products})

def cart(request):
	return render(request,'cart.html')

def checkout(request):
	return render(request,'checkout.html')

def shop(request):
	products=Product.objects.all()
	return render(request,'shop.html',{'products':products})

def single_product(request,pk):
	# if request.method=='POST':		
	# try:
	wishlist_flag=False
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	try:
		Wishlist.objects.get(user=user,product=product)
		wishlist_flag=True
	except:
		pass
	return render(request,'single-product.html',{'product':product,'wishlist_flag':wishlist_flag})
	# except:
	# 	carts_flag=False
	# 	user=User.objects.get(email=request.session['email'])
	# 	carts=Cart.objects.get(pk=pk)
	# 	try:
	# 		Cart.objects.get(user=user)
	# 		carts_flag=True
	# 	except:
	# 		pass
	# 		return render(request,'single-product.html',{'carts_flag':carts_flag})

def signup(request):
	if request.method=="POST":
		try:
			User.objects.get(email=request.POST['email'])
			msg="Email Alredy Registered"
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
						usertype=request.POST['usertype'],
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						address=request.POST['address'],
						profile_pic=request.FILES['profile_pic'],
						password=request.POST['password']
					)
				msg="User Sign Up Successfully"
				return render(request,'signup.html',{'msg':msg})
			else:
				msg="Password & Confirm Password Does Not Matched"
				return render(request,'signup.html',{'msg':msg})
	else:
		return render(request,'signup.html')

def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(
				email=request.POST['email'],
				password=request.POST['password'])

			if user.usertype=="user":
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['profile_pic']=user.profile_pic.url
				wishlists=Wishlist.objects.filter(user=user)
				request.session['wishlist_count']=len(wishlists)
				carts=Cart.objects.filter(user=user,status="pending")
				net_price=0
				for i in carts:
					net_price=net_price+i.total_price
				request.session['net_price']=net_price
				request.session['cart_count']=len(carts)
				return render(request,'index.html')
			else:
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['profile_pic']=user.profile_pic.url
				# products=Product.objects.all()
				# return render(request,'seller_index.html',{'products':products})
				return redirect('seller_index')
		except:
			msg="Email or Password Is Incorrect"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['profile_pic']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				msg="New Password & Confirm New Password Does Not Matched"
				return render(request,'change_password.html',{'msg':msg})
		else:
			msg="Old Password Is Incorrect"
			return render(request,'change_password.html',{'msg':msg})
	else:
		return render(request,'change_password.html')

def seller_add_product(request):
	if request.method=="POST":
		seller=User.objects.get(email=request.session['email'])
		Product.objects.create(
				seller=seller,
				product_company=request.POST['product_company'],
				product_model=request.POST['product_model'],
				product_price=request.POST['product_price'],
				product_desc=request.POST['product_desc'],
				product_image=request.FILES['product_image'],
			)
		msg="Product Added Successfully"
		return render(request,'seller_add_product.html',{'msg':msg})
	else:
		return render(request,'seller_add_product.html')

def seller_product_detail(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller_single_product.html',{'product':product})

def seller_edit_product(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_company=request.POST['product_company']
		product.product_model=request.POST['product_model']
		product.product_price=request.POST['product_price']
		product.product_desc=request.POST['product_desc']
		try:
			product.product_image=request.FILES['product_image']
		except:
			pass
		product.save()
		msg="Product Edited Successfully"
		return render(request,'seller_edit_product.html',{'product':product,'msg':msg})
	else:
		return render(request,'seller_edit_product.html',{'product':product})

def seller_delete_product(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('seller_index')

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(
			user=user,
			product=product
		)
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return redirect('wishlist')

def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	return render(request,'wishlist.html',{'wishlists':wishlists})



def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(
			user=user,
			product=product,
			product_price=product.product_price,
			total_price=product.product_price
		)
	return redirect('cart')

def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,status="pending")
	for i in carts:
		net_price=net_price+i.total_price
	request.session['net_price']=net_price
	request.session['cart_count']=len(carts)
	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return redirect('wishlist')

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')

def change_qty(request,pk):
	print("change called")
	cart=Cart.objects.get(pk=pk)
	product_qty=int(request.POST['product_qty'])
	cart.product_qty=product_qty
	cart.total_price=cart.product_price*product_qty
	print(cart.total_price)
	cart.save()
	return redirect('cart')

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,status="paid")
	return render(request,'myorder.html',{'carts':carts})