from rest_framework import serializers
from cricket_app.models import (team_model,
                                international_match_announcement_model,
                                international_series_announcement_model,
                                international_match_model,
                                international_series_result_model,
                                team_stats,
                        )
from datetime import date

class team_serializer(serializers.ModelSerializer):
    class Meta:
        model=team_model
        fields="__all__"


class international_series_announcement_serializer(serializers.ModelSerializer):
    class Meta:
        model=international_series_announcement_model
        fields="__all__"
    def validate(self, attrs):
        if attrs["team_1"] == attrs["team_2"]:
            raise serializers.ValidationError(
                "Team 1 and Team 2 cannot be the same."
            )
        return attrs


class international_match_announcement_serializer(serializers.ModelSerializer):

    class Meta:
        model=international_match_announcement_model
        fields="__all__"

    def validate(self, data):
        series = data["series_number"]

        queryset = international_match_announcement_model.objects.filter(
            series_number=series,
            match_number=data["match_number"]
        )
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "this matchnumber of the series is already added"
            )

        return data

    def create(self, validated_data):
        series=validated_data["series_number"]
        match_team=f"{series.team_1} v/s {series.team_2}"
        return international_match_announcement_model.objects.create(**validated_data,
                                                                     match_team=match_team
                                                                    )

    def update(self,instance,validated_data):
        series=validated_data.get("series_number",instance.series_number)
        for field,value in validated_data.items():
            setattr(instance,field,value)
        instance.match_team=f"{series.team_1} v/s {series.team_2}"
        instance.save()
        return instance
        

class international_match_serializer(serializers.ModelSerializer):

    class Meta:
        model=international_match_model
        fields="__all__"
        read_only_fields=["winner","loser","result_type","won_by"]

    def validate(self, data):
        series=data["match_id"].series_number
        match=data["match_id"].match_number
        match_date=data["match_id"].match_date
        if match>series.total_matches:
            raise serializers.ValidationError("match_number cannot be greater than series total match")
        if series.start_date>match_date or  series.end_date<match_date:
            raise serializers.ValidationError("match date should be between start and end date")
        if data["team_1_ball_faced"] > 300 or data["team_2_ball_faced"] > 300:
            raise serializers.ValidationError("Teams cannot face more than 300 balls")
        if data["team_1_wicket"] > 10 or data["team_2_wicket"] > 10:
            raise serializers.ValidationError("Team cannot lose more than 10 wickets")
        return data

    def create(self, validated_data):
        series=validated_data["match_id"].series_number
        if validated_data["batting_first"]=="team_1" and validated_data["team_1_score"]>validated_data["team_2_score"]:
            winner=series.team_1
            loser=series.team_2
            result_type="run"
            won_by=validated_data["team_1_score"]-validated_data["team_2_score"]

        elif validated_data["batting_first"]=="team_2" and validated_data["team_2_score"]>validated_data["team_1_score"]:
            winner=series.team_2
            loser=series.team_1
            result_type="run"
            won_by=validated_data["team_2_score"]-validated_data["team_1_score"]

        elif validated_data["batting_first"]=="team_1" and validated_data["team_2_score"]>validated_data["team_1_score"] and  validated_data["team_2_wicket"]<10:
            winner=series.team_2
            loser=series.team_1
            result_type="wicket"
            won_by=10-validated_data["team_2_wicket"]

        elif validated_data["batting_first"]=="team_2" and validated_data["team_1_score"]>validated_data["team_2_score"] and  validated_data["team_1_wicket"]<10:
            winner=series.team_1
            loser=series.team_2
            result_type="wicket"
            won_by=10-validated_data["team_1_wicket"]

        else:
            winner=None
            loser=None
            result_type="tie"
            won_by=0

        return international_match_model.objects.create(**validated_data,
                                                        winner=winner,
                                                        loser=loser,
                                                        result_type=result_type,
                                                        won_by=won_by
                                                        )

    def update(self,instances,validated_data):
        series = instances.match_id.series_number
        batting_first=validated_data.get("batting_first",instances.batting_first)
        team_1_score=validated_data.get("team_1_score",instances.team_1_score)
        team_2_score=validated_data.get("team_2_score",instances.team_2_score)
        team_1_wicket=validated_data.get("team_1_wicket",instances.team_1_wicket)
        team_2_wicket=validated_data.get("team_2_wicket",instances.team_2_wicket)

        for field,value in validated_data.items():
            setattr(instances,field,value)

        if batting_first=="team_1" and team_1_score>team_2_score:
            instances.winner=series.team_1
            instances.loser=series.team_2
            instances.result_type="run"
            instances.won_by=team_1_score-team_2_score

        elif batting_first=="team_2" and team_2_score>team_1_score:
            instances.winner=series.team_2
            instances.loser=series.team_1
            instances.result_type="run"
            instances.won_by=team_2_score-team_1_score

        elif batting_first=="team_1" and team_2_score>team_1_score and team_2_wicket<10:
            instances.winner=series.team_2
            instances.loser=series.team_1
            instances.result_type="wicket"
            instances.won_by=10-team_2_wicket

        elif batting_first=="team_2" and team_1_score>team_2_score and team_1_wicket<10:
            instances.winner=series.team_1
            instances.loser=series.team_2
            instances.result_type="wicket"
            instances.won_by=10-team_1_wicket

        else:
            instances.winner=None
            instances.loser=None
            instances.result_type="tie"
            instances.won_by=0
        instances.save()
        return instances


class international_series_result_serializer(serializers.ModelSerializer):
    class Meta:
        model=international_series_result_model
        fields="__all__"
        read_only_fields=["series_winner","series_loser","series_result"]


class team_stat_serializer(serializers.ModelSerializer):
    class Meta:
        model=team_stats
        fields="__all__"