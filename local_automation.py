# local_automation.py - AI Creative Automation Suite (Local Version)
import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Add your existing code to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'src'))

# Import your existing naming generator
try:
    from naming_generator import generate_project_folder_name, generate_output_name, get_image_description
    print("✅ Successfully imported your existing naming_generator.py")
except ImportError as e:
    print(f"❌ Could not import naming_generator.py: {e}")
    print("Make sure the file exists in app/src/naming_generator.py")

class LocalAutomation:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.assets_path = self.project_root / "Assets" / "Videos"
        self.connectors_path = self.assets_path / "connectors"
        self.quiz_outro_path = self.assets_path / "quiz_outro"
        
        # Load API keys from .env
        self.load_api_keys()
        
    def load_api_keys(self):
        """Load API keys from .env file"""
        env_path = self.project_root / ".env"
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value.strip('"')
            print("✅ Loaded API keys from .env file")
        else:
            print("❌ .env file not found. Please create it with your API keys.")
    
    def get_trello_card(self, card_id):
        """Get Trello card data"""
        # You'll need to add your Trello API credentials here
        print(f"📋 Getting Trello card: {card_id}")
        # This would connect to Trello API
        return {"name": "Test Card", "desc": "Test description"}
    
def parse_project_info(self, folder_name):
    """Parse project information from folder name"""
    print(f"🔍 Parsing folder name: {folder_name}")
    
    # Use regex to extract components - FIXED PATTERN
    import re
    pattern = r'^([A-Z]+)_(.+?)_AD_([A-Z]+)-(\d+)_(\d+x\d+)_(\d+)$'
    match = re.match(pattern, folder_name)
    
    if match:
        prefix, project_name, ad_type, test_number, dimensions, date = match.groups()
        return {
            "project_name": project_name.replace(' Ad', ''),
            "ad_type": ad_type,
            "test_name": test_number,
            "dimensions": dimensions,
            "date": date
        }
    return None
    
    def download_google_drive_files(self, folder_url):
        """Download files from Google Drive folder"""
        print(f"📥 Downloading files from: {folder_url}")
        # This would connect to Google Drive API
        return ["video1.mp4", "video2.mp4", "video3.mp4"]
    
    def process_videos(self, project_info, video_files):
        """Process videos using your existing stitcher"""
        print(f"🎬 Processing videos for project: {project_info['project_name']}")
        
        # Use your existing naming generator
        try:
            project_folder = generate_project_folder_name(
                project_info['project_name'],
                video_files[0] if video_files else "default.mp4",
                "Quiz"
            )
            print(f"📁 Generated project folder: {project_folder}")
            
            # Generate output names for each video
            output_names = []
            for i, video_file in enumerate(video_files, 1):
                output_name = generate_output_name(
                    project_info['project_name'],
                    video_file,
                    "Quiz",
                    f"description{i}",
                    i
                )
                output_names.append(output_name)
                print(f"📝 Generated filename {i}: {output_name}")
            
            return {
                "project_folder": project_folder,
                "output_names": output_names,
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Error processing videos: {e}")
            return {"status": "error", "error": str(e)}
    
    def log_to_google_sheets(self, project_info, processing_results):
        """Log results to Google Sheets"""
        print("📊 Logging to Google Sheets...")
        
        # Create rows for Google Sheets
        rows = []
        for i in range(3):  # 3 versions
            row = [
                f"GH {project_info['project_name']} {project_info['ad_type']} {project_info['test_name']} Quiz",
                f"v{i+1:02d}",
                f"New Ad from video_{i+1}.mp4 + blake connector + quiz",
                f"{project_info['project_name'].replace(' ', '_')}_v{i+1:02d}_Quiz"
            ]
            rows.append(row)
        
        # Add empty row
        rows.append(["", "", "", ""])
        
        print(f"📝 Created {len(rows)} rows for Google Sheets")
        return rows
    
    def run_automation(self, trello_card_id=None, google_drive_url=None):
        """Run the complete automation workflow"""
        print("🚀 Starting AI Creative Automation Suite (Local Version)")
        print("=" * 60)
        
        try:
            # Step 1: Get Trello card (if provided)
            if trello_card_id:
                card_data = self.get_trello_card(trello_card_id)
                print(f"✅ Retrieved Trello card: {card_data['name']}")
            
            # Step 2: Parse project information
            folder_name = "OO_Grocery Store Oils Ad_AD_VTD-12036_4x5_250721"
            project_info = self.parse_project_info(folder_name)
            if project_info:
                print(f"✅ Parsed project info: {project_info}")
            else:
                print("❌ Failed to parse project information")
                return
            
            # Step 3: Download Google Drive files (if URL provided)
            video_files = []
            if google_drive_url:
                video_files = self.download_google_drive_files(google_drive_url)
                print(f"✅ Downloaded {len(video_files)} video files")
            else:
                # Use sample files for testing
                video_files = ["sample_video_A.mp4", "sample_video_B.mp4", "sample_video_C.mp4"]
                print(f"📝 Using sample video files: {video_files}")
            
            # Step 4: Process videos
            processing_results = self.process_videos(project_info, video_files)
            if processing_results["status"] == "success":
                print("✅ Video processing completed successfully")
            else:
                print(f"❌ Video processing failed: {processing_results.get('error')}")
                return
            
            # Step 5: Log to Google Sheets
            sheet_rows = self.log_to_google_sheets(project_info, processing_results)
            print("✅ Google Sheets data prepared")
            
            # Step 6: Summary
            print("\n" + "=" * 60)
            print("🎉 AUTOMATION COMPLETED SUCCESSFULLY!")
            print(f"📁 Project Folder: {processing_results['project_folder']}")
            print(f"📝 Generated {len(processing_results['output_names'])} output files")
            print(f"📊 Prepared {len(sheet_rows)} rows for Google Sheets")
            print("=" * 60)
            
            return {
                "status": "success",
                "project_info": project_info,
                "processing_results": processing_results,
                "sheet_rows": sheet_rows
            }
            
        except Exception as e:
            print(f"❌ Automation failed: {e}")
            return {"status": "error", "error": str(e)}

# Main execution
if __name__ == "__main__":
    print("🤖 AI Creative Automation Suite - Local Version")
    print("Integrating with your existing Slice 1 tools...")
    
    # Create automation instance
    automation = LocalAutomation()
    
    # Run the automation
    result = automation.run_automation()
    
    if result["status"] == "success":
        print("\n✅ All done! Your automation is working locally!")
    else:
        print(f"\n❌ Automation failed: {result.get('error')}")# local_automation.py - AI Creative Automation Suite (Local Version)
import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Add your existing code to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'src'))

# Import your existing naming generator
try:
    from naming_generator import generate_project_folder_name, generate_output_name, get_image_description
    print("✅ Successfully imported your existing naming_generator.py")
except ImportError as e:
    print(f"❌ Could not import naming_generator.py: {e}")
    print("Make sure the file exists in app/src/naming_generator.py")

class LocalAutomation:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.assets_path = self.project_root / "Assets" / "Videos"
        self.connectors_path = self.assets_path / "connectors"
        self.quiz_outro_path = self.assets_path / "quiz_outro"
        
        # Load API keys from .env
        self.load_api_keys()
        
    def load_api_keys(self):
        """Load API keys from .env file"""
        env_path = self.project_root / ".env"
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value.strip('"')
            print("✅ Loaded API keys from .env file")
        else:
            print("❌ .env file not found. Please create it with your API keys.")
    
    def get_trello_card(self, card_id):
        """Get Trello card data"""
        # You'll need to add your Trello API credentials here
        print(f"📋 Getting Trello card: {card_id}")
        # This would connect to Trello API
        return {"name": "Test Card", "desc": "Test description"}
    
    def parse_project_info(self, folder_name):
        """Parse project information from folder name"""
        print(f"🔍 Parsing folder name: {folder_name}")
        
        # Use regex to extract components
        import re
        pattern = r'^([A-Z]+)_(.+?)_AD_([A-Z]+)-(\\d+)_(\\d+x\\d+)_(\\d+)$'
        match = re.match(pattern, folder_name)
        
        if match:
            prefix, project_name, ad_type, test_number, dimensions, date = match.groups()
            return {
                "project_name": project_name.replace(' Ad', ''),
                "ad_type": ad_type,
                "test_name": test_number,
                "dimensions": dimensions,
                "date": date
            }
        return None
    
    def download_google_drive_files(self, folder_url):
        """Download files from Google Drive folder"""
        print(f"📥 Downloading files from: {folder_url}")
        # This would connect to Google Drive API
        return ["video1.mp4", "video2.mp4", "video3.mp4"]
    
    def process_videos(self, project_info, video_files):
        """Process videos using your existing stitcher"""
        print(f"🎬 Processing videos for project: {project_info['project_name']}")
        
        # Use your existing naming generator
        try:
            project_folder = generate_project_folder_name(
                project_info['project_name'],
                video_files[0] if video_files else "default.mp4",
                "Quiz"
            )
            print(f"📁 Generated project folder: {project_folder}")
            
            # Generate output names for each video
            output_names = []
            for i, video_file in enumerate(video_files, 1):
                output_name = generate_output_name(
                    project_info['project_name'],
                    video_file,
                    "Quiz",
                    f"description{i}",
                    i
                )
                output_names.append(output_name)
                print(f"📝 Generated filename {i}: {output_name}")
            
            return {
                "project_folder": project_folder,
                "output_names": output_names,
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Error processing videos: {e}")
            return {"status": "error", "error": str(e)}
    
    def log_to_google_sheets(self, project_info, processing_results):
        """Log results to Google Sheets"""
        print("📊 Logging to Google Sheets...")
        
        # Create rows for Google Sheets
        rows = []
        for i in range(3):  # 3 versions
            row = [
                f"GH {project_info['project_name']} {project_info['ad_type']} {project_info['test_name']} Quiz",
                f"v{i+1:02d}",
                f"New Ad from video_{i+1}.mp4 + blake connector + quiz",
                f"{project_info['project_name'].replace(' ', '_')}_v{i+1:02d}_Quiz"
            ]
            rows.append(row)
        
        # Add empty row
        rows.append(["", "", "", ""])
        
        print(f"📝 Created {len(rows)} rows for Google Sheets")
        return rows
    
    def run_automation(self, trello_card_id=None, google_drive_url=None):
        """Run the complete automation workflow"""
        print("🚀 Starting AI Creative Automation Suite (Local Version)")
        print("=" * 60)
        
        try:
            # Step 1: Get Trello card (if provided)
            if trello_card_id:
                card_data = self.get_trello_card(trello_card_id)
                print(f"✅ Retrieved Trello card: {card_data['name']}")
            
            # Step 2: Parse project information
            folder_name = "OO_Grocery Store Oils Ad_AD_VTD-12036_4x5_250721"
            project_info = self.parse_project_info(folder_name)
            if project_info:
                print(f"✅ Parsed project info: {project_info}")
            else:
                print("❌ Failed to parse project information")
                return
            
            # Step 3: Download Google Drive files (if URL provided)
            video_files = []
            if google_drive_url:
                video_files = self.download_google_drive_files(google_drive_url)
                print(f"✅ Downloaded {len(video_files)} video files")
            else:
                # Use sample files for testing
                video_files = ["sample_video_A.mp4", "sample_video_B.mp4", "sample_video_C.mp4"]
                print(f"📝 Using sample video files: {video_files}")
            
            # Step 4: Process videos
            processing_results = self.process_videos(project_info, video_files)
            if processing_results["status"] == "success":
                print("✅ Video processing completed successfully")
            else:
                print(f"❌ Video processing failed: {processing_results.get('error')}")
                return
            
            # Step 5: Log to Google Sheets
            sheet_rows = self.log_to_google_sheets(project_info, processing_results)
            print("✅ Google Sheets data prepared")
            
            # Step 6: Summary
            print("\n" + "=" * 60)
            print("🎉 AUTOMATION COMPLETED SUCCESSFULLY!")
            print(f"📁 Project Folder: {processing_results['project_folder']}")
            print(f"📝 Generated {len(processing_results['output_names'])} output files")
            print(f"📊 Prepared {len(sheet_rows)} rows for Google Sheets")
            print("=" * 60)
            
            return {
                "status": "success",
                "project_info": project_info,
                "processing_results": processing_results,
                "sheet_rows": sheet_rows
            }
            
        except Exception as e:
            print(f"❌ Automation failed: {e}")
            return {"status": "error", "error": str(e)}

# Main execution
if __name__ == "__main__":
    print("🤖 AI Creative Automation Suite - Local Version")
    print("Integrating with your existing Slice 1 tools...")
    
    # Create automation instance
    automation = LocalAutomation()
    
    # Run the automation
    result = automation.run_automation()
    
    if result["status"] == "success":
        print("\n✅ All done! Your automation is working locally!")
    else:
        print(f"\n❌ Automation failed: {result.get('error')}")