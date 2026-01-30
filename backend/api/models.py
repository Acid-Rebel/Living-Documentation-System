from django.db import models
import uuid
import os

def project_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/projects/<project_name>/<commit_hash>.<ext>
    ext = filename.split('.')[-1]
    return f'projects/{instance.project.name}/{instance.commit_hash}.{ext}'

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    repo_url = models.CharField(max_length=500)

    webhook_secret = models.UUIDField(default=uuid.uuid4, editable=False)
    last_commit_hash = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DiagramVersion(models.Model):
    project = models.ForeignKey(Project, related_name='diagrams', on_delete=models.CASCADE)
    commit_hash = models.CharField(max_length=40)
    commit_message = models.TextField(blank=True)
    author = models.CharField(max_length=255, blank=True)
    image_file = models.ImageField(upload_to=project_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.name} - {self.commit_hash}"


def diagram_image_path(instance, filename):
    # projects/<project_name>/<commit_hash>/<filename>
    return f'projects/{instance.version.project.name}/{instance.version.commit_hash}/{filename}'

class DiagramImage(models.Model):
    version = models.ForeignKey(DiagramVersion, related_name='images', on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to=diagram_image_path)
    diagram_type = models.CharField(max_length=50) # 'class_global', 'class_module', 'call', 'dependency', 'api'
    description = models.CharField(max_length=255) # e.g. "Global Class Diagram", "Module: utils"
    
    def __str__(self):
        return f"{self.version} - {self.description}"
