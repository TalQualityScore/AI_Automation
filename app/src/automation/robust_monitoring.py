# app/src/automation/robust_monitoring.py
import time
import threading
import os
from dataclasses import dataclass

@dataclass
class ProcessingStatus:
    step: str
    progress: float
    message: str
    start_time: float
    timeout_seconds: int = 300

class RobustMonitoringSystem:
    """Handles activity-based monitoring and timeout detection"""
    
    def __init__(self):
        self.current_status = None
        self.timeout_monitor = None
        self.last_activity_time = None
        self.activity_detected = False
        self.monitor_active = False
    
    def execute_with_activity_monitoring(self, operation_func, operation_name, no_activity_timeout=300):
        """Execute operation with activity-based monitoring instead of simple timeout"""
        
        print(f"🔍 Starting {operation_name} with activity monitoring...")
        
        # Stop any previous monitor cleanly
        self._stop_current_monitor()
        
        # Set up new monitoring
        self.current_status = ProcessingStatus(
            step=operation_name,
            progress=0.0,
            message=f"Starting {operation_name}...",
            start_time=time.time(),
            timeout_seconds=no_activity_timeout
        )
        
        self.last_activity_time = time.time()
        self.activity_detected = False
        self.monitor_active = True
        
        # Start activity monitor in separate thread
        self.timeout_monitor = threading.Thread(
            target=self._monitor_activity, 
            args=(operation_name, no_activity_timeout), 
            daemon=True
        )
        self.timeout_monitor.start()
        
        try:
            result = operation_func()
            # Properly stop monitoring
            self._stop_current_monitor()
            print(f"✅ {operation_name} completed successfully")
            return result
            
        except Exception as e:
            # Properly stop monitoring on error
            self._stop_current_monitor()
            print(f"❌ {operation_name} failed: {str(e)}")
            raise e
    
    def _stop_current_monitor(self):
        """Cleanly stop the current monitoring thread"""
        if self.current_status:
            self.monitor_active = False
            self.current_status = None
            
        if self.timeout_monitor and self.timeout_monitor.is_alive():
            # Give the thread a moment to see the stop signal
            time.sleep(0.1)
            # Wait up to 2 seconds for clean shutdown
            self.timeout_monitor.join(timeout=2)
    
    def update_activity(self, message=None):
        """Call this to indicate activity is happening"""
        if self.monitor_active:
            self.last_activity_time = time.time()
            self.activity_detected = True
            if message and self.current_status:
                self.current_status.message = message
    
    def _monitor_activity(self, operation_name, no_activity_timeout):
        """Monitor for lack of activity (stuck operations)"""
        while self.monitor_active and self.current_status:
            current_time = time.time()
            elapsed_total = current_time - self.current_status.start_time
            time_since_activity = current_time - self.last_activity_time
            
            # Show progress every 30 seconds
            if int(elapsed_total) % 30 == 0 and elapsed_total > 0:
                if self.activity_detected:
                    print(f"⏳ {operation_name} active... ({elapsed_total:.0f}s total, last activity: {time_since_activity:.0f}s ago)")
                else:
                    print(f"⏳ {operation_name} running... ({elapsed_total:.0f}s elapsed)")
            
            # Only timeout if NO activity detected for the timeout period
            if time_since_activity > no_activity_timeout:
                print(f"\n⚠️ ACTIVITY TIMEOUT: {operation_name} stuck for {time_since_activity:.0f} seconds")
                print(f"   No activity detected - operation appears frozen")
                print(f"   This usually indicates:")
                print(f"   • Network connectivity issues")
                print(f"   • Invalid Google Drive links") 
                print(f"   • Missing or corrupted files")
                print(f"   • API service problems")
                print(f"   Please check your inputs and try again.")
                
                # Force stop the operation
                self.monitor_active = False
                self.current_status = None
                os._exit(1)  # Force terminate if stuck
            
            # Check every second, but break if monitoring was stopped
            for _ in range(10):  # Check 10 times per second for quicker response
                if not self.monitor_active or not self.current_status:
                    return
                time.sleep(0.1)