from diagram_generator.generate_repo_diagrams import generate_repo_diagrams

if __name__ == "__main__":
    # Change this repo URL to test different repositories
    generate_repo_diagrams(
        "https://github.com/psf/requests.git"
    )
