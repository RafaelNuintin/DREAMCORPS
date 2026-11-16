from django.db import models

class ParticipantSession(models.Model):
    STATUS_CHOICES = [
        ('ACCEPTABLE', 'ACCEPTABLE'),
        ('UNSTABLE', 'UNSTABLE'),
        ('REQUIRES REVIEW', 'REQUIRES REVIEW'),
        ('INTEGRATED', 'INTEGRATED'),
    ]

    player_name = models.CharField(max_length=64, default="SUBJECT_003")
    dsi = models.IntegerField(default=10000, help_text="Dream Stability Index")
    phase_reached = models.CharField(max_length=64, default="Phase I: The Bedroom")
    artifacts_collected = models.IntegerField(default=0)
    corruption_level = models.IntegerField(default=0, help_text="Layer Corruption percentage (0-100%)")
    entity_encounters = models.IntegerField(default=0)
    play_time_seconds = models.IntegerField(default=0)
    participant_status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='ACCEPTABLE')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-dsi', '-artifacts_collected', 'play_time_seconds']

    def calculate_status(self):
        """Avalia automaticamente o status do participante conforme regras da Dreamcorps™."""
        if self.corruption_level >= 80 or self.entity_encounters >= 5:
            return 'REQUIRES REVIEW'
        elif self.phase_reached.startswith("Phase V"):
            return 'INTEGRATED'
        elif self.corruption_level >= 45 or self.dsi < 5000:
            return 'UNSTABLE'
        return 'ACCEPTABLE'

    def save(self, *args, **kwargs):
        if not self.participant_status or self.participant_status == 'ACCEPTABLE':
            self.participant_status = self.calculate_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player_name} | DSI: {self.dsi} | Status: {self.participant_status}"
