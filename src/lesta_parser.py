import os
import json
import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class LestaParser:
    def __init__(self, base_url="https://lesta.ru", output_dir="parsed_data"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.start_url = f"{base_url}/shop/tb/prem"
        self.driver = None

    def _init_driver(self):
        """Настройка и запуск Headless Chrome driver."""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless") 
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def _slugify(self, text):
        """Принцип DRY: Безопасное имя для папок и файлов."""
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9а-яё\s_-]', '', text)
        text = re.sub(r'[\s_-]+', '_', text)
        return text if text else "folder"

    def _download_image(self, url, category_slug, product_name, index):
        """Скачивание картинки товара в папку соответствующей категории."""
        folder = os.path.join(self.output_dir, "images", category_slug)
        os.makedirs(folder, exist_ok=True)
        
        filename = f"{self._slugify(product_name)}_{index}.png"
        local_path = os.path.join(folder, filename)
        
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                return local_path
        except Exception as e:
            print(f"  [Ошибка скачивания изображения]: {e}")
        return None

    def parse_menu(self):
        """Парсинг вкладок меню категорий."""
        print(" Сбор категорий меню...")
        self.driver.get(self.start_url)
        
        WebDriverWait(self.driver, 12).until(
            EC.presence_of_element_located((By.CLASS_NAME, "category-menu_wrap"))
        )
        
        categories = []
        menu_links = self.driver.find_elements(By.CSS_SELECTOR, ".category-menu_wrap a.category-menu_link")
        
        for link in menu_links:
            name = link.text.strip()
            href = link.get_attribute("href")
            if href.startswith("/"):
                href = self.base_url + href
                
            categories.append({
                "name": name if name else "Без названия",
                "url": href,
                "slug": self._slugify(name if name else "without_name")
            })
        print(f" Найдено вкладок меню: {len(categories)}")
        return categories

    def parse_category_page(self, category):
        """Парсинг всех карточек товаров на странице категории."""
        print(f"\n Открываю категорию '{category['name']}': {category['url']}")
        self.driver.get(category['url'])
        
        time.sleep(4) # Ожидание рендеринга Vue компонентов
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        products = []
        cards = self.driver.find_elements(By.CSS_SELECTOR, "article.product")
        print(f" Найдено карточек: {len(cards)}")
        
        for index, card in enumerate(cards):
            try:
                name = card.find_element(By.CSS_SELECTOR, ".product_name-text").text.strip()
                
                quantity = "1 предмет"
                try:
                    quantity = card.find_element(By.CSS_SELECTOR, ".product_items").text.strip()
                except: pass
                    
                price_current = "0 ₽"
                price_old = None
                try:
                    price_current = card.find_element(By.CSS_SELECTOR, "[data-qa='product_price']").text.replace('\u00a0', ' ').strip()
                    price_old = card.find_element(By.CSS_SELECTOR, "[data-qa='original_product_price']").text.replace('\u00a0', ' ').strip()
                except: pass
                
                discount = "0%"
                try:
                    discount = card.find_element(By.CSS_SELECTOR, "[data-qa='offer_item_promo']").text.strip()
                except: pass
                    
                is_giftable = len(card.find_elements(By.CSS_SELECTOR, ".gift-indicator, [data-qa='gift_indicator']")) > 0
                
                image_url = None
                try:
                    image_url = card.find_element(By.CSS_SELECTOR, "img.product_picture").get_attribute("src")
                except: pass

                local_image_path = None
                if image_url:
                    local_image_path = self._download_image(image_url, category['slug'], name, index)

                products.append({
                    "category": category['name'],
                    "name": name,
                    "price": price_current,
                    "old_price": price_old,
                    "discount": discount,
                    "quantity": quantity,
                    "is_giftable": is_giftable,
                    "image_url": image_url,
                    "local_image_path": local_image_path,
                    "product_page_url": card.find_element(By.CSS_SELECTOR, "a.product_link").get_attribute("href")
                })
                print(f"  [Успех] {name} ({price_current})")
            except:
                continue
        return products

    def save_to_json(self, data, filename):
        os.makedirs(self.output_dir, exist_ok=True)
        path = os.path.join(self.output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def run(self):
        """Главный оркестратор жизненного цикла парсера."""
        self._init_driver()
        all_products = []
        gift_products = []
        seen_items = set()
        
        try:
            categories = self.parse_menu()
            for cat in categories:
                page_items = self.parse_category_page(cat)
                for item in page_items:
                    # Чистка дубликатов на лету
                    uid = f"{item['category']}_{item['name']}_{item['price']}"
                    if uid in seen_items:
                        continue
                    seen_items.add(uid)
                    
                    all_products.append(item)
                    if item['is_giftable']:
                        gift_products.append(item)
                        
            self.save_to_json(all_products, "all_products.json")
            self.save_to_json(gift_products, "gift_products.json")
            return all_products, gift_products
        finally:
            self.driver.quit()
