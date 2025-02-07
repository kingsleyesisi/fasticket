from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('fasticket_app.urls')),
    path('payments/', include('payment.urls')),
]
