
import flet as ft
from ui.Mobile.components.water_formula_card import WaterFormulaCard
from ui.Mobile.components.reminder_card import ReminderCard

class WaterView(ft.Container):
    
    
    def __init__(self, water_card):
        super().__init__()
        self.expand = True
        
        self.reminder_card = ReminderCard()
        self.formula_card = WaterFormulaCard()
        

        self.content = ft.ListView(
            controls=[
                self.reminder_card,
                water_card,
                self.formula_card
            ],
            spacing=10,
            padding=ft.padding.all(10)
        )
