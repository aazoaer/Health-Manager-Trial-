import flet as ft
from ui.Desktop.components.exercise_card import ExerciseCard
from ui.Desktop.components.exercise_stats_card import ExerciseStatsCard

class ExerciseView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        
        self.exercise_stats_card = ExerciseStatsCard()
        self.exercise_card = ExerciseCard()
        
        self.content = ft.ListView(
            controls=[
                self.exercise_stats_card,
                self.exercise_card
            ],
            spacing=20,
            padding=ft.padding.only(left=20, top=20, right=35, bottom=20)
        )
