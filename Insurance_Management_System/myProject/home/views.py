from home import *;
from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from .models import User
from django.contrib.auth import authenticate, login,logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from patient.models import Patient
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import User
from django.contrib.auth import authenticate, login,logout
from django.utils.encoding import DjangoUnicodeDecodeError
from . import forms,models
from . import models as CMODEL
from . import forms as CFORM
from django.views.generic import View
from .utils import *
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension
#for activating user account
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from .models import Customer, Policy, PolicyRecord, Category, Question
#email
from django.conf import settings
from django.core.mail import EmailMessage
#threading
import threading
#reset passwor generater
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from .models import Customer
class EmailThread(threading.Thread):
       def __init__(self, email_message):
              super().__init__()
              self.email_message=email_message
       def run(self):
              self.email_message.send()
# Create your views here.

@never_cache

def index(request):
    return render(request, 'index.html')
    #return HttpResponse("Hello World..!")
User = get_user_model()

def Sign_up(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.warning(request, "Password is not matching")
            return render(request, 'signup.html')

        try:
            # Check if the email is already taken
            if User.objects.get(username=email):
                messages.warning(request, "Email is already taken")
                return render(request, 'signup.html')
        except User.DoesNotExist:
            pass

        # Create a user with email and password
        user = User.objects.create_user(email=email, password=password, username=email, role='CUSTOMER')
        user.is_active = False
        user.save()

        # Create a Customer instance with additional details
        customer = Customer.objects.create(
            user=user,
            first_name=request.POST['fname'],
            last_name=request.POST['lname'],
            phone=request.POST['phone'],
            address=request.POST['address'],
            # Add other fields as needed
        )
        
        # Handle image field separately if it's included in the form
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            try:
                # Validate the image file extension
                validate_image_file_extension(profile_picture)
            except ValidationError as e:
                messages.warning(request, f"Invalid image file: {e}")
                return render(request, 'signup.html')

            customer.image = profile_picture

        # # Handle image field separately if it's included in the form
        # if 'image' in request.FILES:
        #     customer.image = request.FILES['image']

        customer.save()

        # Send activation email
        current_site = get_current_site(request)
        email_subject = "Activate your account"
        message = render_to_string('activate.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        })

        email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
        email_message.send()

        messages.info(request, "Activate your account by clicking the link sent to your email")
        return redirect('/handlelogin')

    return render(request, 'signup.html')

class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account activated sucessfully")
            return redirect('/handlelogin')
        user.is_active=True
        user.save()
        return redirect('/handlelogin')
        #return render(request,"activatefail.html")

def handlelogin(request):
    if request.method == "POST":
        username = request.POST['email']
        password = request.POST['password']
        myuser = authenticate(request, username=username, password=password)

        if myuser is not None:
            login(request, myuser)
            request.session['username'] = username

            if myuser.role == 'CUSTOMER':
                #return redirect('customer_dashboard_view')
                return redirect('customer_dashboard')
            elif myuser.role == 'SELLER':
                return HttpResponse("seller login")
            elif myuser.role == 'ADMIN':
                return redirect('/admin_dashboard/')  # Redirect to the admin dashboard page
            elif myuser.role == 'HOSPITAL':
                return redirect('/hospital_dashboard/')

        else:
            messages.error(request, "Enter valid credentials")
            return redirect('/handlelogin')
    
    response = render(request, 'login.html')
    response['Cache-Control'] = 'no-store, must-revalidate'
    return response

@never_cache
@login_required(login_url='/handlelogin/')
def customer_home(request):
       if 'username' in request.session:
        response = render(request,'customer_page.html')
        response['Cache-Control'] = 'no-store,must-revalidate'
        return response
       else:
             return redirect('handlelogin')

def handlelogout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('/')

@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict={
        'total_user':CMODEL.Customer.objects.all().count(),
        'total_policy':models.Policy.objects.all().count(),
        'total_category':models.Category.objects.all().count(),
        'total_question':models.Question.objects.all().count(),
        'total_policy_holder':models.PolicyRecord.objects.all().count(),
        'approved_policy_holder':models.PolicyRecord.objects.all().filter(status='Approved').count(),
        'disapproved_policy_holder':models.PolicyRecord.objects.all().filter(status='Disapproved').count(),
        'waiting_policy_holder':models.PolicyRecord.objects.all().filter(status='Pending').count(),
    }
    return render(request,'dashboard.html',context=dict)

#################################################################################################
#################################################################################################
#################################################################################################

#@login_required(login_url='adminlogin')
def admin_view_customer_view(request):
    # Fetch data from the User and Customer models
    all_customers = Customer.objects.all()
    #all_users = User.objects.all()


    return render(request, 'admin/admin_view_customer.html', {'all_customers': all_customers})

@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=CMODEL.Customer.objects.get(id=pk)
    user=CMODEL.User.objects.get(id=customer.user_id)
    userForm=CFORM.CustomerUserForm(instance=user)
    customerForm=CFORM.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=CFORM.CustomerUserForm(request.POST,instance=user)
        customerForm=CFORM.CustomerForm(request.POST,request.FILES,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('admin-view-customer')
    return render(request,'admin/update_customer.html',context=mydict)



@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=CMODEL.Customer.objects.get(id=pk)
    user=User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return HttpResponseRedirect('/admin-view-customer')



def admin_category_view(request):
    return render(request,'admin/admin_category.html')

def admin_add_category_view(request):
    categoryForm=forms.CategoryForm() 
    if request.method=='POST':
        categoryForm=forms.CategoryForm(request.POST)
        if categoryForm.is_valid():
            categoryForm.save()
            return redirect('admin-view-category')
    return render(request,'admin/admin_add_category.html',{'categoryForm':categoryForm})

def admin_view_category_view(request):
    categories = models.Category.objects.all()
    return render(request,'admin/admin_view_category.html',{'categories':categories})

def admin_delete_category_view(request):
    categories = models.Category.objects.all()
    return render(request,'admin/admin_delete_category.html',{'categories':categories})
    
def delete_category_view(request,pk):
    category = models.Category.objects.get(id=pk)
    category.delete()
    return redirect('admin-delete-category')

def admin_update_category_view(request):
    categories = models.Category.objects.all()
    return render(request,'admin/admin_update_category.html',{'categories':categories})

@login_required(login_url='adminlogin')
def update_category_view(request,pk):
    category = models.Category.objects.get(id=pk)
    categoryForm=forms.CategoryForm(instance=category)
    
    if request.method=='POST':
        categoryForm=forms.CategoryForm(request.POST,instance=category)
        
        if categoryForm.is_valid():

            categoryForm.save()
            return redirect('admin-update-category')
    return render(request,'admin/update_category.html',{'categoryForm':categoryForm})
  
def admin_policy_view(request):
    return render(request,'admin/admin_policy.html')


def admin_add_policy_view(request):
    policyForm=forms.PolicyForm() 
    
    if request.method=='POST':
        policyForm=forms.PolicyForm(request.POST)
        if policyForm.is_valid():
            categoryid = request.POST.get('category')
            category = models.Category.objects.get(id=categoryid)
            
            policy = policyForm.save(commit=False)
            policy.category=category
            policy.save()
            return redirect('admin-view-policy')
    return render(request,'admin/admin_add_policy.html',{'policyForm':policyForm})

def admin_view_policy_view(request):
    policies = models.Policy.objects.all()
    return render(request,'admin/admin_view_policy.html',{'policies':policies})

def admin_update_policy_view(request):
    policies = models.Policy.objects.all()
    return render(request,'admin/admin_update_policy.html',{'policies':policies})

@login_required(login_url='adminlogin')
def update_policy_view(request,pk):
    policy = models.Policy.objects.get(id=pk)
    policyForm=forms.PolicyForm(instance=policy)
    
    if request.method=='POST':
        policyForm=forms.PolicyForm(request.POST,instance=policy)
        
        if policyForm.is_valid():

            categoryid = request.POST.get('category')
            category = models.Category.objects.get(id=categoryid)
            
            policy = policyForm.save(commit=False)
            policy.category=category
            policy.save()
           
            return redirect('admin-update-policy')
    return render(request,'admin/update_policy.html',{'policyForm':policyForm})
  
  
def admin_delete_policy_view(request):
    policies = models.Policy.objects.all()
    return render(request,'admin/admin_delete_policy.html',{'policies':policies})
    
def delete_policy_view(request,pk):
    policy = models.Policy.objects.get(id=pk)
    policy.delete()
    return redirect('admin-delete-policy')

def admin_view_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all()
    return render(request,'admin/admin_view_policy_holder.html',{'policyrecords':policyrecords})

def admin_view_approved_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Approved')
    return render(request,'admin/admin_view_approved_policy_holder.html',{'policyrecords':policyrecords})

def admin_view_disapproved_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Disapproved')
    return render(request,'admin/admin_view_disapproved_policy_holder.html',{'policyrecords':policyrecords})

def admin_view_waiting_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Pending')
    return render(request,'admin/admin_view_waiting_policy_holder.html',{'policyrecords':policyrecords})

def approve_request_view(request,pk):
    policyrecords = models.PolicyRecord.objects.get(id=pk)
    policyrecords.status='Approved'
    policyrecords.save()
    return redirect('admin-view-policy-holder')

def disapprove_request_view(request,pk):
    policyrecords = models.PolicyRecord.objects.get(id=pk)
    policyrecords.status='Disapproved'
    policyrecords.save()
    return redirect('admin-view-policy-holder')


def admin_question_view(request):
    questions = models.Question.objects.all()
    return render(request,'admin/admin_question.html',{'questions':questions})

def update_question_view(request,pk):
    question = models.Question.objects.get(id=pk)
    questionForm=forms.QuestionForm(instance=question)
    
    if request.method=='POST':
        questionForm=forms.QuestionForm(request.POST,instance=question)
        
        if questionForm.is_valid():

            admin_comment = request.POST.get('admin_comment')
            
            
            question = questionForm.save(commit=False)
            question.admin_comment=admin_comment
            question.save()
           
            return redirect('admin-question')
    return render(request,'admin/update_question.html',{'questionForm':questionForm})

##################################################################################################
##################################################################################################
##################################################################################################


@never_cache
@login_required(login_url='/handlelogin/')
def hospital_dashboard(request):
      patients=Patient.objects.all()

      return render(request,"hospital/hospital_dashboard.html",{'patients': patients})


def customer_dashboard(request):
    customer = get_object_or_404(Customer, user=request.user)

    available_policy_count = Policy.objects.all().count()
    applied_policy_count = PolicyRecord.objects.filter(customer=customer).count()
    total_category_count = Category.objects.all().count()
    total_question_count = Question.objects.filter(customer=customer).count()

    context = {
        'customer': customer,
        'available_policy': available_policy_count,
        'applied_policy': applied_policy_count,
        'total_category': total_category_count,
        'total_question': total_question_count,
    }

    return render(request, 'customer/customer_dashboard.html', context)

# def apply_policy_view(request):
#     customer = get_object_or_404(models.Customer,user_id=request.user.id)
#     policies = CMODEL.Policy.objects.all()
#     return render(request,'customer/apply_policy.html',{'policies':policies,'customer':customer})

from django.shortcuts import render, get_object_or_404
import razorpay
from . import models as CMODEL  # Assuming your models are in models.py within the same app

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def apply_policy_view(request):
    customer = get_object_or_404(CMODEL.Customer, user_id=request.user.id)
    policies = CMODEL.Policy.objects.all()

    # Fixed amount for Razorpay payment, for demonstration
    currency = 'INR'
    amount = 2000  # Rs. 200

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))

    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler/'  # Ensure this URL is configured to handle the payment status

    # Context for rendering in the template
    context = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,
        'currency': currency,
        'callback_url': callback_url,
        'policies': policies,
        'customer': customer
    }

    # Use the 'apply_policy.html' template or another template that includes the Razorpay JavaScript code
    return render(request, 'customer/apply_policy.html', context=context)


def apply_view(request,pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policy = CMODEL.Policy.objects.get(id=pk)
    policyrecord = CMODEL.PolicyRecord()
    policyrecord.Policy = policy
    policyrecord.customer = customer
    policyrecord.save()
    return redirect('history')

def history_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.PolicyRecord.objects.all().filter(customer=customer)
    return render(request,'customer/history.html',{'policies':policies,'customer':customer})

def ask_question_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    questionForm=CFORM.QuestionForm() 
    
    if request.method=='POST':
        questionForm=CFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            
            question = questionForm.save(commit=False)
            question.customer=customer
            question.save()
            return redirect('question-history')
    return render(request,'customer/ask_question.html',{'questionForm':questionForm,'customer':customer})

def question_history_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    questions = CMODEL.Question.objects.all().filter(customer=customer)
    return render(request,'customer/question_history.html',{'questions':questions,'customer':customer})



"""def employee_signup(request):
    if request.method == 'POST':
        # Handle User registration (username and password)
        email = request.POST['email']
        password = request.POST['password']

        # Set the username to the user's email
        username = email

        # Create a User instance
        user = User.objects.create_user(username=username, email=email, password=password)

        # Handle EmployeeRegistration
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        address = request.POST['address']
        resume_upload = request.FILES['resume_upload']

        # Create an EmployeeRegistration instance
        employee_registration = EmployeeRegistration(
            user=user,  # Link the User to the EmployeeRegistration
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            resume_upload=resume_upload
        )
        employee_registration.save()

        # Redirect to a success page or do other necessary actions
        return redirect('index')  # Change 'success_page' to the URL for the success page

    # Handle form errors and render the registration form
    return render(request, 'employee_signup.html')"""

   

# def Sign_up(request):
#     if request.method=="POST":
#             fname=request.POST['fname']
#             lname=request.POST['lname']
#             email=request.POST['email']
#             #phone=request.POST['phone']
#             username=email
            
#             password=request.POST['password']
#             confirm_password=request.POST['confirm_password']


            
#             if password!=confirm_password:
#                     messages.warning(request,"password is not matching")
#                     return render(request,'signup.html')
#             try:
#                       if User.objects.get(username=email):
#                              messages.warning(request,"Email is already taken")
#                              return render(request,'signup.html')
#             except Exception as identifiers:
#                       pass

#             user=User.objects.create_user(first_name=fname,last_name=lname,email=email,password=password,username=username,role='CUSTOMER')
#             user.is_active=False 
#             user.save()
#             current_site=get_current_site(request)  
#             email_subject="Activate your account"
#             message=render_to_string('activate.html',{
#                    'user':user,
#                    'domain':current_site.domain,
#                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
#                    'token':generate_token.make_token(user)


#             })

#             email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email],)
#             EmailThread(email_message).start()
#             messages.info(request,"Active your account by clicking the link send to your email")



           
#             return redirect('/handlelogin')
           
             
           
#     return render(request,'signup.html')


# def customer_dashboard(request):
#     # dict={
#     #     'customer':get_object_or_404(models.Customer,user_id=request.user.id),
#     #     'available_policy':CMODEL.Policy.objects.all().count(),
#     #     'applied_policy':CMODEL.PolicyRecord.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),
#     #     'total_category':CMODEL.Category.objects.all().count(),
#     #     'total_question':CMODEL.Question.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),

#     # }
#     return render(request,'customer/customer_dashboard.html')



from .models import Office

def office_registration(request):
    if request.method == "POST":
        # Process form data
        officeid = request.POST.get('officeid')
        address = request.POST.get('address')
        place = request.POST.get('place')
        location = request.POST.get('location')
        pin = request.POST.get('pin')
        phone = request.POST.get('phone')
        district = request.POST.get('district')
        state = request.POST.get('state')
        regdate = request.POST.get('regdate')
        
        # Create and save new Office instance
        Office.objects.create(
            officeid=officeid, address=address, place=place, location=location,
            pin=pin, phone=phone, district=district, state=state, regdate=regdate
        )

        user = User.objects.create_user(email=email, password=password, username=email, role='CUSTOMER')
        user.is_active = False
        user.save()
        return render(request, 'officereg.html')
          # Redirect or show a success message
    else:
        # GET request, show empty form
        return render(request, 'officereg.html')