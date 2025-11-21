from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.student_list, name='student_list'),
    path('nuevo/', views.student_create, name='student_create'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/editar/', views.student_edit, name='student_edit'),
    path('<int:pk>/eliminar/', views.student_delete, name='student_delete'),
    path('<int:student_pk>/bono/nuevo/', views.voucher_create, name='voucher_create'),
    path('<int:student_pk>/pago/nuevo/', views.payment_create, name='payment_create'),
    path('historial/', views.audit_log_list, name='audit_log_list'),
    # Ruta pública para subir recibos (sin login)
    path('recibo/<str:token>/', views.upload_receipt, name='upload_receipt'),
]
