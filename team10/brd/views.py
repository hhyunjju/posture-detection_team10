from django.http import HttpResponse

from .models import Post
from django.http import Http404
from .models import User, Post, Comment

from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import redirect
from .forms import PostModelForm, CommentForm

# 전체 목록 보기
def list(request):
        # 맨 처음 페이지를 요청해서 받아왔을 때
    post_list = Post.objects.all() 
    # return HttpResponse(post_all)
        # 이후 검색창에 검색어를 넣고 submit 했을 때
    search_key = request.GET.get('keyword')
    if search_key :
            # 이전에 입력했던 데이터는 search_key에 남아있다. 
            # 이전 입력 데이터도 쓰고자 한다면 context로 넘기면 된다.
        post_list = Post.objects.filter(title__contains=search_key)
    return render(request, 'brd/list.html', {'post_all':post_list, 'q':search_key})

# 상세 보기
def detail(request, no):
    post = get_object_or_404(Post, id=no)
    comment_form = CommentForm()
    comments = post.comments.all()
    return render(request, 'brd/post_detail.html', {'post':post, 
                                                    'comment_form':comment_form, 
                                                    'comments': comments})

# form 기반 데이터 추가 작업
# request.POST는 사용자가 제출한 POST 데이터
def post_create(request):
    if request.method == 'POST':
        form = PostModelForm(request.POST, request.FILES)
        if form.is_valid():
            # DB에 추가
            # cleaned_data : dictionary
            # post = Post.objects.create(**form.cleaned_data)
            post = form.save(commit=False)
            post.ip = request.META['REMOTE_ADDR']
            post.save()
            return redirect(post)
    else:
        form = PostModelForm()
    return render(request, 'brd/post_form.html', {'form':form,})

# form 기반 데이터 수정 작업
def post_update(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        # post로 입력 받았을 때
        # 0. 입력받은 데이터 바인딩
        form = PostModelForm(request.POST, request.FILES, instance=post) #request.FILES로 이미지파일도 넘겨줘야한다
        if form.is_valid():
            form.save()
            return redirect('brd:detail', no=post.id)
    else:
        form = PostModelForm(instance=post)
    return render(request, 'brd/post_update.html', {'form':form,})

# 데이터 삭제 작업
def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        post.delete()
        return redirect('brd:notice_board')
    else:
        return render(request, 'brd/post_delete.html', {'post':post})

def faq_view(request):
    # FAQ 페이지에 필요한 데이터를 처리
    # 예시: context = {'faq_data': faq_data}

    # FAQ 페이지의 템플릿을 렌더링하여 반환
    return render(request, 'brd/faq.html')

def comments_create(request, pk):
    #post가져오기
    post = get_object_or_404(Post, id=pk)
    #comment_form에 사용자가 입력한 데이터 채워주기: request.POST
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        #comment 객체를 수정하기 위해 Comment모델의 인스턴스 반환
        comment = comment_form.save(commit=False)
        comment.post = post #댓글이 어떤 포스트에 속할지 지정
        comment.save()
    return redirect('brd:detail', post.pk)

def comments_delete(request, post_pk, comment_pk):
        comment = get_object_or_404(Comment, id=comment_pk)
        comment.delete()
        return redirect('brd:detail', post_pk)