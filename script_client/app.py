#!/usr/bin/env python3
"""
Script Client - Minecraft Utility Client
Main GUI Application with DearPyGui Interface

A clean GUI for Minecraft utilities using Minecraft textures.
"""

import dearpygui.dearpygui as dpg
import os
import sys
import threading
import time
import json
from datetime import datetime

# Import modules
from modules import Triggerbot
from modules.mace_swap import MaceSwap

class ScriptClientApp:
    def __init__(self):
        self.triggerbot = Triggerbot()
        self.mace_swap = MaceSwap()
        self.textures_path = os.path.join(os.path.dirname(__file__), 'textures')
        
        # Connect mace swap to triggerbot
        self.triggerbot.set_attack_callback(self.mace_swap.trigger_swap)
        
        # Keybind system
        self.keybind_enabled = False
        self.keybind_key = "F1"  # Default keybind
        self.keybind_thread = None
        
        # Create logs directory
        self.logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        
        # Session log file
        self.session_log_file = os.path.join(self.logs_dir, f"script_client_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the DearPyGui interface with Minecraft theming"""
        dpg.create_context()
        
        # Create texture registry
        with dpg.texture_registry():
            # Load Minecraft textures for icons
            self.load_textures()
        
        # Create main window
        with dpg.window(label="Script Client", tag="main_window", width=500, height=400):
            dpg.add_text("Minecraft Script Client", color=[255, 255, 0])  # Gold color
            dpg.add_separator()
            
            # Create tab bar
            with dpg.tab_bar():
                # Combat Tab
                with dpg.tab(label="⚔️ Combat", tag="combat_tab"):
                    self.create_combat_tab()
                
                # Debug Tab
                with dpg.tab(label="🐛 Debug", tag="debug_tab"):
                    self.create_debug_tab()
                
                # Player Info Tab (placeholder)
                with dpg.tab(label="👤 Player", tag="player_tab"):
                    dpg.add_text("Player Info - Coming Soon!", color=[200, 200, 200])
                
                # Settings Tab (placeholder)
                with dpg.tab(label="⚙️ Settings", tag="settings_tab"):
                    dpg.add_text("Settings - Coming Soon!", color=[200, 200, 200])
    
    def load_textures(self):
        """Load Minecraft textures for GUI icons"""
        try:
            # Load sword texture for combat tab
            sword_path = os.path.join(self.textures_path, 'item', 'iron_sword.png')
            if os.path.exists(sword_path):
                width, height, channels, data = dpg.load_image(sword_path)
                dpg.add_static_texture(width=width, height=height, default_value=data, tag="sword_texture")
            
            # Load player head texture
            player_path = os.path.join(self.textures_path, 'entity', 'player', 'head.png')
            if os.path.exists(player_path):
                width, height, channels, data = dpg.load_image(player_path)
                dpg.add_static_texture(width=width, height=height, default_value=data, tag="player_texture")
            
            # Load settings gear texture
            gear_path = os.path.join(self.textures_path, 'item', 'clock.png')  # Using clock as gear
            if os.path.exists(gear_path):
                width, height, channels, data = dpg.load_image(gear_path)
                dpg.add_static_texture(width=width, height=height, default_value=data, tag="gear_texture")
                
        except Exception as e:
            print(f"Warning: Could not load textures: {e}")
    
    def create_combat_tab(self):
        """Create the combat tab with triggerbot controls"""
        dpg.add_text("Triggerbot", color=[255, 100, 100])  # Red color
        dpg.add_separator()
        
        # Status display
        with dpg.group(horizontal=True):
            dpg.add_text("Status:")
            dpg.add_text("OFF", tag="triggerbot_status", color=[255, 100, 100])
        
        dpg.add_separator()
        
        # Delay control
        dpg.add_text("Attack Delay Range (ticks):")
        with dpg.group(horizontal=True):
            dpg.add_text("Min:")
            dpg.add_input_int(
                label="",
                default_value=2,
                min_value=1,
                max_value=40,
                callback=self.update_triggerbot_delay_min_ticks,
                tag="triggerbot_delay_min_input",
                width=80
            )
            dpg.add_text("Max:")
            dpg.add_input_int(
                label="",
                default_value=2,
                min_value=1,
                max_value=40,
                callback=self.update_triggerbot_delay_max_ticks,
                tag="triggerbot_delay_max_input",
                width=80
            )
        dpg.add_text("Range: 2-2 ticks (0.10s-0.10s)", tag="triggerbot_delay_text")
        dpg.add_text("Note: 20 ticks = 1 second", color=[150, 150, 150])
        
        dpg.add_separator()
        
        # Range control
        dpg.add_text("Attack Range Range (blocks):")
        with dpg.group(horizontal=True):
            dpg.add_text("Min:")
            dpg.add_input_float(
                label="",
                default_value=3.0,
                min_value=1.0,
                max_value=10.0,
                callback=self.update_triggerbot_range_min,
                tag="triggerbot_range_min_input",
                width=80,
                format="%.1f"
            )
            dpg.add_text("Max:")
            dpg.add_input_float(
                label="",
                default_value=3.0,
                min_value=1.0,
                max_value=10.0,
                callback=self.update_triggerbot_range_max,
                tag="triggerbot_range_max_input",
                width=80,
                format="%.1f"
            )
        dpg.add_text("Range: 3.0 - 3.0 blocks", tag="triggerbot_range_text")
        
        # Attack method selection
        dpg.add_text("Attack Method:", color=[255, 255, 255])
        dpg.add_radio_button(
            items=["Minescript", "Win32 API"],
            default_value=0,
            callback=self.update_attack_method,
            tag="attack_method_radio"
        )
        dpg.add_text("Minescript", tag="attack_method_text", color=[200, 200, 200])
        
        dpg.add_separator()
        
        # Weapon-only mode
        dpg.add_checkbox(
            label="Weapon Only Mode",
            callback=self.update_weapon_only,
            tag="weapon_only_checkbox"
        )
        dpg.add_text("Only attack when holding a weapon", color=[200, 200, 200])
        
        # Weapon selector (initially hidden)
        dpg.add_button(
            label="Select Weapons",
            callback=self.toggle_weapon_selector,
            tag="weapon_selector_button",
            width=150
        )
        
        # Weapon selector window (initially hidden)
        with dpg.window(label="Weapon Selector", tag="weapon_selector_window", 
                       width=400, height=300, show=False, modal=True):
            dpg.add_text("Select which weapons to allow:", color=[255, 255, 255])
            dpg.add_separator()
            
            # Weapon checkboxes
            weapons = [
                ("sword", "Sword", "textures/item/iron_sword.png"),
                ("axe", "Axe", "textures/item/iron_axe.png"), 
                ("mace", "Mace", "textures/item/mace.png"),
                ("trident", "Trident", "textures/item/trident.png"),
                ("bow", "Bow", "textures/item/bow.png"),
                ("crossbow", "Crossbow", "textures/item/crossbow_standby.png")
            ]
            
            for weapon_id, weapon_name, texture_path in weapons:
                with dpg.group(horizontal=True):
                    dpg.add_checkbox(
                        label=weapon_name,
                        callback=lambda s, a, u: self.update_weapon_selection(weapon_id, a),
                        tag=f"weapon_{weapon_id}_checkbox"
                    )
                    # Try to load weapon texture
                    try:
                        full_path = os.path.join(self.textures_path, texture_path)
                        if os.path.exists(full_path):
                            with dpg.texture_registry():
                                dpg.add_static_texture(width=16, height=16, 
                                                     default_value=[255, 255, 255, 255], 
                                                     tag=f"weapon_{weapon_id}_texture")
                            dpg.add_image(f"weapon_{weapon_id}_texture", width=16, height=16)
                    except:
                        pass
            
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(label="Apply", callback=self.apply_weapon_selection, width=100)
                dpg.add_button(label="Cancel", callback=self.close_weapon_selector, width=100)
        
        dpg.add_separator()
        
        # Control buttons
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Start Triggerbot",
                callback=self.start_triggerbot,
                tag="triggerbot_start_button",
                width=150
            )
            dpg.add_button(
                label="Stop Triggerbot", 
                callback=self.stop_triggerbot,
                tag="triggerbot_stop_button",
                width=150,
                enabled=False
            )
        
        dpg.add_separator()
        
        # Keybind Section
        dpg.add_text("Keybind", color=[255, 200, 100])  # Orange color
        dpg.add_separator()
        
        with dpg.group(horizontal=True):
            dpg.add_text("Toggle Key:")
            dpg.add_input_text(
                label="",
                default_value="F1",
                callback=self.update_keybind_key,
                tag="keybind_input",
                width=80
            )
        
        dpg.add_checkbox(
            label="Enable Keybind",
            callback=self.update_keybind_enabled,
            tag="keybind_enabled_checkbox"
        )
        dpg.add_text("Press the key to toggle triggerbot on/off", color=[200, 200, 200])
        
        dpg.add_separator()
        
        # Info text
        dpg.add_text("Hold right-click to aim at target", color=[200, 200, 200])
        dpg.add_text("Triggerbot will auto-attack when target is detected", color=[200, 200, 200])
        dpg.add_text("Works on mobs and players", color=[200, 200, 200])
        
        dpg.add_separator()
        
        # Mace Swap Section
        dpg.add_text("Mace Swap", color=[255, 200, 100])  # Orange color
        dpg.add_separator()
        
        # Mace Swap Status
        with dpg.group(horizontal=True):
            dpg.add_text("Status:")
            dpg.add_text("OFF", tag="mace_swap_status", color=[255, 100, 100])
        
        # Enable/Disable toggle
        dpg.add_checkbox(
            label="Enable Mace Swap",
            callback=self.update_mace_swap_enabled,
            tag="mace_swap_enabled_checkbox"
        )
        dpg.add_text("Auto swap to mace after attacking", color=[200, 200, 200])
        
        # Mace Swap Delay control
        dpg.add_text("Swap Delay (ticks):")
        with dpg.group(horizontal=True):
            dpg.add_text("Delay:")
            dpg.add_input_int(
                label="",
                default_value=1,
                min_value=1,
                max_value=20,
                callback=self.update_mace_swap_delay_ticks,
                tag="mace_swap_delay_input",
                width=80
            )
        dpg.add_text("Delay: 1 tick (0.05s)", tag="mace_swap_delay_text")
        
        # Start/Stop buttons
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Start Mace Swap",
                callback=self.start_mace_swap,
                tag="mace_swap_start_button",
                width=150
            )
            dpg.add_button(
                label="Stop Mace Swap",
                callback=self.stop_mace_swap,
                tag="mace_swap_stop_button",
                enabled=False,
                width=150
            )
        
        dpg.add_text("Instructions: Make sure you have a mace in your hotbar", color=[200, 200, 200])
        
    
    def create_debug_tab(self):
        """Create the debug tab with logging"""
        dpg.add_text("Debug Logs", color=[255, 200, 100])  # Orange color
        dpg.add_separator()
        
        # Debug controls
        with dpg.group(horizontal=True):
            dpg.add_button(
                label="Refresh Logs",
                callback=self.refresh_debug_logs,
                width=120
            )
            dpg.add_button(
                label="Clear Logs",
                callback=self.clear_debug_logs,
                width=120
            )
        
        dpg.add_separator()
        
        # Debug log display
        dpg.add_text("Recent Debug Messages:", color=[200, 200, 200])
        with dpg.child_window(height=250, tag="debug_log_window"):
            dpg.add_text("Debug logs will appear here...", tag="debug_logs_text")
    
    def refresh_debug_logs(self):
        """Refresh the debug logs display"""
        triggerbot_logs = self.triggerbot.get_debug_logs()
        mace_swap_logs = self.mace_swap.get_debug_logs()
        
        all_logs = []
        if triggerbot_logs:
            all_logs.extend([f"[TRIGGERBOT] {log}" for log in triggerbot_logs])
        if mace_swap_logs:
            all_logs.extend([f"[MACE SWAP] {log}" for log in mace_swap_logs])
        
        # Sort by timestamp (assuming logs have timestamps)
        all_logs.sort()
        
        if all_logs:
            log_text = "\n".join(all_logs[-30:])  # Show last 30 logs
        else:
            log_text = "No debug logs yet..."
        
        dpg.set_value("debug_logs_text", log_text)
    
    def clear_debug_logs(self):
        """Clear debug logs"""
        self.triggerbot.clear_debug_logs()
        self.mace_swap.clear_debug_logs()
        dpg.set_value("debug_logs_text", "Debug logs cleared.")
    
    # Keybind methods
    def update_keybind_key(self, sender, value):
        """Update the keybind key"""
        self.keybind_key = value.upper()
        self.add_log(f"Keybind changed to: {self.keybind_key}")
    
    def update_keybind_enabled(self, sender, value):
        """Enable or disable keybind system"""
        self.keybind_enabled = value
        if value:
            self.start_keybind_listener()
            self.add_log(f"Keybind enabled: {self.keybind_key}")
        else:
            self.stop_keybind_listener()
            self.add_log("Keybind disabled")
    
    def start_keybind_listener(self):
        """Start the keybind listener thread"""
        if self.keybind_thread and self.keybind_thread.is_alive():
            return
        
        self.keybind_thread = threading.Thread(target=self._keybind_listener, daemon=True)
        self.keybind_thread.start()
    
    def stop_keybind_listener(self):
        """Stop the keybind listener thread"""
        if self.keybind_thread and self.keybind_thread.is_alive():
            self.keybind_enabled = False
            self.keybind_thread.join(timeout=0.5)
    
    def _keybind_listener(self):
        """Keybind listener thread"""
        try:
            import keyboard
            self.add_log(f"Keybind listener started for key: {self.keybind_key}")
            
            while self.keybind_enabled:
                try:
                    if keyboard.is_pressed(self.keybind_key.lower()):
                        # Toggle triggerbot
                        if self.triggerbot.is_running:
                            self.triggerbot.stop()
                            self.add_log("Triggerbot stopped via keybind")
                        else:
                            self.triggerbot.start()
                            self.add_log("Triggerbot started via keybind")
                        
                        # Update GUI
                        dpg.set_value("triggerbot_status", "OFF" if not self.triggerbot.is_running else "ON")
                        color = [255, 100, 100] if not self.triggerbot.is_running else [100, 255, 100]
                        dpg.configure_item("triggerbot_status", color=color)
                        
                        # Wait to prevent multiple toggles
                        time.sleep(0.5)
                    
                    time.sleep(0.01)  # Small delay to prevent high CPU usage
                except Exception as e:
                    self.add_log(f"Keybind error: {e}")
                    time.sleep(0.1)
        except ImportError:
            self.add_log("keyboard module not found. Install with: pip install keyboard")
        except Exception as e:
            self.add_log(f"Keybind listener error: {e}")
    
    def add_log(self, message):
        """Add a log message"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Write to session log file
        try:
            with open(self.session_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"Failed to write to log file: {e}")
    
    # Mace Swap callback methods
    def update_mace_swap_enabled(self, sender, value):
        """Update mace swap enabled state"""
        self.mace_swap.set_enabled(value)
        status = "ON" if value else "OFF"
        color = [100, 255, 100] if value else [255, 100, 100]
        dpg.set_value("mace_swap_status", status)
        dpg.configure_item("mace_swap_status", color=color)

    def update_mace_swap_delay_ticks(self, sender, value):
        """Update mace swap delay in ticks"""
        value = max(1, min(20, value))
        self.mace_swap.set_delay_ticks(value)
        dpg.set_value("mace_swap_delay_input", value)
        self._update_mace_swap_delay_text()

    def _update_mace_swap_delay_text(self):
        """Update mace swap delay text display"""
        delay_ticks = self.mace_swap.get_delay_ticks()
        delay_sec = self.mace_swap.ticks_to_seconds(delay_ticks)
        dpg.set_value("mace_swap_delay_text", f"Delay: {delay_ticks} tick{'s' if delay_ticks != 1 else ''} ({delay_sec:.2f}s)")

    def start_mace_swap(self):
        """Start the mace swap"""
        if self.mace_swap.start():
            dpg.set_value("mace_swap_status", "ON")
            dpg.configure_item("mace_swap_status", color=[100, 255, 100])  # Green
            dpg.configure_item("mace_swap_start_button", enabled=False)
            dpg.configure_item("mace_swap_stop_button", enabled=True)
            self.refresh_debug_logs()

    def stop_mace_swap(self):
        """Stop the mace swap"""
        if self.mace_swap.stop():
            dpg.set_value("mace_swap_status", "OFF")
            dpg.configure_item("mace_swap_status", color=[255, 100, 100])  # Red
            dpg.configure_item("mace_swap_start_button", enabled=True)
            dpg.configure_item("mace_swap_stop_button", enabled=False)
            self.refresh_debug_logs()
    
    def update_triggerbot_delay_min_ticks(self, sender, value):
        """Update triggerbot delay minimum value in ticks"""
        # Clamp value to valid range
        value = max(1, min(40, value))
        delay_min_ticks, delay_max_ticks = self.triggerbot.get_delay_range_ticks()
        if value > delay_max_ticks:
            value = delay_max_ticks
        self.triggerbot.set_delay_range_ticks(value, delay_max_ticks)
        self._update_delay_text()
    
    def update_triggerbot_delay_max_ticks(self, sender, value):
        """Update triggerbot delay maximum value in ticks"""
        # Clamp value to valid range
        value = max(1, min(40, value))
        delay_min_ticks, delay_max_ticks = self.triggerbot.get_delay_range_ticks()
        if value < delay_min_ticks:
            value = delay_min_ticks
        self.triggerbot.set_delay_range_ticks(delay_min_ticks, value)
        self._update_delay_text()
    
    def _update_delay_text(self):
        """Update delay text display"""
        delay_min_ticks, delay_max_ticks = self.triggerbot.get_delay_range_ticks()
        delay_min_seconds = self.triggerbot.ticks_to_seconds(delay_min_ticks)
        delay_max_seconds = self.triggerbot.ticks_to_seconds(delay_max_ticks)
        dpg.set_value("triggerbot_delay_text", f"Range: {delay_min_ticks}-{delay_max_ticks} ticks ({delay_min_seconds:.2f}s-{delay_max_seconds:.2f}s)")
    
    def update_triggerbot_range_min(self, sender, value):
        """Update triggerbot range minimum value"""
        # Clamp value to valid range
        value = max(1.0, min(10.0, value))
        range_min, range_max = self.triggerbot.get_range_range()
        if value > range_max:
            value = range_max
        self.triggerbot.set_range_range(value, range_max)
        self._update_range_text()
    
    def update_triggerbot_range_max(self, sender, value):
        """Update triggerbot range maximum value"""
        # Clamp value to valid range
        value = max(1.0, min(10.0, value))
        range_min, range_max = self.triggerbot.get_range_range()
        if value < range_min:
            value = range_min
        self.triggerbot.set_range_range(range_min, value)
        self._update_range_text()
    
    def _update_range_text(self):
        """Update range text display"""
        range_min, range_max = self.triggerbot.get_range_range()
        dpg.set_value("triggerbot_range_text", f"Range: {range_min:.1f} - {range_max:.1f} blocks")
    
    def update_attack_method(self, sender, value):
        """Update attack method"""
        method = "minescript" if value == 0 else "win32"
        self.triggerbot.set_attack_method(method)
        dpg.set_value("attack_method_text", method.title())
    
    def update_weapon_only(self, sender, value):
        """Update weapon-only mode"""
        self.triggerbot.set_weapon_only(value)
    
    def toggle_weapon_selector(self):
        """Toggle weapon selector window"""
        dpg.show_item("weapon_selector_window")
    
    def close_weapon_selector(self):
        """Close weapon selector window"""
        dpg.hide_item("weapon_selector_window")
    
    def update_weapon_selection(self, weapon_id, enabled):
        """Update individual weapon selection"""
        # This will be handled in apply_weapon_selection
        pass
    
    def apply_weapon_selection(self):
        """Apply weapon selection"""
        selected_weapons = []
        weapons = ["sword", "axe", "mace", "trident", "bow", "crossbow"]
        
        for weapon in weapons:
            if dpg.get_value(f"weapon_{weapon}_checkbox"):
                selected_weapons.append(weapon)
        
        self.triggerbot.set_allowed_weapons(selected_weapons)
        dpg.hide_item("weapon_selector_window")
    
    def start_triggerbot(self):
        """Start the triggerbot"""
        if self.triggerbot.start():
            dpg.set_value("triggerbot_status", "ON")
            dpg.configure_item("triggerbot_status", color=[100, 255, 100])  # Green
            dpg.configure_item("triggerbot_start_button", enabled=False)
            dpg.configure_item("triggerbot_stop_button", enabled=True)
            # Auto-refresh debug logs when starting
            self.refresh_debug_logs()
    
    def stop_triggerbot(self):
        """Stop the triggerbot"""
        if self.triggerbot.stop():
            dpg.set_value("triggerbot_status", "OFF")
            dpg.configure_item("triggerbot_status", color=[255, 100, 100])  # Red
            dpg.configure_item("triggerbot_start_button", enabled=True)
            dpg.configure_item("triggerbot_stop_button", enabled=False)
            # Auto-refresh debug logs when stopping
            self.refresh_debug_logs()
    
    def run(self):
        """Run the GUI"""
        dpg.create_viewport(
            title="Script Client - Minecraft Utility", 
            width=500, 
            height=400, 
            resizable=True
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        
        # Main loop
        import time
        last_debug_refresh = time.time()
        
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            
            # Auto-refresh debug logs every 2 seconds
            current_time = time.time()
            if current_time - last_debug_refresh > 2.0:
                self.refresh_debug_logs()
                last_debug_refresh = current_time
        
        # Cleanup
        self.triggerbot.stop()
        dpg.destroy_context()

def main():
    """Main entry point"""
    try:
        app = ScriptClientApp()
        app.run()
    except Exception as e:
        print(f"Error starting Script Client: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()