from django.urls import path

from .views import (
    BlogListView,
    BlogDetailView,
    CategoryDetailView,
    HomeView,
    ServiceDetailView,
    StandalonePageDetailView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("categorie/<slug:slug>/", CategoryDetailView.as_view(), name="category-detail"),
    path(
        "categorie/<slug:category_slug>/soin/<slug:slug>/",
        ServiceDetailView.as_view(),
        name="service-detail",
    ),
    path("page/<slug:slug>/", StandalonePageDetailView.as_view(), name="page-detail"),
    path("blog/", BlogListView.as_view(), name="blog_list"),
    path("blog/<slug:slug>/", BlogDetailView.as_view(), name="blog_detail"),
]
