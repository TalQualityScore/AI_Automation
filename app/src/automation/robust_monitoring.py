# app/src/automation/robust_monitoring.py
import time
import threading
from dataclasses import dataclass
from typing import Optional, Callable, Any

@dataclass
class ProcessingStatus:
    step: str
    progress: float
    message: str
    start_time: float
    timeout_seconds: int = 300

class ActivityTimeoutError(TimeoutError):
    """Custom exception for activity-based timeouts"""
    def __init__(self, operation_name: str, timeout: int):
        super().__init__(f"Operation '{operation_name}' timed out after {timeout} seconds of inactivity")
        self.operation_name = operation_name
        self.timeout = timeout

class RobustMonitoringSystem:
    """Handles activity-based monitoring and timeout detection"""
    
    def __init__(self):
        self.current_status: Optional[ProcessingStatus] = None
        self.timeout_monitor: Optional[threading.Thread] = None
        self.last_activity_time: Optional[float] = None
        self.activity_detected: bool = False
        self.monitor_active: bool = False
        self.timeout_occurred: bool = False
        self.timeout_exception: Optional[Exception] = None
    
    def execute_with_activity_monitoring(self, 
                                        operation_func: Callable, 
                                        operation_name: str, 
                                        no_activity_timeout: int = 300) -> Any:
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
        self.timeout_occurred = False
        self.timeout_exception = None
        
        # Start activity monitor in separate thread
        self.timeout_monitor = threading.Thread(
            target=self._monitor_activity, 
            args=(operation_name, no_activity_timeout), 
            daemon=True
        )
        self.timeout_monitor.start()
        
        try:
            result = operation_func()
            
            # Check if timeout occurred during execution
            if self.timeout_occurred and self.timeout_exception:
                raise self.timeout_exception
            
            # Properly stop monitoring
            self._stop_current_monitor()
            print(f"✅ {operation_name} completed successfully")
            return result
            
        except ActivityTimeoutError:
            # Re-raise timeout errors
            self._stop_current_monitor()
            raise
            
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
    
    def update_activity(self, message: Optional[str] = None):
        """Call this to indicate activity is happening"""
        if self.monitor_active:
            self.last_activity_time = time.time()
            self.activity_detected = True
            if message and self.current_status:
                self.current_status.message = message
    
    def _monitor_activity(self, operation_name: str, no_activity_timeout: int):
        """Monitor for activity in a separate thread"""
        
        print(f"📊 Activity monitor started for {operation_name}")
        last_check_time = time.time()
        
        while self.monitor_active:
            time.sleep(1)  # Check every second
            
            if not self.monitor_active:
                break
            
            current_time = time.time()
            time_since_activity = current_time - self.last_activity_time
            
            # Log periodic status
            if current_time - last_check_time >= 10:  # Every 10 seconds
                if self.activity_detected:
                    print(f"⏱️ {operation_name}: Activity detected, continuing...")
                    self.activity_detected = False
                last_check_time = current_time
            
            # Check for timeout
            if time_since_activity > no_activity_timeout:
                if self.monitor_active:  # Double-check we're still monitoring
                    print(f"\n⚠️ WARNING: No activity detected for {no_activity_timeout} seconds!")
                    print(f"🛑 Timing out operation: {operation_name}")
                    
                    # Set timeout flag and exception instead of hard exit
                    self.timeout_occurred = True
                    self.timeout_exception = ActivityTimeoutError(operation_name, no_activity_timeout)
                    self.monitor_active = False
                    break
        
        print(f"📊 Activity monitor stopped for {operation_name}")

# Global monitoring system instance
monitoring_system = RobustMonitoringSystem()