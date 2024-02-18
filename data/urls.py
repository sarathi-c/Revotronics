from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('login/', views.login, name='login'),
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/profile/', views.create_user, name="profile"),

    path('payment/', views.make_payment, name='payment'),
    path('payment_success/', views.payment_success, name='payment_success'),

    path('registration/', views.register, name='registration'),

    path('checkqr/user_check_id=<str:user_check_id>/',views.qr_check,name='checkqr'),

    path('paper_presentation/', TemplateView.as_view(template_name='paper_presentation.html'), name='paper_presentation'),
    path('guesstronics/', TemplateView.as_view(template_name='guesstronics.html'), name='guesstronics'),
    path('electroswaggers/', TemplateView.as_view(template_name='electroswaggers.html'), name='electroswaggers'),
    path('cs2/', TemplateView.as_view(template_name='cs2.html'), name='cs2'),
    path('electroquest/', TemplateView.as_view(template_name='electroquest.html'), name='electroquest'),
    path('bidwars/', TemplateView.as_view(template_name='bidwars.html'), name='bidwars'),
    path('funopedia/', TemplateView.as_view(template_name='funopedia.html'), name='funopedia'),
    path('guesswork/', TemplateView.as_view(template_name='guesswork.html'), name='guesswork'),
    path('debate/', TemplateView.as_view(template_name='debate.html'), name='debate'),
    path('rhymeredux/', TemplateView.as_view(template_name='rhymeredux.html'), name='rhymeredux'),

    path('registered_list/',views.registered_list,name="registered_list"),
]
