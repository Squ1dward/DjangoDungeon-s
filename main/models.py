from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Race(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

class Location(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

class Character(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    genre = models.IntegerField()
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    origin = models.CharField(max_length=100)
    lastLocation =models.ForeignKey(Location, on_delete=models.CASCADE)
    skin = models.CharField(max_length=1024) #Wir können die Skins als bilder mit base64 hochladen, wenn ihr wollt

class UserCharacter(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    level = models.IntegerField()
    def __str__(self):
        return self.name

class EnchantmentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Enchantment(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.ForeignKey(EnchantmentType, on_delete=models.CASCADE)

class WeaponType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

class Weapon(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.ForeignKey(WeaponType, on_delete=models.CASCADE)
    maxLevel = models.IntegerField()

class Stats(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    maxLevel = models.IntegerField()

class CharacterStats(models.Model):
    id = models.BigIntegerField(primary_key=True)
    UserCharacter = models.ForeignKey(UserCharacter, on_delete=models.CASCADE)
    stats = models.ForeignKey(Stats, on_delete=models.CASCADE)
    level = models.IntegerField()

class CharacterWeapon(models.Model):
    id = models.BigIntegerField(primary_key=True)
    userCharacter = models.ForeignKey(UserCharacter, on_delete=models.CASCADE)
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)

