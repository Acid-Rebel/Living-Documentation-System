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
import stat
import threading

from .models import Project, DiagramVersion
from .serializers import ProjectSerializer, ProjectDetailSerializer, DiagramVersionSerializer
from diagram_generator.generate_repo_diagrams import generate_repo_diagrams

# Lock manager for project synchronization
_project_locks = {}
_global_lock = threading.Lock()

def get_project_lock(project_id):
    """
    Returns a threading.Lock for the specific project ID.
    Exceptions safe.
    """
    with _global_lock:
        if project_id not in _project_locks:
            _project_locks[project_id] = threading.Lock()
        return _project_locks[project_id]



def remove_readonly_and_retry(func, path, exc_info):
    """
    Error handler for Windows file permission issues.
    Makes files writable before deletion.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

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

    @action(detail=True, methods=['get'])
    def api_summary(self, request, pk=None):
        """Generates and returns a PDF summary of the API."""
        project = self.get_object()
        try:
            # 1. Setup Temp Dir & Clone
            temp_dir = os.path.join(settings.BASE_DIR, f"_temp_api_{uuid.uuid4()}")
            from diagram_generator.generate_repo_diagrams import clone_repo
            clone_repo(project.repo_url, temp_dir)
            
            # 2. Generate API Markdown
            api_key = os.environ.get("GEMINI_API_KEY") or "AIzaSyChmVigeUutJFexLHs5n_OCHiDlxOYkgS8"
            from .api_doc_generator import ApiDocGenerator
            generator = ApiDocGenerator(temp_dir, api_key)
            markdown_content = generator.generate_api_docs()
            
            # 3. Convert to PDF
            from .pdf_service import convert_markdown_to_pdf
            pdf_filename = f"{project.name}_api_summary.pdf"
            pdf_path = os.path.join(temp_dir, pdf_filename)
            
            success = convert_markdown_to_pdf(markdown_content, pdf_path)
            
            if not success or not os.path.exists(pdf_path):
                 return Response({"error": "PDF generation failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                 
            # 4. Return File Response
            from django.http import FileResponse
            # Note: We open securely, but we need to ensure it's not deleted before streaming finishes.
            # FileResponse usually handles file handle closure. 
            # However, prompt cleanup of temp_dir is tricky with FileResponse streaming.
            # For simplicity in this context, we will read into memory or rely on OS/cleanup later, 
            # BUT efficient way is to read content and delete file.
            
            f = open(pdf_path, 'rb')
            response = FileResponse(f, as_attachment=True, filename=pdf_filename)
            
            # Hook to clean up file after response closed? 
            # Django doesn't natively support "delete after send" easily without subclassing.
            # We will use a threading timer or simplified cleanup for now (or let OS/cron handle temp).
            # BETTER: Read into IOBytes and cleanup immediately.
            
            content_bytes = f.read()
            f.close()
            # Cleanup immediately
            shutil.rmtree(temp_dir, onerror=remove_readonly_and_retry)
            
            from django.http import HttpResponse
            response = HttpResponse(content_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
            return response
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .models import Project, DiagramVersion, DiagramImage # Ensure DiagramImage imported if not already

def process_and_save_diagram(project, commit_hash, commit_message, author):
    # Acquire lock for this project to ensure sequential processing
    # If an update is running (auto or manual), this will wait (queue).
    lock = get_project_lock(project.id)
    
    with lock:
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
            shutil.rmtree(output_dir, onerror=remove_readonly_and_retry)
            
        # 7. Generate README
        try:
             # Cloning again for README might be redundant if we could reuse output_dir, 
             # but output_dir was from diagram_generator which might not be a full clone or cleaned up.
             # Ideally, we should do this BEFORE cleanup of output_dir if output_dir contains the full repo.
             # However, generate_repo_diagrams returns the path to the *output* of diagrams, not necessarily the repo source.
             # So we will clone separately for now to be safe and modular, or better, implement a dedicated service function.
             
             # For MVP, let's implement the logic inline or call a helper.
             # We need the repo source code. 
             # Let's clone to a temp dir for README generation.
             
             temp_readme_dir = os.path.join(settings.BASE_DIR, f"_temp_readme_{uuid.uuid4()}")
             from diagram_generator.generate_repo_diagrams import clone_repo # Reuse clone function
             clone_repo(project.repo_url, temp_readme_dir)
             
             # API Key
             api_key = os.environ.get("GEMINI_API_KEY") or "AIzaSyChmVigeUutJFexLHs5n_OCHiDlxOYkgS8" # Fallback/Hardcoded
             
             # Generate
             from readme_manager.generator import ReadmeGenerator
             generator = ReadmeGenerator(temp_readme_dir, api_key)
             
             # We want the content string, not just a file. 
             # The current generator.render writes to file. 
             # We can use generator.generate_content() and rendering logic manually, or let it render to file and read it back.
             readme_out_path = os.path.join(temp_readme_dir, "GENERATED_README.md")
             generator.render(readme_out_path)
             
             if os.path.exists(readme_out_path):
                 with open(readme_out_path, 'r', encoding='utf-8') as f:
                     version.readme_content = f.read()
                 version.save()
                 
        except Exception as e:
            print(f"README generation failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
             if os.path.exists(temp_readme_dir):
                 try:
                    shutil.rmtree(temp_readme_dir, onerror=remove_readonly_and_retry)
                 except: pass

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
