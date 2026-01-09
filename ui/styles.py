import flet as ft
import os
import platform
from data.storage import load_user_data, save_user_data

FONT_NAME = "Microsoft YaHei"

class LightColors:
    BACKGROUND = ft.Colors.GREY_50
    PRIMARY = ft.Colors.BLUE_600
    PRIMARY_CONTAINER = ft.Colors.BLUE_100
    TEXT_PRIMARY = ft.Colors.BLUE_GREY_900
    TEXT_SECONDARY = ft.Colors.GREY_600
    
    WATER_BG = ft.Colors.BLUE_50
    WATER_PROGRESS = ft.Colors.BLUE_400
    WATER_TEXT = ft.Colors.BLUE_800
    WATER_COMPLETE = ft.Colors.GREEN_400
    
    FOOD_ICON = ft.Colors.ORANGE_500
    FOOD_TOTAL = ft.Colors.ORANGE_800
    ADD_BUTTON = ft.Colors.GREEN_600
    
    CARD_BG = ft.Colors.WHITE
    CARD_SHADOW = ft.Colors.BLACK12

class DarkColors:
    BACKGROUND = ft.Colors.GREY_800
    PRIMARY = ft.Colors.BLUE_400
    PRIMARY_CONTAINER = ft.Colors.BLUE_900
    TEXT_PRIMARY = ft.Colors.WHITE
    TEXT_SECONDARY = ft.Colors.GREY_300
    
    WATER_BG = ft.Colors.BLUE_GREY_700
    WATER_PROGRESS = ft.Colors.BLUE_100
    WATER_TEXT = ft.Colors.BLUE_50
    WATER_COMPLETE = ft.Colors.GREEN_200
    
    FOOD_ICON = ft.Colors.ORANGE_300
    FOOD_TOTAL = ft.Colors.ORANGE_100
    ADD_BUTTON = ft.Colors.GREEN_300
    
    CARD_BG = ft.Colors.GREY_700
    CARD_SHADOW = ft.Colors.BLACK26

class ThemeManager:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ThemeManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self._subscribers = set()
        self._load_theme_preference()
    
    def _load_theme_preference(self):
        user_data = load_user_data()
        self.theme_mode = user_data.get("theme_mode", "system")
        self._update_colors()
    
    def _update_colors(self):
        if self.theme_mode == "light":
            self.current_colors = LightColors
        elif self.theme_mode == "dark":
            self.current_colors = DarkColors
        else:
            self.current_colors = self._get_system_theme_colors()
    
    def _get_system_theme_colors(self):
        
        system = platform.system()
        
        try:
            if system == "Windows":
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return LightColors if value == 1 else DarkColors
                
            elif system == "Darwin":
                import subprocess
                result = subprocess.run(
                    ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                    capture_output=True, text=True
                )
                return DarkColors if "Dark" in result.stdout else LightColors
                
            else:
                import subprocess
                try:
                    result = subprocess.run(
                        ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                        capture_output=True, text=True
                    )
                    return DarkColors if "dark" in result.stdout.lower() else LightColors
                except Exception:
                    return LightColors
                    
        except Exception:
            return LightColors
    
    def set_theme(self, mode: str):
        if mode in ["system", "light", "dark"]:
            self.theme_mode = mode
            save_user_data({"theme_mode": mode})
            self._update_colors()
            self._notify_subscribers()
    
    def subscribe(self, callback):
        self._subscribers.add(callback)
    
    def unsubscribe(self, callback):
        self._subscribers.discard(callback)
    
    def _notify_subscribers(self):
        for callback in self._subscribers:
            try:
                callback()
            except Exception:
                pass

theme_manager = ThemeManager()
AppColors = theme_manager.current_colors

CARD_STYLE = {
    "padding": 20,
    "bgcolor": AppColors.CARD_BG,
    "border_radius": 15,
    "shadow": ft.BoxShadow(blur_radius=10, color=AppColors.CARD_SHADOW)
}

def get_card_style():
    return {
        "padding": 20,
        "bgcolor": theme_manager.current_colors.CARD_BG,
        "border_radius": 15,
        "shadow": ft.BoxShadow(blur_radius=10, color=theme_manager.current_colors.CARD_SHADOW)
    }

def is_mobile(page: ft.Page) -> bool:
    
    if not page or not page.width or not page.height:
        return False
    return page.height > page.width

def get_responsive_padding(page: ft.Page) -> ft.Padding:
    
    if is_mobile(page):
        return ft.padding.only(left=12, top=12, right=12, bottom=12)
    return ft.padding.only(left=20, top=20, right=35, bottom=20)

def get_responsive_spacing(page: ft.Page) -> int:
    
    return 12 if is_mobile(page) else 20

