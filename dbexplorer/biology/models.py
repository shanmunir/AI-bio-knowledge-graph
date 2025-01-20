from django.db import models

class Species(models.Model):
    specie_name = models.CharField(max_length=100)  # Adjust according to your table schema

    class Meta:
        db_table = 'species'

    def __str__(self):
        return self.specie_name
