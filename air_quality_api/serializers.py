from rest_framework import serializers
from .models import GraphData, GraphValue

class GraphDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphData
        fields = ['id', 'name', 'graph_values']

    graph_values = serializers.SerializerMethodField()
    
    def get_graph_values(self, obj):
        graph_values = GraphValue.objects.filter(graph_data=obj)
        serializer = GraphValueSerializer(graph_values, many=True)
        return serializer.data



class GraphValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = GraphValue
        fields = ['id', 'value', 'date']
    
