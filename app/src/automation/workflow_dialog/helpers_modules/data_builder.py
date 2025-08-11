# app/src/automation/workflow_dialog/helpers_modules/data_builder.py
"""
Confirmation Data Builder Module
Builds the ConfirmationData object with all required information
"""

import os
from ...workflow_data_models import ConfirmationData, ValidationIssue

class ConfirmationDataBuilder:
    """Builds ConfirmationData objects from various inputs"""
    
    def build_confirmation_data(self, project_name, account_display, platform_display,
                               processing_mode, downloaded_videos, templates,
                               estimated_time, validation_issues=None):
        """
        Build the final ConfirmationData object
        
        Args:
            project_name: Name of the project
            account_display: Account display string (e.g., "OO (Olive Oil)")
            platform_display: Platform display string (e.g., "Facebook")
            processing_mode: Processing mode string
            downloaded_videos: List of downloaded video paths
            templates: List of template descriptions
            estimated_time: Estimated processing time
            validation_issues: Optional list of validation issues
            
        Returns:
            ConfirmationData object
        """
        
        # Determine output location
        output_location = self._build_output_location(
            project_name, processing_mode
        )
        
        # Build file list with sizes
        file_sizes = self._get_file_sizes(downloaded_videos)
        
        # Build issues list
        issues = self._build_issues_list(validation_issues)
        
        # Create the confirmation data
        return ConfirmationData(
            project_name=project_name,
            account=account_display,
            platform=platform_display,
            processing_mode=processing_mode.replace('_', ' ').upper(),
            client_videos=[os.path.basename(v) for v in downloaded_videos],
            templates_to_add=templates,
            output_location=output_location,
            estimated_time=estimated_time,
            issues=issues,
            file_sizes=file_sizes
        )
    
    def _build_output_location(self, project_name, processing_mode):
        """Build the output location string"""
        endpoint_type = "Quiz"  # Default
        
        if "svsl" in processing_mode:
            endpoint_type = "SVSL"
        elif "vsl" in processing_mode:
            endpoint_type = "VSL"
        
        # Note: ad_type and test_name would need to be passed in if available
        return f"GH {project_name} {endpoint_type}"
    
    def _get_file_sizes(self, video_paths):
        """Get file sizes for all videos"""
        file_sizes = []
        
        for video_path in video_paths:
            filename = os.path.basename(video_path)
            
            try:
                if os.path.exists(video_path):
                    size_mb = os.path.getsize(video_path) / (1024 * 1024)
                else:
                    size_mb = 150  # Default estimate
            except:
                size_mb = 150  # Default estimate
            
            file_sizes.append((filename, size_mb))
        
        return file_sizes
    
    def _build_issues_list(self, validation_issues):
        """Build the list of ValidationIssue objects"""
        issues = []
        
        if not validation_issues:
            return issues
        
        for issue in validation_issues:
            if isinstance(issue, ValidationIssue):
                issues.append(issue)
            elif isinstance(issue, dict):
                issues.append(ValidationIssue(
                    severity=issue.get('severity', 'info'),
                    message=issue.get('message', str(issue))
                ))
            else:
                issues.append(ValidationIssue(
                    severity='info',
                    message=str(issue)
                ))
        
        return issues