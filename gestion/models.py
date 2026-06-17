from django.contrib.gis.db import models
from django.contrib.auth.models import User


class Caveau(models.Model):
    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('reserve', 'Réservé'),
        ('occupe', 'Occupé'),
        ('non_exploitable', 'Non exploitable'),
    ]

    numero = models.CharField(max_length=20, unique=True)
    section = models.CharField(max_length=50)
    bloc = models.CharField(max_length=50)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='disponible')
    localisation = models.PointField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Caveau {self.numero} - {self.statut}"


class Defunt(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    date_deces = models.DateField()
    caveau = models.ForeignKey(Caveau, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Reservation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('annulee', 'Annulée'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE)
    caveau = models.ForeignKey(Caveau, on_delete=models.CASCADE)
    defunt = models.ForeignKey(Defunt, on_delete=models.SET_NULL, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_reservation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réservation {self.id} - {self.statut}"
    
class Concession(models.Model):
    TYPE_CHOICES = [
        ('temporaire', 'Temporaire'),
        ('perpetuelle', 'Perpétuelle'),
    ]
    
    caveau = models.ForeignKey(Caveau, on_delete=models.CASCADE)
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    type_concession = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    renouvele = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Concession {self.id} - {self.type_concession}"


class Exhumation(models.Model):
    STATUT_CHOICES = [
        ('demande', 'Demande'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
    ]

    caveau = models.ForeignKey(Caveau, on_delete=models.CASCADE)
    defunt = models.ForeignKey(Defunt, on_delete=models.CASCADE)
    demandeur = models.ForeignKey(User, on_delete=models.CASCADE)
    motif = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='demande')
    date_demande = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Exhumation {self.id} - {self.statut}"    