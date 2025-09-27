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
        self.delay_min_ticks = 2  # Minimum delay in ticks (2 ticks = 0.1s)
        self.delay_max_ticks = 2  # Maximum delay in ticks (2 ticks = 0.1s)
        self.triggerbot_thread = None
        self.debug_logs = []
        self.max_logs = 50  # Keep last 50 logs
        self.attack_method = "minescript"  # "minescript" or "win32"
        self.weapon_only = False  # Only attack when holding a weapon
        self.allowed_weapons = set()  # Set of allowed weapon types
        self.range_min = 3.0  # Minimum attack range in blocks
        self.range_max = 3.0  # Maximum attack range in blocks
        self.miss_chance = 0.0  # Chance to miss on purpose (0.0-1.0)
        self.check_line_of_sight = True  # Check for obstacles between player and target
    
    def set_delay_range_ticks(self, delay_min_ticks, delay_max_ticks):
        """Set the attack delay range in ticks"""
        self.delay_min_ticks = delay_min_ticks
        self.delay_max_ticks = delay_max_ticks
    
    def get_delay_range_ticks(self):
        """Get the current delay range in ticks"""
        return self.delay_min_ticks, self.delay_max_ticks
    
    def get_random_delay_ticks(self):
        """Get a random delay in ticks within the range"""
        import random
        return random.randint(self.delay_min_ticks, self.delay_max_ticks)
    
    def ticks_to_seconds(self, ticks):
        """Convert ticks to seconds (20 ticks = 1 second)"""
        return ticks / 20.0
    
    def seconds_to_ticks(self, seconds):
        """Convert seconds to ticks (1 second = 20 ticks)"""
        return int(seconds * 20)
    
    
    def set_miss_chance(self, miss_chance):
        """Set the miss chance (0.0-1.0)"""
        self.miss_chance = max(0.0, min(1.0, miss_chance))
        self.add_debug_log(f"Miss chance set to: {self.miss_chance:.1%}")
    
    
    def set_line_of_sight_check(self, enabled):
        """Set whether to check line of sight"""
        self.check_line_of_sight = enabled
        self.add_debug_log(f"Line of sight check: {'enabled' if enabled else 'disabled'}")
    
    
    def should_miss(self):
        """Check if this attack should miss on purpose"""
        import random
        return random.random() < self.miss_chance
    
    
    def has_line_of_sight(self, player_pos, target_pos):
        """Check if there's a clear line of sight to the target"""
        try:
            if minescript:
                # Sample points along the line between player and target
                steps = 10  # Number of points to check
                dx = (target_pos[0] - player_pos[0]) / steps
                dy = (target_pos[1] - player_pos[1]) / steps
                dz = (target_pos[2] - player_pos[2]) / steps
                
                for i in range(1, steps):
                    check_x = player_pos[0] + (dx * i)
                    check_y = player_pos[1] + (dy * i)
                    check_z = player_pos[2] + (dz * i)
                    
                    # Check if there's a solid block at this position
                    block = minescript.getblock(check_x, check_y, check_z)
                    if block and block != "air" and block != "cave_air":
                        return False
                
                return True
        except Exception as e:
            self.add_debug_log(f"Line of sight check failed: {e}")
            return True  # Default to allowing attack if check fails
    
    
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
    
    def set_weapon_only(self, enabled):
        """Set whether to only attack when holding a weapon"""
        self.weapon_only = enabled
    
    def get_weapon_only(self):
        """Get whether weapon-only mode is enabled"""
        return self.weapon_only
    
    def set_allowed_weapons(self, weapons):
        """Set the allowed weapon types"""
        self.allowed_weapons = set(weapons)
    
    def get_allowed_weapons(self):
        """Get the allowed weapon types"""
        return list(self.allowed_weapons)
    
    def set_range_range(self, range_min, range_max):
        """Set the attack range range"""
        self.range_min = range_min
        self.range_max = range_max
    
    def get_range_range(self):
        """Get the current range range"""
        return self.range_min, self.range_max
    
    def get_random_range(self):
        """Get a random range within the range"""
        import random
        return random.uniform(self.range_min, self.range_max)
    
    def calculate_distance(self, pos1, pos2):
        """Calculate 3D distance between two positions"""
        if not pos1 or not pos2:
            return float('inf')
        
        try:
            # Handle different position formats
            if hasattr(pos1, 'x') and hasattr(pos1, 'y') and hasattr(pos1, 'z'):
                x1, y1, z1 = pos1.x, pos1.y, pos1.z
            elif isinstance(pos1, (list, tuple)) and len(pos1) >= 3:
                x1, y1, z1 = pos1[0], pos1[1], pos1[2]
            else:
                return float('inf')
            
            if hasattr(pos2, 'x') and hasattr(pos2, 'y') and hasattr(pos2, 'z'):
                x2, y2, z2 = pos2.x, pos2.y, pos2.z
            elif isinstance(pos2, (list, tuple)) and len(pos2) >= 3:
                x2, y2, z2 = pos2[0], pos2[1], pos2[2]
            else:
                return float('inf')
            
            # Calculate 3D distance
            dx = x2 - x1
            dy = y2 - y1
            dz = z2 - z1
            distance = (dx*dx + dy*dy + dz*dz) ** 0.5
            
            return distance
        except Exception as e:
            self.add_debug_log(f"Distance calculation failed: {e}")
            return float('inf')
    
    def is_holding_weapon(self):
        """Check if player is holding a weapon"""
        if not minescript:
            return True  # Assume weapon if minescript not available
        
        try:
            hand_items = minescript.player_hand_items()
            if not hand_items:
                return False
            
            # Check main hand and off hand
            for hand in [hand_items.main_hand, hand_items.off_hand]:
                if hand and hasattr(hand, 'item'):
                    item_name = hand.item.lower()
                    
                    # Check if it's a weapon
                    weapon_types = ['sword', 'axe', 'mace', 'trident', 'bow', 'crossbow']
                    if any(weapon in item_name for weapon in weapon_types):
                        # If we have specific weapon filters, check them
                        if self.allowed_weapons:
                            if any(weapon in item_name for weapon in self.allowed_weapons):
                                return True
                        else:
                            return True
            
            return False
        except Exception as e:
            self.add_debug_log(f"Weapon check failed: {e}")
            return True  # Default to allowing attack if check fails
    
    def start(self):
        """Start the triggerbot"""
        if not self.is_running:
            self.is_running = True
            self.triggerbot_thread = threading.Thread(target=self._triggerbot_loop, daemon=True)
            self.triggerbot_thread.start()
            
            # Test Minescript attack function
            if minescript:
                try:
                    self.add_debug_log("Testing Minescript attack function...")
                    minescript.player_press_attack(True)
                    time.sleep(0.1)
                    minescript.player_press_attack(False)
                    self.add_debug_log("Minescript attack test successful")
                except Exception as e:
                    self.add_debug_log(f"Minescript attack test failed: {e}")
            
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
                        # Check if it's a valid target (be more permissive)
                        target_type = getattr(target, 'type', 'unknown')
                        self.add_debug_log(f"Target type: {target_type}")
                        
                        # Attack any entity that's not the player themselves
                        if target_type != 'player' or (hasattr(target, 'name') and target.name != 'Player'):
                            # Check range requirement
                            try:
                                player_pos = minescript.player_position()
                                target_pos = getattr(target, 'position', None)
                                
                                if target_pos:
                                    distance = self.calculate_distance(player_pos, target_pos)
                                    max_range = self.get_random_range()
                                    self.add_debug_log(f"Distance to {target_name}: {distance:.2f} blocks (max: {max_range:.2f})")
                                    
                                    if distance > max_range:
                                        self.add_debug_log(f"Target {target_name} too far ({distance:.2f} > {max_range:.2f}) - skipping attack")
                                        delay_ticks = self.get_random_delay_ticks()
                                        time.sleep(self.ticks_to_seconds(delay_ticks))
                                        continue
                                    
                                    # Check line of sight (if enabled)
                                    if self.check_line_of_sight and not self.has_line_of_sight(player_pos, target_pos):
                                        self.add_debug_log(f"Target {target_name} blocked by obstacles - skipping attack")
                                        delay_ticks = self.get_random_delay_ticks()
                                        time.sleep(self.ticks_to_seconds(delay_ticks))
                                        continue
                                    
                                else:
                                    self.add_debug_log("Could not get target position - skipping range check")
                            except Exception as e:
                                self.add_debug_log(f"Range check failed: {e} - skipping range check")
                            
                            # Check weapon requirement
                            if self.weapon_only and not self.is_holding_weapon():
                                self.add_debug_log("No weapon detected - skipping attack")
                                delay_ticks = self.get_random_delay_ticks()
                                time.sleep(self.ticks_to_seconds(delay_ticks))
                                continue
                            
                            
                            # Check miss chance
                            if self.should_miss():
                                self.add_debug_log(f"Intentionally missing attack on {target_name} (miss chance: {self.miss_chance:.1%})")
                                delay_ticks = self.get_random_delay_ticks()
                                time.sleep(self.ticks_to_seconds(delay_ticks))
                                continue
                            
                            # Attack the target using selected method
                            current_delay_ticks = self.get_random_delay_ticks()
                            current_delay_seconds = self.ticks_to_seconds(current_delay_ticks)
                            hit_info = f"mode: {self.hit_mode}"
                            if self.can_crit():
                                hit_info += " (CRIT!)"
                            if self.is_sprinting():
                                hit_info += " (SPRINT!)"
                            
                            self.add_debug_log(f"Attacking {target_name} (delay: {current_delay_ticks} ticks / {current_delay_seconds:.3f}s, {hit_info}, method: {self.attack_method})")
                            
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
                            
                            time.sleep(current_delay_seconds)
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
