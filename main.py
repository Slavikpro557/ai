from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.core.window import Window
from kivy.clock import Clock
from game.durak_game import DurakGame
from ai.durak_ai import DurakAI
from screen_analyzer.screen_capture import ScreenAnalyzer
import pyautogui
import win32gui
import win32process
import psutil

class DurakApp(App):
    def build(self):
        # Делаем окно прозрачным и поверх других окон
        Window.borderless = True
        Window.clearcolor = (0, 0, 0, 0)
        
        self.game = DurakGame()
        self.ai = DurakAI()
        self.screen_analyzer = ScreenAnalyzer()
        
        # Создаем основной layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.background_color = (0, 0, 0, 0.5)
        
        # Добавляем информацию о приложении
        self.app_info = Label(
            text='Определение приложения...',
            size_hint_y=0.1,
            color=(0.8, 0.8, 1, 1)
        )
        
        # Добавляем статистику обучения
        self.stats_label = Label(
            text='Статистика: загрузка...',
            size_hint_y=0.1,
            color=(1, 0.8, 0.8, 1)
        )
        
        # Добавляем переключатели режимов
        modes = BoxLayout(size_hint_y=0.15)
        
        # Переключатель агрессивного режима
        aggressive_box = BoxLayout(orientation='vertical')
        aggressive_label = Label(text='Агрессивный режим')
        self.aggressive_switch = Switch(active=True)
        self.aggressive_switch.bind(active=self.on_aggressive_mode)
        aggressive_box.add_widget(aggressive_label)
        aggressive_box.add_widget(self.aggressive_switch)
        
        # Переключатель автоигры
        autoplay_box = BoxLayout(orientation='vertical')
        autoplay_label = Label(text='Автоматическая игра')
        self.autoplay_switch = Switch(active=False)
        self.autoplay_switch.bind(active=self.on_auto_play)
        autoplay_box.add_widget(autoplay_label)
        autoplay_box.add_widget(self.autoplay_switch)
        
        modes.add_widget(aggressive_box)
        modes.add_widget(autoplay_box)
        
        # Добавляем кнопки управления
        controls = BoxLayout(size_hint_y=0.1)
        
        self.start_button = Button(
            text='Начать анализ',
            background_color=(0.2, 0.8, 0.2, 0.8)
        )
        self.start_button.bind(on_press=self.start_game)
        
        self.stop_button = Button(
            text='Остановить',
            background_color=(0.8, 0.2, 0.2, 0.8)
        )
        self.stop_button.bind(on_press=self.stop_game)
        
        self.calibrate_button = Button(
            text='Калибровка',
            background_color=(0.2, 0.2, 0.8, 0.8)
        )
        self.calibrate_button.bind(on_press=self.calibrate)
        
        # Добавляем кнопку для записи результата
        self.result_box = BoxLayout(size_hint_y=0.1)
        self.win_button = Button(
            text='Победа',
            background_color=(0.2, 0.8, 0.2, 0.8)
        )
        self.win_button.bind(on_press=lambda x: self.record_game_result(True))
        
        self.lose_button = Button(
            text='Поражение',
            background_color=(0.8, 0.2, 0.2, 0.8)
        )
        self.lose_button.bind(on_press=lambda x: self.record_game_result(False))
        
        self.result_box.add_widget(self.win_button)
        self.result_box.add_widget(self.lose_button)
        
        controls.add_widget(self.calibrate_button)
        controls.add_widget(self.start_button)
        controls.add_widget(self.stop_button)
        
        # Добавляем информационные поля
        self.status_label = Label(
            text='Нажмите "Калибровка" для настройки области анализа',
            size_hint_y=0.1,
            color=(1, 1, 1, 1)
        )
        
        self.suggestion_label = Label(
            text='',
            size_hint_y=0.2,
            color=(0, 1, 0, 1)
        )
        
        layout.add_widget(self.app_info)
        layout.add_widget(self.stats_label)
        layout.add_widget(modes)
        layout.add_widget(self.status_label)
        layout.add_widget(self.suggestion_label)
        layout.add_widget(controls)
        layout.add_widget(self.result_box)
        
        self.analysis_event = None
        self.last_action = None
        
        # Запускаем определение приложения
        Clock.schedule_interval(self.update_app_info, 1.0)
        
        return layout
    
    def get_active_window_info(self):
        """Получение информации об активном окне"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            window_title = win32gui.GetWindowText(hwnd)
            return {
                'pid': pid,
                'name': process.name(),
                'title': window_title
            }
        except:
            return None
    
    def update_app_info(self, dt):
        """Обновление информации о приложении"""
        window_info = self.get_active_window_info()
        if window_info:
            self.app_info.text = f'Приложение: {window_info["name"]} - {window_info["title"]}'
            # Обновляем информацию в ИИ
            self.ai.update_game_state(
                self.game.player_hand,
                self.game.trump_suit,
                self.ai.opponent_cards_count,
                self.ai.deck_remaining,
                window_info["title"]
            )
            
            # Обновляем статистику
            stats = self.ai.learning_engine.get_statistics()
            if stats:
                self.stats_label.text = (
                    f'Игр: {stats["games_played"]}, '
                    f'Побед: {stats["games_won"]}, '
                    f'Винрейт: {stats["win_rate"]:.2%}'
                )
    
    def record_game_result(self, won: bool):
        """Запись результата игры"""
        self.ai.end_game(won)
        result = "победой" if won else "поражением"
        self.status_label.text = f'Игра завершена с {result}'
        self.stop_game(None)
    
    def on_aggressive_mode(self, instance, value):
        self.ai.aggressive_mode = value
        mode = "агрессивный" if value else "осторожный"
        self.status_label.text = f'Режим игры: {mode}'
    
    def on_auto_play(self, instance, value):
        self.ai.set_auto_play(value)
        mode = "автоматический" if value else "рекомендации"
        self.status_label.text = f'Режим игры: {mode}'
    
    def calibrate(self, instance):
        self.status_label.text = 'Выполняется калибровка...'
        try:
            self.screen_analyzer.calibrate_game_region()
            self.status_label.text = 'Калибровка завершена успешно'
        except Exception as e:
            self.status_label.text = f'Ошибка калибровки: {str(e)}'
    
    def start_game(self, instance):
        if not self.screen_analyzer.game_region:
            self.status_label.text = 'Сначала выполните калибровку!'
            return
            
        self.status_label.text = 'Анализ игры запущен'
        self.analysis_event = Clock.schedule_interval(self.analyze_game_state, 1.0)
    
    def stop_game(self, instance):
        if self.analysis_event:
            self.analysis_event.cancel()
        self.status_label.text = 'Анализ остановлен'
        self.suggestion_label.text = ''
        self.last_action = None
    
    def analyze_game_state(self, dt):
        try:
            # Захват и анализ экрана
            screen = self.screen_analyzer.capture_game_screen()
            detected_cards = self.screen_analyzer.detect_cards(screen)
            
            # Обновление состояния игры и ИИ
            player_cards = [card for card, _ in detected_cards]
            table_cards = self.screen_analyzer.detect_table_cards(screen)
            opponent_cards = self.screen_analyzer.count_opponent_cards(screen)
            deck_remaining = self.screen_analyzer.count_deck_cards(screen)
            
            # Получаем информацию о текущем приложении
            window_info = self.get_active_window_info()
            
            self.game.player_hand = player_cards
            self.ai.update_game_state(
                player_cards,
                self.game.trump_suit,
                opponent_cards,
                deck_remaining,
                window_info["title"] if window_info else None
            )
            
            if self.ai.auto_play:
                # Режим автоматической игры
                action, card = self.ai.get_auto_play_action(table_cards)
                
                if action != self.last_action:
                    self.last_action = action
                    if action == "attack" and card:
                        self._play_card(card)
                        self.suggestion_label.text = f'Ход: {card}'
                    elif action == "defend" and card:
                        self._play_card(card)
                        self.suggestion_label.text = f'Отбиваюсь: {card}'
                    elif action == "add" and card:
                        self._play_card(card)
                        self.suggestion_label.text = f'Подкидываю: {card}'
                    elif action == "take":
                        self._click_take_button()
                        self.suggestion_label.text = 'Беру карты'
                    elif action == "done":
                        self._click_done_button()
                        self.suggestion_label.text = 'Бито'
            else:
                # Режим рекомендаций
                action, card = self.ai.get_auto_play_action(table_cards)
                if card:
                    self.suggestion_label.text = f'Рекомендую: {action} {card}'
                else:
                    self.suggestion_label.text = f'Рекомендую: {action}'
                
        except Exception as e:
            self.status_label.text = f'Ошибка анализа: {str(e)}'
    
    def _play_card(self, card):
        """Находит и кликает по карте на экране"""
        card_pos = self.screen_analyzer.find_card_position(card)
        if card_pos:
            pyautogui.click(card_pos[0], card_pos[1])
    
    def _click_take_button(self):
        """Находит и кликает по кнопке 'Взять'"""
        take_pos = self.screen_analyzer.find_take_button()
        if take_pos:
            pyautogui.click(take_pos[0], take_pos[1])
    
    def _click_done_button(self):
        """Находит и кликает по кнопке 'Бито'"""
        done_pos = self.screen_analyzer.find_done_button()
        if done_pos:
            pyautogui.click(done_pos[0], done_pos[1])

if __name__ == '__main__':
    DurakApp().run() 