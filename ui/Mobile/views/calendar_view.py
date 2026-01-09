
import flet as ft
from ui.Mobile.components.calendar_grid_card import CalendarGridCard
from ui.Mobile.components.calendar_chart_card import CalendarChartCard

class CalendarView(ft.Container):
    
    
    def __init__(self):
        super().__init__()
        self.expand = True
        
        self.chart_card = CalendarChartCard()
        self.grid_card = CalendarGridCard(on_month_change=self.chart_card.update_month)
        

        self.content = ft.ListView(
            controls=[
                self.grid_card,
                self.chart_card
            ],
            spacing=10,
            expand=True,
            padding=ft.padding.all(10)
        )
