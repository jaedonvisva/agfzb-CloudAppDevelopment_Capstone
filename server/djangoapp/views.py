from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, analyze_review_sentiments
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        # pull from dictionary
        username = request.POST['username']
        password = request.POST['password']
        # check auth
        user = authenticate(username=username, password=password) 
        if user is not None:
            # login if valid
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    context = {}
    # get user from session id
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    # redirect back to the index.html
    return render(request, 'djangoapp/index.html', context)

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        username = request.POST['username']
        password = request.POST['password']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            return render(request, 'djangoapp/index.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/9c7396a4-e144-463b-8369-f5ea0e853558/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        print(len(dealerships))
        context = {}
        context["dealerships"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url_r = f"https://us-south.functions.appdomain.cloud/api/v1/web/9c7396a4-e144-463b-8369-f5ea0e853558/dealership-package/get-review?id={dealer_id}"
        url_ds = f"https://us-south.functions.appdomain.cloud/api/v1/web/9c7396a4-e144-463b-8369-f5ea0e853558/dealership-package/get-dealership?id{dealer_id}"
        # Get dealers from the URL
        context = {
            "dealer": get_dealers_from_cf(url_ds)[dealer_id-1],
            "reviews": get_dealer_reviews_from_cf(url_r, dealer_id-1),
        }
        
        return render(request, 'djangoapp/dealer_details.html', context)
# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    url_ds = f"https://us-south.functions.appdomain.cloud/api/v1/web/9c7396a4-e144-463b-8369-f5ea0e853558/dealership-package/get-dealership?id{dealer_id}"
    if request.method == "GET":
            context = {}  
            context['dealerid'] = dealer_id
            context['dealer'] = get_dealers_from_cf(url_ds)[dealer_id-1]
            cars = CarModel.objects.filter(dealer_id=int(dealer_id)).all()
            context['cars'] = cars
            return render(request, 'djangoapp/add_review.html',context)
    if request.method == "POST" and request.user.is_authenticated:
        car = CarModel.objects.get(pk=int(request.POST['car']))
        json_payload = {
"review": 
    {
        "id": 1117,
        "name": request.user.username,
        "dealership": dealer_id,
        "review": request.POST['content'],
        "purchase": False,
        "another": "field",
        'purchase': bool(request.POST.get('purchase',False)),
            'purchase_date': datetime.strptime(request.POST['purchasedate'], "%m/%d/%Y").isoformat()
    }
}
        url= "https://us-south.functions.cloud.ibm.com/api/v1/namespaces/69d2c467-206c-4606-b559-fa18d561d7e4/actions/dealership-package/post-review"
        post_request(url=url, json_payload=json_payload)
        
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id, dealer_name=dealer_name)
    else:
        return HttpResponse({"message":"Forbidden"})

