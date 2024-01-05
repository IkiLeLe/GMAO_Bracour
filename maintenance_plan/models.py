import datetime

from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

# Create your models here.
class Lines (models.Model):
    name = models.CharField(max_length=7)
    installation_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    target = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        verbose_name_plural = "Lines"
    
    def __str__(self):
        return self.name


class Equipement (models.Model):
    serial_number = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=50)
    installation_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    manufacturer = models.CharField(max_length=50)
    efficience = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    lineId = models.ForeignKey(Lines, on_delete=models.DO_NOTHING) 
    
    def __str__(self):
        return self.serial_number
    
class Part(models.Model):
    part_name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.part_name}/{self.equipement}'
    
class Document(models.Model):
    document_name = models.CharField(max_length=50)
    upload = models.FileField(upload_to='documents/')
    equipement = models.ManyToManyField(Equipement, blank=True)
        
    def __str__(self):
        return self.document_name
class Contributor(models.Model):
    contributor_name = models.CharField(max_length=50)
    acronym = models.CharField(max_length=5)
    
    def __str__(self):
        return self.contributor_name
    

class Task (models.Model):
    operation = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    FREQUENCY_CHOICES = [
        ('Av', 'Avant production'),
        ('AP', 'Après production'),
        ('J', 'Journalier'),
        ('H', 'Hebdomadaire'),
        ('M', 'Mensuelle'),
        ('TM', 'Trimestrielle'),
        ('SM', 'Semestrielle'),
        ('A', 'Annuelle'),
        ('2A', 'Chaque 2 ans'),
        ('3A', 'Chaque 3 ans'),
        ('4A', 'Chaque 4 ans'),
        ('5A', 'Chaque 5 ans'),
        ('6A', 'Chaque 6 ans'),
        ('N/A', 'inconnue'),
        ]
    frequency = models.CharField(max_length=4,
                                 choices=FREQUENCY_CHOICES,
                                 default='Hebdomadaire', null=True, blank=True
                                 )
    MODE_CHOICES = [
        ('A', 'Arrêt'),
        ('M', 'Marche'),
        ('AJ', 'Ajustage'),
        ('CIP', 'CIP'),
        ('N/A', 'inconnue'),
    ]
    mode = models.CharField(max_length=5, choices=MODE_CHOICES, default='Marche/Arrêt', null=True, blank=True)
    level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    tools = models.CharField(max_length=255, null=True, blank=True)
    component = models.CharField(max_length=75)
    location = models.CharField(max_length=75)
    
    class Meta:
        abstract = True

class PreventiveTask(Task):
    criteria = models.CharField(max_length=255, null=True, blank=True)
    part = models.ForeignKey(Part, on_delete=models.DO_NOTHING)
    ison = models.ManyToManyField(Contributor, through='Contributors')

    def __str__(self):
        return self.operation
    
class CleaningTask(Task):
    aids = models.CharField(max_length=255, null=True, blank=True)
    part = models.ForeignKey(Part, on_delete=models.DO_NOTHING)
    ison = models.ManyToManyField(Contributor, through='Contributors')

    def __str__(self):
        return self.operation

class LubrificationTask(Task):
    lubrificant = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField()
    part = models.ForeignKey(Part, on_delete=models.DO_NOTHING)
    ison = models.ManyToManyField(Contributor, through='Contributors')

    def __str__(self):
        return self.operation

class Contributors(models.Model):
    person = models.ForeignKey(Contributor, on_delete=models.DO_NOTHING) 
    preventive_task = models.ForeignKey(PreventiveTask, on_delete=models.DO_NOTHING, blank=True, null=True)
    cleaning_task = models.ForeignKey(CleaningTask, on_delete=models.DO_NOTHING, blank=True, null=True)
    lubrication_task = models.ForeignKey(LubrificationTask, on_delete=models.DO_NOTHING, blank=True, null=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])