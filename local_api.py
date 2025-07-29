from flask import Flask, jsonify, request
import os
import json
from pathlib import Path

app = Flask(__name__)

# Your actual project paths
PROJECT_ROOT = Path(r"C:\Users\talZ\Desktop\AI Automation")
SLICE1_PATH = PROJECT_ROOT / "app" / "src"  # Where naming_generator.py is located
ASSETS_PATH = PROJECT_ROOT / "Assets" / "Videos"  # Where connectors and quiz_outro are

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running", "message": "Local API is active"})

@app.route('/project-structure', methods=['GET'])
def get_project_structure():
    """Show your project folder structure"""
    structure = {}
    
    # Map your key directories
    if SLICE1_PATH.exists():
        structure['slice1_src'] = [f.name for f in SLICE1_PATH.iterdir() if f.is_file()]
    
    if ASSETS_PATH.exists():
        structure['assets'] = {}
        
        # Check for connectors folder
        connectors_path = ASSETS_PATH / "connectors"
        if connectors_path.exists():
            structure['assets']['connectors'] = [f.name for f in connectors_path.iterdir()]
        
        # Check for quiz_outro folder
        quiz_outro_path = ASSETS_PATH / "quiz_outro"
        if quiz_outro_path.exists():
            structure['assets']['quiz_outro'] = [f.name for f in quiz_outro_path.iterdir()]
    
    return jsonify(structure)

@app.route('/naming-logic', methods=['GET'])
def get_naming_logic():
    """Show your naming conventions from Slice 1"""
    try:
        # Read your naming_generator.py from the correct location
        naming_file = SLICE1_PATH / "naming_generator.py"
        if naming_file.exists():
            with open(naming_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({"naming_code": content, "file_path": str(naming_file)})
        else:
            # List all Python files in the directory to help debug
            py_files = [f.name for f in SLICE1_PATH.iterdir() if f.suffix == '.py']
            return jsonify({
                "error": "naming_generator.py not found", 
                "searched_path": str(naming_file),
                "available_py_files": py_files
            })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/file-paths', methods=['GET'])
def get_file_paths():
    """Show local paths for assets"""
    connectors_path = ASSETS_PATH / "connectors"
    quiz_outro_path = ASSETS_PATH / "quiz_outro"
    
    # Build the base paths dictionary
    paths = {
        "connectors": str(connectors_path) if connectors_path.exists() else "Not found",
        "quiz_outros": str(quiz_outro_path) if quiz_outro_path.exists() else "Not found",
        "output_folder": str(PROJECT_ROOT / "output"),
        "temp_folder": str(PROJECT_ROOT / "temp"),
        "assets_base": str(ASSETS_PATH),
        "slice1_src": str(SLICE1_PATH)
    }
    
    # Create a separate dictionary for existence checks to avoid modifying during iteration
    existence_checks = {}
    for key, path in paths.items():
        if path != "Not found":
            exists = Path(path).exists()
            existence_checks[f"{key}_exists"] = exists
    
    # Combine both dictionaries
    result = {**paths, **existence_checks}
    
    return jsonify(result)

@app.route('/list-directory', methods=['GET'])
def list_directory():
    """Debug endpoint to see what's actually in your directories"""
    try:
        result = {}
        
        # Check Assets/Videos directory
        if ASSETS_PATH.exists():
            result['assets_videos'] = [f.name for f in ASSETS_PATH.iterdir()]
        
        # Check if connectors and quiz_outro exist
        connectors_path = ASSETS_PATH / "connectors"
        quiz_outro_path = ASSETS_PATH / "quiz_outro"
        
        result['connectors_exists'] = connectors_path.exists()
        result['quiz_outro_exists'] = quiz_outro_path.exists()
        
        if connectors_path.exists():
            result['connectors_files'] = [f.name for f in connectors_path.iterdir()]
        
        if quiz_outro_path.exists():
            result['quiz_outro_files'] = [f.name for f in quiz_outro_path.iterdir()]
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/process-video', methods=['POST'])
def process_video():
    """Trigger your existing stitcher"""
    data = request.json
    
    # This would call your existing stitcher code
    # For now, just return what we would do
    return jsonify({
        "status": "ready",
        "would_process": data,
        "message": "Video processing endpoint ready - will integrate with your stitcher"
    })

if __name__ == '__main__':
    print(f"Starting local API server...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Slice1 source: {SLICE1_PATH}")
    print(f"Assets path: {ASSETS_PATH}")
    print(f"Access at: http://localhost:5000")
    
    # Check if paths exist on startup
    print(f"Slice1 path exists: {SLICE1_PATH.exists()}")
    print(f"Assets path exists: {ASSETS_PATH.exists()}")
    print(f"Connectors path exists: {(ASSETS_PATH / 'connectors').exists()}")
    print(f"Quiz outro path exists: {(ASSETS_PATH / 'quiz_outro').exists()}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
