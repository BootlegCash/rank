from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Alcohol fields
    beer = models.IntegerField(default=0, help_text="Number of beers drank (17 ml alcohol per beer)")
    floco = models.IntegerField(default=0, help_text="Number of floco shots (43 ml alcohol per shot)")
    rum = models.IntegerField(default=0, help_text="Number of rum shots (9 ml alcohol per shot)")
    whiskey = models.IntegerField(default=0, help_text="Number of whiskey shots (14 ml alcohol per shot)")
    vodka = models.IntegerField(default=0, help_text="Number of vodka shots (18 ml alcohol per shot)")
    tequila = models.IntegerField(default=0, help_text="Number of tequila shots (23 ml alcohol per shot)")

    # Stats fields
    shotguns = models.IntegerField(default=0, help_text="Number of shotguns")
    snorkels = models.IntegerField(default=0, help_text="Number of snorkels")
    thrown_up = models.IntegerField(default=0, help_text="Times thrown up")
    xp = models.IntegerField(default=0, help_text="User XP")
    rank = models.CharField(max_length=50, default="Bronze", help_text="User rank")

    # Friends field
    friends = models.ManyToManyField('self', symmetrical=False, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def calculate_alcohol_drank(self):
        """Calculate total alcohol consumed in milliliters (ml)"""
        return (
            (self.beer * 17) + 
            (self.floco * 43) + 
            (self.rum * 9) + 
            (self.whiskey * 14) + 
            (self.vodka * 18) + 
            (self.tequila * 23)
        )

    def calculate_xp(self):
        """Calculate XP with bonuses and penalties"""
        alcohol_xp = self.calculate_alcohol_drank() * 0.75
        bonus_xp = (self.shotguns * 5) + (self.snorkels * 15)
        penalties = self.thrown_up * 40
        return max(round(alcohol_xp + bonus_xp - penalties, 2), 0)

    def update_rank(self):
        """Automatically update user rank based on XP"""
        RANKS = [
            (0, 'Bronze'),
            (600, 'Silver'),
            (1300, 'Gold'),
            (3200, 'Platinum'),
            (7300, 'Diamond'),
            (15000, 'Steez')
        ]
        for xp_threshold, rank in reversed(RANKS):
            if self.xp >= xp_threshold:
                self.rank = rank
                break

    def save(self, *args, **kwargs):
        """Auto-calculate XP and rank before saving"""
        self.xp = self.calculate_xp()
        self.update_rank()
        super().save(*args, **kwargs)

    @property
    def xp_to_next_level(self):
        """XP needed to reach next rank"""
        RANK_THRESHOLDS = {
            'Bronze': 600,
            'Silver': 1300,
            'Gold': 3200,
            'Platinum': 7300,
            'Diamond': 15000,
            'Steez': None
        }
        return RANK_THRESHOLDS.get(self.rank, 0)

    @property
    def xp_percentage(self):
        """Progress to next rank as percentage"""
        if self.rank == "Steez":
            return 100
        next_level = self.xp_to_next_level
        if not next_level:
            return 0
        return min(100, int((self.xp / next_level) * 100))

class FriendRequest(models.Model):
    from_user = models.ForeignKey(Profile, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(Profile, related_name='received_friend_requests', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['from_user', 'to_user']

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({'Accepted' if self.accepted else 'Pending'})"

    def accept(self):
        """Accept friend request and establish mutual friendship"""
        self.to_user.friends.add(self.from_user)
        self.from_user.friends.add(self.to_user)
        self.accepted = True
        self.save()

# Auto-create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class Post(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(Profile, related_name='liked_posts', blank=True)

    def __str__(self):
        return f"{self.user.user.username}: {self.content[:20]}..."

    class Meta:
        ordering = ['-created_at']