#!/usr/bin/env python3
"""
Mace Swap Module for Script Client

Automatically swaps to a mace after attacking, compatible with triggerbot.
"""

import threading
import time
import sys
import os
import json
from datetime import datetime

# Add minescript to path
minescript_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'system', 'lib')
if minescript_path not in sys.path:
    sys.path.insert(0, minescript_path)

try:
    import minescript
except ImportError:
    print("Warning: minescript not found. Mace Swap will not work.")
    minescript = None

class MaceSwap:
    def __init__(self):
        self.is_running = False
        self.enabled = False
        self.delay_ticks = 1  # Delay in ticks before swapping to mace
        self.swap_thread = None
        self.debug_logs = []
        self.max_logs = 50  # Keep last 50 logs
        
        # Create logs directory
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        
        # Session log file
        self.session_log_file = os.path.join(self.logs_dir, f"mace_swap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        # Track last attack time to prevent spam
        self.last_attack_time = 0
        self.attack_cooldown = 0.1  # 100ms cooldown between swaps

    def set_enabled(self, enabled):
        """Enable or disable the mace swap"""
        self.enabled = enabled
        self.add_debug_log(f"Mace Swap {'enabled' if enabled else 'disabled'}")

    def set_delay_ticks(self, delay_ticks):
        """Set the swap delay in ticks"""
        self.delay_ticks = max(1, min(20, delay_ticks))  # 1-20 ticks
        self.add_debug_log(f"Swap delay set to {self.delay_ticks} ticks")

    def get_delay_ticks(self):
        """Get the current swap delay in ticks"""
        return self.delay_ticks

    def ticks_to_seconds(self, ticks):
        """Convert ticks to seconds (20 ticks = 1 second)"""
        return ticks / 20.0

    def start(self):
        """Start the mace swap"""
        if not self.enabled:
            self.add_debug_log("Mace Swap is not enabled, cannot start.")
            return False
        if self.swap_thread and self.swap_thread.is_alive():
            self.add_debug_log("Mace Swap is already running.")
            return False

        self.is_running = True
        self.swap_thread = threading.Thread(target=self._swap_loop, daemon=True)
        self.swap_thread.start()
        self.add_debug_log("Mace Swap started.")
        return True

    def stop(self):
        """Stop the mace swap"""
        if self.swap_thread and self.swap_thread.is_alive():
            self.is_running = False
            self.swap_thread.join(timeout=0.5)
            if self.swap_thread.is_alive():
                self.add_debug_log("Warning: Mace Swap thread did not terminate gracefully.")
            self.add_debug_log("Mace Swap stopped.")
            return True
        self.add_debug_log("Mace Swap is not running.")
        return False

    def get_debug_logs(self):
        """Get recent debug logs"""
        return self.debug_logs.copy()

    def clear_debug_logs(self):
        """Clear debug logs"""
        self.debug_logs.clear()
        self.add_debug_log("Mace Swap logs cleared.")

    def add_debug_log(self, message):
        """Add a debug log message"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.debug_logs.append(log_entry)
        
        # Write to session log file
        try:
            with open(self.session_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"Failed to write to log file: {e}")
        
        # Keep only the last max_logs entries
        if len(self.debug_logs) > self.max_logs:
            self.debug_logs.pop(0)

    def has_mace_in_inventory(self):
        """Check if player has a mace in their inventory"""
        try:
            if not minescript:
                self.add_debug_log("Minescript not available for inventory check")
                return False
                
            self.add_debug_log("Checking player inventory for mace...")
            inventory = minescript.player_inventory()
            self.add_debug_log(f"Inventory type: {type(inventory)}")
            
            if not inventory:
                self.add_debug_log("No inventory found")
                return False
                
            self.add_debug_log(f"Inventory length: {len(inventory)}")
            
            for i, item in enumerate(inventory):
                if item and hasattr(item, 'id'):
                    item_id = item.id.lower()
                    self.add_debug_log(f"Slot {i}: {item_id}")
                    if 'mace' in item_id:
                        self.add_debug_log(f"Found mace in slot {i}: {item_id}")
                        return True
                else:
                    self.add_debug_log(f"Slot {i}: No item or no ID")
                    
            self.add_debug_log("No mace found in inventory")
            return False
        except Exception as e:
            self.add_debug_log(f"Inventory check failed: {e}")
            import traceback
            self.add_debug_log(f"Traceback: {traceback.format_exc()}")
        return False

    def find_mace_slot(self):
        """Find the slot number of the first mace in hotbar (0-8)"""
        try:
            if minescript:
                inventory = minescript.player_inventory()
                if inventory:
                    # Check hotbar slots (0-8)
                    for i in range(9):
                        if i < len(inventory):
                            item = inventory[i]
                            if item and hasattr(item, 'id'):
                                item_id = item.id.lower()
                                if 'mace' in item_id:
                                    return i
        except Exception as e:
            self.add_debug_log(f"Mace slot search failed: {e}")
        return -1

    def swap_to_mace(self, slot):
        """Swap to the mace in the specified slot"""
        try:
            if minescript:
                # Use player_inventory_select_slot (0-8 for hotbar)
                if 0 <= slot <= 8:
                    minescript.player_inventory_select_slot(slot)
                    self.add_debug_log(f"Swapped to mace in slot {slot + 1}")
                    return True
        except Exception as e:
            self.add_debug_log(f"Swap to mace failed: {e}")
        return False

    def _swap_loop(self):
        """Main mace swap loop"""
        self.add_debug_log("Mace swap loop started")
        loop_count = 0
        
        while self.is_running:
            try:
                loop_count += 1
                if loop_count % 100 == 0:  # Log every 100 loops
                    self.add_debug_log(f"Mace swap loop iteration {loop_count}")
                
                if not self.enabled:
                    time.sleep(0.1)
                    continue
                
                # Check if we have a mace in inventory
                if not self.has_mace_in_inventory():
                    time.sleep(0.1)
                    continue
                
                # Find mace slot
                mace_slot = self.find_mace_slot()
                if mace_slot == -1:
                    time.sleep(0.1)
                    continue
                
                # Wait for the delay
                delay_seconds = self.ticks_to_seconds(self.delay_ticks)
                time.sleep(delay_seconds)
                
                # Swap to mace
                if self.swap_to_mace(mace_slot):
                    self.add_debug_log("Mace swap executed successfully")
                
                # Small delay before next check
                time.sleep(0.1)
                
            except Exception as e:
                self.add_debug_log(f"Mace swap loop error: {e}")
                import traceback
                self.add_debug_log(f"Traceback: {traceback.format_exc()}")
                time.sleep(1)  # Longer sleep on error

        self.add_debug_log("Mace swap loop terminated.")

    def trigger_swap(self):
        """Trigger a mace swap (called when attack is detected)"""
        current_time = time.time()
        if current_time - self.last_attack_time < self.attack_cooldown:
            return  # Too soon since last swap
        
        self.last_attack_time = current_time
        
        if not self.enabled or not self.is_running:
            return
        
        try:
            # Check if we have a mace
            if not self.has_mace_in_inventory():
                self.add_debug_log("No mace found for swap")
                return
            
            # Find mace slot
            mace_slot = self.find_mace_slot()
            if mace_slot == -1:
                self.add_debug_log("Could not find mace slot")
                return
            
            # Wait for delay then swap
            delay_seconds = self.ticks_to_seconds(self.delay_ticks)
            time.sleep(delay_seconds)
            
            if self.swap_to_mace(mace_slot):
                self.add_debug_log("Mace swap triggered successfully")
            
        except Exception as e:
            self.add_debug_log(f"Trigger swap failed: {e}")
