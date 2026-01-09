import flet as ft
from ui.Desktop.components.sleep_card import SleepCard
from ui.Desktop.components.sleep_stats_card import SleepStatsCard

class SleepView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        
        self.sleep_stats_card = SleepStatsCard()
        self.sleep_card = SleepCard()
        
        self.content = ft.ListView(
            controls=[
                self.sleep_stats_card,
                self.sleep_card
            ],
            spacing=20,
            padding=ft.padding.only(left=20, top=20, right=35, bottom=20)
        )
