from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.views.generic import ListView

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    View for listing all users. Only accessible by staff members.
    """
    model = get_user_model()
    template_name = 'registration/user_list.html'
    context_object_name = 'users'
    ordering = ['username']

    def test_func(self):
        """Only allow staff members to access this view."""
        return self.request.user.is_staff
