CATEGORY_MAP = {
    0: "новости",
    1: "экономика",
    2: "политика",
    3: "мир",
    4: "спорт",
    5: "здоровье",
    8: "наука",
    9: "технологии",
}

# Рабочие RSS ленты - новостные + бизнес
TOP_SMI_RSS = [
    # Основные новостные
    ("https://ria.ru/export/rss2/archive/index.xml", "РИА Новости", 0),
    ("https://tass.ru/rss/v2.xml", "ТАСС", 0),
    ("https://lenta.ru/rss", "Lenta.ru", 0),
    ("https://www.mk.ru/rss/index.xml", "МК", 0),
    ("https://life.ru/rss", "Life", 0),
    ("https://regnum.ru/rss", "REGNUM", 0),
    ("https://nplus1.ru/rss", "N+1", 8),
    
    # Бизнес и технологии
    ("https://vc.ru/rss/new", "VC.ru", 9),
    ("https://habr.com/ru/rss/news/", "Habr", 9),
    ("https://www Forbes.ru/rss/news", "Forbes", 1),
    ("https://www.kommersant.ru/rss", "Коммерсантъ", 1),
]

def get_top_smi_sources() -> list:
    return [
        {
            "url": url,
            "name": name,
            "category": CATEGORY_MAP.get(cat, "новости"),
            "category_id": cat
        }
        for url, name, cat in TOP_SMI_RSS
    ]