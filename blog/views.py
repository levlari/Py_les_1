from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count 

def post_share(request, post_id):
 # Получение статьи по идентификатору.
  post = get_object_or_404(Post, id=post_id,status='published')
  sent = False
  #input('mark all')
  if request.method == 'POST':
   # Форма была отправлена на сохранение.
      #input('mark post')
      form = EmailPostForm(request.POST)
      if form.is_valid():
          #input('mark valid')
      # Все поля формы прошли валидацию.
          cd = form.cleaned_data
      # ... Отправка электронной почты.
          post_url = request.build_absolute_uri(post.get_absolute_url())
          subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
          message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
          #input('mark valid'+subject+message )
          send_mail(subject, message, 'admin@myblog.com', [cd['to']])
          #input('mark valid')
          sent = True
  else:
      form = EmailPostForm(request.GET)
      #input('mark get')
  #input('mark return'+str(post)+str(form))

  return render(request, 'blog/post/share.html', {'post':post, 'form':form, 'sent':sent})
                    
class PostListView(ListView):  
    queryset = Post.published.all()  
    context_object_name = 'posts'  
    paginate_by = 3  
    template_name = 'blog/post/list.html'  
                     

 
def post_list(request, tag_slug=None): 
    object_list = Post.published.all()
    tag = None 
    if tag_slug: 
        tag = get_object_or_404(Tag, slug=tag_slug) 
        object_list = object_list.filter(tags__in=[tag]) 
    paginator = Paginator(object_list, 3) # По 3 статьи на каждой странице.
    page = request.GET.get('page')
    #input(paginator.count)
    #input(paginator.num_pages)

    try:
        #input('try')
        posts = paginator.page(page)
        #input(posts)
    except PageNotAnInteger:
    # Если страница не является целым числом, возвращаем первую страницу.
        posts = paginator.page(1)
        #input(posts.object_list)
    except EmptyPage:
        
    # Если номер страницы больше, чем общее количество страниц, возвращаем последнюю.
        posts = paginator.page(paginator.num_pages)
        #input(posts.object_list)
    # posts = Post.published.all()
    #input(page)
    #input(posts)
    #input(paginator)
    
    return render(request,  
		  'blog/post/list.html',  
		  {'page': page,  
		  'posts': posts,  
		  'tag': tag})


def post_detail(request, year, month, day, post):  
    post = get_object_or_404(Post, slug=post,  
				   status='published',  
				   publish__year=year,  
				   publish__month=month,  
				   publish__day=day)  
      
    # Список активных комментариев к этой записи  
    comments = post.comments.filter(active=True)  
    new_comment = None  
    if request.method == 'POST':  
        # Комментарий был опубликован
          comment_form = CommentForm(data=request.POST)  
          if comment_form.is_valid():  
            # Создайте объект Comment, но пока не сохраняйте в базу данных
	           new_comment = comment_form.save(commit=False)  
            # Назначить текущий пост комментарию
	           new_comment.post = post  
            # Сохранить комментарий в базе данных 
	           new_comment.save()  
    else:  
        comment_form = CommentForm()  
    post_tags_ids = post.tags.values_list('id', flat=True)  
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)  
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request,  
	      'blog/post/detail.html',  
	      {'post': post,  
	      'comments': comments,  
	      'new_comment': new_comment,  
	      'comment_form': comment_form,  
	      'similar_posts': similar_posts})