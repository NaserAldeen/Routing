from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.views.generic import View
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse, Http404
from .models import *
import json
from pandas import *
from math import sin, cos, sqrt, atan2, radians,ceil
import datetime


##################################
########   USER  SECTION  ########
##################################

class Logout(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/ropt/signin/')


class ResetPassword(LoginRequiredMixin, View):
    login_url = '/signin/'
    redirect_field_name = 'next'

    def get(self, request):
        params = {}
        return render(request, 'profile/user/reset-password.html', params)
    def post(self, request):
        params = {}
        success = False
        mimetype = 'application/json'
        message = "Something went wrong, try again."     
        try:       
            op = request.POST.get('old_password')
            np = request.POST.get('new_password')
            rp = request.POST.get('re_password')
            if op and np and np == rp and request.user.is_authenticated:
                if(len(np) < 8):
                    success = False
                else: 
                    saveuser = request.user
                    if saveuser.check_password(op):
                        saveuser.set_password(np)
                        saveuser.save()
                        success = True 
                        message = "Password was reset."
            else:
                success = False 
                message = "Something went wrong, try again."
        except:
            success = False 
    
        response = {'success': success, 'message': message }
        return HttpResponse(json.dumps(response), mimetype)



class ChangeProfile(LoginRequiredMixin, View):
    login_url = '/signin/'
    redirect_field_name = 'next'

    def get(self, request):
        params = {}
        return render(request, 'profile/user/change-profile.html', params)

    def post(self, request):
        params = {}
        success = False
        mimetype = 'application/json'
        message = "Something went wrong, try again."     
        try:       
            new_name = request.POST.get('username')
            profile = request.user.profile
            profile.name = new_name
            profile.save()
            success = True 
        except:
            success = False 
    
        response = {'success': success, 'message': message }
        return HttpResponse(json.dumps(response), mimetype)


##################################
######## DRIVER   SECTION ########
##################################



class DriversGetCities(View):
    def get(self, request):
        params = {}
        data = list(Area.objects.all().values())
        return JsonResponse(data, safe=False)

class DriversList(View):
    def get(self, request):
        params = {}
        params['drivers'] = Driver.objects.all()

        return render(request, 'profile/drivers/list.html', params)

def get_distance(a,b):

    # approximate radius of earth in km
    R = 6373.0
    print(a)
    lat1 = radians(float(a[0]))
    lon1 = radians(float(a[1]))
    lat2 = radians(float(b[0]))
    lon2 = radians(float(b[1]))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def get_lowest_shipment(current_point, shipments, start_time,driver,shipped):
    lowest_distance = 10000000000000000000
    lowest_shipment = None
    lowest_time = None
    
    for shipment in shipments: 
        shipment_point = (shipment.lat,shipment.lng)
        shipment_distance = get_distance(current_point,shipment_point)
        if lowest_distance >= shipment_distance:
            lowest_distance = shipment_distance 
            lowest_shipment = shipment 
            try: 
                # Add a buffer, because Kuwait is mostly straight lines
                lowest_time = int(lowest_distance/60*60*1.5)
            except:
                lowest_time=None
    return (lowest_shipment,lowest_distance,lowest_time, current_point,start_time,driver,shipped+1)


class DriverRoute(View):
    def get(self, request,did):
        driver = Driver.objects.get(id=did)
        shipments = Shipment.objects.filter(is_complete=False) 
        # Find the next shortest point 
        current_point = (driver.lat,driver.lng) 
        route = []
        route_ids = []
        start_time = "8:00"
        shipped = 1
        start_time = datetime.datetime.strptime(start_time, '%H:%M')
        next_shipment = get_lowest_shipment(current_point, shipments,start_time,driver,shipped)
        start_time = start_time +  datetime.timedelta(minutes=next_shipment[2])
        while(next_shipment[0] and shipments.exists()):
            shipped = shipped + 1 
            route.append(next_shipment)
            route_ids.append(next_shipment[0].id)
            current_point = (next_shipment[0].lat,next_shipment[0].lng)
            shipments = shipments.exclude(id__in=route_ids)
            next_shipment = get_lowest_shipment(current_point, shipments,start_time,driver,shipped)
            if(next_shipment[2]):
                start_time = start_time +  datetime.timedelta(minutes=next_shipment[2])

        params = {}
        params['route'] = route
        params['driver'] = driver

        return render(request, 'profile/drivers/route.html', params)





class DriverRouteAssigned(View):
    def get(self, request,did):
        driver = Driver.objects.get(id=did)
        shipments = Shipment.objects.filter(driver=driver, is_complete=False)
        print(shipments) 
        current_point = (driver.lat,driver.lng) 
        route = []
        route_ids = []
        start_time = "8:00"
        shipped = 1
        if(shipments.exists()):
            # Find the next shortest point 
            current_point = (driver.lat,driver.lng) 
            route = []
            route_ids = []
            start_time = "8:00"
            shipped = 1
            start_time = datetime.datetime.strptime(start_time, '%H:%M')
            next_shipment = get_lowest_shipment(current_point, shipments,start_time,driver,shipped)
            start_time = start_time +  datetime.timedelta(minutes=next_shipment[2])
            while(next_shipment[0] and shipments.exists()):
                shipped = shipped + 1 
                route.append(next_shipment)
                route_ids.append(next_shipment[0].id)
                current_point = (next_shipment[0].lat,next_shipment[0].lng)
                shipments =shipments.exclude(id__in=route_ids)
                next_shipment = get_lowest_shipment(current_point, shipments,start_time,driver,shipped)
                if(next_shipment[2]):
                    start_time = start_time +  datetime.timedelta(minutes=next_shipment[2])

        params = {}
        params['route'] = route
        params['driver'] = driver

        return render(request, 'profile/drivers/route-assigned.html', params)

class DriverOptimize(View):
    def get(self, request):
        drivers = Driver.objects.all()
        shipments = Shipment.objects.filter(is_complete=False) 
       
        params = {}
        params['drivers'] = drivers
        params['shipments'] = shipments

        return render(request, 'profile/drivers/optimize.html', params)

    def post(self, request):
        max_shipment = 50
        drivers = request.POST.get('drivers_chosen').split(',')
        shipments = request.POST.get('shipments_chosen').split(',')
        total_drivers = len(drivers)
        total_shipments = len(shipments) 
        shipments_per_driver = ceil(total_shipments/total_drivers)
        route_ids = []
        route = []
        print(shipments_per_driver)
        
        for driver_id in drivers: 
            shipped = 0

            
            driver = Driver.objects.get(id=driver_id)
            shipments = Shipment.objects.filter(id__in=shipments).exclude(id__in=route_ids) 
        # Find the next shortest point 
            current_point = (driver.lat,driver.lng) 
            print('i')
            print(current_point)
            
        
            start_time = "8:00"
            start_time = datetime.datetime.strptime(start_time, '%H:%M')
            try:
                next_shipment = get_lowest_shipment(current_point, shipments,start_time,driver,shipped)
                print(next_shipment)
            except: 
                break
            
            try:
                start_time = start_time +  datetime.timedelta(minutes=next_shipment[2])
            except: 
                break
            while(next_shipment[0] and shipments.exists()):
                if(shipped >= max_shipment or shipped >= shipments_per_driver ):
                    break
                else:
                    route.append(next_shipment)
                    route_ids.append(next_shipment[0].id)
                    current_point = (next_shipment[0].lat,next_shipment[0].lng)
                    shipments = shipments.exclude(id__in=route_ids)
                    
                    next_shipment = get_lowest_shipment(current_point, shipments,start_time,driver,shipped+1)
                    if(next_shipment[2]):
                        start_time = start_time +  datetime.timedelta(minutes=next_shipment[2])
                    shipped = shipped + 1
        print(route)

        params = {}
        params['route'] = route
        params['driver'] = driver

        return render(request, 'profile/drivers/optimized.html', params)


class DriverAssign(LoginRequiredMixin, View):
    login_url = '/signin/'
    redirect_field_name = 'next'
   
    def post(self, request):
        max_shipment = 50
        driver = request.POST.get('driver')
        shipment = request.POST.get('shipment')
        success = False 
        message = "Something went wrong"
        mimetype = 'application/json'

        try:
            shipment = Shipment.objects.get(id=shipment)
            driver = Driver.objects.get(id=driver)
            shipment.driver = driver
            shipment.save()
            success = True 

        except: 
            success = False 
            message = "Something went wrong"


        response = {'success': success, 'message': message }
        return HttpResponse(json.dumps(response), mimetype)




class DriverUnAssign(LoginRequiredMixin, View):
    login_url = '/signin/'
    redirect_field_name = 'next'
   
    def post(self, request):
        max_shipment = 50
        shipment = request.POST.get('shipment')
        success = False 
        message = "Something went wrong"
        mimetype = 'application/json'

        try:
            shipment = Shipment.objects.get(id=shipment)
            shipment.driver = None
            shipment.save()
            success = True 

        except: 
            success = False 
            message = "Something went wrong"


        response = {'success': success, 'message': message }
        return HttpResponse(json.dumps(response), mimetype)



def create_driver(driver_name,driver_username,driver_password, driver_city_id, driver_lat,driver_lng):
    success = False 
    tmp_user = None
    message = "Something went wrong"

    try:   
        driver_area = Area.objects.get(id=driver_city_id)
        if(User.objects.filter(username=driver_username).exists()):
            success = False 
            message = "Something went wrong, try again."     

        else: 
            # Create the user
            tmp_user = User.objects.create_user(driver_username, "", driver_password, 
                            first_name="", last_name="")
            tmp_user.save()

            tmp_user.profile.name = driver_name
            tmp_user.profile.is_driver = True
            tmp_user.profile.save()

            tmp_driver = Driver(user=tmp_user, area=driver_area,lat=driver_lat,lng=driver_lng)
            tmp_driver.save()
            success = True 
    except:
        if(tmp_user):
            tmp_user.delete()
        success = False 
        message = "Something went wrong, try again."     
    return success




class DriversAdd(LoginRequiredMixin, View):
    login_url = '/signin/'
    redirect_field_name = 'next'

    def get(self, request):
        params = {}
        params['cities'] = Area.objects.all().order_by('name')
        return render(request, 'profile/drivers/add.html', params)

    def post(self, request):
        params = {}
        success = False
        mimetype = 'application/json'
        message = "Something went wrong, try again."     
        try: 
            driver_name = request.POST.get('driver_name')
            driver_username = request.POST.get('username')
            driver_password = request.POST.get('password')
            driver_city_id = request.POST.get('city')
            driver_lat = request.POST.get('lat')
            driver_lng = request.POST.get('lng')
            success = create_driver(driver_name,driver_username,driver_password, driver_city_id, driver_lat,driver_lng)
        except: 
            success = False 
        response = {'success': success, 'message': message }
        return HttpResponse(json.dumps(response), mimetype)


class DriversBulk(LoginRequiredMixin, View):
    login_url = '/signin/'
    redirect_field_name = 'next'

    def get(self, request):
        params = {}
        params['cities'] = Area.objects.all().order_by('name')
        return render(request, 'profile/drivers/bulk.html', params)

    def post(self, request):
        params = {}
        success = False
        mimetype = 'application/json'
        message = "Something went wrong, try again."     
        
        try:
            file = request.FILES.get('bulk')
            xls = ExcelFile(file)
            df = xls.parse(xls.sheet_names[0])
            records = df.to_dict(orient='records')
            for record in records: 
                driver_name = record['name']
                driver_username = record['email']
                driver_password = record['password']
                driver_city_id = record['city']
                try: 
                    driver_city_id = Area.objects.get(name=driver_city_id).id
                except: 
                    driver_city_id = None 
                    continue
                driver_lat = record['lat']
                driver_lng = record['lng']

                success = create_driver(driver_name,driver_username,
                                driver_password, driver_city_id, 
                                driver_lat,driver_lng)
            success = True 
        except: 
            success = False 

        response = {'success': success, 'message': message }
        return HttpResponse(json.dumps(response), mimetype)

##################################
######## SHIPMENT SECTION ########
##################################

def create_shipment(shipment_address, shipment_city_id, shipment_lat,shipment_lng):
    success = False 
    message = "Something went wrong"
    tmp_shipment = None
    try:   
        shipment_area = Area.objects.get(id=shipment_city_id)
        tmp_shipment = Shipment(area=shipment_area,lat=shipment_lat,lng=shipment_lng, address = shipment_address)
        tmp_shipment.save()
        success = True 
        message = "Done"
    except:
        if(tmp_shipment):
            tmp_shipment.delete()
        success = False 
        message = "Something went wrong, try again."     
    return success


class ShipmentAdd(LoginRequiredMixin, View):
    login_url = '/signin/'
    redirect_field_name = 'next'

    def get(self, request):
        params = {}
        params['cities'] = Area.objects.all().order_by('name')
        return render(request, 'profile/shipments/add.html', params)

    def post(self, request):
        params = {}
        success = False
        mimetype = 'application/json'
        message = "Something went wrong, try again."     
        try: 
            shipment_address = request.POST.get('address')
            shipment_city_id = request.POST.get('city')
            shipment_lat = request.POST.get('lat')
            shipment_lng = request.POST.get('lng')
       
            success = create_shipment(shipment_address, shipment_city_id, shipment_lat,shipment_lng)
        except: 
            success = False 
        response = {'success': success, 'message': message }
        return HttpResponse(json.dumps(response), mimetype)


class ShipmentBulk(LoginRequiredMixin, View):
    login_url = '/signin/'
    redirect_field_name = 'next'

    def get(self, request):
        params = {}
        params['cities'] = Area.objects.all().order_by('id')
        return render(request, 'profile/shipments/bulk.html', params)

    def post(self, request):
        params = {}
        success = False
        mimetype = 'application/json'
        message = "Something went wrong, try again."     
        
        try:
            file = request.FILES.get('bulk')
            xls = ExcelFile(file)
            df = xls.parse(xls.sheet_names[0])
            records = df.to_dict(orient='records')
            print(records)
            for record in records: 
                
                shipment_address = record['address']
                shipment_city_id = record['city']
                
                try: 
                    shipment_city_id = Area.objects.filter(name=shipment_city_id).first().id
                except: 
                    shipment_city_id = None 
                    continue
                shipment_lat = record['lat']
                shipment_lng = record['lng']

                success = create_shipment(shipment_address, 
                            shipment_city_id, shipment_lat,shipment_lng)

        except: 
            success = False 

        response = {'success': success, 'message': message }
        return HttpResponse(json.dumps(response), mimetype)





class ShipmentComplete(LoginRequiredMixin, View):
    login_url = '/signin/'
    redirect_field_name = 'next'


    def post(self, request):
        params = {}
        success = False
        status = False 
        mimetype = 'application/json'
        message = "Something went wrong, try again."     
        
        try:
            shipment = request.POST.get('shipment')
            shipment = Shipment.objects.get(id=shipment)
            status = shipment.is_complete

            shipment.is_complete =  not status
            shipment.save()
            
            success = True
            status = shipment.is_complete

        except: 
            success = False 
            status = False

        response = {'success': success, 'status': status }
        return HttpResponse(json.dumps(response), mimetype)


class ShipmentList(View):
    def get(self, request):
        params = {}
        params['shipments'] = Shipment.objects.all()

        return render(request, 'profile/shipments/list.html', params)



