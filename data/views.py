from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect

from .helper import *


def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'login.html')


def home(request):
    if request.user.is_authenticated:
            for email, name in email_name_list_from_cache():
                if email == request.user.email:
                    return render(request, 'home.html', {'name': name})

            return redirect('logout')

    return render(request, 'home.html', )


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required(login_url='login')
@csrf_protect
def create_user(request):

    if user_email_list_from_cache() is None:
        return render(request, 'profile.html')

    if request.user.email in user_email_list_from_cache():
        return redirect('home')

    if request.method not in ['POST', 'GET']:
        err_msg = {
            'error_msg': 'You are not allowed to perform this action',
            'landing_url': 'home',
            'landing_msg': 'Go Home'
        }
        return render(request, 'error_notification.html', err_msg)

    if request.method == 'POST':
        if not validate_and_create_user(request, request.POST):
            err_msg = {
                'error_msg': 'Some values entered are wrong, Please try again',
                'landing_url': 'profile',
                'landing_msg': 'Retry'
            }
            return render(request, 'error_notification.html', err_msg)

        return redirect('home')

    return render(request, 'profile.html')


@login_required(login_url='login')
def make_payment(request):
    try:
        User.objects.get(email=request.user.email)
    except Exception as e:
        return redirect('profile')
    result = validate_and_pay(request)

    if result['error']:
        return render(request, 'error_notification.html', result['error_data'])

    return render(request, result['render_page'], result['render_data'])


@login_required(login_url='login')
def payment_success(request):
    try:
        return render(request, validate_payment_and_send_confirmation(request))
    except Exception as e:
        err_msg = {
            'error_msg': 'Something went wrong while processing payment, Please try again',
            'landing_url': 'home',
            'landing_msg': 'Go Home'
        }
        return render(request, 'error_notification.html', err_msg)


@login_required(login_url='login')
def register(request):
    try:
        is_valid = valid_to_register(request)
        if is_valid is not None:
            return render(request, 'error_notification.html', is_valid)

        if request.method == 'GET':
            return render(request, 'registration.html', {'teams': get_team_names()})

        action = request.POST.get('action')

        err_msg = create_team(request) if action == 'create' else join_team(request)
        if err_msg is not None:
            return render(request, 'error_notification.html', err_msg)

        return render(request, 'registration_success.html')
    except Exception as e:
        err_msg = {
            'error_msg': 'Something went wrong while registering. Please try after sometime',
            'landing_url': 'home',
            'landing_msg': 'Go Home'
        }
        return render(request, 'error_notification.html', err_msg)
    

@login_required(login_url='login')
def qr_check(request,user_check_id):
    check_admin_user = User.objects.get(email=request.user.email)
    if(check_admin_user.admin_user):
        template_location, context = validate_qr(user_check_id)
        return render(request,template_location, context)
    else:
        err_msg = {
            'error_msg': 'You are not allowed to perform this action',
            'landing_url': 'home',
            'landing_msg': 'Go Home'
        }
        return render(request, 'error_notification.html', err_msg)
        

@login_required(login_url='login')
def registered_list(request):
    check_admin_user = User.objects.get(email=request.user.email)
    if(check_admin_user.admin_user):
        paid_users = User.objects.filter(payment__is_paid=True)
        return render(request,"registered_list.html",{"paid_users":paid_users})
    else:
        err_msg = {
            'error_msg': 'You are not allowed to perform this action',
            'landing_url': 'home',
            'landing_msg': 'Go Home'
        }
        return render(request, 'error_notification.html', err_msg)
