from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from rentalapp.forms import UserRoleForm


class AuthViews:
    @staticmethod
    def login_view(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Zostałeś zalogowany.")
                return redirect('rentalapp:dashboard')
            else:
                messages.error(request, "Nieprawidłowa nazwa użytkownika lub hasło.")
        return render(request, 'rentalapp/login/login.html')

    @staticmethod
    def logout_view(request):
        logout(request)
        messages.info(request, "Zostałeś wylogowany.")
        return redirect('rentalapp:login')

    @staticmethod
    def assign_role(request):
        if request.method == 'POST':
            form = UserRoleForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                role = form.cleaned_data['role']
                user.groups.clear()
                user.groups.add(role)
                messages.success(request, f"Użytkownik {user.username} otrzymał rolę {role.name}.")
                return redirect('rentalapp:assign_role')
        else:
            form = UserRoleForm()
        return render(request, 'rentalapp/login/assign_role.html', {'form': form})