from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import role_required

# Create your views here.
#@login_required(login_url="login") #check in core.urls.py login name should exist..
@role_required(allowed_roles=["owner"]) #check in core.urls.py login name should exist..
def ownerDashboardView(request):
    return render(request,"gems/owner/owner_dashboard.html")

#@login_required(login_url="login")
@role_required(allowed_roles=["user"]) #check in core.urls.py login name should exist.. 
def userDashboardView(request):
    return render(request,"gems/user/user_dashboard.html")