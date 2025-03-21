from django.db import models
from django.contrib.auth.models import User

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
        """
        Calculate the total alcohol consumed in milliliters (ml).
        """
        beer_alc = self.beer * 17  # 17 ml per beer
        floco_alc = self.floco * 43  # 43 ml per floco shot
        rum_alc = self.rum * 9  # 9 ml per rum shot
        whiskey_alc = self.whiskey * 14  # 14 ml per whiskey shot
        vodka_alc = self.vodka * 18  # 18 ml per vodka shot
        tequila_alc = self.tequila * 23  # 23 ml per tequila shot

        total_alcohol = beer_alc + floco_alc + rum_alc + whiskey_alc + vodka_alc + tequila_alc
        return total_alcohol

    def calculate_xp(self):
        """
        Calculate the user's XP based on alcohol consumed, shotguns, snorkels, and thrown up.
        """
        total_alcohol = self.calculate_alcohol_drank()
        xp = (total_alcohol * 0.75) + (self.shotguns * 5) + (self.snorkels * 15) - (self.thrown_up * 40)
        return max(xp, 0)  # Ensure XP is not negative

    @property
    def xp_to_next_level(self):
        """
        Calculate the XP required to reach the next level.
        """
        if self.rank == "Bronze":
            return 600
        elif self.rank == "Silver":
            return 1300
        elif self.rank == "Gold":
            return 3200
        elif self.rank == "Platinum":
            return 7300
        elif self.rank == "Diamond":
            return 15000  # Updated to 15,000 XP for Steez
        else:
            return 0  # Steez has no next level

    @property
    def xp_percentage(self):
        """
        Calculate the percentage of XP progress towards the next level.
        """
        if self.rank == "Steez":
            return 100  # Steez is the highest rank
        if self.xp_to_next_level == 0:
            return 0  # Avoid division by zero
        return (self.xp / self.xp_to_next_level) * 100

    def update_rank(self):
        """
        Update the user's rank based on their XP.
        """
        if self.xp < 600:
            self.rank = "Bronze"
        elif self.xp < 1300:
            self.rank = "Silver"
        elif self.xp < 3200:
            self.rank = "Gold"
        elif self.xp < 7300:
            self.rank = "Platinum"
        elif self.xp < 15000:  # Updated to 15,000 XP for Diamond
            self.rank = "Diamond"
        else:
            self.rank = "Steez"  # Steez rank at 15,000 XP or higher

    def save(self, *args, **kwargs):
        """
        Automatically calculate XP and update rank before saving the profile.
        """
        self.xp = self.calculate_xp()
        self.update_rank()
        super().save(*args, **kwargs)


class FriendRequest(models.Model):
    from_user = models.ForeignKey(Profile, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(Profile, related_name='received_friend_requests', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.user.username} -> {self.to_user.user.username} ({'Accepted' if self.accepted else 'Pending'})"