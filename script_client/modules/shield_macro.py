#!/usr/bin/env python3
"""
Shield Macro Module for Script Client

Automatically switches to axe and disables shield when looking at a player with a shield.
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
    print("Warning: minescript not found. Shield Macro will not work.")
    minescript = None

class ShieldMacro:
    def __init__(self):
        self.is_running = False
        self.delay_min_ticks = 2  # Minimum delay in ticks (2 ticks = 0.1s)
        self.delay_max_ticks = 2  # Maximum delay in ticks (2 ticks = 0.1s)
        self.macro_thread = None
        self.debug_logs = []
        self.max_logs = 50  # Keep last 50 logs
        self.enabled = False  # Whether the macro is enabled
        
    def set_delay_range_ticks(self, delay_min_ticks, delay_max_ticks):
        """Set the macro delay range in ticks"""
        self.delay_min_ticks = delay_min_ticks
        self.delay_max_ticks = delay_max_ticks
        self.add_debug_log(f"Delay range set to: {delay_min_ticks}-{delay_max_ticks} ticks")
    
    def get_delay_range_ticks(self):
        """Get the current delay range in ticks"""
        return (self.delay_min_ticks, self.delay_max_ticks)
    
    def get_random_delay_ticks(self):
        """Get a random delay within the range"""
        import random
        return random.randint(self.delay_min_ticks, self.delay_max_ticks)
    
    def ticks_to_seconds(self, ticks):
        """Convert ticks to seconds (20 ticks = 1 second)"""
        return ticks / 20.0
    
    def add_debug_log(self, message):
        """Add a debug log message"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.debug_logs.append(log_entry)
        
        # Keep only the last max_logs entries
        if len(self.debug_logs) > self.max_logs:
            self.debug_logs.pop(0)
    
    def get_debug_logs(self):
        """Get all debug logs"""
        return self.debug_logs.copy()
    
    def clear_debug_logs(self):
        """Clear all debug logs"""
        self.debug_logs.clear()
    
    def has_axe_in_inventory(self):
        """Check if player has an axe in their inventory"""
        try:
            if minescript:
                inventory = minescript.player_inventory()
                if inventory:
                    for item in inventory:
                        if item and 'id' in item:
                            item_id = item['id'].lower()
                            if 'axe' in item_id:
                                return True
        except Exception as e:
            self.add_debug_log(f"Inventory check failed: {e}")
        return False
    
    def find_axe_slot(self):
        """Find the slot number of the first axe in inventory"""
        try:
            if minescript:
                inventory = minescript.player_inventory()
                if inventory:
                    for i, item in enumerate(inventory):
                        if item and 'id' in item:
                            item_id = item['id'].lower()
                            if 'axe' in item_id:
                                return i
        except Exception as e:
            self.add_debug_log(f"Axe slot search failed: {e}")
        return -1
    
    def is_holding_shield(self):
        """Check if player is currently holding a shield"""
        try:
            if minescript:
                hand_items = minescript.player_hand_items()
                if hand_items and hasattr(hand_items, 'off_hand'):
                    off_hand_item = hand_items.off_hand
                    if off_hand_item and hasattr(off_hand_item, 'id'):
                        item_id = off_hand_item.id.lower()
                        return 'shield' in item_id
        except Exception as e:
            self.add_debug_log(f"Shield check failed: {e}")
        return False
    
    def is_target_player_with_shield(self):
        """Check if the targeted entity is a player holding a shield"""
        try:
            if minescript:
                target = minescript.player_get_targeted_entity()
                if target and hasattr(target, 'type'):
                    # Check if it's a player
                    if target.type == 'player':
                        # Check if target has shield (we can't directly check their inventory,
                        # but we can assume they might have one if they're a player)
                        return True
        except Exception as e:
            self.add_debug_log(f"Target check failed: {e}")
        return False
    
    def switch_to_axe(self, slot):
        """Switch to the axe in the specified slot"""
        try:
            if minescript:
                # Press the hotbar key for the slot (1-9)
                if 1 <= slot <= 9:
                    minescript.press_key_bind(f"hotbar.{slot}")
                    self.add_debug_log(f"Switched to axe in slot {slot}")
                    return True
        except Exception as e:
            self.add_debug_log(f"Switch to axe failed: {e}")
        return False
    
    def disable_shield(self):
        """Disable the shield by right-clicking"""
        try:
            if minescript:
                # Right-click to disable shield
                minescript.player_press_attack(True)  # Press right mouse button
                time.sleep(0.05)  # Small delay
                minescript.player_press_attack(False)  # Release right mouse button
                self.add_debug_log("Disabled shield")
                return True
        except Exception as e:
            self.add_debug_log(f"Disable shield failed: {e}")
        return False
    
    def _shield_macro_loop(self):
        """Main shield macro loop"""
        self.add_debug_log("Shield macro started")
        
        while self.is_running:
            try:
                if not self.enabled:
                    time.sleep(0.1)
                    continue
                
                # Check if we're looking at a player
                if not self.is_target_player_with_shield():
                    delay_ticks = self.get_random_delay_ticks()
                    time.sleep(self.ticks_to_seconds(delay_ticks))
                    continue
                
                # Check if we have an axe in inventory
                if not self.has_axe_in_inventory():
                    self.add_debug_log("No axe found in inventory - skipping")
                    delay_ticks = self.get_random_delay_ticks()
                    time.sleep(self.ticks_to_seconds(delay_ticks))
                    continue
                
                # Check if we're currently holding a shield
                if not self.is_holding_shield():
                    delay_ticks = self.get_random_delay_ticks()
                    time.sleep(self.ticks_to_seconds(delay_ticks))
                    continue
                
                # Find axe slot and switch to it
                axe_slot = self.find_axe_slot()
                if axe_slot == -1:
                    self.add_debug_log("Could not find axe slot - skipping")
                    delay_ticks = self.get_random_delay_ticks()
                    time.sleep(self.ticks_to_seconds(delay_ticks))
                    continue
                
                # Switch to axe
                if self.switch_to_axe(axe_slot):
                    time.sleep(0.1)  # Wait for switch
                    
                    # Disable shield
                    self.disable_shield()
                    
                    self.add_debug_log("Shield macro executed successfully")
                
                # Wait before next check
                delay_ticks = self.get_random_delay_ticks()
                time.sleep(self.ticks_to_seconds(delay_ticks))
                
            except Exception as e:
                self.add_debug_log(f"Shield macro error: {e}")
                time.sleep(0.1)
    
    def start(self):
        """Start the shield macro"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.macro_thread = threading.Thread(target=self._shield_macro_loop, daemon=True)
        self.macro_thread.start()
        self.add_debug_log("Shield macro thread started")
        return True
    
    def stop(self):
        """Stop the shield macro"""
        if not self.is_running:
            return False
        
        self.is_running = False
        if self.macro_thread:
            self.macro_thread.join(timeout=1.0)
        self.add_debug_log("Shield macro stopped")
        return True
    
    def set_enabled(self, enabled):
        """Enable or disable the shield macro"""
        self.enabled = enabled
        status = "enabled" if enabled else "disabled"
        self.add_debug_log(f"Shield macro {status}")
    
    def is_enabled(self):
        """Check if the shield macro is enabled"""
        return self.enabled
