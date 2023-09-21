from django.utils.timezone import now
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count


from blog.models import Post, Category, User, Comment
from blog.constants import NUMBER_OF_POST_PER_PAGE
from blog.utils import getting_a_list_of_posts
from blog.forms import PostForm, CommentForm, UserForm


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={'username_slug': self.request.user}
        )


def index(request):
    template_name = 'blog/index.html'
    paginator = Paginator(getting_a_list_of_posts(), NUMBER_OF_POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template_name, context)


def post_detail(request, id):
    template_name = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.all().filter(
            category__is_published=True,
            pub_date__lte=timezone.now(),
            is_published=True
        ),
        pk=id
    )
    comments = post.comments.all()
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments
    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(Category, slug=category_slug,
                                 is_published=True,)
    paginator = Paginator(category.posts.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ), NUMBER_OF_POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category, 'page_obj': page_obj
    }
    return render(request, template_name, context)


def user_profile(request, username_slug):
    template_name = 'blog/profile.html'
    profile = get_object_or_404(User, username=username_slug)
    if profile == request.user:
        query = profile.posts.annotate(
            comment_count=Count('comments')
            ).order_by('-created_at')
    else:
        query = profile.posts.filter(
           is_published=True,
           pub_date__lte=now(),
           category__is_published=True
        ).order_by('-created_at').annotate(
            comment_count=Count('comments')
            )
    paginator = Paginator(query, NUMBER_OF_POST_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile, 'page_obj': page_obj
    }
    return render(request, template_name, context)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    pk_url_kwarg = 'id'
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, id=kwargs['id'])
        if instance.author != request.user:
            redirect(
                'blog:post_detail',
                kwargs={'id': kwargs['id']}
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'id': self.kwargs['id']}
        )


@login_required
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id=id)


@login_required
def edit_comment(request, id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    context = {'comment': comment}
    if comment.author != request.user:
        return redirect('blog:post_detail', id=id)
    form = CommentForm(request.POST or None, instance=comment)
    context['form'] = form
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect('blog:post_detail', id=id)
    return render(request, 'blog/comments.html', context)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, id=kwargs['id'])
        if instance.author != request.user:
            redirect(
                'blog:profile',
                kwargs={'username_slug': self.request.user}
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username_slug': self.request.user}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, id=kwargs['id'])
        if instance.author != request.user:
            redirect(
                'blog:post_detail',
                kwargs={'id': kwargs['id']}
            )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'id': self.kwargs['id']}
        )


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        slug_field = 'username_slug'
        return get_object_or_404(User, username=self.request.user)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username_slug': self.request.user}
        )
