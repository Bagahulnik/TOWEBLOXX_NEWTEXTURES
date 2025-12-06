import json
import os
from src.constants import DATA_PATH


class SaveManager:
    def __init__(self):
        self.save_file = f"{DATA_PATH}save_data.json"
        self.data = self.load_data()
    
    def load_data(self):
        """Загружает данные из файла"""
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)
        
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.create_default_data()
        else:
            return self.create_default_data()
    
    def create_default_data(self):
        """Создает данные по умолчанию"""
        return {
            'coins': 0,
            'high_score': 0,
            'unlocked_towers': [1],  # Первая башня открыта
            'selected_tower': 1,
            'total_games': 0
        }
    
    def save_data(self):
        """Сохраняет данные в файл"""
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def add_coins(self, amount):
        """Добавляет монеты"""
        self.data['coins'] += amount
        self.save_data()
    
    def spend_coins(self, amount):
        """Тратит монеты"""
        if self.data['coins'] >= amount:
            self.data['coins'] -= amount
            self.save_data()
            return True
        return False
    
    def unlock_tower(self, tower_id):
        """Открывает башню"""
        if tower_id not in self.data['unlocked_towers']:
            self.data['unlocked_towers'].append(tower_id)
            self.save_data()
            return True
        return False
    
    def is_tower_unlocked(self, tower_id):
        """Проверяет, открыта ли башня"""
        return tower_id in self.data['unlocked_towers']
    
    def set_selected_tower(self, tower_id):
        """Устанавливает выбранную башню"""
        if self.is_tower_unlocked(tower_id):
            self.data['selected_tower'] = tower_id
            self.save_data()
            return True
        return False
    
    def get_selected_tower(self):
        """Возвращает выбранную башню"""
        return self.data['selected_tower']
    
    def update_high_score(self, score):
        """Обновляет рекорд"""
        if score > self.data['high_score']:
            self.data['high_score'] = score
            self.save_data()
            return True
        return False
    
    def get_coins(self):
        """Возвращает количество монет"""
        return self.data['coins']
    
    def get_high_score(self):
        """Возвращает рекорд"""
        return self.data['high_score']
