import threading
import time
import subprocess
import logging
import os
import shutil
from django.db import connection

# We use absolute imports to avoid issues in threads
from api.models import Project, DiagramVersion
from api.views import process_and_save_diagram

logger = logging.getLogger(__name__)

def get_latest_remote_commit(url):
    """Checks the latest commit on the remote repository without cloning."""
    try:
        # git ls-remote returns: <hash> <ref>
        output = subprocess.check_output(["git", "ls-remote", url, "HEAD"], text=True, timeout=15)
        if output:
            full_hash = output.split()[0]
            return full_hash[:7] # Normalize to 7 chars
    except Exception as e:
        logger.error(f"Error checking remote for {url}: {e}")
    return None

def polling_worker():
    """Background worker that polls projects for new commits."""
    print("[POLLING] Background polling service started thread.")
    
    # Wait a few seconds for the server to settle
    time.sleep(5)
    
    while True:
        try:
            # Close stale connections
            connection.close()
            
            projects = Project.objects.all()
            for project in projects:
                # Refresh from DB to get the absolute latest state (including last_commit_hash)
                project.refresh_from_db()
                
                # We only poll remote repositories (http/https/git)
                if project.repo_url.startswith("http") or project.repo_url.startswith("git@"):
                    latest_hash = get_latest_remote_commit(project.repo_url)
                    
                    if latest_hash and latest_hash != project.last_commit_hash:
                        print(f"[POLLING] NEW commit detected for {project.name}: {latest_hash}")
                        
                        try:
                            # Trigger processing
                            process_and_save_diagram(project, latest_hash, "Automatic Web Update", "GitHub Poller")
                            
                            # Note: project.last_commit_hash should be updated inside process_and_save_diagram
                            # but we refresh again to verify
                            project.refresh_from_db()
                            print(f"[POLLING] Successfully updated {project.name} to {project.last_commit_hash}")
                        except Exception as e:
                            logger.error(f"Failed to process polled update for {project.name}: {e}")
                
                time.sleep(1) # Small gap between projects
                
        except Exception as e:
            logger.error(f"Polling loop encountered error: {e}")
        
        # Poll every 20 seconds for faster feedback
        time.sleep(20)

def start_polling():
    """Starts the polling worker in a background thread."""
    thread = threading.Thread(target=polling_worker, daemon=True)
    thread.start()
