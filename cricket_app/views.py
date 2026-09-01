from django.shortcuts import render

# Create your views here.
from cricket_app.models import (
    international_match_model,
    international_series_announcement_model,
    international_series_result_model,
    international_match_announcement_model,
    team_model,
    team_stats
)
from cricket_app.serializers import (team_serializer,
                                     international_series_announcement_serializer,
                                     international_series_result_serializer,
                                     international_match_serializer,
                                     team_stat_serializer,
                                     international_match_announcement_serializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.shortcuts import get_object_or_404
from collections import defaultdict
from datetime import date
from rest_framework import status
from rest_framework import serializers
from cricket_app.permission import IsAdminOrAutenticatedReadOnly
from rest_framework.filters import OrderingFilter
from django.db.models import Q


class team_list(generics.ListCreateAPIView):
    queryset=team_model.objects.all()
    serializer_class=team_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]

class team_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset=team_model.objects.all()
    serializer_class=team_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]


class internationalseriesannouncement_list(generics.ListAPIView):
    serializer_class = international_series_announcement_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]

    def get_queryset(self):
        current_date = date.today()

        return international_series_announcement_model.objects.filter(
            end_date__gte=current_date
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {"message": "No international series have been announced."},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class internationalseriesannouncement_detail(generics.ListAPIView):
    serializer_class = international_series_announcement_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]

    def get_queryset(self):
        current_date = date.today()
        team_1 = self.request.query_params.get("team_1")
        team_2 = self.request.query_params.get("team_2")
        queryset = international_series_announcement_model.objects.filter(
            end_date__gte=current_date
        )
        if team_1 and team_2:
            queryset = queryset.filter(
                Q(
                    team_1__country=team_1,team_2__country=team_2
                 ) |
                Q(
                    team_1__country=team_2,team_2__country=team_1
                )
            )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        team_1 = request.query_params.get("team_1")
        team_2 = request.query_params.get("team_2")

        if not queryset.exists():

            if team_1 and team_2:
                message = (
                    f"No international series found between "
                    f"{team_1} and {team_2}."
                )
            else:
                message = "No international series have been announced."

            return Response(
                {"message": message},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(queryset, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class internationalseriesannouncement_create(generics.CreateAPIView):
    serializer_class = international_series_announcement_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]


class internationalmatchannouncement_list(generics.ListAPIView):
    serializer_class=international_match_announcement_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]

    def get_queryset(self):
        current_date=date.today()
        series=self.kwargs.get("pk")
        return international_match_announcement_model.objects.filter(
            match_date__gte=current_date,series_number=series
        ).order_by("match_date", "match_number")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {"message": "No international matches have been announced."},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class internationalmatchannouncement_create(generics.CreateAPIView):
    serializer_class=international_match_announcement_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]

    def perform_create(self, serializer):
        current_date=date.today()
        if current_date<serializer.validated_data["match_date"]:
            serializer.save()
        else:
            raise serializers.ValidationError(
                 "Match announcement date cannot be in the past."
            )
            
        
class internationalmatchlist(generics.ListAPIView):
    queryset = international_match_model.objects.all()
    serializer_class = international_match_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]

    def get_queryset(self):
        team_1 = self.request.query_params.get("team_1")
        team_2 = self.request.query_params.get("team_2")
        today=date.today()

        return international_match_model.objects.filter(
            match_id__series_number__team_1=team_1,
            match_id__series_number__team_2=team_2,
            match_id__match_date__lt=today
        )


class internationalmatchdetail(generics.ListAPIView):
    queryset = international_match_model.objects.all()
    serializer_class = international_match_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]

    def get_queryset(self):
        team_1 = self.request.query_params.get("team_1")
        team_2 = self.request.query_params.get("team_2")
        match_number=self.request.query_params.get("match_number")

        latest_series = international_series_announcement_model.objects.filter(
            team_1=team_1,
            team_2=team_2,
            end_date__lt=date.today()
        ).order_by("-start_date").first()

        today=date.today()

        if not latest_series:
            return international_match_model.objects.none()
        
        return international_match_model.objects.filter(
            match_id__series_number=latest_series,
            match_id__match_number=match_number,
            match_id__match_date__lt=today
        )

def update_series_result(series):

    completed_matches = international_match_model.objects.filter(
        match_id__series_number=series,
        match_id__match_date__lt=date.today()
    )

    if completed_matches.count() < series.total_matches:
        international_series_result_model.objects.filter(
            series_number=series
        ).delete()
        return

    team_1_win = completed_matches.filter(
        winner=series.team_1
    ).count()

    team_2_win = completed_matches.filter(
        winner=series.team_2
    ).count()

    if team_1_win > team_2_win:
        series_winner = series.team_1
        series_loser = series.team_2
        series_result = f"{series.team_1} won by {team_1_win}-{team_2_win}"

    elif team_2_win > team_1_win:
        series_winner = series.team_2
        series_loser = series.team_1
        series_result = f"{series.team_2} won by {team_2_win}-{team_1_win}"

    else:
        series_winner = None
        series_loser = None
        series_result = "series tied"

    international_series_result_model.objects.update_or_create(
        series_number=series,
        defaults={
            "series_winner": series_winner,
            "series_loser": series_loser,
            "series_result": series_result,
        }
    )


class internationalmatchcreate(generics.CreateAPIView):
    serializer_class = international_match_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]

    def perform_create(self, serializer):
        match_id = self.request.query_params.get("match_id")
        if not match_id:
            raise serializers.ValidationError(
                "match_id is required."
            )
        match = serializer.save(match_id_id=match_id)
        series = match.match_id.series_number
        update_series_result(series)


class internationalmatchupdate(generics.UpdateAPIView):
    serializer_class = international_match_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]

    def get_queryset(self):
        series=self.request.query_params.get("series_number")
        match=self.request.query_params.get("match_number")
        return international_match_model.objects.filter(
            match_id__series_number__id=series,
            match_id__match_number=match
        )
    
    def perform_update(self, serializer):
        match=serializer.save()
        series=match.match_id.series_number
        update_series_result(series)


class internationalmatchdelete(generics.DestroyAPIView):
    serializer_class = international_match_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]

    def get_queryset(self):
        series=self.request.query_params.get("series_number")
        match=self.request.query_params.get("match_number")
        return international_match_model.objects.filter(
            match_id__series_number__id=series,
            match_id__match_number=match
        )
            
    def perform_destroy(self, instance):
        series = instance.match_id.series_number
        instance.delete()
        update_series_result(series)


class internationalseriesresultlist(generics.ListAPIView):
    queryset=international_series_result_model.objects.all()
    serializer_class=international_series_result_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]

    
class internationalseriesresultdetail(generics.RetrieveAPIView):
    serializer_class=international_series_result_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]

    def get_object(self):
        series=self.kwargs.get("pk") 
        return get_object_or_404(
            international_series_result_model,
            series_number=series
        )


def update_team_stat(month, year):
    series_list = international_series_announcement_model.objects.filter(
        end_date__month=month,
        end_date__year=year,
        end_date__lt=date.today()
    )
    stat = defaultdict(lambda: {
        "match_played": 0,
        "win": 0,
        "loss": 0,
        "draw": 0,
        "series_played": 0,
        "series_won": 0,
        "series_loss": 0,
        "team_updated_score": 0.0,
    })

    for series in series_list:
        team_1 = series.team_1
        team_2 = series.team_2
        matches = international_match_model.objects.filter(
            match_id__series_number=series,
            match_id__match_date__lt=date.today()
        )
        if matches.count() < series.total_matches:
            continue

        match_count = matches.count()

        stat[team_1.id]["match_played"] += match_count
        stat[team_1.id]["win"] += matches.filter(
            winner=team_1
        ).count()
        stat[team_1.id]["loss"] += matches.filter(
            loser=team_1
        ).count()
        stat[team_1.id]["draw"] += matches.filter(
            result_type="tie"
        ).count()


        stat[team_2.id]["match_played"] += match_count
        stat[team_2.id]["win"] += matches.filter(
            winner=team_2
        ).count()
        stat[team_2.id]["loss"] += matches.filter(
            loser=team_2
        ).count()
        stat[team_2.id]["draw"] += matches.filter(
            result_type="tie"
        ).count()

        stat[team_1.id]["series_played"] += 1
        stat[team_2.id]["series_played"] += 1

        for match in matches:
            team_1_score = match.team_1_score
            team_2_score = match.team_2_score
            if (
                match.batting_first == "team_1"
                and team_1_score > team_2_score
            ):
                score_difference = team_1_score - team_2_score
                stat[team_1.id]["team_updated_score"] += score_difference
                stat[team_2.id]["team_updated_score"] -= score_difference

            elif (
                match.batting_first == "team_2"
                and team_2_score > team_1_score
            ):
                score_difference = team_2_score - team_1_score
                stat[team_2.id]["team_updated_score"] += score_difference
                stat[team_1.id]["team_updated_score"] -= score_difference

            elif (
                match.batting_first == "team_1"
                and team_2_score > team_1_score
                and match.team_2_wicket < 10
            ):
                if match.team_2_ball_faced > 0:
                    team_2_full_score = (
                        team_2_score * 300
                    ) / match.team_2_ball_faced
                    updated_score = team_2_full_score - team_1_score
                    stat[team_2.id]["team_updated_score"] += updated_score
                    stat[team_1.id]["team_updated_score"] -= updated_score

            elif (
                match.batting_first == "team_2"
                and team_1_score > team_2_score
                and match.team_1_wicket < 10
            ):
                if match.team_1_ball_faced > 0:
                    team_1_full_score = (
                        team_1_score * 300
                    ) / match.team_1_ball_faced
                    updated_score = team_1_full_score - team_2_score
                    stat[team_1.id]["team_updated_score"] += updated_score
                    stat[team_2.id]["team_updated_score"] -= updated_score

        team_1_win = matches.filter(winner=team_1).count()
        team_2_win = matches.filter(winner=team_2).count()
        if team_1_win > team_2_win:
            stat[team_1.id]["series_won"] += 1
            stat[team_2.id]["series_loss"] += 1
        elif team_2_win > team_1_win:
            stat[team_2.id]["series_won"] += 1
            stat[team_1.id]["series_loss"] += 1

    for team_id, data in stat.items():
        match_played = data["match_played"]
        if match_played > 0:
            win_percent = (data["win"] / match_played) * 100
            loss_percent = (data["loss"] / match_played) * 100
        else:
            win_percent = 0
            loss_percent = 0

        team = team_model.objects.get(
            id=team_id
        )
        rating = 500
        rating += (
            (30 * data["win"])
            - (10 * data["loss"])
            + (60 * data["series_won"])
            - (20 * data["series_loss"])
        )
        team_stats.objects.update_or_create(
            country=team,
            defaults={
                "match_played": data["match_played"],
                "win": data["win"],
                "loss": data["loss"],
                "draw": data["draw"],
                "win_percent": win_percent,
                "loss_percent": loss_percent,
                "series_played": data["series_played"],
                "series_won": data["series_won"],
                "series_loss": data["series_loss"],
                "team_updated_score": data["team_updated_score"],
                "rating": rating,
            }
        )


class teamstatlist(generics.ListAPIView):
    serializer_class = team_stat_serializer
    permission_classes = [IsAdminOrAutenticatedReadOnly]
    filter_backends = [OrderingFilter]
    ordering_fields = ["-rating", "team_updated_score"]
    ordering = ["-rating", "-team_updated_score"]


    def get_queryset(self):
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")

        if not month or not year:
            raise serializers.ValidationError(
                "month and year are required"
            )
        update_team_stat(month, year)
        return team_stats.objects.all()