import os

class WebSiteGenerator:
    def __init__(self, output_dir="parsed_data"):
        self.output_dir = output_dir
        self.html_path = os.path.join(output_dir, "index.html")

    def _get_clean_img_path(self, raw_path):
        if not raw_path:
            return "https://placeholder.com"
        return raw_path.replace("parsed_data/", "").replace("parsed_data\\", "")

    def _render_card(self, item):
        price_digits = ''.join(filter(str.isdigit, item.get('price', '0')))
        price_num = int(price_digits) if price_digits else 0
        has_discount = "true" if item.get('discount') and item['discount'] != "0%" else "false"
        img_path = self._get_clean_img_path(item.get('local_image_path'))

        discount_badge = f'<div class="badge-discount">{item["discount"]}</div>' if has_discount == "true" else ''
        gift_badge = '<div class="badge-gift">🤝 Подарок</div>' if item['is_giftable'] else ''
        old_price_html = f'<span class="price-old">{item["old_price"]}</span>' if item.get('old_price') else ''

        return f"""
        <div class="product-card" data-category="{item['category']}" data-price="{price_num}" data-gift="{str(item['is_giftable']).lower()}" data-promo="{has_discount}">
            <div class="card-img-container">
                <img src="{img_path}" alt="{item['name']}" class="card-img">
                {discount_badge}
                {gift_badge}
            </div>
            <div class="card-body">
                <div>
                    <span class="card-cat">{item['category']}</span>
                    <h3 class="card-title" title="{item['name']}">{item['name']}</h3>
                    <p class="card-qty">{item.get('quantity', '1 предмет')}</p>
                </div>
                <div>
                    <div class="price-container">
                        <span class="price-current">{item['price']}</span>
                        {old_price_html}
                    </div>
                    <a href="{item.get('product_page_url', '#')}" target="_blank" class="card-btn">
                        Открыть на сайте ↗
                    </a>
                </div>
            </div>
        </div>"""

    
    def generate(self, products):
            categories = sorted(list(set(item['category'] for item in products if item['category'])))
            
            html_start = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Lesta Gift Parser</title><style>
            body {{ background-color: #0b0f19; color: #e2e8f0; font-family: system-ui, -apple-system, sans-serif; margin: 0; padding-bottom: 50px; }}
            header {{ border-bottom: 1px solid #1f2937; background-color: rgba(17, 24, 39, 0.8); backdrop-filter: blur(8px); position: sticky; top: 0; z-index: 50; padding: 15px 20px; }}
            .header-container {{ max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px; }}
            .logo-block {{ display: flex; align-items: center; gap: 12px; }}
            .logo-title {{ color: #eab308; font-size: 20px; font-weight: bold; margin: 0; letter-spacing: 0.5px; }}
            .logo-sub {{ color: #9ca3af; font-size: 12px; margin: 2px 0 0 0; }}
            .counter-badge {{ background-color: rgba(31, 41, 55, 0.8); border: 1px solid #374151; padding: 8px 16px; border-radius: 8px; font-size: 14px; }}
            .counter-num {{ color: #eab308; font-weight: bold; }}
            main {{ max-width: 1200px; margin: 30px auto 0; padding: 0 20px; }}
            .control-panel {{ background-color: rgba(17, 24, 39, 0.4); border: 1px solid #1f2937; border-radius: 12px; padding: 24px; margin-bottom: 30px; display: flex; flex-direction: column; gap: 20px; }}
            .section-title {{ text-transform: uppercase; font-size: 11px; font-weight: 600; color: #9ca3af; letter-spacing: 1px; display: block; margin-bottom: 12px; }}
            .btn-grid {{ display: flex; flex-wrap: wrap; gap: 8px; }}
            .cat-btn {{ padding: 8px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; border: none; cursor: pointer; transition: all 0.2s; }}
            .btn-inactive {{ background-color: #1f2937; color: #d1d5db; }}
            .btn-inactive:hover {{ background-color: #374151; }}
            .btn-active {{ background-color: #eab308; color: #111827; }}
            .bottom-controls {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; border-top: 1px solid rgba(31,41,55,0.6); padding-top: 16px; }}
            .action-btn {{ padding: 10px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; background-color: #1f2937; color: #d1d5db; border: 1px solid #374151; cursor: pointer; transition: all 0.2s; }}
            .action-btn:hover {{ background-color: #374151; }}
            .btn-gift-active {{ background-color: rgba(234, 179, 8, 0.15) !important; color: #eab308 !important; border-color: rgba(234, 179, 8, 0.4) !important; }}
            .btn-promo-active {{ background-color: rgba(239, 68, 68, 0.15) !important; color: #f87171 !important; border-color: rgba(239, 68, 68, 0.4) !important; }}
            .price-inputs-container {{ display: flex; align-items: center; gap: 8px; }}
            .price-input {{ background-color: #1f2937; border: 1px solid #374151; color: #e2e8f0; font-size: 14px; padding: 8px 12px; border-radius: 8px; width: 100%; box-sizing: border-box; outline: none; }}
            .price-input:focus {{ border-color: #eab308; }}
            .select-sort {{ background-color: #1f2937; border: 1px solid #374151; color: #e2e8f0; font-size: 14px; padding: 8px 12px; border-radius: 8px; width: 100%; outline: none; cursor: pointer; }}
            .products-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 24px; }}
            .card-glow:hover {{ box-shadow: 0 0 15px rgba(234, 179, 8, 0.2); }}
            .products-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 24px; margin-top: 30px; }}
            .product-card {{ background-color: #111827; border: 1px solid #1f2937; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.3s; }}
            .product-card:hover {{ box-shadow: 0 0 15px rgba(234, 179, 8, 0.2); }}
            .card-img-container {{ position: relative; background-color: #030712; aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center; overflow: hidden; border-bottom: 1px solid rgba(31,41,55,0.5); }}
            .card-img {{ object-fit: contain; max-height: 100%; max-width: 100%; transition: transform 0.5s; }}
            .card-img:hover {{ transform: scale(1.05); }}
            .badge-discount {{ position: absolute; top: 12px; left: 12px; background-color: #dc2626; color: white; font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 6px; }}
            .badge-gift {{ position: absolute; top: 12px; right: 12px; background-color: #eab308; color: #0b0f19; font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 6px; }}
            .card-body {{ padding: 16px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; gap: 16px; }}
            .card-cat {{ font-size: 10px; text-transform: uppercase; font-weight: bold; color: #6b7280; letter-spacing: 1px; display: block; margin-bottom: 4px; }}
            .card-title {{ font-size: 14px; font-weight: bold; color: #f3f4f6; margin: 0; line-clamp: 2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 40px; }}
            .card-qty {{ font-size: 12px; color: #9ca3af; margin: 4px 0 0 0; }}
            .price-container {{ display: flex; align-items: baseline; gap: 8px; }}
            .price-current {{ font-size: 20px; font-weight: 900; color: #eab308; }}
            .price-old {{ font-size: 12px; color: #6b7280; text-decoration: line-through; }}
            .card-btn {{ display: block; text-align: center; background-color: #1f2937; color: #d1d5db; text-decoration: none; font-size: 12px; font-weight: bold; padding: 10px; border-radius: 8px; border: 1px solid #374151; transition: all 0.2s; }}
            .card-btn:hover {{ background-color: #eab308; color: #111827; border-color: transparent; }}


            </style></head><body><header><div class="header-container"><div class="logo-block"><span style="font-size:24px;">🎁</span><div><h1 class="logo-title">LESTA SHOP PARSER</h1><p class="logo-sub">Удобный мониторинг предложений и подарков для друзей</p></div></div><div class="counter-badge">Всего товаров: <span class="counter-num" id="total-count">{len(products)}</span></div></div></header><main><div class="control-panel"><div><span class="section-title">Категории:</span><div class="btn-grid"><button onclick="filterCategory('all')" id="btn-cat-all" class="cat-btn btn-active">Все вкладки</button>"""

            for cat in categories:
                html_start += f'<button onclick="filterCategory(\'{cat}\')" id="btn-cat-{cat}" class="cat-btn btn-inactive">{cat}</button>'

            html_middle = """</div></div><div class="bottom-controls"><div><span class="section-title">Тип предложения:</span><div class="btn-grid"><button onclick="toggleGiftOnly()" id="btn-gift" class="action-btn">🤝 Только подарок</button><button onclick="togglePromoOnly()" id="btn-promo" class="action-btn">🔥 Скидки</button></div></div><div><span class="section-title">Диапазон цен (₽):</span><div class="price-inputs-container"><input type="number" id="price-min" oninput="updateDisplay()" placeholder="От" class="price-input"><span>—</span><input type="number" id="price-max" oninput="updateDisplay()" placeholder="До" class="price-input"></div></div><div><span class="section-title">Сортировка по цене:</span><select onchange="sortItems(this.value)" class="select-sort"><option value="default">По умолчанию</option><option value="asc">От дешевых к дорогим</option><option value="desc">От дорогих к дешевым</option></select></div></div></div><div class="products-grid" id="products-grid">"""

            cards_html = "".join(self._render_card(item) for item in products)

            js_lines = [
                "</div></main><script>",
                "let currentCategory = 'all';",
                "let giftOnly = false;",
                "let promoOnly = false;",
                "function filterCategory(cat) {",
                "  currentCategory = cat;",
                "  document.querySelectorAll('.cat-btn')",
                "    .forEach(btn => {",
                "       btn.className = 'cat-btn btn-inactive';",
                "    });",
                "  const activeBtn = document.getElementById(",
                "    'btn-cat-' + cat",
                "  );",
                "  if(activeBtn) {",
                "    activeBtn.className = 'cat-btn btn-active';",
                "  }",
                "  updateDisplay();",
                "}",
                "function toggleGiftOnly() {",
                "  giftOnly = !giftOnly;",
                "  document.getElementById('btn-gift')",
                "    .className = giftOnly ?",
                "    'action-btn btn-gift-active' : 'action-btn';",
                "  updateDisplay();",
                "}",
                "function togglePromoOnly() {",
                "  promoOnly = !promoOnly;",
                "  document.getElementById('btn-promo')",
                "    .className = promoOnly ?",
                "    'action-btn btn-promo-active' : 'action-btn';",
                "  updateDisplay();",
                "}",
                "function sortItems(type) {",
                "  const grid = document.getElementById(",
                "    'products-grid'",
                "  );",
                "  const cards = Array.from(",
                "    grid.getElementsByClassName('product-card')",
                "  );",
                "  if(type !== 'default') {",
                "    cards.sort((a,b) => {",
                "      const priceA = parseInt(",
                "        a.getAttribute('data-price')",
                "      ) || 0;",
                "      const priceB = parseInt(",
                "        b.getAttribute('data-price')",
                "      ) || 0;",
                "      return type === 'asc' ?",
                "        priceA - priceB : priceB - priceA;",
                "    });",
                "    cards.forEach(c => grid.appendChild(c));",
                "  }",
                "}",
                "function updateDisplay() {",
                "  const cards = document",
                "    .getElementsByClassName('product-card');",
                "  const minPrice = parseInt(",
                "    document.getElementById('price-min').value",
                "  ) || 0;",
                "  const maxPrice = parseInt(",
                "    document.getElementById('price-max').value",
                "  ) || Infinity;",
                "  let visibleCount = 0;",
                "  for(let card of cards) {",
                "    const cat = card.getAttribute(",
                "      'data-category'",
                "  );",
                "    const price = parseInt(",
                "      card.getAttribute('data-price')",
                "    ) || 0;",
                "    const isGift = card.getAttribute(",
                "      'data-gift'",
                "    ) === 'true';",
                "    const isPromo = card.getAttribute(",
                "      'data-promo'",
                "    ) === 'true';",
                "    let show = true;",
                "    if (currentCategory !== 'all' && ",
                "        cat !== currentCategory) show = false;",
                "    if (giftOnly && !isGift) show = false;",
                "    if (promoOnly && !isPromo) show = false;",
                "    if (price < minPrice || price > maxPrice) ",
                "        show = false;",
                "    if (show) {",
                "      card.style.display = 'flex';",
                "      visibleCount++;",
                "    } else {",
                "      card.style.display = 'none';",
                "    }",
                "  }",
                "  document.getElementById('total-count')",
                "    .innerText = visibleCount;",
                "}",
                "</script></body></html>"
            ]
            
            html_js_scripts = "\n".join(js_lines)

            with open(self.html_path, 'w', encoding='utf-8') as f:
                f.write(html_start + html_middle + cards_html + html_js_scripts)
