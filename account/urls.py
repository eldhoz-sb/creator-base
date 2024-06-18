from django.urls import path
from account.views import CreatorSignup, SupporterSignup, EditProfile,PasswordChangeDone, addToList, ShowList, listpeople, listpeopledelete,search_users,contact,privacy,PaymentView,withdraw
from account import views
from django.contrib.auth import views as authViews

urlpatterns = [
    path('profile/edit', EditProfile, name='edit-profile'),
    path('creator_signup/', CreatorSignup, name='creator_signup'),
    path('supporter_signup/', SupporterSignup, name='supporter_signup'),
    path('login/', authViews.LoginView.as_view(template_name='registration/login.html'), name='login'),
   	path('logout/', authViews.LogoutView.as_view(), {'next_page' : 'index'}, name='logout'),
    path('changepassword/done', PasswordChangeDone, name='change_password_done'),
   	path('passwordreset/', authViews.PasswordResetView.as_view(), name='password_reset'),
   	path('passwordreset/done', authViews.PasswordResetDoneView.as_view(), name='password_reset_done'),
   	path('passwordreset/<uidb64>/<token>/', authViews.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
   	path('passwordreset/complete/', authViews.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/addtolist', addToList, name='add-to-list'),
	path('mylists', ShowList, name='show-my-lists'),
    path('mylists/<list_id>', listpeople, name='list-people'),
	path('mylists/<list_id>/delete', listpeopledelete, name='list-people-delete'),
    path('search/', search_users, name='search_users'),
    path('contact/', contact, name='contact'),
    path('privacy/', privacy, name='privacy'),
    path('payment/', PaymentView, name='payment'),
    path('withdraw', withdraw, name='withdraw'),
]

'''path('changepassword/done', PasswordChangeDone, name='change_password_done'),
   	path('passwordreset/', authViews.PasswordResetView.as_view(), name='password_reset'),
   	path('passwordreset/done', authViews.PasswordResetDoneView.as_view(), name='password_reset_done'),
   	path('passwordreset/<uidb64>/<token>/', authViews.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
   	path('passwordreset/complete/', authViews.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    path('password_change/', PasswordChange, name='password_change'),
    path('verify_otp/',  VerifyOTP, name='verify_otp'),
    path('password_change_done/', password_change_done, name='password_change_done'),'''