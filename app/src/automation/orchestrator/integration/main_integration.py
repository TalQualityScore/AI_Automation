# app/src/automation/orchestrator/integration/main_integration.py
"""
Main UI Integration Class - Entry point for all UI processing
Simplified from the original 500+ line file
"""

import time
from ...workflow_dialog.helpers import create_processing_result_from_orchestrator
from ..ui_preparation import UIPreparation
from ..ui_processing import UIProcessing
from ..ui_progress import UIProgress
from ..ui_sheets import UISheets

from .single_mode_processor import SingleModeProcessor
from .multi_mode_processor import MultiModeProcessor
from .error_handling import IntegrationErrorHandler

class UIIntegration:
    """Main UI Integration orchestrator - delegates to specialized modules"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        
        # Initialize existing specialized modules
        self.preparation = UIPreparation(orchestrator)
        self.processing = UIProcessing(orchestrator)
        self.progress = UIProgress(orchestrator)
        self.sheets = UISheets(orchestrator)
        
        # Initialize new modular processors
        self.single_mode = SingleModeProcessor(self)
        self.multi_mode = MultiModeProcessor(self)
        self.error_handler = IntegrationErrorHandler(self)
    
    def prepare_confirmation_data(self):
        """Prepare data for the confirmation dialog"""
        return self.preparation.prepare_confirmation_data()
    
    def ui_processing_callback(self, confirmation_data, progress_callback, use_transitions=True):
        """Main processing callback - orchestrates the workflow"""
        
        # Configure transitions
        from ...video_processor import configure_transitions
        configure_transitions(use_transitions)
        print(f"🎬 Processing with transitions: {'ENABLED' if use_transitions else 'DISABLED'}")
        
        try:
            self.orchestrator.start_time = time.time()
            
            # Check for multi-mode processing
            selected_modes = getattr(confirmation_data, 'selected_processing_modes', None)
            if selected_modes and len(selected_modes) > 1:
                print(f"🔄 Multi-mode processing detected: {selected_modes}")
                return self.multi_mode.process_multiple_modes(
                    confirmation_data, selected_modes, progress_callback, use_transitions
                )
            else:
                print(f"🔄 Single-mode processing")
                return self.single_mode.process_single_mode(
                    confirmation_data, progress_callback, use_transitions
                )
            
        except Exception as e:
            return self.error_handler.handle_processing_error(e)