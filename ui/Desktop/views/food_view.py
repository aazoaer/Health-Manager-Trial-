import flet as ft

class FoodView(ft.Container):
    def __init__(self, nutrition_goals_card, food_card):
        super().__init__()
        self.expand = True

        self.content = ft.ListView(
            controls=[
                nutrition_goals_card,
                food_card
            ],
            spacing=20,
            padding=ft.padding.only(left=20, top=20, right=35, bottom=20)
        )
