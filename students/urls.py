from django.urls import path
from . import views

urlpatterns = [
    # Rutas públicas (sin login requerido)
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('recibo/<str:token>/', views.upload_receipt, name='upload_receipt'),

    # Panel de gestión (requiere login)
    path('panel/', views.student_list, name='student_list'),
    path('panel/nuevo/', views.student_create, name='student_create'),
    path('panel/<int:pk>/', views.student_detail, name='student_detail'),
    path('panel/<int:pk>/editar/', views.student_edit, name='student_edit'),
    path('panel/<int:pk>/eliminar/', views.student_delete, name='student_delete'),
    path('panel/<int:student_pk>/bono/nuevo/', views.voucher_create, name='voucher_create'),
    path('panel/<int:student_pk>/pago/nuevo/', views.payment_create, name='payment_create'),
    path('panel/historial/', views.audit_log_list, name='audit_log_list'),
]
