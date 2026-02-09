from rest_framework import serializers
from .models import Project, DiagramVersion, DiagramImage

class DiagramImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagramImage
        fields = ['id', 'image_file', 'diagram_type', 'description']

class DiagramVersionSerializer(serializers.ModelSerializer):
    images = DiagramImageSerializer(many=True, read_only=True)
    class Meta:
        model = DiagramVersion
        fields = ['id', 'commit_hash', 'commit_message', 'author', 'image_file', 'readme_content', 'summary_content', 'created_at', 'images']

class ProjectSerializer(serializers.ModelSerializer):
    latest_diagram = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = ['id', 'name', 'repo_url', 'webhook_secret', 'created_at', 'latest_diagram']
        read_only_fields = ['id', 'webhook_secret', 'created_at']
    
    def get_latest_diagram(self, obj):
        latest = obj.diagrams.first()
        if latest:
            return DiagramVersionSerializer(latest).data
        return None

class ProjectDetailSerializer(ProjectSerializer):
    diagrams = DiagramVersionSerializer(many=True, read_only=True)
    
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['diagrams']
