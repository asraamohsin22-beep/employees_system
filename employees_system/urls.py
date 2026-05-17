from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('secret-admin-123/', admin.site.urls),  # 🔥 هذا السطر مهم جداً
    path('', include('employees.urls')),
    
]