from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.files import File

import os
import shutil
import uuid

from .models import Project, DiagramVersion
from .serializers import ProjectSerializer, ProjectDetailSerializer, DiagramVersionSerializer
from diagram_generator.generate_repo_diagrams import generate_repo_diagrams

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        project = serializer.save()
        # Trigger initial diagram generation
        try:
           process_and_save_diagram(
               project=project,
               commit_hash='initial',
               commit_message='Initial Import',
               author='System'
           )
        except Exception as e:
            print(f"Initial generation failed: {e}")
            # We don't block creation, but we log it.

    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        project = self.get_object()
        try:
             # Trigger generation for 'latest'
             version = process_and_save_diagram(
                 project=project,
                 commit_hash='latest',
                 commit_message='Manual Refresh',
                 author='System'
             )
             serializer = DiagramVersionSerializer(version)
             return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        project = self.get_object()
        diagrams = project.diagrams.all()
        serializer = DiagramVersionSerializer(diagrams, many=True)
        return Response(serializer.data)

from .models import Project, DiagramVersion, DiagramImage # Ensure DiagramImage imported if not already

def process_and_save_diagram(project, commit_hash, commit_message, author):
    # 3. Generate Diagrams
    output_dir = generate_repo_diagrams(project.repo_url)
    
    # Attempt to extract actual commit hash (usually 7-char short hash)
    path_parts = output_dir.strip(os.sep).split(os.sep)
    if len(path_parts) >= 1:
        extracted_commit = path_parts[-1]
        # Prefer the short hash for database and UI consistency
        commit_hash = extracted_commit

    # 4. Locate the main diagram file
    main_image_name = "class_diagram_global.png"
    main_image_path = os.path.join(output_dir, main_image_name)
    
    if not os.path.exists(main_image_path):
            raise Exception("Diagram generation failed (main image not found)")

    # 5. Create DiagramVersion
    version = DiagramVersion(
        project=project,
        commit_hash=commit_hash,
        commit_message=commit_message,
        author=author
    )
    # Save main image to version (legacy/thumbnail use)
    with open(main_image_path, 'rb') as f:
        version.image_file.save(f"{commit_hash}.png", File(f), save=True)
    
    # 6. Scan and Save All Diagrams as DiagramImage
    for filename in os.listdir(output_dir):
        if not filename.endswith(".png"):
            continue
            
        file_path = os.path.join(output_dir, filename)
        
        # Determine Type and Description
        d_type = 'other'
        d_desc = filename
        
        if filename == "class_diagram_global.png":
            d_type = "class_global"
            d_desc = "Global Class Diagram"
        elif filename == "dependency_diagram.png":
            d_type = "dependency"
            d_desc = "Dependency Diagram"
        elif filename == "api_diagram.png":
            d_type = "api"
            d_desc = "API Diagram"
        elif filename.startswith("class_"):
            d_type = "class_module"
            # Extract module name class_foo_bar.png -> foo.bar
            mod = filename[6:-4].replace("_", ".") # simplistic replacement
            d_desc = f"Class Diagram: {mod}"
        elif filename.startswith("call_"):
            d_type = "call"
            mod = filename[5:-4].replace("_", ".")
            d_desc = f"Call Diagram: {mod}"

        # Create DiagramImage
        with open(file_path, 'rb') as f:
            di = DiagramImage(
                version=version,
                diagram_type=d_type,
                description=d_desc
            )
            di.image_file.save(filename, File(f), save=True)

    # Update project's last successfully processed hash
    project.last_commit_hash = commit_hash
    project.save()

    # Clean up temporary generation output
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    return version

class WebhookView(APIView):
    def post(self, request):
        data = request.data
        
        # 1. Identify Project
        project_id = data.get('project_id')
        repo_url = data.get('repository_url')
        
        project = None
        
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return Response({"error": "Invalid project_id"}, status=status.HTTP_404_NOT_FOUND)
        elif repo_url:
            project = Project.objects.filter(repo_url=repo_url).first()
        
        if not project:
             return Response({"error": "Project not found. Please register the repository first."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Extract Commit Metadata
        commit_hash = data.get('commit_sha') or data.get('after') or 'latest'
        # If commit not provided, use uuid as placeholder if just "latest"
        if commit_hash == 'latest':
             commit_hash = str(uuid.uuid4())[:8]
             
        commit_message = data.get('message', '')
        author = data.get('author', 'Unknown')

        try:
            version = process_and_save_diagram(project, commit_hash, commit_message, author)
            
            # Return success with info
            serializer = DiagramVersionSerializer(version)
            return Response({
                "message": "Diagram version created successfully",
                "version": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
