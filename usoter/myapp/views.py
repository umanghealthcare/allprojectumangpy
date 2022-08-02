from django.shortcuts import render ,redirect 
from django.utils.datastructures import MultiValueDictKeyError
from .models import User,Product,Wishlist,Cart,Transaction
from django.conf import settings
from django.core.mail import send_mail
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt

import random
# Create your views here.
def seller_index(request):
	products=Product.objects.all()
	return render(request,'seller_index.html',{'products':products})
def seller_header(request):
	return render(request,'seller_header.html')
def index(request):
	products=Product.objects.all()
	return render(request,"index.html",{'products':products})
def header(request):
	return render(request,"header.html")
def shop(request):
	product=Product.objects.all()
	return render(request,'shop.html',{'product':product})
def single_product(request,pk):
	wishlist_flag=False
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	try:
		Wishlist.objects.get(user=user,product=product)
		wishlist_flag=True
	except:
		pass
	return render(request,'single_product.html',{'product':product,'wishlist_flag':wishlist_flag})
def checkout(request):
	return render(request,'checkout.html')
def signup(request):
	if request.method=='POST':
		try:
			User.objects.get(email=request.POST['email'])
			msg='email is already registered'
			return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
					usertype=request.POST['usertype'],
					fname=request.POST['fname'],
					lname=request.POST['lname'],
					email=request.POST['email'],
					moblie=request.POST['moblie'],
					password=request.POST['password'],
					address=request.POST['address'],
					profile_pic=request.FILES['profile_pic']
					)
				
				msg='signup successfuly'
				return render(request,'signup.html',{'msg':msg})
			else:
				msg='password and confirm password does not match'
				return render(request,'signup.html',{'msg':msg})
	else:
		return render(request,'signup.html')
def login(request):
	if request.method=='POST':
		try:
			user=User.objects.get(
				email=request.POST['email'],
				password=request.POST['password'])
			if user.usertype=='user':
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['profile_pic']=user.profile_pic.url
				wishlist=Wishlist.objects.filter(user=user)
				request.session['wishlist_count']=len(wishlist)
				cats=Cart.objects.filter(user=user, status='pending')
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
				return render(request,'seller_index.html')
		except:
			msg="Email or Password Is Incorrect"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')
def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		return redirect('login')
	except:
		return redirect('login')
def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=='POST':
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.email=request.POST['email']
		user.address=request.POST['address']
		user.moblie=request.POST['moblie']
		try:
			user.profile_pic=request.FILES['profile_pic']
		except:
			pass
		user.save()
		request.session['profile_pic']=user.profile_pic.url
		msg='profile update successfuly'
		return render(request,'profile.html',{'msg':msg,'user':user})
	else:
		return render(request,'profile.html',{'user':user})
def change_password(request):
	if request.method=='POST':
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['opassword']:
			if request.POST['npassword']==request.POST['cpassword']:
				user.password=request.POST['npassword']
				user.save()
				return redirect('logout')
			else:
				msg='new password and confirm password does not match'
				return render(request,'change_password.html',{'msg':msg})
		else:
			msg='old password does not match'
			return render(request,'change_password.html',{'msg':msg})
	else:
		return render(request,'change_password.html')
def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			print(user)
			subject = 'OTP For Forgot Password'
			otp=random.randint(1000,9999)
			message = 'Your OTP For Forgot Password Is '+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email,]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'otp.html',{'otp':otp,'email':user.email})
		except Exception as e:
			print(e)
			msg="Email Not Registered"
			return render(request,'forgot_password.html',{'msg':msg})
	else:
		return render(request,'forgot_password.html')

def verify_otp(request):
	uotp=request.POST['uotp']
	otp=request.POST['otp']
	email=request.POST['email']

	if uotp== otp:
		return render(request,'change.html',{'email':email})
	else:
		msg='otp does not match'
		return render(request,'verify_otp',{'email':email,'otp':otp,'msg':msg})

def change(request):
	email=request.POST['email']
	npassword=request.POST['npassword']
	cpassword=request.POST['cpassword']
	
	if npassword==cpassword:
		user=User.objects.get(email=request.session['email'])
		user.password=npassword
		user.save()
		return redirect('login')
	else:
		msg='new password and confirm password does not match'
		return render('request','change.html',{'msg':msg,'email':email})

def seller_add_product(request):
	if request.method=='POST':
		seller=User.objects.get(email=request.session['email'])
		Product.objects.create(
			seller=seller,
			product_company=request.POST['product_company'],
			product_model=request.POST['product_model'],
			product_price=request.POST['product_price'],
			product_desc=request.POST['product_desc'],
			product_image=request.FILES['product_image'],
			)
		msg='product add successfuly '
		return render(request,'seller_add_product.html',{'msg':msg  })
	else:
		return render(request,'seller_add_product.html ')

def seller_product_details(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller_single_product.html',{'product':product})

def seller_edit_product(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=='POST':
		product.product_company=request.POST['product_company']
		product.product_model=request.POST['product_model']
		product.product_price=request.POST['product_price']
		product.product_desc=request.POST['product_desc']
		try:
			product.product_image=request.FILES['product_image']
		except:
			pass
		product.save()
		msg='product update successfuly '
		return render(request,'seller_edit_product.html',{'msg':msg,'product':product})
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
		product=product,
		)
	wishlist=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlist)
	return redirect('wishlist')
def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	return render(request,'wishlist.html',{'wishlists':wishlists})

def remove_form_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	wishlist=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlist)
	return redirect('wishlist')

def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(
		user=user,
		product=product,
		product_price=product.product_price,
		total_price=product.product_price,
		)
	return redirect('cart')

def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user, status='pending')
	for i in carts:
		net_price=net_price+i.total_price 
	request.session['net_price']=net_price
	request.session['cart_count']=len(carts)
	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')

def change_qty(request,pk):
	cart=Cart.objects.get(pk=pk)
	product_qty=int(request.POST['product_qty'])
	cart.product_qty=product_qty
	cart.total_price=cart.product_price*product_qty
	cart.save()
	return redirect('cart')

def initiate_payment(request):
    try:
        amount = int(request.POST['amount'])
    except:
        return render(request, 'cart.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str('usahu3589@gmail.com')),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()
    carts=Cart.objects.filter(email=email)
    for i in carts:
    	i.status='paid'
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

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,status='paid')
	return render(request,'myorder.html',{'carts':carts})