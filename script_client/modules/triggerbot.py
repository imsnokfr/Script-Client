#!/usr/bin/env python3
"""
Triggerbot Module for Script Client

Handles automatic attacking when targeting entities.
"""

import threading
import time
import sys
import os

# Add minescript to path
minescript_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'system', 'lib')
if minescript_path not in sys.path:
    sys.path.insert(0, minescript_path)

try:
    import minescript
except ImportError:
    print("Warning: minescript not found. Triggerbot will not work.")
    minescript = None

# Try to import win32api for mouse clicking
try:
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    print("Warning: win32api not found. Win32 mouse clicking will not work.")
    WIN32_AVAILABLE = False

class Triggerbot:
    def __init__(self):
        self.is_running = False
        self.delay = 0.1  # Default delay in seconds
        self.triggerbot_thread = None
        self.debug_logs = []
        self.max_logs = 50  # Keep last 50 logs
        self.attack_method = "minescript"  # "minescript" or "win32"
    
    def set_delay(self, delay):
        """Set the attack delay"""
        self.delay = delay
    
    def get_delay(self):
        """Get the current attack delay"""
        return self.delay
    
    def set_attack_method(self, method):
        """Set the attack method: 'minescript' or 'win32'"""
        if method in ["minescript", "win32"]:
            self.attack_method = method
            self.add_debug_log(f"Attack method set to: {method}")
        else:
            self.add_debug_log(f"Invalid attack method: {method}. Use 'minescript' or 'win32'")
    
    def get_attack_method(self):
        """Get the current attack method"""
        return self.attack_method
    
    def start(self):
        """Start the triggerbot"""
        if not self.is_running:
            self.is_running = True
            self.triggerbot_thread = threading.Thread(target=self._triggerbot_loop, daemon=True)
            self.triggerbot_thread.start()
            return True
        return False
    
    def stop(self):
        """Stop the triggerbot"""
        self.is_running = False
        return True
    
    def is_active(self):
        """Check if triggerbot is running"""
        return self.is_running
    
    def get_debug_logs(self):
        """Get recent debug logs"""
        return self.debug_logs.copy()
    
    def add_debug_log(self, message):
        """Add a debug log message"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.debug_logs.append(log_entry)
        
        # Keep only the last max_logs entries
        if len(self.debug_logs) > self.max_logs:
            self.debug_logs = self.debug_logs[-self.max_logs:]
        
        # Also log to chat if minescript is available
        if minescript:
            try:
                minescript.echo(log_entry)
            except:
                pass
    
    def _triggerbot_loop(self):
        """Main triggerbot logic"""
        self.add_debug_log("Triggerbot started")
        
        while self.is_running:
            try:
                if minescript:
                    # Check if player is targeting an entity
                    target = minescript.player_get_targeted_entity()
                    
                    if target:
                        # Debug: Log target info
                        target_name = getattr(target, 'name', 'Unknown')
                        target_type = getattr(target, 'type', 'Unknown')
                        target_info = f"Target: {target_name} (Type: {target_type})"
                        self.add_debug_log(target_info)
                        
                        # Log all available target attributes for debugging
                        attrs = [attr for attr in dir(target) if not attr.startswith('_')]
                        self.add_debug_log(f"Target attributes: {attrs}")
                        
                        # EntityData object has 'type' attribute, not dictionary access
                        if hasattr(target, 'type') and target.type in ['mob', 'player']:
                            # Attack the target using selected method
                            self.add_debug_log(f"Attacking {target.name} (delay: {self.delay}s, method: {self.attack_method})")
                            
                            if self.attack_method == "minescript":
                                # Use Minescript attack method
                                try:
                                    minescript.player_press_attack(True)  # Press attack
                                    time.sleep(0.05)  # Small delay
                                    minescript.player_press_attack(False)  # Release attack
                                    self.add_debug_log(f"Minescript attack sent to {target.name}")
                                except Exception as e:
                                    self.add_debug_log(f"Minescript attack failed: {e}")
                                    # Fallback to win32 API if available
                                    self._win32_attack()
                            elif self.attack_method == "win32":
                                # Use Win32 API attack method
                                self._win32_attack()
                            
                            time.sleep(self.delay)
                        else:
                            # Small delay when no valid target
                            time.sleep(0.01)
                    else:
                        # No target detected
                        time.sleep(0.01)
                else:
                    # Fallback when minescript is not available
                    self.add_debug_log("Minescript not available")
                    time.sleep(0.1)
                    
            except Exception as e:
                error_msg = f"Triggerbot error: {e}"
                self.add_debug_log(error_msg)
                time.sleep(0.1)
        
        self.add_debug_log("Triggerbot stopped")
    
    def _win32_attack(self):
        """Perform attack using win32 API (left mouse click)"""
        if WIN32_AVAILABLE:
            try:
                # Get current mouse position
                x, y = win32api.GetCursorPos()
                
                # Simulate left mouse button down and up
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                time.sleep(0.05)  # Small delay
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
                self.add_debug_log("Win32 attack executed (left click)")
            except Exception as e:
                self.add_debug_log(f"Win32 attack failed: {e}")
        else:
            self.add_debug_log("Win32 API not available")
