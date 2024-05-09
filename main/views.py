from django.shortcuts import render,redirect
from .forms import CreateUserForm, LoginForm, AccountInfoForm, TransactionFilterForm
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate,login
from .models import CustomUser,AccountInfo, Transaction
import random, string
from datetime import timedelta
from django.contrib.auth.decorators import login_required

def homepage(request):
    return render(request,'main/home.html')

def register(request):

    form=CreateUserForm()
    if request.method=="POST":
        form=CreateUserForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.save()
            return redirect('my-login')
        else:
            return render(request,'main/register.html',{'registerform':form})
    

    return render(request,'main/register.html',{'registerform':form})

def mylogin(request):

    if request.method == "POST":
        form=LoginForm(request,data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                user_info = CustomUser.objects.get(username=username)
                if not AccountInfo.objects.filter(username=user_info).exists():
                    account_number = gen_acc_num()
                    acc_info = AccountInfo.objects.create(account_number=account_number, username=user_info)
                    return redirect('accinfo')  
                else:
                    acc_info = AccountInfo.objects.get(username=user_info)
                    if not (acc_info.account_holder_name and acc_info.gender and acc_info.pan_number and acc_info.aadhar_number):
                        return redirect('accinfo')
                    else:
                        return redirect('dashboard')
            else:
                form.add_error(None,"Invalid Credentials.")
    else:
        form=LoginForm()
        
    return render(request, 'main/login.html', {'loginform': form})


@login_required(login_url="my-login")
def accinfo(request):
    
    user_info = CustomUser.objects.get(pk=request.user.pk)
    acc_info = AccountInfo.objects.get(username=user_info.username)
    account_number = acc_info.account_number
    email = user_info.email

    if request.method == 'POST':
        account_form = AccountInfoForm(request.POST,instance=acc_info)
        if account_form.is_valid():
            account_info = account_form.save(commit=False)
            account_info.account_number = account_number
            account_info.username=user_info
            account_info.save()
            messages.success(request, "Account information saved successfully.")
            return redirect('dashboard')
    else:
        initial_data = {
            'account_holder_name': acc_info.account_holder_name,
            'pan_number': acc_info.pan_number,
            'aadhar_number': acc_info.aadhar_number,
            'gender': acc_info.gender,
        }
        account_form = AccountInfoForm(instance=acc_info, initial=initial_data)

    
    return render(request, 'main/accinfo.html', {'account_form': account_form, 'account_number': account_number, 'email': email})




@login_required(login_url="my-login")
def dashboard(request):
    user=request.user
    acc_info = AccountInfo.objects.get(username=user.username)
    amount=acc_info.amount


    context={
        'username':user.username,
        'account_number':acc_info.account_number,
        'amount':amount,
    }
    return render(request,'main/dashboard.html',context=context)

@login_required(login_url="my-login")
def cw(request):
    withdrawal_message=None
    acc_info = AccountInfo.objects.get(username=request.user.username)
    if request.method=='POST':
        amount=request.POST.get('amount')
        if acc_info.amount>=int(amount):
            acc_info.amount-=int(amount)
            acc_info.save()
            Transaction.objects.create(account_number=acc_info,transaction_type='Dr.',amount=-float(amount),balance=acc_info.amount,description="CASH WITHDRAWAL")
            withdrawal_message = f'Cash {amount} Rs withdrawn successfully.'
        else:
            error_message = 'Insufficient balance. Please enter a lower amount.'
            return render(request, 'main/cw.html', {'error_message': error_message})

    return render(request,'main/cw.html',{'withdrawal_message':withdrawal_message})


@login_required(login_url="my-login")
def cd(request):
    deposit_message=None
    acc_info = AccountInfo.objects.get(username=request.user.username)
    if request.method=='POST':
        amount=request.POST.get('amount')
        acc_info.amount+=int(amount)
        acc_info.save()
        Transaction.objects.create(account_number=acc_info,amount=float(amount),transaction_type="Cr.",balance=acc_info.amount,description="CASH DEPOSIT")
        deposit_message = f'Cash {amount} Rs deposited successfully.'
    return render(request,'main/cd.html',{'deposit_message':deposit_message})


@login_required(login_url="my-login")
def th(request):
    form = TransactionFilterForm(request.GET)    
    acc_info = AccountInfo.objects.get(username=request.user.username)
    transactions = Transaction.objects.filter(account_number=acc_info).order_by('-timestamp')
    account_number = acc_info.account_number
    amount = acc_info.amount

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        if start_date:
            transactions = transactions.filter(timestamp__gte=start_date)
        if end_date:
            adjusted_end_date = end_date + timedelta(days=1)
            transactions = transactions.filter(timestamp__lt=adjusted_end_date)
    return render(request, 'main/th.html', {'form':form,'transactions':transactions,'account_number': account_number, 'amount': amount})

def mylogout(request):
    auth.logout(request)

    return redirect("")

def gen_acc_num():
    return int(''.join(random.choices(string.digits,k=10)))


