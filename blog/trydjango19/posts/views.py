from urllib import quote_plus
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect 
from django.contrib import messages

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.utils import timezone 

from .models import Post
from .forms import PostForm

from django.db.models import Q

# Create your views here.

def post_create(request):
	if not request.user.is_staff or not request.user.is_superuser: 
		raise Http404
	
	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		# print(form.cleaned_data.get("title"))
		instance.save()
		#message success
		messages.success(request,"successfully created")
		return HttpResponseRedirect(instance.get_absolute_url())
	# if request.method == "POST":
	# 	print(request.POST.get("content"))
	# 	print(request.POST.get("title"))

	context = {
		'form':form,
	}
	return render(request,'post_form.html',context)

def post_detail(request,slug=None):
	# instance = Post.objects.get(id=3)
	instance = get_object_or_404(Post, slug=slug)
	if instance.draft or instance.publish > timezone.now().date():
		if not request.user.is_superuser or not request.user.is_staff:
			raise Http404
	share_string = quote_plus(instance.content)
	context = {
	'share_string':share_string,
	'instance':instance,
	}
	return render(request,'post_detail.html',context)

def post_list(request):
	today = timezone.now().date()
	queryset_list = Post.objects.all()
	if not request.user.is_staff or not request.user.is_superuser:
		queryset_list = Post.objects.active()
	#filter(draft=False).filter(publish__lte=timezone.now()) #lte->lessthan or equal to #all()#.order_by('-timestamp')

	#this is for the search bro 
	query=request.GET.get("q")
	if query:
		queryset_list = queryset_list.filter(
			Q(title__icontains=query) |
			Q(content__icontains=query) |
			Q(user__first_name__icontains=query)|
			Q(user__last_name__icontains=query)
			).distinct()#it cant have duplicate elements now



	paginator = Paginator(queryset_list, 2) # Show 6 contacts per page
	page_request_var = "goto"
	page = request.GET.get(page_request_var)
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
	# If page is not an integer, deliver first page.
		queryset = paginator.page(1)
	except EmptyPage:
	# If page is out of range (e.g. 9999), deliver last page of results.
		queryset = paginator.page(paginator.num_pages)

	context = {
	'page_request_var':page_request_var,
	'object_list': queryset,
	'today':today
	}

	# if request.user.is_authenticated():
	# 	context = {'title':'user is authenticated'}
	# else:
	# 	context = {'title':'user isnt authenticated'}

	return render(request,'post_list.html',context)


def post_update(request,slug=None):
	if not request.user.is_staff or not request.user.is_superuser: 
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	form = PostForm(request.POST or None, request.FILES or None, instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.user = request.user
		instance.save()
		#message success
		messages.success(request,"<a href='#'>Item</a> successfully edited", extra_tags='html_safe')
		return HttpResponseRedirect(instance.get_absolute_url())

	context = {
	'form':form,
	'instance':instance,
	}
	return render(request,'post_form.html',context)

def post_delete(request, slug=None):
	if not request.user.is_staff or not request.user.is_superuser: 
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	instance.delete()
	messages.success(request,"successfully deleted", extra_tags='html_safe')
	return redirect('posts:list')

