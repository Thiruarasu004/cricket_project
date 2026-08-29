from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator

# Create your models here.
class team_model(models.Model):
    country=models.CharField(max_length=20,unique=True)

    def __str__(self):
        return self.country

class international_series_announcement_model(models.Model):
    total_matches=models.PositiveIntegerField(
        choices=[(3, "3 Matches"),(5, "5 Matches"),]
    )
    team_1=models.ForeignKey(
        team_model,
        on_delete=models.CASCADE,
        related_name="series_announcement_team_1"
    )
    team_2=models.ForeignKey(
        team_model,
        on_delete=models.CASCADE,
        related_name="series_announcement_team_2"
    )
    start_date=models.DateField()
    end_date=models.DateField()

    def __str__(self):
        return f"{self.team_1} v/s {self.team_2}"

class international_match_announcement_model(models.Model):
    series_number=models.ForeignKey(
        international_series_announcement_model,
        on_delete=models.CASCADE,
        related_name="match_announcement_series"
    )
    match_number=models.PositiveIntegerField(
        validators=[MinValueValidator(1),MaxValueValidator(5)]
    )
    match_team=models.CharField(max_length=30)
    match_date=models.DateField()
    location=models.CharField(max_length=20)

    def __str__(self):
        return f"{self.match_number} | {self.series_number.team_1} v/s {self.series_number.team_2}"

class international_match_model(models.Model):
    match_id=models.OneToOneField(
        international_match_announcement_model,
        on_delete=models.CASCADE,
        related_name="match_identification")
    batting_first = models.CharField(
        max_length=10, choices=[("team_1", "Team 1"),("team_2", "Team 2"),]
    )
    team_1_score=models.PositiveIntegerField(default=0)
    team_1_wicket=models.PositiveIntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(10)]
    )
    team_1_ball_faced=models.PositiveIntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(300)]
    )
    team_2_score=models.PositiveIntegerField(default=0)
    team_2_wicket=models.PositiveIntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(10)]
    )
    team_2_ball_faced=models.PositiveIntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(300)]
    )
    winner=models.ForeignKey(
        "team_model",
        on_delete=models.CASCADE,
        related_name="winner_team",
        null=True,
        blank=True
    )
    loser=models.ForeignKey(
        "team_model",
        on_delete=models.CASCADE,
        related_name="loser_team",
        null=True,
        blank=True
    )
    result_type=models.CharField(
        max_length=10,choices=[("run", "Run"),("wicket", "Wicket"), ("tie", "Tie"),]
    )
    won_by=models.PositiveBigIntegerField(default=0)
    man_of_the_match=models.CharField(max_length=20)

    def __str__(self):
        return f"{self.match_id.series_number} - Match {self.match_id.match_number}"

class international_series_result_model(models.Model):
    series_number = models.OneToOneField(
        international_series_announcement_model,
        on_delete=models.CASCADE,
        related_name="series_result"
    )
    series_winner = models.ForeignKey(
        team_model,
        on_delete=models.CASCADE,
        related_name="series_result_winner",
        null=True,
        blank=True
    )
    series_loser = models.ForeignKey(
        team_model,
        on_delete=models.CASCADE,
        related_name="series_result_loser", 
        null=True,
        blank=True
    )
    series_result = models.CharField(max_length=30)

    def __str__(self):
        if self.series_winner:
            return f"{self.series_winner} won by {self.series_result}"
        return self.series_result
    
class team_stats(models.Model):
    country=models.OneToOneField(
        "team_model",
        on_delete=models.CASCADE,
        related_name="team"
    )
    match_played=models.PositiveIntegerField(default=0)
    win=models.PositiveIntegerField(default=0)
    loss=models.PositiveIntegerField(default=0)
    draw=models.PositiveIntegerField(default=0)
    win_percent=models.FloatField(default=0)
    loss_percent=models.FloatField(default=0)
    series_played=models.PositiveIntegerField(default=0)
    series_won=models.PositiveIntegerField(default=0)
    series_loss=models.PositiveIntegerField(default=0)
    team_updated_score=models.FloatField(default=0)
    rating=models.FloatField(default=500)

    def __str__(self):
        return str(self.country)
