import flet as ft
from core.i18n import i18n_manager, I18nText
from data.storage import load_user_data
import copy

class CustomFoodDialog(ft.AlertDialog):
    
    
    def __init__(self, on_save_callback):
        self.on_save_callback = on_save_callback
        

        self.food_items = []
        self.food_items_container = ft.Column(spacing=15)
        

        self._add_food_item()
        

        self.calories_input = ft.TextField(
            label=i18n_manager.t("food_calories") + " (kcal)",
            value="0",
            width=240,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.protein_input = ft.TextField(
            label=i18n_manager.t("food_protein") + " (g)",
            value="0",
            width=240,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.fat_input = ft.TextField(
            label=i18n_manager.t("food_fat") + " (g)",
            value="0",
            width=240,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.carbs_input = ft.TextField(
            label=i18n_manager.t("food_carbs") + " (g)",
            value="0",
            width=240,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.fiber_input = ft.TextField(
            label=i18n_manager.t("food_fiber") + " (g)",
            value="0",
            width=240,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.sugar_input = ft.TextField(
            label=i18n_manager.t("food_sugar") + " (g)",
            value="0",
            width=240,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.sodium_input = ft.TextField(
            label=i18n_manager.t("food_sodium") + " (mg)",
            value="0",
            width=240,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.calcium_input = ft.TextField(
            label=i18n_manager.t("food_calcium") + " (mg)",
            value="0",
            width=240,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.vitamin_c_input = ft.TextField(
            label=i18n_manager.t("food_vitamin_c") + " (mg)",
            value="0",
            width=240,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        self.vitamin_d_input = ft.TextField(
            label=i18n_manager.t("food_vitamin_d") + " (µg)",
            value="0",
            width=240,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        

        self.prompt_text = ft.TextField(
            label=i18n_manager.t("food_custom_ai_prompt"),
            multiline=True,
            min_lines=3,
            max_lines=5,
            read_only=True,
            width=520
        )
        

        content = ft.Column([

            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(i18n_manager.t("food_custom_name"), size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            icon_color=ft.Colors.GREEN_600,
                            tooltip="Add food item",
                            on_click=self._on_add_food_item
                        ),
                        ft.IconButton(
                            icon=ft.Icons.REMOVE_CIRCLE,
                            icon_color=ft.Colors.RED_600,
                            tooltip="Remove last item",
                            on_click=self._on_remove_food_item
                        ),
                    ]),
                    self.food_items_container,
                ], spacing=10),
                padding=ft.padding.only(bottom=15)
            ),
            
            ft.Divider(height=1),
            ft.Container(height=10),
            

            ft.Row([
                ft.ElevatedButton(
                    content=ft.Text(i18n_manager.t("food_custom_generate_prompt")),
                    icon=ft.Icons.AUTO_AWESOME,
                    on_click=self._generate_prompt
                ),
                ft.IconButton(
                    icon=ft.Icons.COPY,
                    tooltip=i18n_manager.t("food_custom_copy_prompt"),
                    on_click=self._copy_prompt
                )
            ], spacing=10),
            ft.Container(height=8),
            self.prompt_text,
            ft.Container(height=8),
            

            self._build_ai_buttons_row(),
            
            ft.Divider(height=1),
            ft.Container(height=15),
            
            I18nText(key="food_custom_nutrition_data", size=14, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            

            ft.Row([
                ft.OutlinedButton(
                    content=ft.Text(i18n_manager.t("food_custom_paste_and_fill"), color=ft.Colors.GREEN_600),
                    icon=ft.Icons.PASTE,
                    icon_color=ft.Colors.GREEN_600,
                    style=ft.ButtonStyle(side=ft.BorderSide(1, ft.Colors.GREEN_600)),
                    on_click=self._paste_and_fill
                ),
            ]),
            ft.Container(height=10),
            
            ft.Row([self.calories_input, self.protein_input], spacing=20),
            ft.Container(height=8),
            ft.Row([self.fat_input, self.carbs_input], spacing=20),
            ft.Container(height=8),
            ft.Row([self.fiber_input, self.sugar_input], spacing=20),
            ft.Container(height=8),
            ft.Row([self.sodium_input, self.calcium_input], spacing=20),
            ft.Container(height=8),
            ft.Row([self.vitamin_c_input, self.vitamin_d_input], spacing=20),
        ], scroll=ft.ScrollMode.AUTO, spacing=5)
        
        super().__init__(
            modal=True,
            title=ft.Container(
                content=ft.Text(i18n_manager.t("food_custom_dialog_title"), size=20, weight=ft.FontWeight.BOLD),
                padding=ft.padding.only(bottom=10)
            ),
            content=ft.Container(
                content=content,
                width=580,
                height=650,
                padding=ft.padding.all(15)
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text(i18n_manager.t("food_details_close")),
                    on_click=self._close
                ),
                ft.ElevatedButton(
                    content=ft.Text(i18n_manager.t("food_add_tooltip")),
                    on_click=self._save
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
    
    def _add_food_item(self):
        
        item_index = len(self.food_items)
        
        name_input = ft.TextField(
            label=f"{i18n_manager.t('food_custom_name')} {item_index + 1}",
            width=260,
            autofocus=(item_index == 0)
        )
        portion_input = ft.TextField(
            label=i18n_manager.t("food_custom_portion"),
            value="100",
            width=120,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        unit_input = ft.TextField(
            label=i18n_manager.t("food_custom_unit"),
            value="g",
            width=80
        )
        
        self.food_items.append({
            "name": name_input,
            "portion": portion_input,
            "unit": unit_input
        })
        
        item_row = ft.Container(
            content=ft.Row([name_input, portion_input, unit_input], spacing=10),

            border_radius=8,
            padding=10
        )
        self.food_items_container.controls.append(item_row)
    
    def _on_add_food_item(self, e):
        
        self._add_food_item()
        self.food_items_container.update()
    
    def _on_remove_food_item(self, e):
        
        if len(self.food_items) > 1:
            self.food_items.pop()
            self.food_items_container.controls.pop()
            self.food_items_container.update()
        
    def _build_ai_buttons_row(self):
        
        user_data = load_user_data()
        china_mode = user_data.get("china_ai_mode", False)
        
        if china_mode:

            return ft.Row([
                ft.TextButton(
                    content=ft.Text(i18n_manager.t("food_custom_open_deepseek")),
                    icon=ft.Icons.ROCKET_LAUNCH,
                    on_click=lambda e: self._open_url("https://chat.deepseek.com/")
                ),
                ft.TextButton(
                    content=ft.Text(i18n_manager.t("food_custom_open_doubao")),
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e: self._open_url("https://www.doubao.com/chat/")
                ),
                ft.TextButton(
                    content=ft.Text(i18n_manager.t("food_custom_open_qwen")),
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e: self._open_url("https://tongyi.aliyun.com/qianwen/")
                ),
            ], alignment=ft.MainAxisAlignment.START, spacing=0)
        else:

            return ft.Row([
                ft.TextButton(
                    content=ft.Text(i18n_manager.t("food_custom_open_chatgpt")),
                    icon=ft.Icons.ROCKET_LAUNCH,
                    on_click=lambda e: self._open_url("https://chatgpt.com/?temporary-chat=true")
                ),
                ft.TextButton(
                    content=ft.Text(i18n_manager.t("food_custom_open_gemini")),
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e: self._open_url("https://gemini.google.com/")
                ),
                ft.TextButton(
                    content=ft.Text(i18n_manager.t("food_custom_open_grok")),
                    icon=ft.Icons.OPEN_IN_NEW,
                    on_click=lambda e: self._open_url("https://grok.com/")
                ),
            ], alignment=ft.MainAxisAlignment.START, spacing=0)
        
    def _open_url(self, url):
        import webbrowser
        webbrowser.open(url)
    
    def _generate_prompt(self, e):
        
        valid_items = []
        is_all_valid = True
        

        for item in self.food_items:
            name = item["name"].value
            portion_str = item["portion"].value
            unit = item["unit"].value
            
            item_valid = True
            

            if not name or not name.strip():
                item_valid = False
            

            if not portion_str or not portion_str.strip():
                item_valid = False
            else:
                try:
                    p = float(portion_str)
                    if p <= 0:
                        item_valid = False
                except ValueError:
                    item_valid = False
            

            if not unit or not unit.strip():
                item_valid = False
            
            if item_valid:
                valid_items.append({
                    "name": name.strip(),
                    "portion": portion_str.strip(),
                    "unit": unit.strip()
                })
            else:
                is_all_valid = False
        
        if not is_all_valid:
            self.prompt_text.value = i18n_manager.t("food_input_invalid")
            self.prompt_text.update()
            return

        food_list = [f"{item['portion']}{item['unit']} {item['name']}" for item in valid_items]
        

        foods_str = "\n- " + "\n- ".join(food_list)
        
        prompt_template = i18n_manager.t("food_custom_ai_prompt_template")
        if not prompt_template:
            prompt_template = "Error loading template"
        

        if len(food_list) > 1:
            prompt_template_multi = i18n_manager.t("food_custom_ai_prompt_template_multi")
            if not prompt_template_multi:
                 prompt_template_multi = "Error loading template"
            prompt = prompt_template_multi.format(foods_str=foods_str)
        else:

            prompt = prompt_template.format(
                portion=valid_items[0]["portion"],
                unit=valid_items[0]["unit"],
                food_name=valid_items[0]["name"]
            )
        
        self.prompt_text.value = prompt
        self.prompt_text.update()
    
    def _copy_prompt(self, e):
        
        if self.prompt_text.value:
            try:

                import subprocess
                process = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
                process.communicate(input=self.prompt_text.value.encode('utf-16-le')) 
            except Exception as ex:
                print(f"Clipboard error: {ex}")

                try:
                    import pyperclip
                    pyperclip.copy(self.prompt_text.value)
                except ImportError:
                    pass

            try:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(i18n_manager.t("food_custom_prompt_copied")),
                    duration=2000
                )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception:
                pass
                
    def _paste_and_fill(self, e):
        
        import json
        import subprocess
        
        clipboard_content = ""
        try:

            if hasattr(self.page, "get_clipboard"):

                pass
            

            cmd = "powershell.exe -command \"Get-Clipboard\""
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error = process.communicate()
            
            if output:

                try:
                    clipboard_content = output.decode('utf-8').strip()
                except UnicodeDecodeError:
                    clipboard_content = output.decode('gbk', errors='ignore').strip()
                    
        except Exception as ex:
            print(f"Paste error: {ex}")
        
        if not clipboard_content:
            return

        try:

            start_idx = clipboard_content.find('{')
            end_idx = clipboard_content.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = clipboard_content[start_idx : end_idx+1]
                data = json.loads(json_str)
                

                self.calories_input.value = str(data.get("calories", 0))
                self.protein_input.value = str(data.get("protein", 0))
                self.fat_input.value = str(data.get("total_fat", 0))
                self.carbs_input.value = str(data.get("total_carbs", 0))
                self.fiber_input.value = str(data.get("fiber", 0))
                self.sugar_input.value = str(data.get("sugars", 0))
                self.sodium_input.value = str(data.get("sodium", 0))
                self.calcium_input.value = str(data.get("calcium", 0))
                self.vitamin_c_input.value = str(data.get("vitamin_c", 0))
                self.vitamin_d_input.value = str(data.get("vitamin_d", 0))
                
                self.update()
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(i18n_manager.t("food_custom_autofill_success")),
                    bgcolor=ft.Colors.GREEN_700,
                    duration=2000
                )
                self.page.snack_bar.open = True
                self.page.update()
            else:
                raise ValueError("No JSON found")
                
        except Exception as ex:
            print(f"JSON Parse Error: {ex}")
            try:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(i18n_manager.t("food_custom_json_error")),
                    bgcolor=ft.Colors.RED_700,
                    duration=3000
                )
                self.page.snack_bar.open = True
                self.page.update()
            except:
                pass

    def _save(self, e):
        

        valid_foods = []
        for item in self.food_items:
            name = item["name"].value
            if name and name.strip():
                try:
                    portion = float(item["portion"].value or "100")
                    if portion <= 0:
                        portion = 100
                except ValueError:
                    portion = 100
                unit = item["unit"].value or "g"
                valid_foods.append({
                    "name": name.strip(),
                    "portion": portion,
                    "unit": unit
                })
        
        if not valid_foods:

            self.food_items[0]["name"].error_text = i18n_manager.t("food_error_select")
            self.food_items[0]["name"].update()
            return
        

        if len(valid_foods) == 1:
            combined_name = valid_foods[0]["name"]
            total_portion = valid_foods[0]["portion"]
            combined_unit = valid_foods[0]["unit"]
        else:
            combined_name = " + ".join([f["name"] for f in valid_foods])
            total_portion = sum([f["portion"] for f in valid_foods])
            combined_unit = "g"
        

        scale = total_portion / 100.0
        
        custom_food = {
            "name": combined_name,
            "level1": {
                "calories": self._parse_float(self.calories_input.value) * scale,
                "protein": self._parse_float(self.protein_input.value) * scale,
                "total_fat": self._parse_float(self.fat_input.value) * scale,
                "total_carbs": self._parse_float(self.carbs_input.value) * scale,
                "fiber": self._parse_float(self.fiber_input.value) * scale,
                "sugars": self._parse_float(self.sugar_input.value) * scale,
                "sodium": self._parse_float(self.sodium_input.value) * scale,
                "calcium": self._parse_float(self.calcium_input.value) * scale,
                "vitamin_c": self._parse_float(self.vitamin_c_input.value) * scale,
                "vitamin_d": self._parse_float(self.vitamin_d_input.value) * scale
            },
            "serving_eaten": {"value": total_portion, "unit": combined_unit},
            "is_custom": True
        }
        

        if self.on_save_callback:
            self.on_save_callback(custom_food)
        
        self._close(e)
    
    def _parse_float(self, value: str) -> float:
        
        try:
            return round(float(value or "0"), 2)
        except ValueError:
            return 0.0
    
    def _close(self, e):
        
        self.open = False
        

        self.food_items.clear()
        self.food_items_container.controls.clear()
        self._add_food_item()
        

        self.calories_input.value = "0"
        self.protein_input.value = "0"
        self.fat_input.value = "0"
        self.carbs_input.value = "0"
        self.fiber_input.value = "0"
        self.sugar_input.value = "0"
        self.sodium_input.value = "0"
        self.calcium_input.value = "0"
        self.vitamin_c_input.value = "0"
        self.vitamin_d_input.value = "0"
        self.prompt_text.value = ""
        
        if self.page:
            self.page.update()
