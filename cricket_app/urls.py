from django.urls import path
from cricket_app.views import (
    team_list,
    team_detail,
    internationalseriesannouncement_list,
    internationalseriesannouncement_create,
    internationalmatchannouncement_list,
    internationalmatchannouncement_create,
    internationalmatchlist,
    internationalmatchdetail,
    internationalmatchcreate,
    internationalmatchupdate,
    internationalmatchdelete,
    internationalseriesresultdetail,
    teamstatlist,
)


urlpatterns = [
    path('team-list/', team_list),
    path('team-detail/', team_detail),
    path('series-announcement-list/',internationalseriesannouncement_list),
    path('series-announcement-create/',internationalseriesannouncement_create),
    path('match-announcement-list/<int:pk>/',internationalmatchannouncement_list),
    path('match-announcement-create/',internationalmatchannouncement_create),
    path('match-list/',internationalmatchlist),
    path('match-detail/',internationalmatchdetail),
    path('match-create/', internationalmatchcreate),
    path('match-update/',internationalmatchupdate),
    path('match-delete/',internationalmatchdelete),
    path('series-result-detail/<int:pk>/', internationalseriesresultdetail),
    path('team-stat-list/',teamstatlist),
]