#!/usr/bin/env python3
"""
Shield Macro Module for Script Client

Automatically switches to axe and disables shield when looking at a player with a shield.
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
        
        # Create logs directory
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        
        # Session log file
        self.session_log_file = os.path.join(self.logs_dir, f"shield_macro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
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
        
        # Write to session log file
        try:
            with open(self.session_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"Failed to write to log file: {e}")
        
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
            if not minescript:
                self.add_debug_log("Minescript not available for inventory check")
                return False
                
            self.add_debug_log("Checking player inventory for axe...")
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
                    if 'axe' in item_id:
                        self.add_debug_log(f"Found axe in slot {i}: {item_id}")
                        return True
                else:
                    self.add_debug_log(f"Slot {i}: No item or no ID")
                    
            self.add_debug_log("No axe found in inventory")
            return False
        except Exception as e:
            self.add_debug_log(f"Inventory check failed: {e}")
            import traceback
            self.add_debug_log(f"Traceback: {traceback.format_exc()}")
        return False
    
    def find_axe_slot(self):
        """Find the slot number of the first axe in hotbar (0-8)"""
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
            if not minescript:
                self.add_debug_log("Minescript not available")
                return False
                
            self.add_debug_log("Checking for target player with shield...")
            target = minescript.player_get_targeted_entity(nbt=True)
            
            if not target:
                self.add_debug_log("No target entity found")
                return False
                
            self.add_debug_log(f"Target found: {type(target)}")
            
            if not hasattr(target, 'type'):
                self.add_debug_log("Target has no 'type' attribute")
                return False
                
            self.add_debug_log(f"Target type: {target.type}")
            
            # Check if it's a player (can be 'player' or 'entity.minecraft.player')
            if target.type not in ['player', 'entity.minecraft.player']:
                self.add_debug_log(f"Target is not a player (type: {target.type})")
                return False
                
            self.add_debug_log("Target is a player, checking for shield...")
            
            # Check if target is holding a shield using NBT data
            self.add_debug_log("Checking target's NBT data for shield...")
            
            if not hasattr(target, 'nbt'):
                self.add_debug_log("Target has no NBT data")
                return False
                
            nbt_data = target.nbt
            self.add_debug_log(f"NBT data: {nbt_data}")
            
            if not nbt_data:
                self.add_debug_log("NBT data is empty")
                return False
            
            # Check main hand for shield
            main_hand_item = nbt_data.get("MainHand", {})
            self.add_debug_log(f"Main hand NBT: {main_hand_item}")
            
            if main_hand_item:
                main_item_id = main_hand_item.get("id", "")
                self.add_debug_log(f"Main hand item ID: {main_item_id}")
                if main_item_id == "minecraft:shield":
                    self.add_debug_log("Target is holding a shield in main hand!")
                    return True
            
            # Check off-hand for shield
            off_hand_item = nbt_data.get("OffHand", {})
            self.add_debug_log(f"Off-hand NBT: {off_hand_item}")
            
            if off_hand_item:
                off_item_id = off_hand_item.get("id", "")
                self.add_debug_log(f"Off-hand item ID: {off_item_id}")
                if off_item_id == "minecraft:shield":
                    self.add_debug_log("Target has shield in off-hand!")
                    return True
            
            self.add_debug_log("Target is not holding a shield in either hand")
            return False
                
        except Exception as e:
            self.add_debug_log(f"Target shield check failed: {e}")
            import traceback
            self.add_debug_log(f"Traceback: {traceback.format_exc()}")
        return False
    
    def switch_to_axe(self, slot):
        """Switch to the axe in the specified slot"""
        try:
            if minescript:
                # Use player_inventory_select_slot (0-8 for hotbar)
                if 0 <= slot <= 8:
                    minescript.player_inventory_select_slot(slot)
                    self.add_debug_log(f"Switched to axe in slot {slot + 1}")
                    return True
        except Exception as e:
            self.add_debug_log(f"Switch to axe failed: {e}")
        return False
    
    def attack_with_axe(self):
        """Attack with axe to disable target's shield"""
        try:
            if minescript:
                # Attack to disable target's shield
                minescript.player_press_attack(True)  # Press left mouse button
                time.sleep(0.05)  # Small delay
                minescript.player_press_attack(False)  # Release left mouse button
                self.add_debug_log("Attacked with axe to disable shield")
                return True
        except Exception as e:
            self.add_debug_log(f"Axe attack failed: {e}")
        return False
    
    def _shield_macro_loop(self):
        """Main shield macro loop"""
        self.add_debug_log("Shield macro started")
        loop_count = 0
        
        while self.is_running:
            try:
                loop_count += 1
                if loop_count % 20 == 0:  # Log every 20 loops
                    self.add_debug_log(f"Shield macro loop iteration {loop_count}")
                
                if not self.enabled:
                    time.sleep(0.1)
                    continue
                
                self.add_debug_log("Checking for target player with shield...")
                # Check if we're looking at a player holding a shield
                if not self.is_target_player_with_shield():
                    self.add_debug_log("No target player with shield found, waiting...")
                    delay_ticks = self.get_random_delay_ticks()
                    time.sleep(self.ticks_to_seconds(delay_ticks))
                    continue
                
                # Check if we have an axe in inventory
                if not self.has_axe_in_inventory():
                    self.add_debug_log("No axe found in inventory - skipping")
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
                
                # Switch to axe and attack to disable target's shield
                if self.switch_to_axe(axe_slot):
                    time.sleep(0.1)  # Wait for switch
                    
                    # Attack with axe to disable target's shield
                    self.attack_with_axe()
                    
                    self.add_debug_log("Shield macro executed successfully - attacked with axe")
                
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
