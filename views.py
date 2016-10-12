from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect, JsonResponse
from django.core.context_processors import csrf
from django.template import RequestContext
from forms import *
from models import *
from django.conf import settings
import os


def index(request):
    values={}
    if request.method =="GET":
        if  User.objects.filter(user__username = request.user.username).count() > 0:
            values["img"]=User.objects.filter(user__username = request.user.username)[0]
        values["Updates"] = Update.objects.all().order_by('-created_on')[:50]
        return render_to_response("index.html", values, context_instance = RequestContext(request))
    elif request.method == "POST":
        if request.POST.get("Update"):  # test the form type
            form = SendUpdates(request.POST)
            if User.objects.filter(user__username=request.user.username).count() > 0:
                values["img"] = User.objects.filter(user__username=request.user.username)[0]
            new_update = Update(text=request.POST['Update'])
            user = User.objects.filter(user__username =request.user)[0]
            new_update.user = user
            new_update.save()
            values["Updates"] = Update.objects.all().order_by('-created_on')[:50]
            return render_to_response("index.html", values, context_instance=RequestContext(request))

        elif request.POST.get("Search"):
            form = SearchUsers(request.POST)
            if form.is_valid():
                values["search"] = request.POST['Search']
                if User.objects.filter(user__username=request.POST["Search"]).count() > 0:
                    values["img"]= User.objects.get(user__username=request.POST["Search"]).img
                    values["Updates"]=Update.objects.filter(user__user__username=request.POST['Search']).order_by('-created_on')
                    if Follows.objects.filter(follows__user__username=request.POST["Search"],user__user__username=request.user).count()>0 :
                        values["following"]=True
                    else:
                        values["following"]=False
                    return render_to_response("User.html", values, context_instance=RequestContext(request))

                else:
                    if User.objects.filter(user__username=request.user.username).count() > 0:
                        values["img"] = User.objects.filter(user__username=request.user.username)[0]

                    values["error"]=["NO USER ACCOUNTS MATCHING SEARCH QUERY. PLEASE, TRY AGAIN . . "]
                    values["Updates"] = Update.objects.all().order_by('-created_on')[:50]
                    return render_to_response("index.html", values, context_instance=RequestContext(request))


        if request.POST.get("Follow"):
            values["user"] = User.objects.filter(user__username=request.user)[0]
            values["tofollow"] = request

            if Follows.objects.filter(follows__user__username=request.POST["Follow"],user__user__username=request.user).count()>0:
                   values["following"] = True
            else:
                values["following"] = False

            resp= follow_user(values)
            return resp
        #if request.POST.get["like"]:
        #    values["user"]=User.objects.filter(user__username=request.user)[0]
        #    values["like_update"]=request
        #    if Likes.objects.filter(update=request.POST["Like"],user__user__username=request.user).count()>0:
        #        values["liked"]=True
        #    else:
        #        values["liked"]=False
        #    resp=like_update(values)
        #    return resp



def like_update(values):
    request = values["like_update"]
    if values["liked"]:
            x = Likes.objects.filter(update=request.POST["like"],user__user__username=values["user"])
            x.delete()
            values["liked"] = False
    else:
            like_method = Likes()
            like_method.user = values["user"]
            like_method.follows = User.objects.get(user__username=request.POST["like"])
            like_method.save()
            values["liked"] = True
    values["img"] = User.objects.get(user__username=request.POST["Follow"]).img
    values["search"] = User.objects.get(user__username=request.POST["Follow"])
    values["Updates"] = Update.objects.filter(user__user__username=request.POST['Follow']).order_by('-created_on')
    resp = render_to_response("index.html", values, context_instance=RequestContext(request))
    return resp


def follow_user(values):
    request = values["tofollow"]
    if values["following"]:
        x=Follows.objects.filter(follows__user__username=request.POST["Follow"],user__user__username=values["user"])
        x.delete()
        values["following"]=False
    else:
        follow_method = Follows()
        follow_method.user = values["user"]
        follow_method.follows = User.objects.get(user__username=request.POST["Follow"])
        follow_method.save()
        values["following"] = True
    values["img"] = User.objects.get(user__username=request.POST["Follow"]).img
    values["search"]=User.objects.get(user__username=request.POST["Follow"])
    values["Updates"] = Update.objects.filter(user__user__username=request.POST['Follow']).order_by('-created_on')
    resp= render_to_response("User.html", values, context_instance=RequestContext(request))
    return resp

def saveFile(file,username):
    if not os.path.exists(settings.MEDIA_ROOT+"/"):
        os.makedirs(settings.MEDIA_ROOT)
    fpath=settings.MEDIA_ROOT+"/"+username+"."+file.name.split(".")[-1]
    with open(fpath, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return fpath

def user_img(request,user):
    import mimetypes
    img= User.objects.get(user__username = user).img
    resp=HttpResponse(content_type = mimetypes.guess_type(img)[0])
    resp.content=open(img).read()
    return resp

def upload(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("../login")
    if request.method=="GET":
        return render_to_response("upload.html",{},context_instance = RequestContext(request))
    elif request.method=="POST":
        query= User.objects.filter(user__username = request.user.username)
        user=None
        if query.count()>0:
            user=query[0]
        else:
            user=User()
            user.user=request.user
        profile_pic=request.FILES["pic"]
        user.img=saveFile(profile_pic,request.user.username)
        user.save()
        return HttpResponseRedirect("/")

def login(request):
    if request.method == "GET":
        values={"form":LogInForm()}
        values.update(csrf(request))
        return render_to_response("login.html",values,context_instance = RequestContext(request))
    elif request.method=="POST":
        from django.contrib.auth import authenticate, login, logout
        user = authenticate(username = request.POST["username"], password = request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect("../")
        else:
            values = {"form": LogInForm(),"Error":"Wrong username or password, try again."}
            values.update(csrf(request))
            return render_to_response("login.html", values, context_instance = RequestContext(request))


def register(request):
    values={}
    if request.method=="GET":
        values={"form":RegisterForm()}
        values.update(csrf(request))
        return render_to_response("register.html",values, context_instance=RequestContext(request))
    elif request.method=="POST":
        form=RegisterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["password1"]==form.cleaned_data["password2"]:
                user=DjUser()
                user.username=form.cleaned_data["username"]
                user.email=form.cleaned_data["email"]
                user.first_name=form.cleaned_data["firstname"]
                user.last_name=form.cleaned_data["lastname"]
                user.set_password(form.cleaned_data["password1"])
                user.save()
                useracc=User()
                useracc.user= user
                useracc.save()
                values["success"]=True
            else:
                form._errors["password2"]=["The passwords don't match."]
        values["form"]= form
        values.update(csrf(request))
        return render_to_response("register.html",values,context_instance = RequestContext(request))
