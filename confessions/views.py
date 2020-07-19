from django.shortcuts import render, HttpResponseRedirect, HttpResponse, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView, View, FormView, TemplateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Deed, Category, Collection, Comment
from .forms import NewDeedForm, CommentForm, ReflectionForm


class PublicMixin:
    """
    QS to allow only non private deeds to be displayed
    """
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        return qs.filter(private=False)


class NewDeed(LoginRequiredMixin, View):
    def get(self, request):
        form = NewDeedForm()
        return render(request, 'confessions/create.html', {'form': form})

    def post(self, request):
        form = NewDeedForm(data=request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            Collection.objects.create(deed=form.instance)
            return render(request, 'confessions/detail.html', {'deed': form.instance})


class ViewDeed(LoginRequiredMixin, DetailView):
    model = Deed
    template_name = 'confessions/detail.html'
    context_object_name = 'deed'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super(ViewDeed, self).get_context_data()
        if self.object.user == self.request.user:
            context['owner'] = True
        coll = Collection.objects.get(deed=self.object)
        coll.price_update()
        context['collection'] = coll
        context['comment_form'] = CommentForm()
        if coll.price > 0:
            context['positive'] = True
        elif coll.price == 0:
            context['neutral'] = True
        else:
            context['negative'] = True

        return context


@login_required
def react(request, id, reaction):
    # Add a logic to only vote once or take the vote away and then vote again.... m2m mod
    # Add a counter later so that people can only vote if they ....  have some cred to them or buy votes.
    deed = Deed.objects.get(id=int(id))
    if reaction in ['li', 'ap', 'me', 'la', 'cr']:
        deed.reaction(reaction)
        return HttpResponseRedirect(reverse('view_deed', kwargs={'id': id}))
    return HttpResponseRedirect(reverse('index'))


class UpdateDeed(LoginRequiredMixin, UpdateView):
    model = Deed
    pk_url_kwarg = 'id'
    fields = ['situation']
    template_name = 'confessions/update.html'


class ListDeed(LoginRequiredMixin, PublicMixin, ListView):
    model = Deed
    template_name = 'confessions/list.html'
    context_object_name = 'deeds'


# Think of just adding these to the main profile page.
class ListDeedPersonal(LoginRequiredMixin, ListView):
    model = Deed
    template_name = 'confessions/list.html'
    context_object_name = 'deeds'

    def get_queryset(self):
        qs = super(ListDeedPersonal, self).get_queryset()
        return qs.objects.filter(user=self.request.user)


class ListCategories(ListView):
    model = Category
    template_name = 'categories/list.html'
    context_object_name = 'categories'

    def get_queryset(self, cat=None):
        if cat:
            category = get_object_or_404(Category, category_name=cat)
            deeds = Deed.objects.filter(category=category)
            return deeds
        return Deed.objects.all()


class Reflection(LoginRequiredMixin, UpdateView):
    model = Deed
    form_class = ReflectionForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'id'


class UpdateReflection(LoginRequiredMixin, UpdateView):
    model = Reflection
    template_name = 'blog/update.html'


@login_required
def comment(request, id):
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            Comment.objects.create(deed=id, user=request.user, body=comment_form.cleaned_data['body'])
            return render(request, 'confessions/detail.html', {'id': id})
