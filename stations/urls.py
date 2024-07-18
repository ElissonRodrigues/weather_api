from django.urls import path
from .views import (
    stations,
    stations_by_id,
    historical_data_by_id,
    historical_data,
    analyze,
    predict,
    station_create,
)

urlpatterns = [
    path("stations/", stations, name="stations"),
    path("stations/create/", station_create, name="station-create"),
    path("stations/<int:pk>/", stations_by_id, name="stations-by-id"),
    path("stations/historical", historical_data, name="historical-data"),
    path("stations/<int:pk>/historical/", historical_data_by_id, name="historical-data-by-id"),
    path("stations/<int:pk>/analyze/", analyze, name="analyze"),
    path("stations/<int:pk>/predict/", predict, name="predict"),
]
