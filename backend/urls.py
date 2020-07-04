"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from api.views import (UserCreateAPIView, UserLoginAPIView)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', UserLoginAPIView.as_view()),
    path('signup/', UserCreateAPIView.as_view())
]


#
# Routing App URLs and imports 
#
import django.contrib.auth.views as auth_views
from django.http import HttpResponseRedirect, HttpResponse, Http404
from ropt.views import *


routing_patterns = [
    # User Profile and Login
    path(r'ropt/signin/', auth_views.LoginView.as_view(),
        {'extra_context': {'registration_form': ''}}, name='ropt_signin'),
    path(r'ropt/signout/', Logout.as_view(), name='ropt_signout'),
    path(r'ropt/user/profile/reset-password/', ResetPassword.as_view(), name='ropt_user_profile_reset-password'),
    path(r'ropt/user/profile/change-profile/', ChangeProfile.as_view(), name='ropt_user_profile_cange-profile'),
    
    # Driver related endpoints
    path(r'ropt/user/drivers/add/', DriversAdd.as_view(), name='ropt_drivers_add'),
    path(r'ropt/user/drivers/bulk/', DriversBulk.as_view(), name='ropt_drivers_bulk'),
    path(r'ropt/user/drivers/list/', DriversList.as_view(), name='ropt_drivers_list'),
    re_path(r'ropt/user/drivers/route/(?P<did>[\w-]+)/assigned/$', DriverRouteAssigned.as_view(), name='ropt_drivers_route_assigned'),
    re_path(r'ropt/user/drivers/route/(?P<did>[\w-]+)/$', DriverRoute.as_view(), name='ropt_drivers_route'),

    re_path(r'ropt/user/drivers/optimize/$', DriverOptimize.as_view(), name='ropt_drivers_optimize'),
    re_path(r'ropt/user/drivers/assign/$', DriverAssign.as_view(), name='ropt_drivers_assign'),
    re_path(r'ropt/user/drivers/unassign/$', DriverUnAssign.as_view(), name='ropt_drivers_unassign'),
    
    # Shipment related endpoints
    path(r'ropt/user/shipments/add/', ShipmentAdd.as_view(), name='ropt_shipments_add'),
    path(r'ropt/user/shipments/bulk/', ShipmentBulk.as_view(), name='ropt_shipments_bulk'),
    path(r'ropt/user/shipments/list/', ShipmentList.as_view(), name='ropt_shipments_list'),
    path(r'ropt/user/shipments/complete/', ShipmentComplete.as_view(), name='ropt_shipments_complete'),
    

]
urlpatterns += routing_patterns 