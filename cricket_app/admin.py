from django.contrib import admin
from cricket_app.models import (team_model,
                                international_match_announcement_model,
                                international_series_announcement_model,
                                international_match_model,
                                international_series_result_model,
                                team_stats,
                        )

admin.site.register(team_model)
admin.site.register(international_series_announcement_model)
admin.site.register(international_match_announcement_model)
admin.site.register(international_match_model)
admin.site.register(international_series_result_model)
admin.site.register(team_stats)
