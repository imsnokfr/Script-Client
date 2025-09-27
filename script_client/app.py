#!/usr/bin/env python3
"""
Script Client - Minecraft Utility Client
Main GUI Application with DearPyGui Interface

A clean GUI for Minecraft utilities using Minecraft textures.
"""

import dearpygui.dearpygui as dpg
import os
import sys

# Import modules
from modules import Triggerbot

class ScriptClientApp:
    def __init__(self):
        self.triggerbot = Triggerbot()
        self.textures_path = os.path.join(os.path.dirname(__file__), 'textures')
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
        dpg.add_text("Attack Delay (seconds):")
        dpg.add_slider_float(
            label="Delay",
            default_value=0.1,
            min_value=0.05,
            max_value=2.0,
            callback=self.update_triggerbot_delay,
            tag="triggerbot_delay_slider"
        )
        dpg.add_text("0.1s", tag="triggerbot_delay_text")
        
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
        
        # Info text
        dpg.add_text("Hold right-click to aim at target", color=[200, 200, 200])
        dpg.add_text("Triggerbot will auto-attack when target is detected", color=[200, 200, 200])
        dpg.add_text("Works on mobs and players", color=[200, 200, 200])
    
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
        logs = self.triggerbot.get_debug_logs()
        if logs:
            log_text = "\n".join(logs[-20:])  # Show last 20 logs
        else:
            log_text = "No debug logs yet..."
        
        dpg.set_value("debug_logs_text", log_text)
    
    def clear_debug_logs(self):
        """Clear debug logs"""
        self.triggerbot.debug_logs.clear()
        dpg.set_value("debug_logs_text", "Debug logs cleared.")
    
    def update_triggerbot_delay(self, sender, value):
        """Update triggerbot delay value"""
        self.triggerbot.set_delay(value)
        dpg.set_value("triggerbot_delay_text", f"{value:.2f}s")
    
    def update_attack_method(self, sender, value):
        """Update attack method"""
        method = "minescript" if value == 0 else "win32"
        self.triggerbot.set_attack_method(method)
        dpg.set_value("attack_method_text", method.title())
    
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