from .forms import CustomUserCreationForm, CustomUserChangeForm, PostForm, CommentForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import Post, Comment, Tag

# Authentication views  
def register(request):
    """
Handles user registration by displaying and processing a registration form.

If the request method is POST, it validates the form data and saves a new user
if the data is valid. Upon successful registration, redirects the user to the 
login page. If the request method is not POST, it initializes an empty 
registration form. Renders the registration page with the form.

Args:
    request: The HTTP request object.

Returns:
    HttpResponse: Renders the registration page with the form.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'blog/register.html', {'form':form})    

@login_required
def profile(request):
    """
    Handles the user profile update by displaying and processing a profile form.

    If the request method is POST, it validates and updates the user's data using
    the provided form. Upon successful update, it redirects the user to the profile
    page. If the request method is not POST, it initializes the form with the current
    user's data. Renders the profile page with the form.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Renders the profile page with the form.
    """
    
    # Get the current user
    user = request.user

    # If the request method is POST, process the form
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)  # Use the form to update the user's data
        if form.is_valid():
            form.save()  # Save the updated data to the database
            return redirect('profile')  # Redirect to the profile page after successful update
    else:
        form = CustomUserChangeForm(instance=user)  # Render the form with current user data

    return render(request, 'blog/profile.html', {'form': form})

# home view for displaying the menu
def home(request):
    """
Renders the home page of the blog application.

This view function handles the HTTP request for the home page and returns an 
HttpResponse object that renders the 'home.html' template.

Args:
    request: The HTTP request object.

Returns:
    HttpResponse: Renders the home page template.
     """
    return render(request, 'blog/home.html')
# Plog post views
# view to list all posts
class ListView(ListView):
    model = Post
    template_name = 'blog/list.html'

# view to display a single post
class DetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

# view to create a new post
@login_required
class CreatView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('post_list')  # Replace with your actual success URL

    def form_valid(self, form):
        # Save the post instance first
        """
        Saves the post instance and associates tags with the post.

        This method is called when the form is valid and is used to override the default behavior
        of the CreateView. It saves the post instance, and then handles the tags by splitting the
        input string into individual tag names, creating each tag if it does not exist, and
        associating each tag with the post.

        Returns:
            HttpResponse: The response object that is returned by the parent class's form_valid method.
        """
        response = super().form_valid(form)
        self.object.save()  # Save the post instance to get a PK

        # Handle tags
        tags_input = form.cleaned_data['tags']
        if tags_input:
            tag_names = [tag.strip() for tag in tags_input.split(',')]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                self.object.tags.add(tag)  # Associate tags with the post

        return response

class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('post_list')  # Replace with your actual success URL

    def form_valid(self, form):
        # Save the post instance first
        """
        Saves the post instance and updates tags associated with the post.

        This method is called when the form is valid and is used to override the default behavior
        of the UpdateView. It saves the post instance, clears existing tags, and then handles the
        tags by splitting the input string into individual tag names, creating each tag if it does
        not exist, and associating each tag with the post.

        Returns:
            HttpResponse: The response object that is returned by the parent class's form_valid method.
        """
        
        response = super().form_valid(form)

        # Handle tags
        self.object.tags.clear()  # Clear existing tags
        tags_input = form.cleaned_data['tags']
        if tags_input:
            tag_names = [tag.strip() for tag in tags_input.split(',')]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                self.object.tags.add(tag)  # Associate tags with the post

        return response

# view to update a post
class UpdateView(UpdateView, UserPassesTestMixin, LoginRequiredMixin):
    model = Post
    template_name = 'blog/update.html'
    form_class = PostForm
    success_url = 'home'

    def test_func(self):
        """
        Checks if the current user is the author of the post to be updated.

        This method is called by the UpdateView to ensure that the user attempting to update
        the post is the same user who created it. If the user is not the author, the view will
        redirect to the login page.

        Returns:
            boolean: Whether the user is authorized to update the post.
        """
        post = self.get_object()
        return self.request.user == post.author

# view to delete a post
class DeleteView(DeleteView, UserPassesTestMixin, LoginRequiredMixin):
    model = Post
    template_name = 'blog/delete.html'
    success_url = 'home'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
# comment views for crud operations
# view to list all comments
class ListViewComment(ListView):
    model = Comment
    template_name = 'blog/comment_list.html'

# view to create comment under post
@login_required
class CommentCreateView(CreateView):
    model = Comment
    template_name = 'blog/comment_create.html'
    form_class = CommentForm

    def form_valid(self, form):
        # Extract post_id from the URL
        """
        Ensures that the comment is associated with the logged-in user and the post
        specified in the URL.

        This method is called when the form is valid and is used to override the default behavior
        of the CreateView. It extracts the post_id from the URL, gets the post instance, and
        sets the comment's author and post fields. Then it calls the parent class's form_valid method
        to save the form.

        Returns:
            HttpResponse: The response object that is returned by the parent class's form_valid method.
        """
        post_id = self.kwargs['post_id']
        # Get the post instance
        post = get_object_or_404(Post, id=post_id)
        # Associate the comment with the logged-in user and the post
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=self.kwargs['post_id'])
        return context

# view to update comment 
class CommentUpdateView(UpdateView, UserPassesTestMixin, LoginRequiredMixin):    
    model = Comment
    template_name = 'blog/comment_update.html'
    form_class = CommentForm

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

# view to delete comment
class CommentDeleteView(UpdateView, UserPassesTestMixin, LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment_delete.html'
    
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        """
        Returns the URL to redirect to after successfully deleting the comment.

        The URL is the 'posts' page with the post_id as a parameter.

        Returns:
            str: The URL to redirect to.
        """
        post_id = self.kwargs['post_id']
        return reverse_lazy('posts', args=[post_id])

def search_view(request):
    """
    Handles the search feature by rendering a page with search results.

    Given a query string and a field name, this view filters the posts by the
    query string and the specified field. The results are then rendered in a
    template with the query string as a parameter.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object that is rendered with the search results.
    """
    query = request.GET.get('q', '')
    field = request.GET.get('field', 'title')  # Default to 'title'

    # Start with an empty queryset
    results = Post.objects.none()

    if query:
        if field == 'title':
            results = Post.objects.filter(title__icontains=query)
        elif field == 'content':
            results = Post.objects.filter(content__icontains=query)
        elif field == 'tags':
            results = Post.objects.filter(tags__name__icontains=query)

        return render(request, 'blog/search_result.html', {'results': results, 'query': query})    
class PostByTagListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        """
        Returns a queryset of posts filtered by the tag name from the URL kwargs.

        Args:
            self (PostByTagListView): The view instance.

        Returns:
            QuerySet: A queryset of posts filtered by the tag name.
        """
        tag_name = self.kwargs['tag_name']
        return Post.objects.filter(tags__name=tag_name)

  
