from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name=""),

    path('register', views.register, name="register"),

    path('accinfo',views.accinfo,name="accinfo"),

    path('my-login', views.mylogin, name="my-login"),

    path('dashboard', views.dashboard, name="dashboard"),

    path('my-logout', views.mylogout, name="my-logout"),

    path('cash-withdrawal',views.cw,name="cw"),

    path('cash-deposit',views.cd,name="cd"),

    path('transaction-history',views.th,name="th")
]