# ParfumAI — Parfüm Eşleme Motoru
# Copyright (c) 2026 Ahmet Rıfai Kuyucu
# Tüm Hakları Saklıdır — All Rights Reserved.

import json
import os
import re
import time
import hashlib
import threading
import tempfile
import traceback
from datetime import datetime
import requests
from bs4 import BeautifulSoup

PERFUME_DATABASE = [
    # ======================================================================
    # YAZ (Summer) - 70 perfumes
    # ======================================================================
    # ===== YAZ (Summer) — 113 perfumes =====
    {"name":"Light Blue","brand":"Dolce & Gabbana","notes_top":["bergamot", "lemon", "green_apple", "juniper"],"notes_middle":["jasmine", "white_rose", "bamboo"],"notes_base":["cedar", "amber", "musk"],"profile":{"top_pct": 45, "middle_pct": 30, "base_pct": 25},"season":"yaz","gender":"kadın","description":"Ferahlatıcı narenciye ve odunsu notalar ile Akdeniz esintisi.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Acqua di Gio","brand":"Giorgio Armani","notes_top":["bergamot", "neroli", "green_tangerine"],"notes_middle":["jasmine", "hyacinth", "coriander", "rose"],"notes_base":["cedar", "patchouli", "musk", "amber"],"profile":{"top_pct": 40, "middle_pct": 35, "base_pct": 25},"season":"yaz","gender":"erkek","description":"Okyanus ferahlığı ile çiçeksi ve odunsu notaların buluşması.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Acqua di Gio Profondo","brand":"Giorgio Armani","notes_top":["bergamot", "mandarin", "green_mandarin"],"notes_middle":["rosemary", "lavender", "sage"],"notes_base":["cedar", "musk", "amber"],"profile":{"top_pct": 42, "middle_pct": 30, "base_pct": 28},"season":"yaz","gender":"erkek","description":"Derin sulardan yükselen modern bir ferahlık.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Sauvage","brand":"Dior","notes_top":["bergamot", "pepper", "ambroxan"],"notes_middle":["pink_pepper", "lavender", "geranium", "elemi"],"notes_base":["cedar", "labdanum", "ambroxan"],"profile":{"top_pct": 45, "middle_pct": 30, "base_pct": 25},"season":"yaz","gender":"erkek","description":"Vahsi, ferah ve maşkülen bir kaya tuzu patlaması.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Acqua di Gioia","brand":"Giorgio Armani","notes_top":["lemon", "mint", "peppermint", "bergamot"],"notes_middle":["jasmine", "peony", "pink_pepper"],"notes_base":["cedar", "amber", "sugar"],"profile":{"top_pct": 45, "middle_pct": 30, "base_pct": 25},"season":"yaz","gender":"kadın","description":"Bir Akdeniz yazının neşe dolu ferah öpücüğü.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Daisy","brand":"Marc Jacobs","notes_top":["strawberry", "grapefruit", "violet_leaf"],"notes_middle":["jasmine", "violet", "gardenia"],"notes_base":["sandalwood", "musk", "vanilla"],"profile":{"top_pct": 40, "middle_pct": 40, "base_pct": 20},"season":"yaz","gender":"kadın","description":"Masum ama çekici, neşeli bir bahar çiçeği.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Daisy Love","brand":"Marc Jacobs","notes_top":["cloudberry", "daisy", "crystal_moss"],"notes_middle":["cashmeran", "musk", "vanilla"],"notes_base":["sandalwood", "patchouli", "amber"],"profile":{"top_pct": 42, "middle_pct": 33, "base_pct": 25},"season":"yaz","gender":"kadın","description":"Parlak ve neşeli bir çiçekseker yorumu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Invictus","brand":"Paco Rabanne","notes_top":["grapefruit", "sea_notes", "bay_leaf", "mandarin"],"notes_middle":["jasmine", "patchouli", "rose"],"notes_base":["amber", "woody_notes", "oakmoss"],"profile":{"top_pct": 42, "middle_pct": 28, "base_pct": 30},"season":"yaz","gender":"erkek","description":"Zaferin ve gücün taze-odunsu kokusu.","price_range":"1100-1700 TL","in_stock":True}
,
    {"name":"Invictus Victory","brand":"Paco Rabanne","notes_top":["bergamot", "grapefruit", "lemon"],"notes_middle":["black_pepper", "lavender", "amber"],"notes_base":["vanilla", "tonka", "sandalwood"],"profile":{"top_pct": 38, "middle_pct": 30, "base_pct": 32},"season":"yaz","gender":"erkek","description":"Zaferin tatlı-odunsu zafer çılğınlığı.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Mon Paris","brand":"Yves Saint Laurent","notes_top":["bergamot", "strawberry", "raspberry"],"notes_middle":["jasmine", "peony", "orange_blossom"],"notes_base":["patchouli", "vanilla", "musk", "amber"],"profile":{"top_pct": 38, "middle_pct": 38, "base_pct": 24},"season":"yaz","gender":"kadın","description":"Bir aşk hikayesinin meyvemsi-çiçeksi kokusu.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Wood Sage & Sea Salt","brand":"Jo Malone","notes_top":["ambrette", "grapefruit"],"notes_middle":["sea_salt", "sage", "seaweed"],"notes_base":["musk", "mineral", "woody"],"profile":{"top_pct": 45, "middle_pct": 30, "base_pct": 25},"season":"yaz","gender":"unisex","description":"Deniz tuzu ve adaçayının özgürlük kokan kaçışı.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Lime Basil & Mandarin","brand":"Jo Malone","notes_top":["lime", "mandarin", "bergamot"],"notes_middle":["basil", "white_thyme", "coriander"],"notes_base":["patchouli", "woody", "amber"],"profile":{"top_pct": 50, "middle_pct": 25, "base_pct": 25},"season":"yaz","gender":"unisex","description":"Ferahlat\u0131c\u0131 narenciye ve aromatik otların patlaması.","price_range":"1800-2800 TL","in_stock":True}
,
    {"name":"L'Eau d'Issey Pour Homme","brand":"Issey Miyake","notes_top":["lemon", "bergamot", "mandarin", "coriander"],"notes_middle":["nutmeg", "saffron", "lily", "muguet"],"notes_base":["cedar", "sandalwood", "musk", "tobacco"],"profile":{"top_pct": 42, "middle_pct": 30, "base_pct": 28},"season":"yaz","gender":"erkek","description":"Bir su bahçesinin narenciye ve odunsu yansıması.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"L'Eau d'Issey","brand":"Issey Miyake","notes_top":["melon", "lotus", "freesia", "mandarin"],"notes_middle":["lily", "peony", "carnation", "rose"],"notes_base":["musk", "sandalwood", "amber", "tuberose"],"profile":{"top_pct": 42, "middle_pct": 32, "base_pct": 26},"season":"yaz","gender":"kadın","description":"Bir lotus çiçeğinin su uzerindeki ferahlığı.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Versace Eau Fraiche","brand":"Versace","notes_top":["lemon", "bergamot", "grapefruit", "rosewood"],"notes_middle":["sage", "cedar", "tarragon", "pepper"],"notes_base":["musk", "amber", "saffron", "olibanum"],"profile":{"top_pct": 48, "middle_pct": 28, "base_pct": 24},"season":"yaz","gender":"erkek","description":"Akdeniz narenciyesinin ferah ve odunsu dansi.","price_range":"800-1300 TL","in_stock":True}
,
    {"name":"Ck One","brand":"Calvin Klein","notes_top":["bergamot", "lemon", "mandarin", "pineapple", "green_notes"],"notes_middle":["jasmine", "rose", "violet", "nutmeg"],"notes_base":["sandalwood", "cedar", "musk", "amber"],"profile":{"top_pct": 44, "middle_pct": 30, "base_pct": 26},"season":"yaz","gender":"unisex","description":"90'larin devrim niteliğindeki unisex ferah ikonu.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"CK Be","brand":"Calvin Klein","notes_top":["bergamot", "lavender", "mandarin", "mint"],"notes_middle":["jasmine", "magnolia", "pepper"],"notes_base":["sandalwood", "oakmoss", "cedar", "musk"],"profile":{"top_pct": 40, "middle_pct": 30, "base_pct": 30},"season":"yaz","gender":"unisex","description":"Minimal ve özgür ruhlu bir unisex klasiği.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Aventus Cologne","brand":"Creed","notes_top":["bergamot", "lemon", "ginger", "mandarin"],"notes_middle":["rose", "jasmine", "cinnamon", "patchouli"],"notes_base":["cedar", "musk", "sandalwood", "vanilla"],"profile":{"top_pct": 42, "middle_pct": 30, "base_pct": 28},"season":"yaz","gender":"unisex","description":"Yaz icin yeniden yorumlanmis bir efsane.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Versace Bright Crystal","brand":"Versace","notes_top":["lemon", "pomegranate", "bergamot"],"notes_middle":["peony", "magnolia", "lotus", "water_lily"],"notes_base":["musk", "amber", "sandalwood"],"profile":{"top_pct": 40, "middle_pct": 38, "base_pct": 22},"season":"yaz","gender":"kadın","description":"Kristal berraklığında meyvemsi-çiçeksi bir yaz klasiği.","price_range":"1000-1600 TL","in_stock":True}
,
    {"name":"Davidoff Cool Water","brand":"Davidoff","notes_top":["sea_water", "mint", "lavender", "coriander"],"notes_middle":["jasmine", "geranium", "neroli", "sandalwood"],"notes_base":["amber", "musk", "cedar", "tobacco"],"profile":{"top_pct": 45, "middle_pct": 28, "base_pct": 27},"season":"yaz","gender":"erkek","description":"Okyanus ferahlığınin efsanevi maşkülen ikonu.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Davidoff Cool Water Intense","brand":"Davidoff","notes_top":["grapefruit", "mandarin", "sea_notes"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["sandalwood", "musk", "amber", "cedar"],"profile":{"top_pct": 42, "middle_pct": 28, "base_pct": 30},"season":"yaz","gender":"erkek","description":"Cool Water'\u0131n yoğun ve maşkülen yorumu.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"Armani Si","brand":"Giorgio Armani","notes_top":["black_currant", "bergamot", "mandarin"],"notes_middle":["rose", "jasmine", "freesia"],"notes_base":["vanilla", "patchouli", "amber", "oakmoss"],"profile":{"top_pct": 35, "middle_pct": 38, "base_pct": 27},"season":"yaz","gender":"kadın","description":"Modern feminenliğin narin ve güçlu yorumu.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Prada Candy","brand":"Prada","notes_top":["caramel", "orange", "bergamot"],"notes_middle":["vanilla", "benzoin", "almond"],"notes_base":["musk", "amber", "sandalwood"],"profile":{"top_pct": 35, "middle_pct": 30, "base_pct": 35},"season":"yaz","gender":"kadın","description":"Tatli karamelin sıcak ve neşeli sarisi.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Prada Candy Kiss","brand":"Prada","notes_top":["orange", "bergamot", "vanilla"],"notes_middle":["orange_blossom", "musk", "vanilla"],"notes_base":["musk", "amber", "sandalwood"],"profile":{"top_pct": 33, "middle_pct": 37, "base_pct": 30},"season":"yaz","gender":"kadın","description":"Daha hafif, daha taze bir Candy yorumu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Bvlgari Aqva","brand":"Bvlgari","notes_top":["bergamot", "orange", "sea_notes"],"notes_middle":["lavender", "sage", "rosemary"],"notes_base":["amber", "cedar", "musk"],"profile":{"top_pct": 44, "middle_pct": 30, "base_pct": 26},"season":"yaz","gender":"erkek","description":"Derin sulardan yükselen ferah ve maşkülen koku.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Bvlgari Aqva Amara","brand":"Bvlgari","notes_top":["grapefruit", "bergamot", "sea_notes"],"notes_middle":["coriander", "lavender", "olibanum"],"notes_base":["amber", "tonka", "musk"],"profile":{"top_pct": 45, "middle_pct": 28, "base_pct": 27},"season":"yaz","gender":"erkek","description":"Deniz ve Akdeniz otlarınin buluşması.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Gucci Bloom","brand":"Gucci","notes_top":["jasmine", "tuberose", "honeysuckle"],"notes_middle":["jasmine", "tuberose", "iris", "neroli"],"notes_base":["musk", "sandalwood", "vanilla"],"profile":{"top_pct": 30, "middle_pct": 48, "base_pct": 22},"season":"yaz","gender":"kadın","description":"Beyaz çiçeklerin bahçesinde yurumek gibi.","price_range":"1600-2400 TL","in_stock":True}
,
    {"name":"Allure Homme Sport","brand":"Chanel","notes_top":["bergamot", "mandarin", "orange", "sea_notes"],"notes_middle":["pepper", "nutmeg", "cedar"],"notes_base":["amber", "vanilla", "musk"],"profile":{"top_pct": 45, "middle_pct": 25, "base_pct": 30},"season":"yaz","gender":"erkek","description":"Spor bir zarafetin ferah ve odunsu ifadesi.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Allure Homme Sport Eau Extreme","brand":"Chanel","notes_top":["bergamot", "mandarin", "grapefruit"],"notes_middle":["pepper", "cedar", "sage"],"notes_base":["amber", "vanilla", "tonka"],"profile":{"top_pct": 42, "middle_pct": 28, "base_pct": 30},"season":"yaz","gender":"erkek","description":"Daha yoğun, daha ışıltılı bir spor zarafet.","price_range":"2200-3200 TL","in_stock":True}
,
    {"name":"Orange Sanguine","brand":"Atelier Cologne","notes_top":["orange", "bergamot", "mandarin", "lemon"],"notes_middle":["jasmine", "geranium", "neroli"],"notes_base":["sandalwood", "musk", "amber"],"profile":{"top_pct": 55, "middle_pct": 25, "base_pct": 20},"season":"yaz","gender":"unisex","description":"Taze sıkılmış portakal suyu gibi canlandırıcı.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Philosykos","brand":"Diptyque","notes_top":["fig_leaf", "green", "bergamot"],"notes_middle":["coconut", "fig", "green_notes"],"notes_base":["woody", "cedar", "musk"],"profile":{"top_pct": 38, "middle_pct": 35, "base_pct": 27},"season":"yaz","gender":"unisex","description":"Bir incir  ağacının gölgesinde yeşil ve kremsi bir yolculuk.","price_range":"2500-3500 TL","in_stock":True}
,
    {"name":"Eau des Sens","brand":"Diptyque","notes_top":["orange_blossom", "bitter_orange", "juniper"],"notes_middle":["angelica", "patchouli"],"notes_base":["musk", "amber", "cedar"],"profile":{"top_pct": 42, "middle_pct": 30, "base_pct": 28},"season":"yaz","gender":"unisex","description":"Portakal  ağacının her halini kucaklayan bir koku.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Hermes Un Jardin Sur Le Nil","brand":"Hermes","notes_top":["grapefruit", "green_mango", "coriander"],"notes_middle":["lotus", "water_lily", "syringa"],"notes_base":["musk", "woody", "amber"],"profile":{"top_pct": 48, "middle_pct": 32, "base_pct": 20},"season":"yaz","gender":"unisex","description":"Nil kıyısında yeşil ve meyvemsi bir bahçe.","price_range":"1500-2500 TL","in_stock":True}
,
    {"name":"Hermes Un Jardin En Mediterranee","brand":"Hermes","notes_top":["bergamot", "lemon", "orange"],"notes_middle":["fig", "juniper", "carnation"],"notes_base":["cedar", "musk", "amber", "olibanum"],"profile":{"top_pct": 42, "middle_pct": 30, "base_pct": 28},"season":"yaz","gender":"unisex","description":"Akdeniz bahçesinde bir dolaşım.","price_range":"1500-2500 TL","in_stock":True}
,
    {"name":"Neroli Portofino","brand":"Tom Ford","notes_top":["bergamot", "mandarin", "lemon", "lavender"],"notes_middle":["orange_blossom", "neroli", "jasmine"],"notes_base":["amber", "musk", "angelica"],"profile":{"top_pct": 50, "middle_pct": 30, "base_pct": 20},"season":"yaz","gender":"unisex","description":"Portofino kıyılarında narenciye çiçeklerinin büyüsü.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Costa Azzurra","brand":"Tom Ford","notes_top":["bergamot", "grapefruit", "sea_notes"],"notes_middle":["cistus", "lavender", "myrtle"],"notes_base":["cedar", "musk", "amber"],"profile":{"top_pct": 42, "middle_pct": 30, "base_pct": 28},"season":"yaz","gender":"erkek","description":"Akdeniz sahilinin vahşi ve odunsu kıyısı.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Mandarino di Amalfi","brand":"Tom Ford","notes_top":["mandarin", "grapefruit", "lemon", "bergamot"],"notes_middle":["mint", "basil", "pepper"],"notes_base":["musk", "amber", "sandalwood"],"profile":{"top_pct": 52, "middle_pct": 25, "base_pct": 23},"season":"yaz","gender":"unisex","description":"Amalfi kıyılarından taze narenciye ve otlar.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Chance Eau Tendre","brand":"Chanel","notes_top":["grapefruit", "quince", "hyacinth"],"notes_middle":["jasmine", "iris", "rose"],"notes_base":["musk", "vanilla", "amber", "cedar"],"profile":{"top_pct": 42, "middle_pct": 35, "base_pct": 23},"season":"yaz","gender":"kadın","description":"Yumusak ve romantik bir çiçek meyve dansi.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Chance Eau Fraiche","brand":"Chanel","notes_top":["cedar", "lemon", "teak"],"notes_middle":["jasmine", "water_hyacinth", "iris"],"notes_base":["musk", "vanilla", "amber", "patchouli"],"profile":{"top_pct": 45, "middle_pct": 30, "base_pct": 25},"season":"yaz","gender":"kadın","description":"Ferah ve odunsu bir Chance yorumu.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Chloe","brand":"Chloe","notes_top":["peony", "lychee", "freesia", "bergamot"],"notes_middle":["rose", "magnolia", "lily", "muguet"],"notes_base":["cedar", "amber", "musk", "vanilla"],"profile":{"top_pct": 33, "middle_pct": 38, "base_pct": 29},"season":"yaz","gender":"kadın","description":"Feminenligin narin ve zarif gülümsemesi.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Chloe Nomade","brand":"Chloe","notes_top":["bergamot", "mirabelle", "green"],"notes_middle":["freesia", "jasmine", "rose"],"notes_base":["oakmoss", "patchouli", "amber"],"profile":{"top_pct": 35, "middle_pct": 35, "base_pct": 30},"season":"yaz","gender":"kadın","description":"Ozgur ruhlu bir gezginin çiçeksi ve yosunsu izi.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Bvlgari Omnia Crystalline","brand":"Bvlgari","notes_top":["bamboo", "pear", "water"],"notes_middle":["lotus", "buttercup", "water_lily"],"notes_base":["musk", "quince", "sandalwood"],"profile":{"top_pct": 44, "middle_pct": 33, "base_pct": 23},"season":"yaz","gender":"kadın","description":"Kristal berraklığında bir su bahçesi.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Bvlgari Splendida Iris d'Or","brand":"Bvlgari","notes_top":["bergamot", "orange", "narcissus"],"notes_middle":["iris", "jasmine", "rose"],"notes_base":["vanilla", "musk", "amber"],"profile":{"top_pct": 35, "middle_pct": 42, "base_pct": 23},"season":"yaz","gender":"kadın","description":"Iris çiçeğinin pudralı ve asil duruyor.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Eternity","brand":"Calvin Klein","notes_top":["mandarin", "bergamot", "lemon"],"notes_middle":["jasmine", "rose", "narcissus", "violet"],"notes_base":["sandalwood", "musk", "amber", "vanilla"],"profile":{"top_pct": 38, "middle_pct": 37, "base_pct": 25},"season":"yaz","gender":"kadın","description":"Sonsuzluga adanmis bir çiçeksi klasik.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Eternity Air","brand":"Calvin Klein","notes_top":["bergamot", "pear", "water"],"notes_middle":["jasmine", "iris", "lily"],"notes_base":["musk", "sandalwood", "amber"],"profile":{"top_pct": 44, "middle_pct": 32, "base_pct": 24},"season":"yaz","gender":"kadın","description":"Hafif ve havadar bir Eternity yorumu.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Polo Blue","brand":"Ralph Lauren","notes_top":["cucumber", "bergamot", "melon"],"notes_middle":["basil", "sage", "geranium"],"notes_base":["musk", "amber", "suede"],"profile":{"top_pct": 46, "middle_pct": 28, "base_pct": 26},"season":"yaz","gender":"erkek","description":"Ferah ve maşkülen bir sucul klasik.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"Polo Red","brand":"Ralph Lauren","notes_top":["grapefruit", "orange", "lemon"],"notes_middle":["cranberry", "sage", "lavender"],"notes_base":["coffee", "amber", "cedar"],"profile":{"top_pct": 42, "middle_pct": 30, "base_pct": 28},"season":"yaz","gender":"erkek","description":"Enerjik, sıcak ve maşkülen bir koku.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"Aqua di Parma Colonia","brand":"Acqua di Parma","notes_top":["bergamot", "lemon", "orange", "neroli"],"notes_middle":["lavender", "rose", "violet"],"notes_base":["musk", "amber", "sandalwood", "vetiver"],"profile":{"top_pct": 50, "middle_pct": 28, "base_pct": 22},"season":"yaz","gender":"unisex","description":"Italyan zarafetinin zamansiz kolonyasi.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Fico di Amalfi","brand":"Acqua di Parma","notes_top":["bergamot", "lemon", "grapefruit"],"notes_middle":["fig", "juniper", "pink_pepper"],"notes_base":["cedar", "musk", "benzoin"],"profile":{"top_pct": 46, "middle_pct": 30, "base_pct": 24},"season":"yaz","gender":"unisex","description":"Amalfi incir bahçelerinde bir yolculuk.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Florabotanica","brand":"Balenciaga","notes_top":["mint", "pepper", "cannabis"],"notes_middle":["rose", "violet", "iris"],"notes_base":["musk", "amber", "patchouli", "oakmoss"],"profile":{"top_pct": 40, "middle_pct": 35, "base_pct": 25},"season":"yaz","gender":"kadın","description":"Modern ve yeşil bir botanik bahçe.","price_range":"800-1300 TL","in_stock":True}
,
    {"name":"Mojave Ghost","brand":"Byredo","notes_top":["bergamot", "juniper", "angelica"],"notes_middle":["mimosa", "violet", "sandalwood"],"notes_base":["musk", "amber", "cedar"],"profile":{"top_pct": 40, "middle_pct": 33, "base_pct": 27},"season":"yaz","gender":"unisex","description":"Colun ortasinda acan nadide bir çiçek.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Bal d'Afrique","brand":"Byredo","notes_top":["bergamot", "lemon", "marigold"],"notes_middle":["violet", "jasmine", "cyclamen"],"notes_base":["musk", "amber", "vetiver"],"profile":{"top_pct": 42, "middle_pct": 33, "base_pct": 25},"season":"yaz","gender":"unisex","description":"Afrika'nin sıcak ve neşeli dans partisi.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Blanche","brand":"Byredo","notes_top":["aldehyde", "white_rose", "pink_pepper"],"notes_middle":["violet", "musk", "neroli"],"notes_base":["sandalwood", "cedar", "vanilla"],"profile":{"top_pct": 48, "middle_pct": 28, "base_pct": 24},"season":"yaz","gender":"unisex","description":"Bembeyaz temiz bir sayfa gibi saf ve duru.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Beach Walk","brand":"Maison Margiela","notes_top":["bergamot", "lemon", "pink_pepper"],"notes_middle":["ylang", "coconut", "heliotrope"],"notes_base":["musk", "amber", "benzoin", "cedar"],"profile":{"top_pct": 42, "middle_pct": 35, "base_pct": 23},"season":"yaz","gender":"kadın","description":"Bir plaj günunun anısini sise hapsetmek.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Sailing Day","brand":"Maison Margiela","notes_top":["sea_notes", "aldehyde", "bergamot"],"notes_middle":["lavender", "iris", "rose"],"notes_base":["musk", "amber", "cedar"],"profile":{"top_pct": 50, "middle_pct": 25, "base_pct": 25},"season":"yaz","gender":"unisex","description":"Acik denizde ruzgarla dans eden bir yelkenli.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Under the Lemon Trees","brand":"Maison Margiela","notes_top":["lemon", "mandarin", "bergamot"],"notes_middle":["green_notes", "coriander", "tea"],"notes_base":["musk", "amber", "woody"],"profile":{"top_pct": 55, "middle_pct": 25, "base_pct": 20},"season":"yaz","gender":"unisex","description":"Limon agaclarinin altında huzurlu bir oglen.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Versace Bright Crystal Absolu","brand":"Versace","notes_top":["pomegranate", "bergamot", "ice"],"notes_middle":["peony", "magnolia", "lotus"],"notes_base":["musk", "amber", "sandalwood"],"profile":{"top_pct": 40, "middle_pct": 38, "base_pct": 22},"season":"yaz","gender":"kadın","description":"Daha yoğun ve ışıltılı bir Bright Crystal.","price_range":"1000-1600 TL","in_stock":True}
,
    {"name":"Kenzo World","brand":"Kenzo","notes_top":["pepper", "bergamot", "raspberry"],"notes_middle":["iris", "jasmine", "peony"],"notes_base":["musk", "amber", "cedar"],"profile":{"top_pct": 38, "middle_pct": 40, "base_pct": 22},"season":"yaz","gender":"kadın","description":"Cesur ve enerjik bir çiçeksel patlama.","price_range":"800-1300 TL","in_stock":True}
,
    {"name":"Kenzo Flower","brand":"Kenzo","notes_top":["hawthorn", "rose", "bergamot"],"notes_middle":["jasmine", "violet", "rose"],"notes_base":["musk", "vanilla", "amber"],"profile":{"top_pct": 35, "middle_pct": 42, "base_pct": 23},"season":"yaz","gender":"kadın","description":"Gelincik tarlasinda ruzgarin fiskirmasi.","price_range":"800-1300 TL","in_stock":True}
,
    {"name":"Moschino Fresh Couture","brand":"Moschino","notes_top":["bergamot", "mandarin", "lemon"],"notes_middle":["jasmine", "rose", "peony"],"notes_base":["musk", "sandalwood", "amber"],"profile":{"top_pct": 45, "middle_pct": 30, "base_pct": 25},"season":"yaz","gender":"kadın","description":"Temizlik urunu sisesinde sakli çiçeksi bir surpriz.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"Gucci Flora Gorgeous Gardenia","brand":"Gucci","notes_top":["gardenia", "jasmine", "bergamot"],"notes_middle":["jasmine", "tuberose", "hibiscus"],"notes_base":["musk", "vanilla", "sandalwood", "patchouli"],"profile":{"top_pct": 38, "middle_pct": 42, "base_pct": 20},"season":"yaz","gender":"kadın","description":"Bir bahçe partisinin çiçeksi nefesi.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Burberry Brit Sheer","brand":"Burberry","notes_top":["mandarin", "honeysuckle", "ice"],"notes_middle":["peony", "almond", "jasmine"],"notes_base":["musk", "amber", "vanilla"],"profile":{"top_pct": 42, "middle_pct": 33, "base_pct": 25},"season":"yaz","gender":"kadın","description":"Hafif, neşeli ve çiçeksi bir Burberry yorumu.","price_range":"800-1300 TL","in_stock":True}
,
    {"name":"Lancome Idole","brand":"Lancome","notes_top":["bergamot", "pear", "pink_pepper"],"notes_middle":["rose", "jasmine", "iris"],"notes_base":["vanilla", "musk", "cedar", "patchouli"],"profile":{"top_pct": 38, "middle_pct": 40, "base_pct": 22},"season":"yaz","gender":"kadın","description":"Modern feminenliğin ışıltılı ve çiçeksi idolu.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"YSL Libre","brand":"Yves Saint Laurent","notes_top":["lavender", "mandarin", "bergamot"],"notes_middle":["lavender", "jasmine", "orange_blossom"],"notes_base":["vanilla", "musk", "amber", "cedar"],"profile":{"top_pct": 35, "middle_pct": 38, "base_pct": 27},"season":"yaz","gender":"kadın","description":"Ozgur kadının lavanta-çiçek imzasi.","price_range":"1600-2400 TL","in_stock":True}
,
    {"name":"YSL L'Homme","brand":"Yves Saint Laurent","notes_top":["ginger", "bergamot", "lemon"],"notes_middle":["cedar", "violet", "pepper"],"notes_base":["musk", "amber", "tonka"],"profile":{"top_pct": 40, "middle_pct": 32, "base_pct": 28},"season":"yaz","gender":"erkek","description":"Modern erkeğin zarif ve çekici kokusu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Givenchy L'Interdit","brand":"Givenchy","notes_top":["bergamot", "pear", "blood_orange"],"notes_middle":["jasmine", "rose", "tuberose", "orange_blossom"],"notes_base":["vanilla", "patchouli", "ambroxan", "cedar"],"profile":{"top_pct": 30, "middle_pct": 40, "base_pct": 30},"season":"yaz","gender":"kadın","description":"Yasak çiçeklerin bastan çıkaranici beyaz buketi.","price_range":"1600-2400 TL","in_stock":True}
,
    {"name":"Dolce & Gabbana Dolce","brand":"Dolce & Gabbana","notes_top":["neroli", "papaya", "bergamot"],"notes_middle":["jasmine", "lily", "rose"],"notes_base":["musk", "sandalwood", "amber"],"profile":{"top_pct": 38, "middle_pct": 42, "base_pct": 20},"season":"yaz","gender":"kadın","description":"Beyaz çiçeklerin saf ve masum buketi.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Acqua di Parma Colonia Essenza","brand":"Acqua di Parma","notes_top":["bergamot", "lemon", "neroli", "orange"],"notes_middle":["lavender", "rose", "jasmine"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 48, "middle_pct": 28, "base_pct": 24},"season":"yaz","gender":"unisex","description":"Colonia'nin daha yoğun ve kalıcı versiyonu.","price_range":"2500-3500 TL","in_stock":True}
,
    {"name":"Acqua di Parma Mirto di Panarea","brand":"Acqua di Parma","notes_top":["myrtle", "bergamot", "lemon"],"notes_middle":["jasmine", "rose", "lavender"],"notes_base":["cedar", "musk", "amber"],"profile":{"top_pct": 44, "middle_pct": 30, "base_pct": 26},"season":"yaz","gender":"unisex","description":"Panarea adasinin mersin kokulu Akdeniz ruzgari.","price_range":"2200-3200 TL","in_stock":True}
,
    {"name":"Jo Malone Peony & Blush Suede","brand":"Jo Malone","notes_top":["red_apple", "bergamot", "peony"],"notes_middle":["peony", "jasmine", "rose"],"notes_base":["suede", "musk", "vanilla"],"profile":{"top_pct": 38, "middle_pct": 40, "base_pct": 22},"season":"yaz","gender":"kadın","description":"Peoninin narinden suetin sıcakligina.","price_range":"1800-2800 TL","in_stock":True}
,
    {"name":"Jo Malone English Pear & Freesia","brand":"Jo Malone","notes_top":["pear", "bergamot", "lemon"],"notes_middle":["freesia", "jasmine", "rose"],"notes_base":["musk", "amber", "patchouli", "vanilla"],"profile":{"top_pct": 42, "middle_pct": 35, "base_pct": 23},"season":"yaz","gender":"kadın","description":"Ingiliz armutunun sulu ve çiçeksi dansi.","price_range":"1800-2800 TL","in_stock":True}
,
    {"name":"Jo Malone Wild Bluebell","brand":"Jo Malone","notes_top":["bluebell", "bergamot", "cucumber"],"notes_middle":["jasmine", "lily", "rose"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 44, "middle_pct": 34, "base_pct": 22},"season":"yaz","gender":"kadın","description":"Yabani bir orman çiçeğinin tazeligi.","price_range":"1800-2800 TL","in_stock":True}
,
    {"name":"Byredo Rose of No Man's Land","brand":"Byredo","notes_top":["pink_pepper", "rose", "raspberry"],"notes_middle":["rose", "iris", "violet"],"notes_base":["musk", "vanilla", "amber", "cedar"],"profile":{"top_pct": 35, "middle_pct": 38, "base_pct": 27},"season":"yaz","gender":"kadın","description":"Savasta acan bir güle saygi duruyor.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Byredo Pulp","brand":"Byredo","notes_top":["bergamot", "apple", "lemon"],"notes_middle":["jasmine", "fruity", "red_fruit"],"notes_base":["musk", "vanilla", "amber", "cedar"],"profile":{"top_pct": 45, "middle_pct": 30, "base_pct": 25},"season":"yaz","gender":"unisex","description":"Olgün meyvelerin sulu ve tatlı patlaması.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Diptyque Do Son","brand":"Diptyque","notes_top":["bergamot", "pepper", "iris"],"notes_middle":["tuberose", "jasmine", "orange_blossom"],"notes_base":["musk", "amber", "benzoin", "sandalwood"],"profile":{"top_pct": 30, "middle_pct": 48, "base_pct": 22},"season":"yaz","gender":"kadın","description":"Tuberose çiçeğinin bastan çıkaranici buketi.","price_range":"2200-3200 TL","in_stock":True}
,
    {"name":"Diptyque Fleur de Peau","brand":"Diptyque","notes_top":["bergamot", "aldehyde", "pepper"],"notes_middle":["iris", "jasmine", "rose"],"notes_base":["musk", "amber", "vanilla", "sandalwood"],"profile":{"top_pct": 35, "middle_pct": 38, "base_pct": 27},"season":"yaz","gender":"unisex","description":"Ten uzerinde acan bir çiçeğin miski.","price_range":"2200-3200 TL","in_stock":True}
,
    {"name":"Diptyque Olene","brand":"Diptyque","notes_top":["bergamot", "narcissus", "honeysuckle"],"notes_middle":["jasmine", "lily", "wisteria"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 32, "middle_pct": 46, "base_pct": 22},"season":"yaz","gender":"kadın","description":"Bir Venedik bahçesinde yasemin ve zambak buluşması.","price_range":"2200-3200 TL","in_stock":True}
,
    {"name":"Maison Margiela Lazy Sunday Morning","brand":"Maison Margiela","notes_top":["aldehyde", "pear", "bergamot"],"notes_middle":["iris", "rose", "orange_blossom"],"notes_base":["musk", "vanilla", "amber", "cedar"],"profile":{"top_pct": 42, "middle_pct": 33, "base_pct": 25},"season":"yaz","gender":"unisex","description":"Temiz carsaflar ve pazar sabahi huzuru.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Maison Margiela Flower Market","brand":"Maison Margiela","notes_top":["bergamot", "green", "pepper"],"notes_middle":["jasmine", "rose", "tuberose", "freesia"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 32, "middle_pct": 48, "base_pct": 20},"season":"yaz","gender":"kadın","description":"Paris çiçek pazarinda bir sabah gezintisi.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Tom Ford Soleil Blanc","brand":"Tom Ford","notes_top":["bergamot", "pistachio", "cardamom"],"notes_middle":["tuberose", "jasmine", "ylang"],"notes_base":["vanilla", "amber", "musk", "coconut"],"profile":{"top_pct": 35, "middle_pct": 35, "base_pct": 30},"season":"yaz","gender":"kadın","description":"Guneslenen tenin sıcak ve kremsi kokusu.","price_range":"3500-5000 TL","in_stock":True}
,
    {"name":"Tom Ford Eau de Soleil Blanc","brand":"Tom Ford","notes_top":["bergamot", "pepper", "cucumber"],"notes_middle":["jasmine", "tuberose", "orange_blossom"],"notes_base":["musk", "amber", "vanilla", "sandalwood"],"profile":{"top_pct": 42, "middle_pct": 30, "base_pct": 28},"season":"yaz","gender":"kadın","description":"Soleil Blanc'in daha ferah ve ışıltılı yorumu.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Tom Ford Ombre de Hyacinth","brand":"Tom Ford","notes_top":["hyacinth", "bergamot", "green"],"notes_middle":["jasmine", "iris", "clove"],"notes_base":["musk", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 42, "middle_pct": 32, "base_pct": 26},"season":"yaz","gender":"unisex","description":"Yesil ve çiçeksi bir bahar sabahi.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Hermes Eau de Rhubarbe Ecarlate","brand":"Hermes","notes_top":["rhubarb", "bergamot", "lemon"],"notes_middle":["jasmine", "rose", "musk"],"notes_base":["musk", "cedar", "vanilla", "amber"],"profile":{"top_pct": 48, "middle_pct": 28, "base_pct": 24},"season":"yaz","gender":"unisex","description":"Ekstasi raventin ferah ve enerjik patlaması.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Hermes Eau de Citron Noir","brand":"Hermes","notes_top":["lemon", "bergamot", "grapefruit"],"notes_middle":["jasmine", "green_tea", "ginger"],"notes_base":["musk", "amber", "cedar", "vanilla"],"profile":{"top_pct": 50, "middle_pct": 25, "base_pct": 25},"season":"yaz","gender":"unisex","description":"Kara limonun derin ve isli ferahlığı.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Guerlain Aqua Allegoria Pera Granita","brand":"Guerlain","notes_top":["pear", "bergamot", "lemon"],"notes_middle":["jasmine", "iris", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 46, "middle_pct": 30, "base_pct": 24},"season":"yaz","gender":"kadın","description":"Armut granitasinin buzlu ve sulu ferahlığı.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Guerlain Aqua Allegoria Bergamote Calabria","brand":"Guerlain","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "ginger", "patchouli"],"notes_base":["musk", "amber", "cedar", "vanilla"],"profile":{"top_pct": 52, "middle_pct": 25, "base_pct": 23},"season":"yaz","gender":"unisex","description":"Kalabrya bergamotunun günesli parıltısı.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Chanel Cristalle","brand":"Chanel","notes_top":["bergamot", "lemon", "hyacinth"],"notes_middle":["jasmine", "rose", "lily"],"notes_base":["musk", "amber", "vetiver", "cedar"],"profile":{"top_pct": 45, "middle_pct": 30, "base_pct": 25},"season":"yaz","gender":"kadın","description":"Kristal berraklığında yeşil-çiçeksi bir Chanel klasiği.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Dior Diorissimo","brand":"Dior","notes_top":["bergamot", "lily", "green"],"notes_middle":["lily", "muguet", "jasmine", "rose"],"notes_base":["musk", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 38, "middle_pct": 44, "base_pct": 18},"season":"yaz","gender":"kadın","description":"Vadideki zambagin en saf ve en asil ifadesi.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Creed Original Vetiver","brand":"Creed","notes_top":["bergamot", "mandarin", "lemon"],"notes_middle":["vetiver", "iris", "rose"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 42, "middle_pct": 28, "base_pct": 30},"season":"yaz","gender":"erkek","description":"Vetiverin en asil ve en klasik yorumu.","price_range":"3500-5000 TL","in_stock":True}
,
    {"name":"Creed Himalaya","brand":"Creed","notes_top":["bergamot", "grapefruit", "lemon"],"notes_middle":["jasmine", "rose", "sandalwood"],"notes_base":["musk", "amber", "cedar", "vanilla"],"profile":{"top_pct": 42, "middle_pct": 30, "base_pct": 28},"season":"yaz","gender":"erkek","description":"Himalaya zirvelerinin temiz ve maşkülen kokusu.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Penhaligons Juniper Sling","brand":"Penhaligons","notes_top":["juniper", "bergamot", "orange"],"notes_middle":["rose", "pepper", "coriander"],"notes_base":["musk", "amber", "cedar", "vanilla"],"profile":{"top_pct": 44, "middle_pct": 28, "base_pct": 28},"season":"yaz","gender":"unisex","description":"Cin ve ardicin London'daki en zarif dansi.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Penhaligons Blenheim Bouquet","brand":"Penhaligons","notes_top":["lemon", "bergamot", "pine"],"notes_middle":["lavender", "rosemary", "pepper"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 48, "middle_pct": 26, "base_pct": 26},"season":"yaz","gender":"erkek","description":"Ingiliz kirlarindan bir narenciye buketi.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Lalique White","brand":"Lalique","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "iris", "geranium"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 44, "middle_pct": 28, "base_pct": 28},"season":"yaz","gender":"erkek","description":"Bembeyaz bir temizlik ve zarafet.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"Bentley Azure","brand":"Bentley","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 44, "middle_pct": 28, "base_pct": 28},"season":"yaz","gender":"erkek","description":"Luks bir otomobilin ferah yaz kokusu.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"Mercedes-Benz Man Pure","brand":"Mercedes-Benz","notes_top":["bergamot", "mandarin", "lemon"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 42, "middle_pct": 28, "base_pct": 30},"season":"yaz","gender":"erkek","description":"Alman mhendisliginin maşkülen ve ferah yuzu.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Nautica Voyage","brand":"Nautica","notes_top":["apple", "bergamot", "water"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "cedar", "oakmoss"],"profile":{"top_pct": 46, "middle_pct": 26, "base_pct": 28},"season":"yaz","gender":"erkek","description":"Uygün fiyatli bir deniz yolculugünun kokusu.","price_range":"300-500 TL","in_stock":True}
,
    {"name":"Abercrombie Fierce","brand":"Abercrombie & Fitch","notes_top":["lemon", "bergamot", "mandarin"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 44, "middle_pct": 28, "base_pct": 28},"season":"yaz","gender":"erkek","description":"2000'lerin efsanevi maşkülen alisveris merkezi kokusu.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Hollister Jake","brand":"Hollister","notes_top":["grapefruit", "mandarin", "lemon"],"notes_middle":["jasmine", "rose", "lavender"],"notes_base":["musk", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 46, "middle_pct": 26, "base_pct": 28},"season":"yaz","gender":"erkek","description":"Kaliforniya sahillerinin genç ve enerjik kokusu.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"Guess Girl","brand":"Guess","notes_top":["bergamot", "mandarin", "pear"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 44, "middle_pct": 30, "base_pct": 26},"season":"yaz","gender":"kadın","description":"Genc ve eglenceli bir kiz cocugu enerjisi.","price_range":"300-600 TL","in_stock":True}
,
    {"name":"Tous Baby Doll","brand":"Tous","notes_top":["bergamot", "mandarin", "raspberry"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 44, "middle_pct": 30, "base_pct": 26},"season":"yaz","gender":"kadın","description":"Oyuncak ayi kadar tatlı ve sevimli bir koku.","price_range":"500-800 TL","in_stock":True}
,
    {"name":"Tous Floral Touch","brand":"Tous","notes_top":["bergamot", "mandarin", "peony"],"notes_middle":["jasmine", "rose", "lily"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 38, "middle_pct": 38, "base_pct": 24},"season":"yaz","gender":"kadın","description":"Ciceksi ve pudralı bir Touche dokunusu.","price_range":"500-800 TL","in_stock":True}
,
    {"name":"Loewe 7","brand":"Loewe","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["rose", "jasmine", "violet"],"notes_base":["musk", "amber", "cedar", "vanilla"],"profile":{"top_pct": 40, "middle_pct": 32, "base_pct": 28},"season":"yaz","gender":"kadın","description":"Ispanyol bir çiçek bahçesinin zarif yorumu.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Salvatore Ferragamo Incanto Shine","brand":"Salvatore Ferragamo","notes_top":["bergamot", "lemon", "pineapple"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 46, "middle_pct": 28, "base_pct": 26},"season":"yaz","gender":"kadın","description":"Italyan güneşinin ışıltılı ve meyvemsi yansıması.","price_range":"500-800 TL","in_stock":True}
,
    {"name":"Salvatore Ferragamo Incanto Bloom","brand":"Salvatore Ferragamo","notes_top":["bergamot", "mandarin", "pear"],"notes_middle":["jasmine", "rose", "peony"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 40, "middle_pct": 36, "base_pct": 24},"season":"yaz","gender":"kadın","description":"Ackan bir bahçenin neşeli çiçeksel kokusu.","price_range":"500-800 TL","in_stock":True}
,
    {"name":"Police To Be Woman","brand":"Police","notes_top":["bergamot", "mandarin", "raspberry"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 42, "middle_pct": 32, "base_pct": 26},"season":"yaz","gender":"kadın","description":"Bir polis memuru kadar dikkat çekici ve güçlu.","price_range":"300-500 TL","in_stock":True}
,
    {"name":"Marc Jacobs Perfect","brand":"Marc Jacobs","notes_top":["bergamot", "mandarin", "rhubarb"],"notes_middle":["jasmine", "rose", "almond"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 42, "middle_pct": 33, "base_pct": 25},"season":"yaz","gender":"kadın","description":"Mukemmel olmanin keyfini çıkaranan bir koku.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Marc Jacobs Dot","brand":"Marc Jacobs","notes_top":["bergamot", "mandarin", "raspberry"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 42, "middle_pct": 34, "base_pct": 24},"season":"yaz","gender":"kadın","description":"Nokta kadar sevimli ve çiçeksi bir koku.","price_range":"1000-1600 TL","in_stock":True}
,
    {"name":"Nina Ricci Nina","brand":"Nina Ricci","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 44, "middle_pct": 30, "base_pct": 26},"season":"yaz","gender":"kadın","description":"Elma seklindeki sisesinden yayilan tatlı-çiçeksi bir koku.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"Anna Sui Secret Wish","brand":"Anna Sui","notes_top":["bergamot", "lemon", "raspberry"],"notes_middle":["jasmine", "rose", "peony"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 44, "middle_pct": 30, "base_pct": 26},"season":"yaz","gender":"kadın","description":"Peri masalindaki gizli dilek kadar büyülüyor.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Vera Wang Princess","brand":"Vera Wang","notes_top":["bergamot", "mandarin", "apple"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 42, "middle_pct": 32, "base_pct": 26},"season":"yaz","gender":"kadın","description":"Bir prensese yakisir meyvemsi-çiçeksi zarafet.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"Xerjoff Nio","brand":"Xerjoff","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 55, "middle_pct": 22, "base_pct": 23},"season":"yaz","gender":"unisex","description":"Nis pazarinda narenciyenin zirvesi.","price_range":"5000-7500 TL","in_stock":True}
,
    {"name":"Xerjoff Mefisto","brand":"Xerjoff","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "violet", "iris"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 44, "middle_pct": 30, "base_pct": 26},"season":"yaz","gender":"unisex","description":"Bir Italyan nis markasinin ferah ve asil yuzu.","price_range":"5000-7500 TL","in_stock":True}
,
    {"name":"Roja Parfums Elysium","brand":"Roja Parfums","notes_top":["grapefruit", "lemon", "bergamot", "lime"],"notes_middle":["jasmine", "rose", "coriander", "sage"],"notes_base":["musk", "amber", "cedar", "vanilla"],"profile":{"top_pct": 48, "middle_pct": 26, "base_pct": 26},"season":"yaz","gender":"unisex","description":"Cennetin en l\u00fcks narenciye yorumu.","price_range":"8000-12000 TL","in_stock":True}
,
    # ===== KIS (Winter) — 102 perfumes =====
    {"name":"Black Opium","brand":"Yves Saint Laurent","notes_top":["coffee", "pink_pepper", "orange_blossom"],"notes_middle":["jasmine", "bitter_almond", "licorice"],"notes_base":["vanilla", "cedar", "patchouli", "musk"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"kis","gender":"kadın","description":"Karanlik ve bagimlilik yaratan vanilya-kahve dueti.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"La Vie Est Belle","brand":"Lancome","notes_top":["black_currant", "pear", "orange_blossom"],"notes_middle":["iris", "jasmine", "orange_blossom"],"notes_base":["vanilla", "patchouli", "tonka", "praline"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"kis","gender":"kadın","description":"Mutlulugün kokusu: iris, vanilya ve paculi dansi.","price_range":"1600-2400 TL","in_stock":True}
,
    {"name":"Good Girl","brand":"Carolina Herrera","notes_top":["almond", "coffee", "bergamot", "lemon"],"notes_middle":["jasmine", "tuberose", "iris", "orange_blossom"],"notes_base":["vanilla", "cocoa", "tonka", "cedar"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"kis","gender":"kadın","description":"Topuklu ayakkabi sisesinde çiçeksi-gurme başyapıt.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Terre d'Hermes","brand":"Hermes","notes_top":["orange", "grapefruit", "pepper"],"notes_middle":["geranium", "patchouli", "cedar"],"notes_base":["vetiver", "benzoin", "oakmoss", "leather"],"profile":{"top_pct": 22, "middle_pct": 28, "base_pct": 50},"season":"kis","gender":"erkek","description":"Topragin ve gökyüzünun zamansiz buluşması.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Spicebomb","brand":"Viktor & Rolf","notes_top":["pink_pepper", "bergamot", "grapefruit"],"notes_middle":["cinnamon", "saffron", "paprika", "chili"],"notes_base":["tobacco", "leather", "vetiver", "amber"],"profile":{"top_pct": 30, "middle_pct": 30, "base_pct": 40},"season":"kis","gender":"erkek","description":"Baharatin ve derinin patlayici fuzyonu.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Spicebomb Extreme","brand":"Viktor & Rolf","notes_top":["bergamot", "grapefruit", "pink_pepper"],"notes_middle":["cinnamon", "saffron", "cumin"],"notes_base":["vanilla", "tobacco", "leather", "tonka"],"profile":{"top_pct": 25, "middle_pct": 28, "base_pct": 47},"season":"kis","gender":"erkek","description":"Spicebomb'\u00fcn daha sıcak ve yoğun iksiri.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"1 Million","brand":"Paco Rabanne","notes_top":["grapefruit", "peppermint", "blood_mandarin"],"notes_middle":["rose", "cinnamon", "spice"],"notes_base":["leather", "amber", "patchouli", "vanilla"],"profile":{"top_pct": 28, "middle_pct": 27, "base_pct": 45},"season":"kis","gender":"erkek","description":"Altin kulcede cesur ve ışıltılı maşkülenlik.","price_range":"1300-1900 TL","in_stock":True}
,
    {"name":"1 Million Lucky","brand":"Paco Rabanne","notes_top":["plum", "grapefruit", "bergamot"],"notes_middle":["honey", "cedar", "patchouli"],"notes_base":["amber", "tonka", "vanilla", "musk"],"profile":{"top_pct": 28, "middle_pct": 28, "base_pct": 44},"season":"kis","gender":"erkek","description":"1 Million'un daha tatlı ve sansli kardesi.","price_range":"1300-1900 TL","in_stock":True}
,
    {"name":"Alien","brand":"Thierry Mugler","notes_top":["jasmine", "solar_notes"],"notes_middle":["cashmeran", "wood", "amber"],"notes_base":["white_musk", "sandalwood", "vanilla"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"kis","gender":"kadın","description":"Dunya disi, büyülüyor ve zamansiz bir amber-oriental.","price_range":"1600-2400 TL","in_stock":True}
,
    {"name":"Angel","brand":"Thierry Mugler","notes_top":["cotton_candy", "bergamot", "tropical_fruit"],"notes_middle":["vanilla", "caramel", "chocolate", "rose"],"notes_base":["patchouli", "amber", "musk", "cedar"],"profile":{"top_pct": 28, "middle_pct": 32, "base_pct": 40},"season":"kis","gender":"kadın","description":"Gurme parfüm akiminin devrim niteliğindeki oncusu.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Baccarat Rouge 540","brand":"Maison Francis Kurkdjian","notes_top":["saffron", "jasmine"],"notes_middle":["cedar", "amber", "ambre"],"notes_base":["musk", "vanilla", "fir_resin"],"profile":{"top_pct": 20, "middle_pct": 28, "base_pct": 52},"season":"kis","gender":"unisex","description":"Kristal bir safran-amber ışıltısi, modern bir efsane.","price_range":"5000-7500 TL","in_stock":True}
,
    {"name":"Oud Wood","brand":"Tom Ford","notes_top":["oud", "sandalwood", "cardamom", "pepper"],"notes_middle":["vanilla", "tonka", "cinnamon"],"notes_base":["amber", "musk", "cedar", "patchouli"],"profile":{"top_pct": 22, "middle_pct": 28, "base_pct": 50},"season":"kis","gender":"unisex","description":"Oudun en sofistike ve ulasilabilir yorumu.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Tobacco Vanille","brand":"Tom Ford","notes_top":["tobacco", "vanilla", "chocolate"],"notes_middle":["tonka", "tobacco_blossom", "cinnamon"],"notes_base":["vanilla", "benzoin", "musk", "dried_fruit"],"profile":{"top_pct": 18, "middle_pct": 27, "base_pct": 55},"season":"kis","gender":"unisex","description":"Tutun ve vanilyanın en lüks ve sıcak yorumu.","price_range":"3500-5000 TL","in_stock":True}
,
    {"name":"Santal 33","brand":"Le Labo","notes_top":["violet", "cardamom", "iris"],"notes_middle":["sandalwood", "cedar", "leather"],"notes_base":["musk", "vanilla", "amber"],"profile":{"top_pct": 20, "middle_pct": 32, "base_pct": 48},"season":"kis","gender":"unisex","description":"Modern cagin en ikonik sandal  ağacı yorumu.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Eros","brand":"Versace","notes_top":["mint", "green_apple", "lemon"],"notes_middle":["tonka", "amber", "geranium"],"notes_base":["vanilla", "oakmoss", "cedar", "patchouli"],"profile":{"top_pct": 32, "middle_pct": 28, "base_pct": 40},"season":"kis","gender":"erkek","description":"Tutkulu, güçlu ve Yunan tanrisi kadar iddiali.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Eros Flame","brand":"Versace","notes_top":["mandarin", "lemon", "pepper"],"notes_middle":["rose", "jasmine", "patchouli"],"notes_base":["musk", "amber", "tonka", "vanilla"],"profile":{"top_pct": 30, "middle_pct": 30, "base_pct": 40},"season":"kis","gender":"erkek","description":"Eros'un daha atesli ve enerjik versiyonu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Encre Noire","brand":"Lalique","notes_top":["cypress", "bergamot"],"notes_middle":["vetiver", "cedar", "patchouli"],"notes_base":["musk", "amber", "leather"],"profile":{"top_pct": 18, "middle_pct": 32, "base_pct": 50},"season":"kis","gender":"erkek","description":"Karanlik bir ormanin derinliklerinde kara murekkep.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"Black Orchid","brand":"Tom Ford","notes_top":["jasmine", "bergamot", "lemon", "truffle"],"notes_middle":["orchid", "patchouli", "sandalwood", "vetiver"],"notes_base":["amber", "vanilla", "incense", "musk"],"profile":{"top_pct": 22, "middle_pct": 28, "base_pct": 50},"season":"kis","gender":"unisex","description":"Karanlik çiçeklerin ve egzotik baharatlarin dansi.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Portrait of a Lady","brand":"Frederic Malle","notes_top":["rose", "raspberry", "cinnamon"],"notes_middle":["rose", "sandalwood", "patchouli"],"notes_base":["amber", "benzoin", "musk", "frankincense"],"profile":{"top_pct": 18, "middle_pct": 35, "base_pct": 47},"season":"kis","gender":"kadın","description":"Bir kadının portresinde bin gül yapragi.","price_range":"5000-7500 TL","in_stock":True}
,
    {"name":"Musc Ravageur","brand":"Frederic Malle","notes_top":["bergamot", "mandarin", "cinnamon"],"notes_middle":["clove", "jasmine", "rose"],"notes_base":["musk", "vanilla", "amber", "tonka"],"profile":{"top_pct": 20, "middle_pct": 28, "base_pct": 52},"season":"kis","gender":"unisex","description":"Miskin en vahşi ve en zarif yorumu.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Scandal","brand":"Jean Paul Gaultier","notes_top":["blood_mandarin", "bergamot", "pear"],"notes_middle":["jasmine", "rose", "honey", "peach"],"notes_base":["vanilla", "tonka", "patchouli", "caramel"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"kis","gender":"kadın","description":"Bal ve vanilyanın skandal kokusu.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"La Belle","brand":"Jean Paul Gaultier","notes_top":["bergamot", "pear"],"notes_middle":["jasmine", "tuberose", "iris"],"notes_base":["vanilla", "tonka", "sandalwood", "musk"],"profile":{"top_pct": 25, "middle_pct": 28, "base_pct": 47},"season":"kis","gender":"kadın","description":"Vanilyanin ve armutun bastan çıkaranan ikilisi.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Le Male","brand":"Jean Paul Gaultier","notes_top":["mint", "lavender", "bergamot", "cardamom"],"notes_middle":["cinnamon", "orange_blossom", "caraway"],"notes_base":["vanilla", "tonka", "sandalwood", "cedar"],"profile":{"top_pct": 30, "middle_pct": 32, "base_pct": 38},"season":"kis","gender":"erkek","description":"Maşkulenligin ikonik vanilya-lavanta yorumu.","price_range":"1300-1900 TL","in_stock":True}
,
    {"name":"Le Beau","brand":"Jean Paul Gaultier","notes_top":["bergamot", "coconut", "green"],"notes_middle":["tonka", "cinnamon", "amber"],"notes_base":["sandalwood", "vanilla", "musk"],"profile":{"top_pct": 30, "middle_pct": 28, "base_pct": 42},"season":"kis","gender":"erkek","description":"Yakışlık bir erkeğe yakisir sıcak ve odunsu koku.","price_range":"1300-1900 TL","in_stock":True}
,
    {"name":"Dior Homme Intense","brand":"Dior","notes_top":["lavender", "iris"],"notes_middle":["iris", "pear", "apple"],"notes_base":["cedar", "sandalwood", "musk", "vanilla"],"profile":{"top_pct": 20, "middle_pct": 38, "base_pct": 42},"season":"kis","gender":"erkek","description":"Irisin pudralı zarafetiyle maşkülen bir başyapıt.","price_range":"1800-2600 TL","in_stock":True}
,
    {"name":"Dior Homme Parfum","brand":"Dior","notes_top":["lavender", "iris", "sage"],"notes_middle":["iris", "cocoa", "leather"],"notes_base":["cedar", "sandalwood", "musk", "vanilla"],"profile":{"top_pct": 18, "middle_pct": 30, "base_pct": 52},"season":"kis","gender":"erkek","description":"Dior Homme'un en yoğun ve derin ifadesi.","price_range":"2200-3200 TL","in_stock":True}
,
    {"name":"L'Instant de Guerlain","brand":"Guerlain","notes_top":["citrus", "anıs", "lavender"],"notes_middle":["iris", "jasmine", "rose", "heliotrope"],"notes_base":["vanilla", "amber", "cocoa", "musk"],"profile":{"top_pct": 24, "middle_pct": 32, "base_pct": 44},"season":"kis","gender":"unisex","description":"Sicak, pudralı ve duygusal bir Guerlain klasiği.","price_range":"1800-2800 TL","in_stock":True}
,
    {"name":"Hypnotic Poison","brand":"Dior","notes_top":["plum", "coconut", "apricot"],"notes_middle":["rose", "jasmine", "lily", "muguet"],"notes_base":["vanilla", "almond", "sandalwood", "musk"],"profile":{"top_pct": 25, "middle_pct": 28, "base_pct": 47},"season":"kis","gender":"kadın","description":"Badem ve vanilyanın hipnotik ve büyülüyor zehri.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Pure Havane","brand":"Thierry Mugler","notes_top":["honey", "tobacco", "bergamot"],"notes_middle":["cocoa", "vanilla", "tonka"],"notes_base":["patchouli", "leather", "amber", "musk"],"profile":{"top_pct": 25, "middle_pct": 28, "base_pct": 47},"season":"kis","gender":"erkek","description":"Bal ve tutunun sıcak ve maşkülen sarisi.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Grand Soir","brand":"Maison Francis Kurkdjian","notes_top":["bergamot", "lavender"],"notes_middle":["amber", "labdanum", "cistus"],"notes_base":["vanilla", "benzoin", "musk"],"profile":{"top_pct": 20, "middle_pct": 30, "base_pct": 50},"season":"kis","gender":"unisex","description":"Bir aksam güneşinin amber ve vanilya ile vedasi.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Layton","brand":"Parfums de Marly","notes_top":["apple", "bergamot", "lavender"],"notes_middle":["violet", "rose", "jasmine"],"notes_base":["vanilla", "sandalwood", "patchouli", "musk"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"kis","gender":"erkek","description":"Modern bir nis markasinin en sevilen kokusu.","price_range":"2500-3500 TL","in_stock":True}
,
    {"name":"Herod","brand":"Parfums de Marly","notes_top":["cinnamon", "pepper", "tobacco"],"notes_middle":["incense", "patchouli", "vetiver"],"notes_base":["vanilla", "musk", "amber", "cedar"],"profile":{"top_pct": 22, "middle_pct": 28, "base_pct": 50},"season":"kis","gender":"erkek","description":"Tutun ve baharatin l\u00fcks ve maşkülen dansi.","price_range":"2500-3500 TL","in_stock":True}
,
    {"name":"By the Fireplace","brand":"Maison Margiela","notes_top":["pink_pepper", "orange_blossom", "clove"],"notes_middle":["chestnut", "guaiac_wood", "juniper"],"notes_base":["vanilla", "benzoin", "musk", "cashmeran"],"profile":{"top_pct": 20, "middle_pct": 30, "base_pct": 50},"season":"kis","gender":"unisex","description":"Sobanin basinda sıcak ve buhurlu bir kis aksami.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Jazz Club","brand":"Maison Margiela","notes_top":["lemon", "grapefruit", "bergamot"],"notes_middle":["clary_sage", "geranium", "rum"],"notes_base":["vanilla", "tobacco", "vetiver", "amber"],"profile":{"top_pct": 25, "middle_pct": 32, "base_pct": 43},"season":"kis","gender":"unisex","description":"Bir caz kulubunun sıcak ve sisli atmosferi.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"L'Homme Ideal","brand":"Guerlain","notes_top":["bergamot", "orange", "rosemary"],"notes_middle":["almond", "tonka", "cedar"],"notes_base":["vanilla", "leather", "sandalwood"],"profile":{"top_pct": 30, "middle_pct": 32, "base_pct": 38},"season":"kis","gender":"erkek","description":"Badem ve vanilyayla ideal erkeğin portresi.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Le Male Le Parfum","brand":"Jean Paul Gaultier","notes_top":["bergamot", "cardamom", "lavender"],"notes_middle":["iris", "orange_blossom", "rose"],"notes_base":["vanilla", "tonka", "musk", "amber"],"profile":{"top_pct": 22, "middle_pct": 30, "base_pct": 48},"season":"kis","gender":"erkek","description":"Daha karanlık ve sofistike bir Le Male yorumu.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Club de Nuit Intense Man","brand":"Armaf","notes_top":["pineapple", "bergamot", "black_currant"],"notes_middle":["rose", "jasmine", "birch"],"notes_base":["musk", "vanilla", "amber", "cedar"],"profile":{"top_pct": 30, "middle_pct": 30, "base_pct": 40},"season":"kis","gender":"erkek","description":"Efsanevi bir kreasyonun erisilebilir yorumu.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"A*Men","brand":"Thierry Mugler","notes_top":["lavender", "mint", "coriander"],"notes_middle":["caramel", "patchouli", "musk"],"notes_base":["vanilla", "tonka", "sandalwood", "cedar"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"kis","gender":"erkek","description":"Yogün, tatlı ve maşkülen bir gurme bombasi.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Ultra Male","brand":"Jean Paul Gaultier","notes_top":["pear", "mint", "bergamot"],"notes_middle":["cinnamon", "sage", "cumin"],"notes_base":["vanilla", "musk", "amber", "patchouli"],"profile":{"top_pct": 32, "middle_pct": 28, "base_pct": 40},"season":"kis","gender":"erkek","description":"Le Male'in daga ışıltılı ve ultra maşkülen versiyonu.","price_range":"1300-1900 TL","in_stock":True}
,
    {"name":"The One for Men","brand":"Dolce & Gabbana","notes_top":["bergamot", "coriander", "basil"],"notes_middle":["cardamom", "ginger", "orange_blossom", "cedar"],"notes_base":["amber", "tobacco", "leather", "musk"],"profile":{"top_pct": 28, "middle_pct": 32, "base_pct": 40},"season":"kis","gender":"erkek","description":"O anin ve zamansizligin maşkülen bir dansi.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"The One for Women","brand":"Dolce & Gabbana","notes_top":["bergamot", "peach", "lychee"],"notes_middle":["jasmine", "rose", "lily", "plum"],"notes_base":["vanilla", "amber", "musk", "cedar"],"profile":{"top_pct": 30, "middle_pct": 38, "base_pct": 32},"season":"kis","gender":"kadın","description":"Bir kadının zamansiz ve bastan çıkaranici imzasi.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Fahrenheit","brand":"Dior","notes_top":["nutmeg", "hawthorn", "violet", "lemon"],"notes_middle":["jasmine", "rose", "carnation", "cinnamon"],"notes_base":["leather", "sandalwood", "vanilla", "musk"],"profile":{"top_pct": 28, "middle_pct": 32, "base_pct": 40},"season":"kis","gender":"erkek","description":"Devrim niteliğindeki deri ve menekse senfonisi.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Instant Crush","brand":"Maison Francis Kurkdjian","notes_top":["saffron", "ginger", "bergamot"],"notes_middle":["jasmine", "orange_blossom", "iris"],"notes_base":["amber", "vanilla", "musk", "sandalwood"],"profile":{"top_pct": 22, "middle_pct": 28, "base_pct": 50},"season":"kis","gender":"unisex","description":"Anlik bir vurgünun sıcak ve sarhoş edici kokusu.","price_range":"3500-5000 TL","in_stock":True}
,
    {"name":"Gentleman Givenchy","brand":"Givenchy","notes_top":["bergamot", "pepper", "cardamom"],"notes_middle":["lavender", "iris", "geranium"],"notes_base":["vanilla", "tonka", "cedar", "musk"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"kis","gender":"erkek","description":"Modern bir centilmenin sofistike imzasi.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Stronger With You","brand":"Emporio Armani","notes_top":["cardamom", "pink_pepper", "mint"],"notes_middle":["sage", "lavender", "cinnamon"],"notes_base":["vanilla", "amber", "chestnut", "suede"],"profile":{"top_pct": 28, "middle_pct": 28, "base_pct": 44},"season":"kis","gender":"erkek","description":"Modern bir aşk hikayesinin sıcak kokusu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Stronger With You Intensely","brand":"Emporio Armani","notes_top":["bergamot", "pink_pepper", "cardamom"],"notes_middle":["sage", "cinnamon", "geranium"],"notes_base":["vanilla", "amber", "tonka", "cedar"],"profile":{"top_pct": 24, "middle_pct": 28, "base_pct": 48},"season":"kis","gender":"erkek","description":"Daha yoğun, daha tutkulu bir Stronger With You.","price_range":"1300-1900 TL","in_stock":True}
,
    {"name":"Boss Bottled Oud","brand":"Hugo Boss","notes_top":["apple", "bergamot", "oud"],"notes_middle":["geranium", "cinnamon", "nard"],"notes_base":["sandalwood", "cedar", "musk", "olibanum"],"profile":{"top_pct": 25, "middle_pct": 28, "base_pct": 47},"season":"kis","gender":"erkek","description":"Boss Bottled'in oud'lu ve dogülu yorumu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Gucci Guilty Absolute","brand":"Gucci","notes_top":["blackberry", "leather", "labdanum"],"notes_middle":["patchouli", "cedar", "vetiver", "iris"],"notes_base":["musk", "amber", "oud", "leather"],"profile":{"top_pct": 20, "middle_pct": 28, "base_pct": 52},"season":"kis","gender":"erkek","description":"Deri ve odunun en saf ve en ham hali.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Armani Code","brand":"Giorgio Armani","notes_top":["bergamot", "lemon", "star_anıse"],"notes_middle":["tobacco", "tonka", "geranium"],"notes_base":["leather", "cedar", "musk", "amber"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"kis","gender":"erkek","description":"Maşkulenligin gizli ve çekici kodu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Armani Code Absolu","brand":"Giorgio Armani","notes_top":["mandarin", "orange", "bergamot"],"notes_middle":["almond", "tonka", "cinnamon"],"notes_base":["vanilla", "sandalwood", "amber", "musk"],"profile":{"top_pct": 24, "middle_pct": 28, "base_pct": 48},"season":"kis","gender":"erkek","description":"Armani Code'un daha tatlı ve yoğun kardesi.","price_range":"1300-1900 TL","in_stock":True}
,
    {"name":"Omnia Amethyste","brand":"Bvlgari","notes_top":["pepper", "grapefruit", "iris"],"notes_middle":["rose", "violet", "jasmine"],"notes_base":["musk", "sandalwood", "amber"],"profile":{"top_pct": 30, "middle_pct": 40, "base_pct": 30},"season":"kis","gender":"kadın","description":"Mor ametist gibi gizemli ve asil bir çiçeksel.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Omnia Coral","brand":"Bvlgari","notes_top":["bergamot", "goji", "pomegranate"],"notes_middle":["hibiscus", "jasmine", "peony"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 35, "middle_pct": 35, "base_pct": 30},"season":"kis","gender":"kadın","description":"Sicak ve egzotik bir çiçek-meyve dansi.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Signorina","brand":"Salvatore Ferragamo","notes_top":["black_currant", "pepper", "pink_pepper"],"notes_middle":["jasmine", "peony", "rose"],"notes_base":["patchouli", "musk", "vanilla", "amber"],"profile":{"top_pct": 32, "middle_pct": 35, "base_pct": 33},"season":"kis","gender":"kadın","description":"Genc bir kizin tatlı ve çiçeksi hikayesi.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"Idole","brand":"Lancome","notes_top":["bergamot", "pear", "pink_pepper"],"notes_middle":["rose", "jasmine", "iris"],"notes_base":["vanilla", "musk", "cedar", "patchouli"],"profile":{"top_pct": 30, "middle_pct": 40, "base_pct": 30},"season":"kis","gender":"kadın","description":"Modern bir idole yakisan çiçeksi ışıltı.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Tresor","brand":"Lancome","notes_top":["rose", "peach", "lily", "bergamot"],"notes_middle":["iris", "jasmine", "lilac", "violet"],"notes_base":["musk", "amber", "vanilla", "sandalwood"],"profile":{"top_pct": 28, "middle_pct": 38, "base_pct": 34},"season":"kis","gender":"kadın","description":"90'larin efsanevi romantik çiçeksel hazinesi.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Black Opium Extreme","brand":"Yves Saint Laurent","notes_top":["coffee", "bergamot", "mandarin"],"notes_middle":["jasmine", "orange_blossom", "almond"],"notes_base":["vanilla", "patchouli", "musk", "amber"],"profile":{"top_pct": 20, "middle_pct": 28, "base_pct": 52},"season":"kis","gender":"kadın","description":"Black Opium'un daha karanlık ve yoğun iksiri.","price_range":"1700-2400 TL","in_stock":True}
,
    {"name":"Mon Guerlain","brand":"Guerlain","notes_top":["lavender", "bergamot", "coriander"],"notes_middle":["lavender", "jasmine", "iris", "rose"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 25, "middle_pct": 35, "base_pct": 40},"season":"kis","gender":"kadın","description":"Guerlain'in modern kadına armagani.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Flowerbomb Nectar","brand":"Viktor & Rolf","notes_top":["bergamot", "osmanthus", "tea"],"notes_middle":["jasmine", "rose", "orchid"],"notes_base":["patchouli", "musk", "vanilla", "honey"],"profile":{"top_pct": 22, "middle_pct": 35, "base_pct": 43},"season":"kis","gender":"kadın","description":"Flowerbomb'un en tatlı ve en yoğun hali.","price_range":"1800-2600 TL","in_stock":True}
,
    {"name":"Prada Luna Rossa Carbon","brand":"Prada","notes_top":["bergamot", "pepper", "water"],"notes_middle":["lavender", "geranium", "asphalt"],"notes_base":["musk", "amber", "patchouli"],"profile":{"top_pct": 40, "middle_pct": 28, "base_pct": 32},"season":"kis","gender":"erkek","description":"Modern ve temiz bir maşkülen ferahlık.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Prada Luna Rossa Black","brand":"Prada","notes_top":["bergamot", "pepper", "angelica"],"notes_middle":["patchouli", "musk", "geranium"],"notes_base":["musk", "amber", "vanilla", "sandalwood"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"kis","gender":"erkek","description":"Prada'nin daha karanlık ve pudralı maşkülen yorumu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Mugler Aura","brand":"Thierry Mugler","notes_top":["bergamot", "rhubarb", "lemon"],"notes_middle":["jasmine", "orange_blossom", "gardenia"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"kis","gender":"kadın","description":"Yesil ve vanilyalı bir Mugler yorumu.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Mugler Womanity","brand":"Thierry Mugler","notes_top":["bergamot", "mandarin", "fig"],"notes_middle":["jasmine", "rose", "caviar"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 25, "middle_pct": 35, "base_pct": 40},"season":"kis","gender":"kadın","description":"Tuzlu ve tatlınin Mugler'a ozgu dansi.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Givenchy Ange ou Demon","brand":"Givenchy","notes_top":["bergamot", "mandarin", "lemon"],"notes_middle":["jasmine", "rose", "lily"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"kis","gender":"kadın","description":"Bir melek mi yoksa seytan mi oldugünuza karar verin.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Givenchy Organza","brand":"Givenchy","notes_top":["bergamot", "mandarin", "lemon"],"notes_middle":["jasmine", "rose", "iris"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 22, "middle_pct": 32, "base_pct": 46},"season":"kis","gender":"kadın","description":"Bir opera ici gibi ihti samli ve çiçeksi.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Lancome Tresor Hypnotic","brand":"Lancome","notes_top":["bergamot", "mandarin", "peach"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 25, "middle_pct": 32, "base_pct": 43},"season":"kis","gender":"kadın","description":"Tresor'un daha hipnotik ve derin yorumu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Guerlain Vol de Nuit","brand":"Guerlain","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 22, "middle_pct": 30, "base_pct": 48},"season":"kis","gender":"unisex","description":"Gece ucusunun özgürlugu ve gizemi.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Guerlain Mitsouko","brand":"Guerlain","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "amber", "oakmoss", "vanilla"],"profile":{"top_pct": 20, "middle_pct": 30, "base_pct": 50},"season":"kis","gender":"kadın","description":"100 yillik bir simpate-odunsu klasik.","price_range":"2000-3500 TL","in_stock":True}
,
    {"name":"Guerlain L'Heure Bleue","brand":"Guerlain","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "iris"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 22, "middle_pct": 32, "base_pct": 46},"season":"kis","gender":"kadın","description":"Alacakaranligin huzurlu ve pudralı anısina saygi.","price_range":"2000-3500 TL","in_stock":True}
,
    {"name":"Caron Pour Un Homme","brand":"Caron","notes_top":["lavender", "lemon", "bergamot"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "vanilla", "sandalwood"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"kis","gender":"erkek","description":"Lavantanin en klasik ve en maşkülen yorumu.","price_range":"800-1200 TL","in_stock":True}
,
    {"name":"Dior Fahrenheit Absolute","brand":"Dior","notes_top":["nutmeg", "violet", "lemon"],"notes_middle":["jasmine", "rose", "cinnamon"],"notes_base":["leather", "vanilla", "musk", "amber"],"profile":{"top_pct": 22, "middle_pct": 30, "base_pct": 48},"season":"kis","gender":"erkek","description":"Fahrenheit'in daha derin ve karanlık soyutlamasi.","price_range":"1800-2600 TL","in_stock":True}
,
    {"name":"YSL L'Homme Ultime","brand":"Yves Saint Laurent","notes_top":["bergamot", "grapefruit", "ginger"],"notes_middle":["rose", "sage", "juniper"],"notes_base":["cedar", "musk", "amber"],"profile":{"top_pct": 35, "middle_pct": 32, "base_pct": 33},"season":"kis","gender":"erkek","description":"L'Homme'un modern ve çiçeksi yorumu.","price_range":"1300-1900 TL","in_stock":True}
,
    {"name":"Prada Luna Rossa Extreme","brand":"Prada","notes_top":["bergamot", "pepper", "lavender"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "vanilla", "sandalwood"],"profile":{"top_pct": 28, "middle_pct": 28, "base_pct": 44},"season":"kis","gender":"erkek","description":"Luna Rossa'nin en ekstrem ve maşkülen uyesi.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Armani Code Profumo","brand":"Giorgio Armani","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "iris"],"notes_base":["vanilla", "musk", "amber", "cedar"],"profile":{"top_pct": 24, "middle_pct": 28, "base_pct": 48},"season":"kis","gender":"erkek","description":"Armani Code'un gizemli ve derin parfüm yorumu.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Hugo Boss The Scent","brand":"Hugo Boss","notes_top":["ginger", "bergamot", "mandarin"],"notes_middle":["lavender", "sage", "coriander"],"notes_base":["vanilla", "musk", "amber", "cedar"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"kis","gender":"erkek","description":"Kendine guvenen bir erkeğe yakisir cesur koku.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Hugo Boss The Scent Absolute","brand":"Hugo Boss","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["leather", "musk", "vanilla", "amber"],"profile":{"top_pct": 22, "middle_pct": 28, "base_pct": 50},"season":"kis","gender":"erkek","description":"The Scent'in daha derin ve deri agirlikli versiyonu.","price_range":"1200-1700 TL","in_stock":True}
,
    {"name":"Montblanc Legend Night","brand":"Montblanc","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 28, "middle_pct": 28, "base_pct": 44},"season":"kis","gender":"erkek","description":"Legend'in gece ve gizemli versiyonu.","price_range":"700-1100 TL","in_stock":True}
,
    {"name":"Dunhill Icon Absolute","brand":"Dunhill","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["leather", "musk", "vanilla", "amber"],"profile":{"top_pct": 24, "middle_pct": 28, "base_pct": 48},"season":"kis","gender":"erkek","description":"Bir Ingiliz beyefendisine yakisir deri-vanilya kokusu.","price_range":"800-1300 TL","in_stock":True}
,
    {"name":"Rochas Moustache","brand":"Rochas","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["patchouli", "musk", "vanilla", "amber"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"kis","gender":"erkek","description":"Biyikli bir Fransiz centilmeninin kokusu.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"Paco Rabanne Pour Homme","brand":"Paco Rabanne","notes_top":["lavender", "bergamot", "lemon"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "cedar", "oakmoss"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"kis","gender":"erkek","description":"1973'ten beri zamansiz bir maşkülen klasik.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Azzaro Pour Homme","brand":"Azzaro","notes_top":["bergamot", "lemon", "lavender"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "cedar", "oakmoss"],"profile":{"top_pct": 28, "middle_pct": 32, "base_pct": 40},"season":"kis","gender":"erkek","description":"1978'den beri anason ve lavantanin efsanevi buluşması.","price_range":"500-800 TL","in_stock":True}
,
    {"name":"Azzaro Wanted by Night","brand":"Azzaro","notes_top":["bergamot", "lemon", "pepper"],"notes_middle":["jasmine", "rose", "cinnamon"],"notes_base":["vanilla", "musk", "amber", "tobacco"],"profile":{"top_pct": 26, "middle_pct": 28, "base_pct": 46},"season":"kis","gender":"erkek","description":"Gecenin karanliginda aranan daha yoğun bir koku.","price_range":"700-1100 TL","in_stock":True}
,
    {"name":"Versace Oud Noir","brand":"Versace","notes_top":["bergamot", "lemon", "oud"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "vanilla", "cedar"],"profile":{"top_pct": 22, "middle_pct": 28, "base_pct": 50},"season":"kis","gender":"erkek","description":"Versace'nin oud'u yorumu: l\u00fcks ve karanlık.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Fendi Fan di Fendi","brand":"Fendi","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "vanilla", "amber", "leather"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"kis","gender":"kadın","description":"Bir Fendi kadınına yakisir zarif ve derin koku.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Valentino Valentina","brand":"Valentino","notes_top":["bergamot", "mandarin", "pear"],"notes_middle":["jasmine", "rose", "orange_blossom"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 28, "middle_pct": 35, "base_pct": 37},"season":"kis","gender":"kadın","description":"Bir Valentino elbisesi kadar romantik ve feminen.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Valentino Donna","brand":"Valentino","notes_top":["bergamot", "mandarin", "pear"],"notes_middle":["jasmine", "rose", "iris"],"notes_base":["vanilla", "musk", "amber", "leather"],"profile":{"top_pct": 25, "middle_pct": 32, "base_pct": 43},"season":"kis","gender":"kadın","description":"Valentino kadınınin imza kokusu: zarafet ve güç.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Bottega Veneta","brand":"Bottega Veneta","notes_top":["bergamot", "lemon", "pepper"],"notes_middle":["jasmine", "rose", "patchouli"],"notes_base":["leather", "musk", "vanilla", "amber"],"profile":{"top_pct": 22, "middle_pct": 30, "base_pct": 48},"season":"kis","gender":"kadın","description":"Bottega Veneta derisinin l\u00fcks ve sıcak kokusu.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Narciso Rodriguez For Her EDT","brand":"Narciso Rodriguez","notes_top":["bergamot", "mandarin", "pepper"],"notes_middle":["musk", "jasmine", "rose"],"notes_base":["musk", "vanilla", "amber", "cedar"],"profile":{"top_pct": 25, "middle_pct": 35, "base_pct": 40},"season":"kis","gender":"kadın","description":"Miskin çiçeklerle dansinin orijinali.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Calvin Klein Euphoria","brand":"Calvin Klein","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"kis","gender":"kadın","description":"Bir oryantal çiçek bahçesinde mutluluk hali.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Calvin Klein Obsession","brand":"Calvin Klein","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "cinnamon"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 22, "middle_pct": 30, "base_pct": 48},"season":"kis","gender":"kadın","description":"80'lerin en ikonik oryantal-çiçek takintisi.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Roberto Cavalli Oro","brand":"Roberto Cavalli","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "peony"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"kis","gender":"kadın","description":"Altin kadar degerli ve parlak bir Cavalli yorumu.","price_range":"800-1300 TL","in_stock":True}
,
    {"name":"Bvlgari Jasmin Noir","brand":"Bvlgari","notes_top":["bergamot", "mandarin", "pear"],"notes_middle":["jasmine", "almond", "licorice"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 22, "middle_pct": 30, "base_pct": 48},"season":"kis","gender":"kadın","description":"Yasemini karanlık vanilyayla bulusan bir Bvlgari başyapıtı.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Dolce & Gabbana Pour Homme","brand":"Dolce & Gabbana","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "cedar", "tobacco"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"kis","gender":"erkek","description":"Sicilyali bir erkeğe yakisir baharatlı-odunsu koku.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Dolce & Gabbana Pour Femme","brand":"Dolce & Gabbana","notes_top":["bergamot", "mandarin", "raspberry"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 25, "middle_pct": 35, "base_pct": 40},"season":"kis","gender":"kadın","description":"Sicilyali bir kadına yakisir çiçeksi-oriental koku.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Carolina Herrera CH","brand":"Carolina Herrera","notes_top":["bergamot", "mandarin", "lemon"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 25, "middle_pct": 32, "base_pct": 43},"season":"kis","gender":"kadın","description":"Carolina Herrera'nin imza kokusu: çiçeksi ve asil.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Nina Ricci L'Air du Temps","brand":"Nina Ricci","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 28, "middle_pct": 38, "base_pct": 34},"season":"kis","gender":"kadın","description":"1948'den beri barisin ve aşkin kokusu.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"Cacharel Ana\u00efs Ana\u00efs","brand":"Cacharel","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "lily"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 28, "middle_pct": 40, "base_pct": 32},"season":"kis","gender":"kadın","description":"1978'den beri genç kizlarin en masum çiçek kokusu.","price_range":"500-800 TL","in_stock":True}
,
    {"name":"Cacharel Amor Amor","brand":"Cacharel","notes_top":["bergamot", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 30, "middle_pct": 35, "base_pct": 35},"season":"kis","gender":"kadın","description":"Ask aşka adanmis enerjik ve çiçeksi bir koku.","price_range":"500-800 TL","in_stock":True}
,
    {"name":"L'Occitane Eau de Baux","brand":"L'Occtiane","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["vanilla", "musk", "amber", "cedar"],"profile":{"top_pct": 28, "middle_pct": 28, "base_pct": 44},"season":"kis","gender":"unisex","description":"Provence'ta bir zeytinlik kadar sıcak ve dogal.","price_range":"800-1200 TL","in_stock":True}
,
    {"name":"Davidoff Cool Water Wave","brand":"Davidoff","notes_top":["bergamot", "mandarin", "sea_notes"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 30, "middle_pct": 28, "base_pct": 42},"season":"kis","gender":"erkek","description":"Cool Water'in daha sıcak ve odunsu yorumu.","price_range":"500-800 TL","in_stock":True}
,
    {"name":"Adidas Dynamic Pulse","brand":"Adidas","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 32, "middle_pct": 28, "base_pct": 40},"season":"kis","gender":"erkek","description":"Spor ve dinamik bir yasam tarzinin kokusu.","price_range":"200-300 TL","in_stock":True}
,
    {"name":"Lacoste Pour Homme","brand":"Lacoste","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 32, "middle_pct": 28, "base_pct": 40},"season":"kis","gender":"erkek","description":"Fransiz spor zarafetinin maşkülen yorumu.","price_range":"500-800 TL","in_stock":True}
,
    # ===== DORT MEVSIM (All Season) — 128 perfumes =====
    {"name":"Aventus","brand":"Creed","notes_top":["pineapple", "bergamot", "black_currant", "apple"],"notes_middle":["rose", "jasmine", "birch", "patchouli"],"notes_base":["musk", "oakmoss", "vanilla", "cedar"],"profile":{"top_pct": 33, "middle_pct": 32, "base_pct": 35},"season":"dört_mevsim","gender":"unisex","description":"Efsanevi meyvemsi-odunsu dört mevsim klasiği.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Green Irish Tweed","brand":"Creed","notes_top":["lemon", "bergamot", "mint"],"notes_middle":["violet", "geranium", "sandalwood"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 35, "middle_pct": 32, "base_pct": 33},"season":"dört_mevsim","gender":"erkek","description":"Yesil, ferah ve zamansiz bir Irlanda tweed'i.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Silver Mountain Water","brand":"Creed","notes_top":["bergamot", "green_tea", "mandarin"],"notes_middle":["black_currant", "galbanum", "sandalwood"],"notes_base":["musk", "amber", "vanilla", "cedar"],"profile":{"top_pct": 38, "middle_pct": 30, "base_pct": 32},"season":"dört_mevsim","gender":"unisex","description":"Dag zirvesinde temiz bir su kaynagi.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Bleu de Chanel","brand":"Chanel","notes_top":["grapefruit", "lemon", "pepper", "mint"],"notes_middle":["ginger", "nutmeg", "jasmine", "iso_e_super"],"notes_base":["cedar", "sandalwood", "amber", "frankincense"],"profile":{"top_pct": 30, "middle_pct": 32, "base_pct": 38},"season":"dört_mevsim","gender":"erkek","description":"Modern maşkülenligin odunsu-taze simgesi.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Coco Mademoiselle","brand":"Chanel","notes_top":["orange", "bergamot", "grapefruit"],"notes_middle":["rose", "jasmine", "lychee"],"notes_base":["vanilla", "musk", "patchouli", "vetiver"],"profile":{"top_pct": 30, "middle_pct": 35, "base_pct": 35},"season":"dört_mevsim","gender":"kadın","description":"Modern, özgür ve zamansiz bir siklik ifadesi.","price_range":"2000-3200 TL","in_stock":True}
,
    {"name":"No 5","brand":"Chanel","notes_top":["aldehyde", "ylang", "neroli", "bergamot"],"notes_middle":["jasmine", "rose", "iris", "lily"],"notes_base":["vanilla", "musk", "vetiver", "sandalwood"],"profile":{"top_pct": 30, "middle_pct": 36, "base_pct": 34},"season":"dört_mevsim","gender":"kadın","description":"Tum zamanlarin en ikonik aldehit-çiçek başyapıtı.","price_range":"2500-4000 TL","in_stock":True}
,
    {"name":"J'adore","brand":"Dior","notes_top":["bergamot", "pear", "melon", "peach"],"notes_middle":["jasmine", "rose", "lily", "violet", "orchid"],"notes_base":["musk", "vanilla", "cedar"],"profile":{"top_pct": 30, "middle_pct": 40, "base_pct": 30},"season":"dört_mevsim","gender":"kadın","description":"Altin çiçeklerin zarif ve zamansiz senfonisi.","price_range":"1800-2600 TL","in_stock":True}
,
    {"name":"Miss Dior","brand":"Dior","notes_top":["pineapple", "cherry", "mandarin"],"notes_middle":["rose", "jasmine", "peony"],"notes_base":["musk", "vanilla", "patchouli", "sandalwood"],"profile":{"top_pct": 33, "middle_pct": 37, "base_pct": 30},"season":"dört_mevsim","gender":"kadın","description":"Ask ve asi gençligin çiçeksi imzasi.","price_range":"1600-2400 TL","in_stock":True}
,
    {"name":"Sauvage Elixir","brand":"Dior","notes_top":["grapefruit", "nutmeg", "cinnamon"],"notes_middle":["lavender", "cardamom", "mace"],"notes_base":["amber", "sandalwood", "vanilla", "licorice"],"profile":{"top_pct": 28, "middle_pct": 32, "base_pct": 40},"season":"dört_mevsim","gender":"erkek","description":"Sauvage'in kusursuz ve yoğun iksiri.","price_range":"2500-3500 TL","in_stock":True}
,
    {"name":"Flowerbomb","brand":"Viktor & Rolf","notes_top":["bergamot", "tea", "osmanthus"],"notes_middle":["jasmine", "rose", "orchid", "freesia"],"notes_base":["patchouli", "musk", "vanilla"],"profile":{"top_pct": 28, "middle_pct": 42, "base_pct": 30},"season":"dört_mevsim","gender":"kadın","description":"Patlayici çiçek buketi ile vanilya sarmali.","price_range":"1700-2500 TL","in_stock":True}
,
    {"name":"Gypsy Water","brand":"Byredo","notes_top":["bergamot", "juniper", "lemon", "pink_pepper"],"notes_middle":["pine", "iris", "orris"],"notes_base":["sandalwood", "vanilla", "amber"],"profile":{"top_pct": 35, "middle_pct": 30, "base_pct": 35},"season":"dört_mevsim","gender":"unisex","description":"Orman ruhuyla vanilyanın büyülü dansi.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Narciso Rodriguez For Her","brand":"Narciso Rodriguez","notes_top":["rose", "peach", "bergamot"],"notes_middle":["musk", "amber", "patchouli"],"notes_base":["sandalwood", "vanilla", "cedar"],"profile":{"top_pct": 25, "middle_pct": 35, "base_pct": 40},"season":"dört_mevsim","gender":"kadın","description":"Miskin büyüsünde kaybolmus feminen bir klasik.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Montblanc Explorer","brand":"Montblanc","notes_top":["bergamot", "pink_pepper", "clary_sage"],"notes_middle":["leather", "patchouli", "vetiver"],"notes_base":["cedar", "ambroxan", "musk"],"profile":{"top_pct": 35, "middle_pct": 30, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Kasif ruhu icin odunsu-taze bir macera.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Molecule 01","brand":"Escentric Molecules","notes_top":["iso_e_super", "woody"],"notes_middle":["cedar", "vetiver"],"notes_base":["musk", "amber"],"profile":{"top_pct": 30, "middle_pct": 30, "base_pct": 40},"season":"dört_mevsim","gender":"unisex","description":"Molekuler bir mucize: her tende farkli acilan tek nota.","price_range":"1500-2500 TL","in_stock":True}
,
    {"name":"Prada L'Homme","brand":"Prada","notes_top":["neroli", "bergamot", "black_pepper"],"notes_middle":["iris", "violet", "geranium"],"notes_base":["cedar", "amber", "musk", "sandalwood"],"profile":{"top_pct": 30, "middle_pct": 35, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Temiz ve pudralı bir maşkülen zarafet.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Boss Bottled","brand":"Hugo Boss","notes_top":["apple", "bergamot", "lemon", "plum"],"notes_middle":["geranium", "cinnamon", "vanilla"],"notes_base":["sandalwood", "cedar", "musk", "olibanum"],"profile":{"top_pct": 33, "middle_pct": 32, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Basari ve guvenin odunsu-baharatlı kokusu.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Shalimar","brand":"Guerlain","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "iris", "vetiver"],"notes_base":["vanilla", "amber", "incense", "leather", "musk"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"dört_mevsim","gender":"kadın","description":"100 yillik bir aşk ve vanilya-amber efsanesi.","price_range":"2000-3500 TL","in_stock":True}
,
    {"name":"Y Eau de Parfum","brand":"Yves Saint Laurent","notes_top":["bergamot", "ginger", "apple"],"notes_middle":["sage", "cedar", "lavender"],"notes_base":["amber", "musk", "vanilla", "woody"],"profile":{"top_pct": 33, "middle_pct": 33, "base_pct": 34},"season":"dört_mevsim","gender":"erkek","description":"Cesur, enerjik ve modern maşkülenligin güçu.","price_range":"1600-2400 TL","in_stock":True}
,
    {"name":"Burberry Her","brand":"Burberry","notes_top":["black_currant", "blueberry", "raspberry"],"notes_middle":["jasmine", "violet", "rose"],"notes_base":["musk", "amber", "vanilla", "sandalwood"],"profile":{"top_pct": 35, "middle_pct": 33, "base_pct": 32},"season":"dört_mevsim","gender":"kadın","description":"Londra ruhunun meyvemsi-çiçeksi modern yorumu.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Dylan Blue","brand":"Versace","notes_top":["bergamot", "grapefruit", "fig_leaf"],"notes_middle":["black_pepper", "lavender", "patchouli"],"notes_base":["amber", "musk", "vanilla", "saffron"],"profile":{"top_pct": 35, "middle_pct": 30, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Akdeniz ruhunun taze-odunsu maşkülen yansıması.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Versace Pour Homme","brand":"Versace","notes_top":["bergamot", "lemon", "neroli", "rosewood"],"notes_middle":["hyacinth", "jasmine", "sage", "geranium"],"notes_base":["musk", "amber", "tonka", "cedar"],"profile":{"top_pct": 38, "middle_pct": 30, "base_pct": 32},"season":"dört_mevsim","gender":"erkek","description":"Akdeniz esintili ferah ve sofistike bir maşkülen koku.","price_range":"800-1300 TL","in_stock":True}
,
    {"name":"Pour Homme","brand":"Bvlgari","notes_top":["bergamot", "pepper", "cardamom"],"notes_middle":["jasmine", "coriander", "geranium"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 35, "middle_pct": 30, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Beyaz çiçekler ve miskin zarif maşkülen yorumu.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Hermes H24","brand":"Hermes","notes_top":["sage", "rhubarb", "green"],"notes_middle":["rosewood", "narcissus", "clary_sage"],"notes_base":["musk", "amber", "wood", "vetiver"],"profile":{"top_pct": 38, "middle_pct": 30, "base_pct": 32},"season":"dört_mevsim","gender":"erkek","description":"Modern erkeğin yeşil ve teknolojik kokusu.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Encre Noire Sport","brand":"Lalique","notes_top":["bergamot", "grapefruit", "cypress"],"notes_middle":["vetiver", "cedar", "patchouli"],"notes_base":["musk", "amber", "leather"],"profile":{"top_pct": 40, "middle_pct": 28, "base_pct": 32},"season":"dört_mevsim","gender":"erkek","description":"Encre Noire'in daha ferah ve sportif kardesi.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"Eau de Lacoste L.12.12","brand":"Lacoste","notes_top":["grapefruit", "bergamot", "coriander"],"notes_middle":["jasmine", "ylang", "mimosa"],"notes_base":["sandalwood", "cedar", "musk", "amber"],"profile":{"top_pct": 38, "middle_pct": 30, "base_pct": 32},"season":"dört_mevsim","gender":"erkek","description":"Ferah ve rahat bir spor klasiği.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Armani Acqua di Gio Absolu","brand":"Giorgio Armani","notes_top":["bergamot", "grapefruit", "apple"],"notes_middle":["rose", "jasmine", "sage"],"notes_base":["cedar", "patchouli", "musk", "amber"],"profile":{"top_pct": 35, "middle_pct": 30, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Acqua di Gio'nun daha sofistike ve odunsu yorumu.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Acqua di Gio Profumo","brand":"Giorgio Armani","notes_top":["bergamot", "sea_notes", "mandarin"],"notes_middle":["sage", "geranium", "lavender"],"notes_base":["patchouli", "musk", "amber", "incense"],"profile":{"top_pct": 32, "middle_pct": 30, "base_pct": 38},"season":"dört_mevsim","gender":"erkek","description":"Deniz ve buhurun olaganustu birlikteligi.","price_range":"1600-2400 TL","in_stock":True}
,
    {"name":"L'Homme Ultime","brand":"Yves Saint Laurent","notes_top":["bergamot", "grapefruit", "ginger"],"notes_middle":["rose", "sage", "juniper"],"notes_base":["cedar", "musk", "amber"],"profile":{"top_pct": 35, "middle_pct": 32, "base_pct": 33},"season":"dört_mevsim","gender":"erkek","description":"L'Homme'un modern ve çiçeksi yorumu.","price_range":"1300-1900 TL","in_stock":True}
,
    {"name":"Dior Homme","brand":"Dior","notes_top":["lavender", "sage", "bergamot"],"notes_middle":["iris", "cocoa", "pear"],"notes_base":["cedar", "leather", "musk", "vanilla"],"profile":{"top_pct": 30, "middle_pct": 35, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Modern maşkülenligin zarif ve pudralı başyapıtı.","price_range":"1600-2400 TL","in_stock":True}
,
    {"name":"Chance","brand":"Chanel","notes_top":["pepper", "pineapple", "iris"],"notes_middle":["jasmine", "rose", "hyacinth"],"notes_base":["musk", "vanilla", "amber", "vetiver"],"profile":{"top_pct": 33, "middle_pct": 35, "base_pct": 32},"season":"dört_mevsim","gender":"kadın","description":"Sansa yer birakmayan bir çiçeksel patlama.","price_range":"1900-2800 TL","in_stock":True}
,
    {"name":"Chance Eau Vive","brand":"Chanel","notes_top":["grapefruit", "blood_orange", "mandarin"],"notes_middle":["jasmine", "rose", "iris"],"notes_base":["musk", "vanilla", "amber"],"profile":{"top_pct": 40, "middle_pct": 30, "base_pct": 30},"season":"dört_mevsim","gender":"kadın","description":"Chance'in en enerjik ve ışıltılı versiyonu.","price_range":"1900-2800 TL","in_stock":True}
,
    {"name":"Angel Schlesser Essence","brand":"Angel Schlesser","notes_top":["bergamot", "grapefruit", "mandarin"],"notes_middle":["violet", "jasmine", "iris"],"notes_base":["musk", "vanilla", "sandalwood", "amber"],"profile":{"top_pct": 35, "middle_pct": 32, "base_pct": 33},"season":"dört_mevsim","gender":"kadın","description":"Temiz, taze ve ışıltılı bir feminen koku.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"Emporio Armani Because It's You","brand":"Emporio Armani","notes_top":["raspberry", "grapefruit", "neroli"],"notes_middle":["rose", "jasmine", "orange_blossom"],"notes_base":["musk", "amber", "vanilla", "patchouli"],"profile":{"top_pct": 36, "middle_pct": 36, "base_pct": 28},"season":"dört_mevsim","gender":"kadın","description":"Ask ve tutkunun meyvemsi-çiçeksi ilani.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"L'Eau d'Issey Pure","brand":"Issey Miyake","notes_top":["bergamot", "mandarin", "lemon"],"notes_middle":["jasmine", "rose", "lily"],"notes_base":["musk", "cedar", "amber", "vanilla"],"profile":{"top_pct": 38, "middle_pct": 32, "base_pct": 30},"season":"dört_mevsim","gender":"kadın","description":"L'Eau d'Issey'in daha saf ve berrak yorumu.","price_range":"900-1400 TL","in_stock":True}
,
    {"name":"Davidoff Cool Water Reborn","brand":"Davidoff","notes_top":["bergamot", "mandarin", "cucumber"],"notes_middle":["lavender", "rosemary", "geranium"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 38, "middle_pct": 30, "base_pct": 32},"season":"dört_mevsim","gender":"erkek","description":"Cool Water'in yeniden dogan modern yorumu.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"CK One Shock","brand":"Calvin Klein","notes_top":["bergamot", "mandarin", "cucumber"],"notes_middle":["jasmine", "rose", "violet"],"notes_base":["musk", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 35, "middle_pct": 32, "base_pct": 33},"season":"dört_mevsim","gender":"erkek","description":"CK One'in daha karanlık ve baharatlı kardesi.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Burberry Weekend","brand":"Burberry","notes_top":["lemon", "grapefruit", "tangerine"],"notes_middle":["jasmine", "rose", "iris"],"notes_base":["musk", "sandalwood", "cedar", "vanilla"],"profile":{"top_pct": 38, "middle_pct": 30, "base_pct": 32},"season":"dört_mevsim","gender":"kadın","description":"Haftasonu huzurunu yansitan bir çiçeksi klasik.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"Burberry Brit","brand":"Burberry","notes_top":["bergamot", "mandarin", "lemon"],"notes_middle":["rose", "jasmine", "cedar"],"notes_base":["musk", "vanilla", "amber", "patchouli"],"profile":{"top_pct": 33, "middle_pct": 32, "base_pct": 35},"season":"dört_mevsim","gender":"kadın","description":"Modern bir Ingiliz klasiğinin sıcak yorumu.","price_range":"700-1100 TL","in_stock":True}
,
    {"name":"Lancome Tresor In Love","brand":"Lancome","notes_top":["pear", "bergamot", "mandarin"],"notes_middle":["rose", "jasmine", "peony"],"notes_base":["musk", "vanilla", "cedar", "patchouli"],"profile":{"top_pct": 36, "middle_pct": 35, "base_pct": 29},"season":"dört_mevsim","gender":"kadın","description":"Genc aşka adanmis meyvemsi-çiçeksi bir Tresor.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Montblanc Legend","brand":"Montblanc","notes_top":["bergamot", "grapefruit", "lemon"],"notes_middle":["lavender", "geranium", "oakmoss"],"notes_base":["musk", "sandalwood", "cedar", "amber"],"profile":{"top_pct": 35, "middle_pct": 30, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Zamansiz bir maşkülen klasiğin modern yorumu.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"Armaf Club de Nuit","brand":"Armaf","notes_top":["bergamot", "grapefruit", "lemon"],"notes_middle":["jasmine", "rose", "cinnamon"],"notes_base":["musk", "amber", "vanilla", "cedar"],"profile":{"top_pct": 35, "middle_pct": 30, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Luks markalara erisilebilir bir alternatif.","price_range":"300-600 TL","in_stock":True}
,
    {"name":"Tom Ford Grey Vetiver","brand":"Tom Ford","notes_top":["bergamot", "orange_blossom", "grapefruit"],"notes_middle":["vetiver", "sage", "iris"],"notes_base":["musk", "amber", "oakmoss", "cedar"],"profile":{"top_pct": 35, "middle_pct": 30, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Vetiverin en temis ve en zarif yorumu.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Tom Ford Noir Extreme","brand":"Tom Ford","notes_top":["mandarin", "bergamot", "pepper"],"notes_middle":["orange_blossom", "jasmine", "saffron"],"notes_base":["vanilla", "amber", "musk", "sandalwood"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"dört_mevsim","gender":"erkek","description":"Dogu ve Bati'nin kesistigi lüks bir maşkülen koku.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Carnal Flower","brand":"Frederic Malle","notes_top":["tuberose", "bergamot", "eucalyptus"],"notes_middle":["jasmine", "tuberose", "orange_blossom"],"notes_base":["musk", "vanilla", "coconut", "amber"],"profile":{"top_pct": 28, "middle_pct": 45, "base_pct": 27},"season":"dört_mevsim","gender":"kadın","description":"Tuberose çiçeğinin en vahşi ve en gercek ifadesi.","price_range":"5000-7500 TL","in_stock":True}
,
    {"name":"Lys Mediterranee","brand":"Frederic Malle","notes_top":["bergamot", "mandarin", "pepper"],"notes_middle":["lily", "musk", "angelica"],"notes_base":["cedar", "vanilla", "amber"],"profile":{"top_pct": 30, "middle_pct": 42, "base_pct": 28},"season":"dört_mevsim","gender":"kadın","description":"Akdeniz zambaginin ışıltılı ve temiz kokusu.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"En Passant","brand":"Frederic Malle","notes_top":["bergamot", "cucumber", "water"],"notes_middle":["lilac", "wisteria", "carnation"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 35, "middle_pct": 40, "base_pct": 25},"season":"dört_mevsim","gender":"kadın","description":"Bir bahar yagmurunda leylak tarlasindan gecerken.","price_range":"3500-5000 TL","in_stock":True}
,
    {"name":"Kilian Love Don't Be Shy","brand":"Kilian","notes_top":["orange_blossom", "bergamot", "neroli"],"notes_middle":["jasmine", "rose", "iris"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 30, "middle_pct": 32, "base_pct": 38},"season":"dört_mevsim","gender":"kadın","description":"Marshmallow ve portakal çiçeğinin bastan çıkaranici dansi.","price_range":"3500-5000 TL","in_stock":True}
,
    {"name":"Kilian Black Phantom","brand":"Kilian","notes_top":["rum", "sugar", "cane"],"notes_middle":["coffee", "cocoa", "cardamom"],"notes_base":["vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"dört_mevsim","gender":"unisex","description":"Karanlik ve tatlı bir gurme yolculugu.","price_range":"3500-5000 TL","in_stock":True}
,
    {"name":"Creed Virgin Island Water","brand":"Creed","notes_top":["lime", "coconut", "bergamot"],"notes_middle":["jasmine", "hibiscus", "ginger"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 42, "middle_pct": 30, "base_pct": 28},"season":"dört_mevsim","gender":"unisex","description":"Karayiplere tropik bir koku yolculugu.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Prada Infusion d'Iris","brand":"Prada","notes_top":["mandarin", "orange", "neroli"],"notes_middle":["iris", "violet", "rosemary"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 35, "middle_pct": 38, "base_pct": 27},"season":"dört_mevsim","gender":"kadın","description":"Irisin pudralı ve asil sadeligi.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Prada Candy Florale","brand":"Prada","notes_top":["orange", "bergamot", "peony"],"notes_middle":["jasmine", "violet", "almond"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 35, "middle_pct": 35, "base_pct": 30},"season":"dört_mevsim","gender":"kadın","description":"Candy'nin daha çiçeksi ve hafif yorumu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Guerlain La Petite Robe Noire","brand":"Guerlain","notes_top":["bergamot", "almond", "cherry"],"notes_middle":["rose", "iris", "jasmine"],"notes_base":["vanilla", "musk", "amber", "patchouli"],"profile":{"top_pct": 32, "middle_pct": 35, "base_pct": 33},"season":"dört_mevsim","gender":"kadın","description":"Kucuk siyah elbise kadar zamansiz ve feminen.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Guerlain Aqua Allegoria Mandarine Basilic","brand":"Guerlain","notes_top":["mandarin", "bergamot", "citrus"],"notes_middle":["basil", "green_tea", "jasmine"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 45, "middle_pct": 30, "base_pct": 25},"season":"dört_mevsim","gender":"unisex","description":"Mandalin ve feslegenin ferah ve yeşil dansi.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Bottega Veneta Illusione","brand":"Bottega Veneta","notes_top":["bergamot", "lemon", "black_currant"],"notes_middle":["jasmine", "iris", "rose"],"notes_base":["musk", "vanilla", "amber", "olibanum"],"profile":{"top_pct": 35, "middle_pct": 35, "base_pct": 30},"season":"dört_mevsim","gender":"kadın","description":"Modern bir illuzyon: sıcak, temiz ve zarif.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Narciso Rodriguez Pure Musc","brand":"Narciso Rodriguez","notes_top":["bergamot", "jasmine", "orange_blossom"],"notes_middle":["musk", "peony", "rose"],"notes_base":["musk", "vanilla", "amber", "cedar"],"profile":{"top_pct": 33, "middle_pct": 35, "base_pct": 32},"season":"dört_mevsim","gender":"kadın","description":"Miskin en saf ve en temiz hali.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Givenchy Very Irresistible","brand":"Givenchy","notes_top":["anıse", "star_anıse", "pepper"],"notes_middle":["rose", "jasmine", "peony"],"notes_base":["musk", "vanilla", "amber", "cedar"],"profile":{"top_pct": 32, "middle_pct": 40, "base_pct": 28},"season":"dört_mevsim","gender":"kadın","description":"Karsi konulmaz bir çiçeksel bastan çıkaranma.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"YSL Black Opium Illicit Green","brand":"Yves Saint Laurent","notes_top":["coffee", "bergamot", "green"],"notes_middle":["jasmine", "orange_blossom", "iris"],"notes_base":["vanilla", "musk", "amber", "cedar"],"profile":{"top_pct": 30, "middle_pct": 32, "base_pct": 38},"season":"dört_mevsim","gender":"kadın","description":"Black Opium'un daha yeşil ve taze yorumu.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"Carolina Herrera 212 VIP","brand":"Carolina Herrera","notes_top":["rum", "pink_pepper", "bergamot"],"notes_middle":["jasmine", "rose", "orchid"],"notes_base":["musk", "vanilla", "amber", "sandalwood"],"profile":{"top_pct": 35, "middle_pct": 32, "base_pct": 33},"season":"dört_mevsim","gender":"kadın","description":"VIP partiler icin ışıltılı ve enerjik bir koku.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Olympea","brand":"Paco Rabanne","notes_top":["salt", "ginger", "bergamot"],"notes_middle":["jasmine", "vanilla", "cinnamon"],"notes_base":["musk", "amber", "sandalwood", "cashmeran"],"profile":{"top_pct": 35, "middle_pct": 30, "base_pct": 35},"season":"dört_mevsim","gender":"kadın","description":"Bir tanricanin tuzlu-vanilyalı imzasi.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Lady Million","brand":"Paco Rabanne","notes_top":["raspberry", "lemon", "honey"],"notes_middle":["jasmine", "rose", "orange_blossom"],"notes_base":["musk", "amber", "vanilla", "patchouli"],"profile":{"top_pct": 35, "middle_pct": 35, "base_pct": 30},"season":"dört_mevsim","gender":"kadın","description":"Bir milyon dolarlik çiçeksel ve ışıltılı guzellik.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Olympea Legend","brand":"Paco Rabanne","notes_top":["salt", "ginger", "bergamot"],"notes_middle":["vanilla", "jasmine", "cinnamon"],"notes_base":["musk", "amber", "sandalwood", "cashmeran"],"profile":{"top_pct": 32, "middle_pct": 30, "base_pct": 38},"season":"dört_mevsim","gender":"kadın","description":"Olympea'nin daha karanlık ve efsanevi versiyonu.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Gucci Guilty","brand":"Gucci","notes_top":["lavender", "pepper", "bergamot"],"notes_middle":["orange_blossom", "jasmine", "rose"],"notes_base":["musk", "amber", "patchouli", "cedar"],"profile":{"top_pct": 35, "middle_pct": 32, "base_pct": 33},"season":"dört_mevsim","gender":"kadın","description":"Modern bir suclulugün bastan çıkaranici kokusu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Gucci Guilty Pour Homme","brand":"Gucci","notes_top":["lavender", "bergamot", "lemon"],"notes_middle":["orange_blossom", "jasmine", "rose"],"notes_base":["musk", "amber", "patchouli", "cedar"],"profile":{"top_pct": 35, "middle_pct": 30, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Erkek versiyonu da en az kadıni kadar suclu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Bentley For Men Intense","brand":"Bentley","notes_top":["pepper", "bergamot", "lavender"],"notes_middle":["jasmine", "rose", "leather"],"notes_base":["musk", "amber", "vanilla", "cedar"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"dört_mevsim","gender":"erkek","description":"Bir lüks araba kadar maşkülen ve güçlu.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"Jimmy Choo Man","brand":"Jimmy Choo","notes_top":["lavender", "pineapple", "bergamot"],"notes_middle":["geranium", "patchouli", "cinnamon"],"notes_base":["musk", "amber", "sandalwood", "vanilla"],"profile":{"top_pct": 35, "middle_pct": 30, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Modern bir erkeğin sofistike ve çekici kokusu.","price_range":"800-1300 TL","in_stock":True}
,
    {"name":"Jimmy Choo Man Blue","brand":"Jimmy Choo","notes_top":["coconut", "grapefruit", "bergamot"],"notes_middle":["lavender", "geranium", "sage"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 40, "middle_pct": 28, "base_pct": 32},"season":"dört_mevsim","gender":"erkek","description":"Jimmy Choo Man'in ferah ve havadar yorumu.","price_range":"800-1300 TL","in_stock":True}
,
    {"name":"Guess 1981 Los Angeles","brand":"Guess","notes_top":["bergamot", "mandarin", "lemon"],"notes_middle":["lavender", "geranium", "sage"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 36, "middle_pct": 30, "base_pct": 34},"season":"dört_mevsim","gender":"erkek","description":"LA ruhunu yansitan ferah ve maşkülen bir koku.","price_range":"300-600 TL","in_stock":True}
,
    {"name":"John Varvatos Artisan","brand":"John Varvatos","notes_top":["mandarin", "lemon", "ginger"],"notes_middle":["orange_blossom", "jasmine", "coriander"],"notes_base":["musk", "amber", "woody", "vanilla"],"profile":{"top_pct": 40, "middle_pct": 28, "base_pct": 32},"season":"dört_mevsim","gender":"erkek","description":"El yapimi bir zanaatkarligin kokusu.","price_range":"800-1300 TL","in_stock":True}
,
    {"name":"Creed Royal Water","brand":"Creed","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "geranium", "clary_sage"],"notes_base":["musk", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 38, "middle_pct": 30, "base_pct": 32},"season":"dört_mevsim","gender":"unisex","description":"Kraliyet ailesine yakisir ferah ve zarif bir su.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Roja Parfums Enigma Pour Homme","brand":"Roja Parfums","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "coriander", "sage"],"notes_base":["vanilla", "musk", "amber", "cognac", "tobacco"],"profile":{"top_pct": 30, "middle_pct": 28, "base_pct": 42},"season":"dört_mevsim","gender":"erkek","description":"Konyak ve tutunun en l\u00fcks maşkülen yorumu.","price_range":"8000-12000 TL","in_stock":True}
,
    {"name":"Xerjoff 1861 Renaissance","brand":"Xerjoff","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 36, "middle_pct": 30, "base_pct": 34},"season":"dört_mevsim","gender":"unisex","description":"Nis parfümeride bir Italyan başyapıtı.","price_range":"5000-7500 TL","in_stock":True}
,
    {"name":"Xerjoff Comandante","brand":"Xerjoff","notes_top":["bergamot", "lemon", "grapefruit", "pepper"],"notes_middle":["rose", "jasmine", "iris", "cinnamon"],"notes_base":["leather", "musk", "amber", "vanilla", "cedar"],"profile":{"top_pct": 32, "middle_pct": 30, "base_pct": 38},"season":"dört_mevsim","gender":"erkek","description":"Bir komutana yakisir güçlu ve maşkülen koku.","price_range":"5000-7500 TL","in_stock":True}
,
    {"name":"Amouage Reflection Man","brand":"Amouage","notes_top":["bergamot", "lemon", "mandarin", "rosemary"],"notes_middle":["jasmine", "rose", "iris", "geranium"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 32, "middle_pct": 36, "base_pct": 32},"season":"dört_mevsim","gender":"erkek","description":"Umman lüksunun en zarif maşkülen yansıması.","price_range":"6000-9000 TL","in_stock":True}
,
    {"name":"Amouage Reflection Woman","brand":"Amouage","notes_top":["bergamot", "lemon", "mandarin", "coriander"],"notes_middle":["jasmine", "rose", "iris", "geranium"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 30, "middle_pct": 38, "base_pct": 32},"season":"dört_mevsim","gender":"kadın","description":"Amouage'un feminen yuzu: asil ve çiçeksi.","price_range":"6000-9000 TL","in_stock":True}
,
    {"name":"Amouage Interlude Man","brand":"Amouage","notes_top":["bergamot", "lemon", "pepper", "sage"],"notes_middle":["jasmine", "rose", "cinnamon", "patchouli"],"notes_base":["musk", "amber", "oud", "vanilla", "leather"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"dört_mevsim","gender":"erkek","description":"Oudun ve baharatin en güçlu Umman dansi.","price_range":"6000-9000 TL","in_stock":True}
,
    {"name":"Amouage Epic Man","brand":"Amouage","notes_top":["bergamot", "lemon", "coriander", "sage"],"notes_middle":["jasmine", "rose", "geranium", "cinnamon"],"notes_base":["musk", "amber", "oud", "leather", "vanilla"],"profile":{"top_pct": 30, "middle_pct": 30, "base_pct": 40},"season":"dört_mevsim","gender":"erkek","description":"Bir destani anlatan epik bir koku.","price_range":"6000-9000 TL","in_stock":True}
,
    {"name":"Amouage Lyric Man","brand":"Amouage","notes_top":["bergamot", "lemon", "ginger", "coriander"],"notes_middle":["rose", "jasmine", "geranium", "ylang"],"notes_base":["musk", "amber", "sandalwood", "vanilla", "cedar"],"profile":{"top_pct": 32, "middle_pct": 36, "base_pct": 32},"season":"dört_mevsim","gender":"erkek","description":"Bir güle adanmis en lirik ve en dogülu koku.","price_range":"6000-9000 TL","in_stock":True}
,
    {"name":"Amouage Jubilation XXV Man","brand":"Amouage","notes_top":["bergamot", "lemon", "mandarin", "coriander"],"notes_middle":["jasmine", "rose", "geranium", "cinnamon"],"notes_base":["musk", "amber", "oud", "vanilla", "incense"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"dört_mevsim","gender":"erkek","description":"25. yila ozel çıkaranilmis bir başyapıt.","price_range":"7000-10000 TL","in_stock":True}
,
    {"name":"MFK Oud Satin Mood","brand":"Maison Francis Kurkdjian","notes_top":["bergamot", "lemon", "mandarin", "saffron"],"notes_middle":["rose", "jasmine", "violet", "geranium"],"notes_base":["oud", "vanilla", "musk", "amber", "sandalwood"],"profile":{"top_pct": 25, "middle_pct": 30, "base_pct": 45},"season":"dört_mevsim","gender":"kadın","description":"Oudun vanilyayla en saten yumuşakligi.","price_range":"5000-7500 TL","in_stock":True}
,
    {"name":"MFK L'Homme A la Rose","brand":"Maison Francis Kurkdjian","notes_top":["bergamot", "lemon", "grapefruit", "pepper"],"notes_middle":["rose", "jasmine", "geranium", "violet"],"notes_base":["musk", "amber", "sandalwood", "cedar", "vanilla"],"profile":{"top_pct": 35, "middle_pct": 35, "base_pct": 30},"season":"dört_mevsim","gender":"unisex","description":"Bir erkeğe hediye edilmis en guzel gül.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"MFK Aqua Universalis","brand":"Maison Francis Kurkdjian","notes_top":["bergamot", "lemon", "mandarin", "bitter_orange"],"notes_middle":["jasmine", "rose", "violet", "lily"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 38, "middle_pct": 32, "base_pct": 30},"season":"dört_mevsim","gender":"unisex","description":"Herkes icin evrensel bir ferah sukluk.","price_range":"3500-5000 TL","in_stock":True}
,
    {"name":"MFK Petit Matin","brand":"Maison Francis Kurkdjian","notes_top":["lemon", "bergamot", "mandarin", "lavender"],"notes_middle":["jasmine", "rose", "iris", "sage"],"notes_base":["musk", "amber", "sandalwood", "cedar", "vanilla"],"profile":{"top_pct": 42, "middle_pct": 30, "base_pct": 28},"season":"dört_mevsim","gender":"unisex","description":"Kucuk bir sabahin ışıltılı ve ferah keyfi.","price_range":"3500-5000 TL","in_stock":True}
,
    {"name":"Kilian Angels Share","brand":"Kilian","notes_top":["cognac", "bergamot", "lemon", "cinnamon"],"notes_middle":["jasmine", "rose", "violet", "tonka"],"notes_base":["vanilla", "musk", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"dört_mevsim","gender":"unisex","description":"Bir melegenin ici: konyak ve vanilya ilahisi.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Kilian Good Girl Gone Bad","brand":"Kilian","notes_top":["bergamot", "mandarin", "lemon", "pepper"],"notes_middle":["jasmine", "rose", "tuberose", "orange_blossom"],"notes_base":["musk", "vanilla", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 28, "middle_pct": 42, "base_pct": 30},"season":"dört_mevsim","gender":"kadın","description":"Iyi bir kizin kotu tarafina yaptigi yolculuk.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Frederic Malle Vetiver Extraordinaire","brand":"Frederic Malle","notes_top":["bergamot", "lemon", "mandarin", "coriander"],"notes_middle":["vetiver", "jasmine", "rose", "cedar"],"notes_base":["musk", "amber", "sandalwood", "vanilla", "oakmoss"],"profile":{"top_pct": 32, "middle_pct": 30, "base_pct": 38},"season":"dört_mevsim","gender":"unisex","description":"Vetiverin en siradisi ve en zarif hali.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Frederic Malle L'Eau d'Hiver","brand":"Frederic Malle","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "iris", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 35, "middle_pct": 35, "base_pct": 30},"season":"dört_mevsim","gender":"unisex","description":"Kis suyunun sıcak ve pudralı kucaklayisi.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Memo Irish Leather","brand":"Memo Paris","notes_top":["bergamot", "lemon", "mandarin", "violet"],"notes_middle":["jasmine", "rose", "iris", "geranium"],"notes_base":["leather", "musk", "amber", "vanilla", "cedar"],"profile":{"top_pct": 30, "middle_pct": 30, "base_pct": 40},"season":"dört_mevsim","gender":"unisex","description":"Irlanda kirlarinda deriyi andiran yeşil bir yolculuk.","price_range":"4000-6000 TL","in_stock":True}
,
    {"name":"Memo Winter Palace","brand":"Memo Paris","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "cinnamon", "saffron"],"notes_base":["musk", "amber", "vanilla", "cedar", "tea"],"profile":{"top_pct": 30, "middle_pct": 30, "base_pct": 40},"season":"dört_mevsim","gender":"unisex","description":"Bir kis sarayinin ihti samli ve sıcak kokusu.","price_range":"4500-6500 TL","in_stock":True}
,
    {"name":"Serge Lutens Ambre Sultan","brand":"Serge Lutens","notes_top":["bergamot", "lemon", "mandarin", "coriander"],"notes_middle":["jasmine", "rose", "amber", "patchouli"],"notes_base":["musk", "amber", "vanilla", "cedar", "sandalwood"],"profile":{"top_pct": 22, "middle_pct": 28, "base_pct": 50},"season":"dört_mevsim","gender":"unisex","description":"Bir sultanin amber hazinesinin kapilari.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Serge Lutens Chergui","brand":"Serge Lutens","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "iris", "honey", "tobacco"],"notes_base":["musk", "amber", "vanilla", "cedar", "sandalwood"],"profile":{"top_pct": 22, "middle_pct": 32, "base_pct": 46},"season":"dört_mevsim","gender":"unisex","description":"Bir col ruzgarinda bal ve tutunun buluşması.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Serge Lutens La Fille de Berlin","brand":"Serge Lutens","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["rose", "jasmine", "violet", "geranium"],"notes_base":["musk", "vanilla", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 28, "middle_pct": 40, "base_pct": 32},"season":"dört_mevsim","gender":"kadın","description":"Berlinli bir kizin asi ve romantik rose kokusu.","price_range":"2000-3000 TL","in_stock":True}
,
    {"name":"Acqua di Parma Colonia Oud","brand":"Acqua di Parma","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["oud", "musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 30, "middle_pct": 28, "base_pct": 42},"season":"dört_mevsim","gender":"unisex","description":"Colonia'nin oud'lu ve dogülu soy'dan gelen versiyonu.","price_range":"3000-4500 TL","in_stock":True}
,
    {"name":"Dior Homme Sport 2021","brand":"Dior","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 38, "middle_pct": 28, "base_pct": 34},"season":"dört_mevsim","gender":"erkek","description":"Spor bir Dior Homme'un ferah ve modern yorumu.","price_range":"1800-2600 TL","in_stock":True}
,
    {"name":"Chanel No 5 L'Eau","brand":"Chanel","notes_top":["aldehyde", "ylang", "neroli", "bergamot", "lemon"],"notes_middle":["jasmine", "rose", "iris", "lily", "geranium"],"notes_base":["musk", "vanilla", "vetiver", "sandalwood", "cedar"],"profile":{"top_pct": 38, "middle_pct": 32, "base_pct": 30},"season":"dört_mevsim","gender":"kadın","description":"No 5'in daha ferah, daha genç ve daha ışıltılı yorumu.","price_range":"2200-3200 TL","in_stock":True}
,
    {"name":"Chanel Coco Noir","brand":"Chanel","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "iris", "geranium"],"notes_base":["musk", "vanilla", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 25, "middle_pct": 32, "base_pct": 43},"season":"dört_mevsim","gender":"kadın","description":"Coco'nun karanlık ve gizemli kardesi.","price_range":"2200-3200 TL","in_stock":True}
,
    {"name":"YSL Black Opium Neon","brand":"Yves Saint Laurent","notes_top":["coffee", "bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "iris", "orange_blossom"],"notes_base":["vanilla", "musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 32, "middle_pct": 30, "base_pct": 38},"season":"dört_mevsim","gender":"kadın","description":"Black Opium'un neon ışıltılariyla aydinlanan yorumu.","price_range":"1500-2200 TL","in_stock":True}
,
    {"name":"YSL Manifesto","brand":"Yves Saint Laurent","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "iris", "geranium"],"notes_base":["vanilla", "musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 28, "middle_pct": 35, "base_pct": 37},"season":"dört_mevsim","gender":"kadın","description":"YSL kadınınin manifestosu: cesur ve çiçeksi.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Prada Candy Night","brand":"Prada","notes_top":["bergamot", "lemon", "mandarin", "orange"],"notes_middle":["jasmine", "rose", "violet", "iris"],"notes_base":["vanilla", "musk", "amber", "sandalwood", "patchouli"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"dört_mevsim","gender":"kadın","description":"Candy'nin gece ve daha derin yorumu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Valentino Uomo","brand":"Valentino","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "iris", "geranium"],"notes_base":["vanilla", "musk", "amber", "cedar", "leather"],"profile":{"top_pct": 30, "middle_pct": 32, "base_pct": 38},"season":"dört_mevsim","gender":"erkek","description":"Bir Valentino erke gine yakisir zarif ve çekici koku.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Valentino Uomo Intense","brand":"Valentino","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "iris", "geranium"],"notes_base":["vanilla", "musk", "amber", "leather", "cedar"],"profile":{"top_pct": 26, "middle_pct": 30, "base_pct": 44},"season":"dört_mevsim","gender":"erkek","description":"Uomo'nun daha yoğun ve derin kardesi.","price_range":"1300-1900 TL","in_stock":True}
,
    {"name":"Bvlgari Man In Black","brand":"Bvlgari","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["leather", "musk", "amber", "vanilla", "cedar"],"profile":{"top_pct": 28, "middle_pct": 30, "base_pct": 42},"season":"dört_mevsim","gender":"erkek","description":"Siyah icindeki bir adamin gizemli kokusu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Bvlgari Goldea","brand":"Bvlgari","notes_top":["bergamot", "mandarin", "pear", "pepper"],"notes_middle":["jasmine", "rose", "violet", "geranium"],"notes_base":["musk", "vanilla", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 32, "middle_pct": 32, "base_pct": 36},"season":"dört_mevsim","gender":"kadın","description":"Altin kadar degerli ve ışıltılı bir Bvlgari klasiği.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Gucci Bloom Acqua di Fiori","brand":"Gucci","notes_top":["bergamot", "lemon", "mandarin", "coriander"],"notes_middle":["jasmine", "rose", "violet", "iris"],"notes_base":["musk", "vanilla", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 38, "middle_pct": 35, "base_pct": 27},"season":"dört_mevsim","gender":"kadın","description":"Gucci Bloom'un daha yeşil ve ferah yorumu.","price_range":"1600-2400 TL","in_stock":True}
,
    {"name":"Gucci Gorgeous Magnolia","brand":"Gucci","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["magnolia", "jasmine", "rose", "violet"],"notes_base":["musk", "vanilla", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 35, "middle_pct": 38, "base_pct": 27},"season":"dört_mevsim","gender":"kadın","description":"Magnolia çiçeğinin muhtesem ve büyülü kokusu.","price_range":"1400-2000 TL","in_stock":True}
,
    {"name":"Burberry Brit Rhythm","brand":"Burberry","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "geranium", "sage"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 34, "middle_pct": 30, "base_pct": 36},"season":"dört_mevsim","gender":"erkek","description":"Ingiliz muzik sahnesinin ritmini yakalayan bir koku.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"Ralph Lauren Polo Ultra Blue","brand":"Ralph Lauren","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 38, "middle_pct": 28, "base_pct": 34},"season":"dört_mevsim","gender":"erkek","description":"Polo Blue'un daha derin ve yoğun versiyonu.","price_range":"600-1000 TL","in_stock":True}
,
    {"name":"Tommy Hilfiger Tommy","brand":"Tommy Hilfiger","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 36, "middle_pct": 28, "base_pct": 36},"season":"dört_mevsim","gender":"erkek","description":"Amerikan ruyasinin en klasik maşkülen kokusu.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"Tommy Hilfiger Tommy Girl","brand":"Tommy Hilfiger","notes_top":["bergamot", "mandarin", "pear", "lemon"],"notes_middle":["jasmine", "rose", "violet", "geranium"],"notes_base":["musk", "vanilla", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 38, "middle_pct": 32, "base_pct": 30},"season":"dört_mevsim","gender":"kadın","description":"Tommy Hilfiger kizinin enerjik ve çiçeksi kokusu.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"Kenneth Cole Black","brand":"Kenneth Cole","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 34, "middle_pct": 30, "base_pct": 36},"season":"dört_mevsim","gender":"erkek","description":"New York'lu modern bir erkeğe yakisir koku.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"Perry Ellis 360 Red","brand":"Perry Ellis","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 36, "middle_pct": 28, "base_pct": 36},"season":"dört_mevsim","gender":"erkek","description":"Uygün fiyatli ama kaliteli bir günluk maşkülen koku.","price_range":"300-500 TL","in_stock":True}
,
    {"name":"Brut","brand":"Faberge","notes_top":["bergamot", "lemon", "lavender", "anıs"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "oakmoss", "vanilla"],"profile":{"top_pct": 34, "middle_pct": 30, "base_pct": 36},"season":"dört_mevsim","gender":"erkek","description":"1962'den beri erkekligin sembolu olmus bir klasik.","price_range":"150-300 TL","in_stock":True}
,
    {"name":"Pino Silvestre","brand":"Pino Silvestre","notes_top":["bergamot", "lemon", "mandarin", "pine"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "pine", "oakmoss"],"profile":{"top_pct": 38, "middle_pct": 26, "base_pct": 36},"season":"dört_mevsim","gender":"erkek","description":"Bir cam ormaninin ferah ve yeşil maşkülen kokusu.","price_range":"200-400 TL","in_stock":True}
,
    {"name":"Davidoff Champion","brand":"Davidoff","notes_top":["bergamot", "lemon", "mandarin"],"notes_middle":["jasmine", "rose", "geranium"],"notes_base":["musk", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 30, "middle_pct": 28, "base_pct": 42},"season":"dört_mevsim","gender":"erkek","description":"Bir sapiyona yakisir enerjik ve maşkülen koku.","price_range":"400-600 TL","in_stock":True}
,
    {"name":"Hugo Boss Bottled Night","brand":"Hugo Boss","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 32, "middle_pct": 30, "base_pct": 38},"season":"dört_mevsim","gender":"erkek","description":"Bottled'in gece ve gizemli kardesi.","price_range":"800-1200 TL","in_stock":True}
,
    {"name":"Boss Bottled Infinite","brand":"Hugo Boss","notes_top":["apple", "bergamot", "lemon", "plum"],"notes_middle":["geranium", "cinnamon", "vanilla"],"notes_base":["sandalwood", "cedar", "musk", "olibanum"],"profile":{"top_pct": 33, "middle_pct": 32, "base_pct": 35},"season":"dört_mevsim","gender":"erkek","description":"Boss Bottled'in sonsuzluğa uzanan yorumu.","price_range":"1000-1500 TL","in_stock":True}
,
    {"name":"Carolina Herrera 212 Men","brand":"Carolina Herrera","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 36, "middle_pct": 28, "base_pct": 36},"season":"dört_mevsim","gender":"erkek","description":"New York gecelerine yakisir maşkülen bir koku.","price_range":"700-1100 TL","in_stock":True}
,
    {"name":"Carolina Herrera 212 Sexy Men","brand":"Carolina Herrera","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 34, "middle_pct": 30, "base_pct": 36},"season":"dört_mevsim","gender":"erkek","description":"212'nin daha seksi ve sıcak kardesi.","price_range":"700-1100 TL","in_stock":True}
,
    {"name":"Emporio Armani He","brand":"Emporio Armani","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 36, "middle_pct": 28, "base_pct": 36},"season":"dört_mevsim","gender":"erkek","description":"Giorgio Armani genç erkeğe hitap eden koku.","price_range":"800-1200 TL","in_stock":True}
,
    {"name":"Emporio Armani She","brand":"Emporio Armani","notes_top":["bergamot", "mandarin", "pear", "lemon"],"notes_middle":["jasmine", "rose", "violet", "geranium"],"notes_base":["musk", "vanilla", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 36, "middle_pct": 32, "base_pct": 32},"season":"dört_mevsim","gender":"kadın","description":"Giorgio Armani genç kadınına hitap eden koku.","price_range":"800-1200 TL","in_stock":True}
,
    {"name":"Lanvin L'Homme","brand":"Lanvin","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 34, "middle_pct": 30, "base_pct": 36},"season":"dört_mevsim","gender":"erkek","description":"Fransiz moda evinin maşkülen ve zarif kokusu.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"Lanvin Eclat d'Arpege","brand":"Lanvin","notes_top":["bergamot", "mandarin", "pear", "lemon"],"notes_middle":["jasmine", "rose", "violet", "geranium"],"notes_base":["musk", "vanilla", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 36, "middle_pct": 34, "base_pct": 30},"season":"dört_mevsim","gender":"kadın","description":"Bir arpejin ışıltılı ve çiçeksi yankisi.","price_range":"400-700 TL","in_stock":True}
,
    {"name":"St Dupont Pour Homme","brand":"St Dupont","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 34, "middle_pct": 30, "base_pct": 36},"season":"dört_mevsim","gender":"erkek","description":"Fransiz lüksunun maşkülen yansıması.","price_range":"500-900 TL","in_stock":True}
,
    {"name":"Balenciaga B","brand":"Balenciaga","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "violet", "geranium"],"notes_base":["musk", "vanilla", "amber", "cedar", "sandalwood"],"profile":{"top_pct": 34, "middle_pct": 30, "base_pct": 36},"season":"dört_mevsim","gender":"unisex","description":"Balenciaga'nin modern unisex kokusu.","price_range":"1200-1800 TL","in_stock":True}
,
    {"name":"Jil Sander Sun Men","brand":"Jil Sander","notes_top":["bergamot", "lemon", "mandarin", "grapefruit"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 38, "middle_pct": 28, "base_pct": 34},"season":"dört_mevsim","gender":"erkek","description":"Alman moda devinin maşkülen ve günesli kokusu.","price_range":"300-500 TL","in_stock":True}
,
    {"name":"Jil Sander Sun Women","brand":"Jil Sander","notes_top":["bergamot", "mandarin", "pear", "lemon"],"notes_middle":["jasmine", "rose", "violet", "geranium"],"notes_base":["musk", "vanilla", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 38, "middle_pct": 30, "base_pct": 32},"season":"dört_mevsim","gender":"kadın","description":"Alman moda devinin feminen ve günesli kokusu.","price_range":"300-500 TL","in_stock":True}
,
    {"name":"Escada Moon Sparkle","brand":"Escada","notes_top":["bergamot", "mandarin", "pear", "lemon"],"notes_middle":["jasmine", "rose", "violet", "geranium"],"notes_base":["musk", "vanilla", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 36, "middle_pct": 32, "base_pct": 32},"season":"dört_mevsim","gender":"kadın","description":"Mehtap altında bir yaz gecesi ışıltısi.","price_range":"500-800 TL","in_stock":True}
,
    {"name":"Boucheron Place Vendome","brand":"Boucheron","notes_top":["bergamot", "mandarin", "pear", "lemon"],"notes_middle":["jasmine", "rose", "violet", "geranium"],"notes_base":["musk", "vanilla", "amber", "sandalwood", "cedar"],"profile":{"top_pct": 34, "middle_pct": 34, "base_pct": 32},"season":"dört_mevsim","gender":"kadın","description":"Paris'in en lüks meydanina saygi duruyor.","price_range":"800-1200 TL","in_stock":True}
,
    {"name":"Swiss Army Classic","brand":"Swiss Army","notes_top":["bergamot", "lemon", "mandarin", "pepper"],"notes_middle":["jasmine", "rose", "geranium", "coriander"],"notes_base":["musk", "amber", "cedar", "sandalwood", "vanilla"],"profile":{"top_pct": 36, "middle_pct": 28, "base_pct": 36},"season":"dört_mevsim","gender":"erkek","description":"Isvicre cakisi kadar kullanısli ve guvenilir bir koku.","price_range":"300-500 TL","in_stock":True}
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DATA_DIR, "perfume_database.json")
DB_LOCK = threading.Lock()

def _init_database():
    global PERFUME_DATABASE
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    PERFUME_DATABASE = data
                    return data
    except (json.JSONDecodeError, FileNotFoundError):
        corrupted_path = DB_PATH + ".corrupted." + datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            os.rename(DB_PATH, corrupted_path)
            _write_audit("system", "RECOVER", "perfume_database", 0,
                        {"error": "corrupted_json"}, {"recovered_to": corrupted_path})
        except:
            pass
    save_database()
    return PERFUME_DATABASE

def save_database():
    os.makedirs(DATA_DIR, exist_ok=True)
    with DB_LOCK:
        fd, tmp_path = tempfile.mkstemp(suffix=".json", dir=DATA_DIR)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(PERFUME_DATABASE, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, DB_PATH)
        except:
            os.unlink(tmp_path)
            raise

def _write_audit(actor, action, table_name, record_id, old_values=None, new_values=None):
    try:
        log_path = os.path.join(DATA_DIR, "audit_log.jsonl")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "actor": actor,
            "action": action,
            "table": table_name,
            "record_id": record_id,
            "old_values": old_values,
            "new_values": new_values
        }
        with DB_LOCK:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except:
        pass

def check_critical_stock(perfume_name=None, old_stock=None, new_stock=None):
    try:
        if old_stock is not None and new_stock is not None:
            if old_stock is True and new_stock is False:
                _write_audit("system", "CRITICAL_STOCK", "perfume_database", 0,
                            {}, {"message": f"Stok bitti: {perfume_name}"})
    except:
        pass

class PerfumeMatchingEngine:
    def __init__(self):
        self.parfümler = _init_database()
        self.cache_dir = os.path.join(os.path.dirname(__file__), "data", "cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def find_matches(self, nota_profili, gender="unisex"):
        top_dominant = nota_profili.get("top_dominant", "citrus")
        middle_dominant = nota_profili.get("middle_dominant", "floral")
        base_dominant = nota_profili.get("base_dominant", "musk")
        top_pct = nota_profili.get("top_pct", 33)
        middle_pct = nota_profili.get("middle_pct", 33)
        base_pct = nota_profili.get("base_pct", 34)
        profile_type = nota_profili.get("profile_type", self._belirleme(top_pct, middle_pct, base_pct))

        scored = []
        for p in self.parfümler:
            if not self._gender_allowed(p["gender"], gender):
                continue
            sim = self._calculate_similarity(p, top_dominant, middle_dominant, base_dominant, top_pct, middle_pct, base_pct)
            bonus = 30 if p["gender"] == gender else (15 if p["gender"] == "unisex" and gender != "unisex" else 0)
            scored.append((sim + bonus, sim, p))

        scored.sort(key=lambda x: x[0], reverse=True)

        yazlık = [x for x in scored if x[2]["season"] == "yaz"]
        kışlık = [x for x in scored if x[2]["season"] == "kis"]
        dört_mevsim = [x for x in scored if x[2]["season"] in ("dört_mevsim", "dort_mevsim")]

        def season_sort_key(season_list, weight_field):
            return sorted(season_list, key=lambda x: x[2]["profile"][weight_field] * 0.3 + x[1] * 0.7, reverse=True)

        yazlık = season_sort_key(yazlık, "top_pct")
        kışlık = season_sort_key(kışlık, "base_pct")

        def balance_key(x):
            p = x[2]["profile"]
            return (50 - abs(p["top_pct"] - 33) - abs(p["middle_pct"] - 33) - abs(p["base_pct"] - 34)) * 0.3 + x[1] * 0.7
        dört_mevsim = sorted(dört_mevsim, key=balance_key, reverse=True)

        def pick_unique(candidates, count, exclude_names):
            result = []
            for _, _, p in candidates:
                if p["name"] not in exclude_names and len(result) < count:
                    result.append(p)
                    exclude_names.add(p["name"])
                if len(result) >= count:
                    break
            return result

        def fallback_fill(season_list, season_value, count, exclude_names, all_scored):
            result = list(season_list)
            if len(result) >= count:
                return result
            for _, _, p in all_scored:
                if p["season"] != season_value and (season_value == "dört_mevsim" or p["season"] != ("dört_mevsim" if season_value == "kis" else "dört_mevsim")):
                    if season_value == "yaz" and p["season"] not in ("yaz", "dört_mevsim", "dort_mevsim"):
                        continue
                    if season_value == "kis" and p["season"] not in ("kis", "dört_mevsim", "dort_mevsim"):
                        continue
                    if season_value in ("dört_mevsim", "dort_mevsim") and p["season"] not in ("dört_mevsim", "dort_mevsim"):
                        continue
                if p["name"] not in exclude_names and len(result) < count:
                    result.append(p)
                    exclude_names.add(p["name"])
                if len(result) >= count:
                    break
            return result

        used_names = set()
        oneri_yaz = pick_unique(yazlık, 3, used_names)
        oneri_kis = pick_unique(kışlık, 3, used_names)
        oneri_dört = pick_unique(dört_mevsim, 3, used_names)

        oneri_yaz = fallback_fill(oneri_yaz, "yaz", 3, used_names, scored)
        oneri_kis = fallback_fill(oneri_kis, "kis", 3, used_names, scored)
        oneri_dört = fallback_fill(oneri_dört, "dört_mevsim", 3, used_names, scored)

        return {
            "yaz": oneri_yaz,
            "kis": oneri_kis,
            "dört_mevsim": oneri_dört,
            "profile_type": profile_type
        }

    def _gender_allowed(self, perfume_gender, user_gender):
        if user_gender == "unisex":
            return True
        if perfume_gender == "unisex":
            return True
        return perfume_gender == user_gender

    def _belirleme(self, top_pct, middle_pct, base_pct):
        max_pct = max(top_pct, middle_pct, base_pct)
        if max_pct >= 40:
            if max_pct == top_pct:
                return "Yaz-Kehribar (Top Note Agirlikli)"
            elif max_pct == base_pct:
                return "Kis-Derin (Base Note Agirlikli)"
            elif max_pct == middle_pct:
                return "Ilkbahar-Yaz (Middle Note Agirlikli)"
            else:
                return "Karma Profil"
        elif top_pct >= 35:
            return "Hafif Yaz Egilimli"
        elif base_pct >= 35:
            return "Hafif Kis Egilimli"
        elif top_pct >= 25 and middle_pct >= 25 and base_pct >= 20:
            return "4 Mevsim Unisex (Dengeli Profil)"
        else:
            return "Karma Profil"

    def _calculate_similarity(self, parfüm, top_dom, mid_dom, base_dom, top_pct, mid_pct, base_pct):
        score = 0
        note_map = {
            "citrus": ["citrus", "bergamot", "lemon", "orange", "grapefruit", "mandarin", "lime", "yuzu", "tangerine", "blood_orange", "blood_mandarin", "green_tangerine", "green_mandarin", "bitter_orange"],
            "bergamot": ["bergamot"],
            "green": ["green", "grass", "leaf", "galbanum", "fig", "violet_leaf", "hay_top", "bamboo", "cucumber", "cane", "bay_leaf", "crystal_moss"],
            "aqua": ["aqua", "marine", "sea", "salt", "ozone", "calone", "ocean", "water", "caviar", "ice", "sea_water", "water_hyacinth", "seaweed"],
            "fruity_top": ["apple", "pear", "pineapple", "tropical", "berry", "melon", "cassis", "strawberry", "papaya", "goji", "quince", "cranberry", "blueberry", "nectarine", "rhubarb", "cloudberry", "red_apple", "fruity"],
            "aldehyde": ["aldehyde", "aldehydic", "soapy", "sparkling", "solar_notes"],
            "spice_top": ["pepper", "pink_pepper", "black_pepper", "chili", "elemi"],
            "aromatic_top": ["mint", "peppermint", "eucalyptus", "anıs", "anıse", "basil", "tarragon", "star_anıse"],
            "floral": ["rose", "jasmine", "ylang", "orchid", "gardenia", "freesia", "lily", "carnation", "champaca", "violet", "peony", "magnolia", "hibiscus", "osmanthus", "lilac", "hyacinth", "wisteria", "cyclamen", "daisy", "hawthorn", "narcissus", "marigold", "buttercup", "bluebell", "lotus", "muguet", "syringa", "white_rose"],
            "white_floral": ["jasmine", "tuberose", "gardenia", "lily", "neroli", "orange_blossom", "stephanotis", "honeysuckle"],
            "spice_mid": ["cinnamon", "clove", "cardamom", "ginger", "nutmeg", "saffron", "coriander", "caraway", "cumin", "mace", "paprika", "spice"],
            "herbal": ["lavender", "sage", "rosemary", "thyme", "basil", "mint", "chamomile", "clary_sage", "geranium", "angelica", "cannabis", "myrtle", "tea", "white_thyme", "nard"],
            "fruity_mid": ["peach", "apricot", "plum", "raspberry", "lychee", "blackberry", "cherry", "apple_mid", "pear_mid", "black_currant", "pomegranate", "mirabelle", "red_fruit"],
            "powdery": ["iris", "violet", "almond", "heliotrope", "powdery", "orris", "mimosa", "bitter_almond", "licorice"],
            "honey_tobacco": ["honey", "tobacco_blossom", "beeswax", "hay", "broom"],
            "woody_mid": ["cedar_mid", "sandalwood_mid", "pine_mid", "cashmeran_mid", "cedar", "sandalwood"],
            "woody": ["cedar", "sandalwood", "pine", "woody", "cashmeran", "cypress", "juniper", "akigalawood", "guaiac_wood", "teak", "rosewood", "wood"],
            "amber": ["amber", "ambroxan", "ambergris", "labdanum", "golden_amber", "succinic", "ambre", "cistus", "iso_e_super"],
            "vanilla_gourmand": ["vanilla", "tonka", "benzoin", "caramel", "praline", "cocoa", "chocolate", "sugar", "cotton_candy", "almond", "coffee", "coconut", "cognac", "rum", "pistachio", "chestnut"],
            "musk": ["musk", "white_musk", "vegetal_musk", "silky_musk", "ambrette"],
            "leather": ["leather", "suede", "isobutyl_quinoline", "birch_tar", "styrax", "asphalt"],
            "oud": ["oud", "agarwood", "oudh"],
            "patchouli_earthy": ["patchouli", "earthy", "soil", "moss", "oakmoss", "tree_moss", "vetiver", "mineral", "truffle", "fir_resin"],
            "incense_tobacco": ["incense", "frankincense", "myrrh", "tobacco", "hay", "dried_fruit", "raisin", "olibanum"]
        }

        # 1) Dominant note matching — strong signal
        note_layers = [
            (top_dom, parfüm["notes_top"]),
            (mid_dom, parfüm["notes_middle"]),
            (base_dom, parfüm["notes_base"])
        ]
        for dom, notes in note_layers:
            if dom in note_map:
                for keyword in note_map[dom]:
                    for p_note in notes:
                        if keyword == p_note or p_note.startswith(keyword + "_") or keyword.startswith(p_note + "_"):
                            score += 10
                            break

        # 2) Profile percentage similarity — PRIMARY differentiator
        pct_diff = abs(parfüm["profile"]["top_pct"] - top_pct) + \
                   abs(parfüm["profile"]["middle_pct"] - mid_pct) + \
                   abs(parfüm["profile"]["base_pct"] - base_pct)
        score += max(0, 50 - pct_diff)

        # 3) Penalty for mismatched dominant layer
        p_top = parfüm["profile"]["top_pct"]
        p_mid = parfüm["profile"]["middle_pct"]
        p_base = parfüm["profile"]["base_pct"]
        if top_pct > 40 and p_top < 25:
            score -= 15
        if mid_pct > 40 and p_mid < 25:
            score -= 15
        if base_pct > 40 and p_base < 25:
            score -= 15

        return score

    def search_fragrantica(self, query, max_results=5):
        cache_key = hashlib.md5(f"fragrantica_{query}".encode()).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) < 86400:
            with open(cache_path, "r") as f:
                return json.load(f)

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            url = f"https://www.fragrantica.com/search/?q={query.replace(' ', '+')}"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return []
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            items = soup.select(".grid-item a, .search-result-item, .perfume-card")[:max_results]
            for item in items:
                name = item.get_text(strip=True)
                link = item.get("href", "")
                if name and link:
                    results.append({"name": name, "url": f"https://www.fragrantica.com{link}" if link.startswith("/") else link})
            with open(cache_path, "w") as f:
                json.dump(results, f)
            return results
        except:
            return []

    def search_parfümo(self, query, max_results=5):
        cache_key = hashlib.md5(f"parfümo_{query}".encode()).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) < 86400:
            with open(cache_path, "r") as f:
                return json.load(f)
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            url = f"https://www.parfümo.com/search?q={query.replace(' ', '+')}"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return []
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            items = soup.select(".perfume-card, .search-item, a[href*='perfume']")[:max_results]
            seen = set()
            for item in items:
                href = item.get("href", "")
                text = item.get_text(strip=True)
                if href and text and "perfume" in href.lower():
                    full_url = f"https://www.parfümo.com{href}" if href.startswith("/") else href
                    if text not in seen:
                        seen.add(text)
                        results.append({"name": text, "url": full_url})
            with open(cache_path, "w") as f:
                json.dump(results, f)
            return results
        except:
            return []

# Global matching engine instance (used by routes)
matching_engine = PerfumeMatchingEngine()
