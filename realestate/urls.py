from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('buy-developments/', views.buy_developments_view, name='buy_developments'),
    path('buy-portfolio/', views.buy_portfolio_view, name='buy_portfolio'),
    path('buy-developments/', views.buy_developments_view, name='buy_developments'),
    path('commercial-buy/', views.commercial_buy_view, name='commercial_buy'),
    path('buy-land/', views.buy_land_view, name='buy_land'),
    path('buy/residential/', views.residential_buy_list, name='residential_buy_list'),
    path('residential-buy/<int:pk>/', views.ResidentialBuyDetailView.as_view(), name='property_detail'),


    path('rent/commercial/', views.rent_commercial_list, name='rent_commercial'),
    path('rent/residential/', views.rent_residential_list, name='rent_residential_list'),
    path('rent/residential/<int:pk>/', views.residential_rent_detail, name='residential_rent_detail'),



    path('about/', views.about_view, name='about'),
   # path('blog/', views.blog_view, name='blog'),
    path('contact/', views.contact_view, name='contact'),
    path('terian/', views.terian_view, name='terian'),
    path('sell/', views.sell_view, name='sell'),

    path('search/', views.search_view, name='search'),
    path('contact/submit/', views.contact_form_submit, name='contact_form_submit'),

    path('residential-buy/<int:pk>/', views.ResidentialBuyDetailView.as_view(), name='residential_buy_detail'),
    path('buy-development/<int:pk>/', views.BuyDevelopmentDetailView.as_view(), name='buy_development_detail'),
    path('commercial-buy/<int:pk>/', views.CommercialBuyDetailView.as_view(), name='commercial_buy_detail'),
    path('buy-land/<int:pk>/', views.BuyLandDetailView.as_view(), name='buy_land_detail'),
    path('residential-rent/<int:pk>/', views.residential_rent_detail, name='residential_rent_detail'),
    path('commercial-rent/<int:pk>/', views.CommercialRentDetailView.as_view(), name='commercial_rent_detail'),

    # Add other URLs as needed
]