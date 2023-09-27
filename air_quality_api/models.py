from django.db import models
from django.contrib.auth.models import User

class GraphData(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name

class GraphValue(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    graph_data = models.ForeignKey(GraphData, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return super().__str__()