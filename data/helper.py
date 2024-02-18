import qrcode
import yagmail
from instamojo_wrapper import Instamojo

from symposium.settings import env
from .models import User, Payment, UserEvents, TeamEvents
from django.core.cache import cache
from django.conf import settings
from .constants import *


def valid_to_register(request):
    user = User.objects.get(email=request.user.email)
    payment_detail = Payment.objects.get(user=user)
    try:
        user_event = UserEvents.objects.get(user=user)
    except UserEvents.DoesNotExist:
        user_event = None
    err_msg = {
        'landing_url': 'home',
        'landing_msg': 'Go Home',
        'error_msg': ALREADY_REGISTERED if payment_detail.is_paid else NOT_ALLOWED
    }

    return err_msg if not (user_event is None and payment_detail.is_paid) else None


def get_team_names():
    team_names = TeamEvents.objects.values_list('team_name', flat=True)
    return team_names


def create_team(request):
    team_name = request.POST.get('create_team_name')
    team_key = request.POST.get('create_team_key')

    if team_name == '' or team_key == '':
        err_msg = {
            'landing_url': 'registration',
            'landing_msg': 'Retry',
            'error_msg': 'Type Team Name and team password'
        }
        return err_msg
    
    if team_name in get_team_names():
        # return that team name already exists
        err_msg = {
            'landing_url': 'registration',
            'landing_msg': 'Retry',
            'error_msg': 'Team name already exists. Please try a different name'
        }
        return err_msg

    user = User.objects.get(email=request.user.email)

    team_events = TeamEvents.objects.create(
        event_name='PAPER_PRESENTATION',
        team_name=team_name,
        team_key=team_key
    )
    team_events.team.add(user)
    team_events.save()
    create_user_event(user)


def join_team(request):
    team_name = request.POST.get('join_team_name')
    team_key = request.POST.get('join_team_key')

    team_event = TeamEvents.objects.get(team_name=team_name)
    if team_key != team_event.team_key:
        # return team name or password is wrong
        err_msg = {
            'landing_url': 'registration',
            'landing_msg': 'Retry',
            'error_msg': 'The entered password is wrong. Please try again.'
        }
        return err_msg

    if team_event.team.count() >= 3:
        # return team limit reached
        err_msg = {
            'landing_url': 'registration',
            'landing_msg': 'Retry',
            'error_msg': 'Team limit exceeded'
        }
        return err_msg

    user = User.objects.get(email=request.user.email)
    team_event.team.add(user)
    team_event.save()
    create_user_event(user)


def create_user_event(user):
    UserEvents.objects.create(
        user=user,
        email=user.email,
        event_status='active'
    )


def validate_payment_and_send_confirmation(request):
    payment_request_id = request.GET.get('payment_request_id')
    payment_details = Payment.objects.get(order_id=payment_request_id)

    if payment_details.is_paid:
        return 'already_paid.html'

    update_payment(request, payment_details)
    send_payment_confirmation_email(request)
    return 'payment_success.html'


def update_payment(request, payment_details):
    payment_details.payment_id = request.GET.get('payment_id')
    payment_details.is_paid = True
    payment_details.save()


def send_payment_confirmation_email(request):
    user = User.objects.get(email=request.user.email)
    qr_file_path = 'qrs/user_' + str(user.uuid) + '.png'
    create_qr(user, qr_file_path)
    email_body = EMAIL_CONTENT
    yag = yagmail.SMTP(env("SMTP_FROM_EMAIL"), env("SMTP_EMAIL_PASSWORD"))
    yag.send(user.email, env("EMAIL_SUBJECT"), email_body, qr_file_path)
    yag.close()


def create_qr(user, qr_file):
    qr_payload = env("QR_LINK") + str(user.uuid)
    qrcode.QRCode(version=1, box_size=40, border=3)
    qr = qrcode.make(qr_payload)
    qr.save(qr_file)


def validate_and_pay(request):
    try:
        user = User.objects.get(email=request.user.email)
        payment_details, _ = Payment.objects.get_or_create(
            user=user,
            email=request.user.email,
        )

        if payment_details.is_paid:
            return {
                'error': False,
                'render_page': 'already_paid.html',
                'render_data': {}
            }


        payment_response = make_payment_request(user.name, user.email)
        payment_details.order_id = payment_response['payment_request']['id']
        payment_details.instamojo_response = payment_response
        payment_details.save()
        return {
            'error': False,
            'render_page': 'payment.html',
            'render_data': {'payment_url': payment_response['payment_request']['longurl']}
        }

    except Exception:
        return {
            'error': True,
            'error_data': {
                'error_msg': 'Something went wrong while processing payment. Please try again after sometime',
                'landing_url': 'home',
                'landing_msg': 'Go Home'
            }
        }


def make_payment_request(user_name, user_email):
    instamojo_request = Instamojo(
        api_key=settings.API_KEY,
        auth_token=settings.AUTH_TOKEN,
        endpoint=env("PAYMENT_API_ENDPOINT")
    )
    response = instamojo_request.payment_request_create(
        amount=env("PAYMENT_AMOUNT"),
        purpose=env("PAYMENT_MESSAGE"),
        buyer_name=user_name,
        email=user_email,
        redirect_url=env("PAYMENT_REDIRECT_URL"),
    )
    return response


def validate_and_create_user(request, user_params):
    return create_user_in_db(request, user_params) if validate_user(request, user_params) else False


def validate_user(request, user_params):
    return True


def create_user_in_db(request, user_params):
    try:
        User.objects.create(
            name=user_params.get('username'),
            email=request.user.email,
            phone=user_params.get('phone'),
            year=user_params.get('year'),
            department=user_params.get('department'),
            section=user_params.get('section'),
            reg=user_params.get('reg'),
            college=user_params.get('college'),
            admin_user=False,
            attendance=False
        )
        reset_cache()
        return True
    except Exception:
        return False


def validate_qr(user_check_id):
    try:
        user = User.objects.get(uuid=user_check_id)
        payment_check=Payment.objects.get(user=user)
        if payment_check.is_paid==True:
            user.attendance = True
            user.save()
            context = {
                'user_name':user.name,
                'user_reg':user.reg
            }
            return ("qr_check_paid.html",context)
        else:
            return ("qr_check_unpaid.html",None)
    except Exception:
            return ("qr_check_unpaid.html",None)


def reset_cache():
    cache.set('cache::user_email_list', list(User.objects.values_list('email', flat=True)))
    cache.set('cache::email_name_list', list(User.objects.values_list('email', 'name')))


def email_name_list_from_cache():
    # if cache.get('cache::email_name_list') is None:
    #     return list(User.objects.values_list('email', 'name'))
    #
    # return cache.get('cache::email_name_list')
    return list(User.objects.values_list('email', 'name'))


def user_email_list_from_cache():
    # if cache.get('cache::user_email_list') is None:
    #     return list(User.objects.values_list('email', flat=True))
    #
    # return cache.get('cache::user_email_list')
    return list(User.objects.values_list('email', flat=True))



