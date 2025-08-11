# app/src/automation/workflow_dialog/helpers.py - REFACTORED VERSION
"""
Workflow Dialog Helpers - Main Orchestrator
Now uses modular components for better organization
"""

from .helpers_modules import (
    AccountDetector,
    ConfirmationDataBuilder,
    TemplateGenerator,
    EstimationCalculator,
    ResultProcessor
)

def create_confirmation_data_from_orchestrator(card_data: dict, 
                                              processing_mode: str,
                                              project_info: dict,
                                              downloaded_videos: list,
                                              validation_issues: list = None):
    """
    Convert orchestrator data to ConfirmationData format
    Now simplified to ~30 lines using modular components
    """
    
    # Step 1: Detect account and platform
    detector = AccountDetector()
    account_code, platform_code, account_display, platform_display = \
        detector.detect_account_and_platform(card_data, project_info)
    
    # Step 2: Generate templates
    template_gen = TemplateGenerator()
    templates = template_gen.generate_templates(processing_mode, platform_display)
    
    # Step 3: Calculate estimates
    estimator = EstimationCalculator()
    estimated_time = estimator.calculate_time_estimate(
        len(downloaded_videos), processing_mode
    )
    
    # Step 4: Build confirmation data
    builder = ConfirmationDataBuilder()
    project_name = project_info.get('project_name', 'Unknown Project')
    
    confirmation_data = builder.build_confirmation_data(
        project_name=project_name,
        account_display=account_display,
        platform_display=platform_display,
        processing_mode=processing_mode,
        downloaded_videos=downloaded_videos,
        templates=templates,
        estimated_time=estimated_time,
        validation_issues=validation_issues
    )
    
    print(f"✅ Confirmation data created successfully")
    return confirmation_data


def create_processing_result_from_orchestrator(processed_files: list,
                                              start_time: float,
                                              output_folder: str,
                                              success: bool = True):
    """
    Create processing result from orchestrator data
    Now simplified using ResultProcessor
    """
    
    processor = ResultProcessor()
    
    result = processor.create_processing_result(
        processed_files=processed_files,
        start_time=start_time,
        output_folder=output_folder,
        success=success
    )
    
    print(f"✅ Processing result created: {result.duration}")
    return result


# Export the main functions
__all__ = [
    'create_confirmation_data_from_orchestrator',
    'create_processing_result_from_orchestrator'
]