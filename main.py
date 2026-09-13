import sys
import os
from src.lesta_parser import LestaParser
from src.site_generator import WebSiteGenerator

def main():
    print("=== ЗАПУСК ЕДИНОГО КОНВЕЙЕРА ПАРСИНГА И ВИЗУАЛИЗАЦИИ ===")
    
    OUTPUT_DIR = "parsed_data"
    
    # Шаг 1: Парсинг данных через ООП-класс
    parser = LestaParser(base_url="https://lesta.ru", output_dir=OUTPUT_DIR)
    all_products, gift_products = parser.run()
    
    if not all_products:
        print("\n[Критическая ошибка] Не удалось собрать товары. Сборка сайта отменена.")
        sys.exit(1)
        
    # Шаг 2: Генерация интерактивной HTML-витрины
    generator = WebSiteGenerator(output_dir=OUTPUT_DIR)
    generator.generate(all_products)
    
    print("\n=== ВСЕ ЭТАПЫ УСПЕШНО ВЫПОЛНЕНЫ! ===")
    print(f"Результат можно посмотреть тут: {os.path.abspath(os.path.join(OUTPUT_DIR, 'index.html'))}")

if __name__ == "__main__":
    main()
