from django.db import models
from django.contrib.auth.models import User
# TODO: main menu: make it stylish and set some program logic
# TODO: db: Extended user info - Foreign key on User db + chess games stuff - statistics and history.
# TODO: chess: match history - save it and store it.


class SavedGame(models.Model):
    player_color = models.TextField(max_length=100, null=True)
    turns_history = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="current_user_id")
    enemy_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="enemy_user_id")
    result = models.TextField(max_length=100, null=True)
    mode = models.TextField(max_length=100, null=True)


