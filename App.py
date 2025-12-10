
import os
import sys
import time
import json
import base64
import random
import traceback
import re
from functools import lru_cache

from flask import (
    Flask, render_template, jsonify, request, send_from_directory,
    Response, abort
)
from werkzeug.utils import secure_filename
import requests

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
TEMPLATES_FOLDER = os.path.join(BASE_PATH, 'Templates')
STATIC_FOLDER = os.path.join(BASE_PATH, 'static')
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(
    __name__,
    template_folder=TEMPLATES_FOLDER,
    static_folder=STATIC_FOLDER
)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 MB

REAL_ARTIFACTS = [
    {
        'id': 1,
        'name': 'Rosetta Stone',
        'museum': 'British Museum',
        'city': 'London',
        'country': 'United Kingdom',
        'latitude': 51.5194,
        'longitude': -0.1270,
        'status': 'Contested',
        'year_taken': 1801,
        'description': 'The key that unlocked Egyptian hieroglyphs. Contains the same text in three scripts: hieroglyphic, demotic, and Greek. Captured from French forces by the British.',
        'artifact_type': 'Granodiorite Stone',
        'current_location': 'British Museum, London',
        'image_url': '/static/images/rosetta_stone.jpg',
        'images': ['/static/images/rosetta_1.jpg', '/static/images/rosetta_2.jpg']
    },
    {
        'id': 2,
        'name': 'Bust of Nefertiti',
        'museum': 'Neues Museum',
        'city': 'Berlin',
        'country': 'Germany',
        'latitude': 52.5200,
        'longitude': 13.3967,
        'status': 'Contested',
        'year_taken': 1912,
        'description': 'Iconic limestone bust of Queen Nefertiti, renowned for its beauty and preservation. Acquired by German archaeologist Ludwig Borchardt under disputed circumstances.',
        'artifact_type': 'Limestone Bust',
        'current_location': 'Neues Museum, Berlin',
        'image_url': '/static/images/nefertiti_bust.jpg',
        'images': ['/static/images/nefertiti_1.jpg', '/static/images/nefertiti_2.jpg']
    },
    {
        'id': 3,
        'name': 'Dendera Zodiac',
        'museum': 'Louvre Museum',
        'city': 'Paris',
        'country': 'France',
        'latitude': 48.8606,
        'longitude': 2.3376,
        'status': 'Contested',
        'year_taken': 1820,
        'description': 'Celestial bas-relief from the Temple of Hathor ceiling. Removed by French archaeologist Sébastien Louis Saulnier using saws and explosives.',
        'artifact_type': 'Sandstone Relief',
        'current_location': 'Louvre Museum, Paris',
        'image_url': '/static/images/dendera_zodiac.jpg',
        'images': ['/static/images/dendera_1.jpg', '/static/images/dendera_2.jpg']
    },
    {
        'id': 4,
        'name': 'Colossal Statue of Ramesses II',
        'museum': 'Ramesseum',
        'city': 'Luxor',
        'country': 'Egypt',
        'latitude': 25.7280,
        'longitude': 32.6100,
        'status': 'In Egypt',
        'year_taken': 'Never Taken',
        'description': '7.5-ton granite statue of Pharaoh Ramesses II from the Ramesseum temple. The main colossus remains in situ at the Ramesseum.',
        'artifact_type': 'Granite Statue',
        'current_location': 'Ramesseum, Luxor, Egypt',
        'image_url': '/static/images/ramesses_british.jpg',
        'images': ['/static/images/ramesses_1.jpg']
    },
    {
        'id': 5,
        'name': "Sarcophagus of Seti I",
        'museum': "Sir John Soane's Museum",
        'city': 'London',
        'country': 'United Kingdom',
        'latitude': 51.5175,
        'longitude': -0.1167,
        'status': 'Contested',
        'year_taken': 1821,
        'description': 'Magnificent alabaster sarcophagus of Pharaoh Seti I, father of Ramesses II. Acquired by Giovanni Belzoni from the Valley of the Kings.',
        'artifact_type': 'Alabaster Sarcophagus',
        'current_location': "Sir John Soane's Museum, London",
        'image_url': '/static/images/seti_sarcophagus.jpg',
        'images': ['/static/images/seti_1.jpg']
    },
    {
        'id': 6,
        'name': 'Statue of Hemiunu',
        'museum': 'Roemer und Pelizaeus Museum',
        'city': 'Hildesheim',
        'country': 'Germany',
        'latitude': 52.1500,
        'longitude': 9.9500,
        'status': 'Contested',
        'year_taken': 1912,
        'description': 'Life-sized limestone statue of Hemiunu, nephew of Pharaoh Khufu and probable architect of the Great Pyramid. Found in his mastaba tomb at Giza.',
        'artifact_type': 'Limestone Statue',
        'current_location': 'Roemer und Pelizaeus Museum, Hildesheim',
        'image_url': '/static/images/hemiunu.jpg',
        'images': ['/static/images/hemiunu_1.jpg']
    },
    {
        'id': 7,
        'name': 'Green Head of Osiris',
        'museum': 'Egyptian Museum of Berlin',
        'city': 'Berlin',
        'country': 'Germany',
        'latitude': 52.5200,
        'longitude': 13.3967,
        'status': 'Contested',
        'year_taken': 1911,
        'description': 'Exquisite basalt head of Osiris from the Late Period. Considered one of the finest examples of Egyptian sculpture in existence.',
        'artifact_type': 'Basalt Sculpture',
        'current_location': 'Egyptian Museum of Berlin',
        'image_url': '/static/images/green_head.jpg',
        'images': ['/static/images/green_head_1.jpg']
    },
    {
        'id': 8,
        'name': 'Statue of Ka-Aper',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1860,
        'description': 'Wooden statue of a priest from the 5th Dynasty. Known as "Sheikh el-Balad" (Village Chief) due to its lifelike appearance. Found at Saqqara.',
        'artifact_type': 'Wooden Statue',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/ka_aper.jpg',
        'images': ['/static/images/ka_aper_1.jpg']
    },
    {
        'id': 9,
        'name': 'Sphinx of Hatshepsut',
        'museum': 'Metropolitan Museum of Art',
        'city': 'New York',
        'country': 'USA',
        'latitude': 40.7794,
        'longitude': -73.9631,
        'status': 'Contested',
        'year_taken': 1930,
        'description': 'Granite sphinx bearing the features of Pharaoh Hatshepsut. One of several sphinxes from her temple at Deir el-Bahri.',
        'artifact_type': 'Granite Sphinx',
        'current_location': 'Metropolitan Museum of Art, New York',
        'image_url': '/static/images/hatshepsut_sphinx.jpg',
        'images': ['/static/images/hatshepsut_1.jpg']
    },
    {
        'id': 10,
        'name': 'Narmer Palette',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1898,
        'description': 'Ceremonial palette commemorating the unification of Upper and Lower Egypt under King Narmer. One of the earliest historical documents from ancient Egypt.',
        'artifact_type': 'Slate Palette',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/narmer_palette.jpg',
        'images': ['/static/images/narmer_1.jpg']
    },
    {
        'id': 11,
        'name': 'Bust of Ankhhaf',
        'museum': 'Museum of Fine Arts',
        'city': 'Boston',
        'country': 'USA',
        'latitude': 42.3393,
        'longitude': -71.0940,
        'status': 'Contested',
        'year_taken': 1925,
        'description': 'Limestone bust of Prince Ankhhaf, son of Pharaoh Sneferu. Considered one of the masterpieces of Old Kingdom portraiture.',
        'artifact_type': 'Limestone Bust',
        'current_location': 'Museum of Fine Arts, Boston',
        'image_url': '/static/images/ankhhaf.jpg',
        'images': ['/static/images/ankhhaf_1.jpg']
    },
    {
        'id': 12,
        'name': 'Statue of Khafre',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1860,
        'description': 'Diorite statue of Pharaoh Khafre, builder of the second pyramid at Giza. Found in his valley temple by Auguste Mariette.',
        'artifact_type': 'Diorite Statue',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/khafre.jpg',
        'images': ['/static/images/khafre_1.jpg']
    },
    {
        'id': 13,
        'name': 'Seated Statue of Hatshepsut',
        'museum': 'Metropolitan Museum of Art',
        'city': 'New York',
        'country': 'USA',
        'latitude': 40.7794,
        'longitude': -73.9631,
        'status': 'Contested',
        'year_taken': 1930,
        'description': 'Large seated statue of Pharaoh Hatshepsut in traditional royal regalia. From her mortuary temple at Deir el-Bahri.',
        'artifact_type': 'Granite Statue',
        'current_location': 'Metropolitan Museum of Art, New York',
        'image_url': '/static/images/hatshepsut_seated.jpg',
        'images': ['/static/images/hatshepsut_2.jpg']
    },
    {
        'id': 14,
        'name': 'Mummy Mask of Satdjehuty',
        'museum': 'British Museum',
        'city': 'London',
        'country': 'United Kingdom',
        'latitude': 51.5194,
        'longitude': -0.1270,
        'status': 'Contested',
        'year_taken': 1827,
        'description': 'Gilded cartonnage mummy mask of Queen Satdjehuty, daughter of Pharaoh Seqenenre Tao. From her tomb at Thebes.',
        'artifact_type': 'Gilded Mask',
        'current_location': 'British Museum, London',
        'image_url': '/static/images/satdjehuty_mask.jpg',
        'images': ['/static/images/satdjehuty_1.jpg']
    },
    {
        'id': 15,
        'name': 'Statue of Amenhotep III and Tiye',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1889,
        'description': 'Colossal statue depicting Pharaoh Amenhotep III with his wife Queen Tiye. From the temple at Medinet Habu.',
        'artifact_type': 'Quartzite Statue',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/amenhotep_tiye.jpg',
        'images': ['/static/images/amenhotep_1.jpg']
    },
    {
        'id': 16,
        'name': 'Bust of Akhenaten',
        'museum': 'Louvre Museum',
        'city': 'Paris',
        'country': 'France',
        'latitude': 48.8606,
        'longitude': 2.3376,
        'status': 'Contested',
        'year_taken': 1922,
        'description': 'Sandstone bust of the "heretic pharaoh" Akhenaten, showing the distinctive Amarna artistic style. From Karnak temple.',
        'artifact_type': 'Sandstone Bust',
        'current_location': 'Louvre Museum, Paris',
        'image_url': '/static/images/akhenaten_bust.jpg',
        'images': ['/static/images/akhenaten_1.jpg']
    },
    {
        'id': 17,
        'name': "Golden Throne of Tutankhamun",
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1922,
        'description': "Exquisitely crafted golden throne found in Tutankhamun's tomb. Features the young king with his wife Ankhesenamun.",
        'artifact_type': 'Golden Throne',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/tut_throne.jpg',
        'images': ['/static/images/tut_throne_1.jpg']
    },
    {
        'id': 18,
        'name': 'Rosicrucian Egyptian Museum Collection',
        'museum': 'Rosicrucian Egyptian Museum',
        'city': 'San Jose',
        'country': 'USA',
        'latitude': 37.3329,
        'longitude': -121.9046,
        'status': 'Contested',
        'year_taken': 1930,
        'description': 'Large collection of Egyptian artifacts including mummies, sarcophagi, and funerary objects acquired through various expeditions.',
        'artifact_type': 'Museum Collection',
        'current_location': 'Rosicrucian Egyptian Museum, San Jose',
        'image_url': '/static/images/rosicrucian.jpg',
        'images': ['/static/images/rosicrucian_1.jpg']
    },
    {
        'id': 19,
        'name': 'Statue of Senusret III',
        'museum': 'British Museum',
        'city': 'London',
        'country': 'United Kingdom',
        'latitude': 51.5194,
        'longitude': -0.1270,
        'status': 'Contested',
        'year_taken': 1838,
        'description': 'Granite statue of the powerful Middle Kingdom pharaoh Senusret III, known for his military campaigns and administrative reforms.',
        'artifact_type': 'Granite Statue',
        'current_location': 'British Museum, London',
        'image_url': '/static/images/senusret_iii.jpg',
        'images': ['/static/images/senusret_1.jpg']
    },
    {
        'id': 20,
        'name': 'Sarcophagus of Nedjemankh',
        'museum': 'Returned to Egypt',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'Returned',
        'year_taken': 2011,
        'description': "Gilded silver coffin of a high priest. Looted after the 2011 revolution and returned by the Metropolitan Museum in 2019 after investigation.",
        'artifact_type': 'Gilded Coffin',
        'current_location': 'Grand Egyptian Museum, Cairo',
        'image_url': '/static/images/nedjemankh.jpg',
        'images': ['/static/images/nedjemankh_1.jpg']
    },
    {
        'id': 21,
        'name': 'Statue of Mentuhotep II',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1898,
        'description': 'Sandstone statue of Pharaoh Mentuhotep II, the ruler who reunified Egypt and began the Middle Kingdom. From his mortuary temple at Deir el-Bahri.',
        'artifact_type': 'Sandstone Statue',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/mentuhotep.jpg',
        'images': ['/static/images/mentuhotep_1.jpg']
    },
    {
        'id': 22,
        'name': 'Bust of Cleopatra VII',
        'museum': 'Altes Museum',
        'city': 'Berlin',
        'country': 'Germany',
        'latitude': 52.5200,
        'longitude': 13.3967,
        'status': 'Contested',
        'year_taken': 1840,
        'description': 'Marble bust believed to depict Cleopatra VII, the last active ruler of the Ptolemaic Kingdom of Egypt.',
        'artifact_type': 'Marble Bust',
        'current_location': 'Altes Museum, Berlin',
        'image_url': '/static/images/cleopatra_bust.jpg',
        'images': ['/static/images/cleopatra_1.jpg']
    },
    {
        'id': 23,
        'name': 'Canopic Jar of Tutankhamun',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1922,
        'description': 'One of four alabaster canopic jars that contained the internal organs of King Tutankhamun. Each jar protected by a goddess.',
        'artifact_type': 'Alabaster Jar',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/tut_canopic.jpg',
        'images': ['/static/images/tut_canopic_1.jpg']
    },
    {
        'id': 24,
        'name': 'Statue of Ptah',
        'museum': 'Louvre Museum',
        'city': 'Paris',
        'country': 'France',
        'latitude': 48.8606,
        'longitude': 2.3376,
        'status': 'Contested',
        'year_taken': 1826,
        'description': 'Bronze statue of the creator god Ptah, patron deity of craftsmen and architects. From the temple at Memphis.',
        'artifact_type': 'Bronze Statue',
        'current_location': 'Louvre Museum, Paris',
        'image_url': '/static/images/ptah_statue.jpg',
        'images': ['/static/images/ptah_1.jpg']
    },
    {
        'id': 25,
        'name': 'Mummy Mask of Wendjebauendjed',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1940,
        'description': "Silver and gold mummy mask of General Wendjebauendjed from the 21st Dynasty. One of the few silver masks from ancient Egypt.",
        'artifact_type': 'Silver Mask',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/wendjebauendjed.jpg',
        'images': ['/static/images/wendjebauendjed_1.jpg']
    },
    {
        'id': 26,
        'name': 'Statue of Sekhmet',
        'museum': 'British Museum',
        'city': 'London',
        'country': 'United Kingdom',
        'latitude': 51.5194,
        'longitude': -0.1270,
        'status': 'Contested',
        'year_taken': 1818,
        'description': 'Granite statue of the lion-headed goddess Sekhmet from the temple of Mut at Karnak. One of hundreds commissioned by Amenhotep III.',
        'artifact_type': 'Granite Statue',
        'current_location': 'British Museum, London',
        'image_url': '/static/images/sekhmet.jpg',
        'images': ['/static/images/sekhmet_1.jpg']
    },
    {
        'id': 27,
        'name': 'Fayum Mummy Portraits',
        'museum': 'Various Museums Worldwide',
        'city': 'Multiple Cities',
        'country': 'Multiple Countries',
        'latitude': 51.5194,
        'longitude': -0.1270,
        'status': 'Contested',
        'year_taken': 1880,
        'description': 'Collection of realistic portraits attached to mummies from Roman Egypt. Scattered across museums in Europe and America.',
        'artifact_type': 'Mummy Portraits',
        'current_location': 'Various International Museums',
        'image_url': '/static/images/fayum_portraits.jpg',
        'images': ['/static/images/fayum_1.jpg']
    },
    {
        'id': 28,
        'name': 'Statue of Ankhwa',
        'museum': 'British Museum',
        'city': 'London',
        'country': 'United Kingdom',
        'latitude': 51.5194,
        'longitude': -0.1270,
        'status': 'Contested',
        'year_taken': 1890,
        'description': 'One of the earliest metal statues from ancient Egypt, depicting the shipbuilder Ankhwa from the 3rd Dynasty.',
        'artifact_type': 'Bronze Statue',
        'current_location': 'British Museum, London',
        'image_url': '/static/images/ankhwa.jpg',
        'images': ['/static/images/ankhwa_1.jpg']
    },
    {
        'id': 29,
        'name': 'Kalabsha Gate',
        'museum': 'Egyptian Museum of Berlin',
        'city': 'Berlin',
        'country': 'Germany',
        'latitude': 52.5200,
        'longitude': 13.3967,
        'status': 'Contested',
        'year_taken': 1812,
        'description': 'Large Roman-era gate from Kalabsha Temple in Nubia. Saved from flooding and relocated to Germany.',
        'artifact_type': 'Stone Gate',
        'current_location': 'Egyptian Museum, Berlin',
        'image_url': '/static/images/kalabsha_gate.jpg',
        'images': ['/static/images/kalabsha_1.jpg']
    },
    {
        'id': 30,
        'name': 'Statue of Merneptah',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1896,
        'description': 'Granite statue of Pharaoh Merneptah, son of Ramesses II. Known for his victory stele that contains the first known reference to Israel.',
        'artifact_type': 'Granite Statue',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/merneptah.jpg',
        'images': ['/static/images/merneptah_1.jpg']
    },
    {
        'id': 31,
        'name': 'Coffin of Hor',
        'museum': 'Louvre Museum',
        'city': 'Paris',
        'country': 'France',
        'latitude': 48.8606,
        'longitude': 2.3376,
        'status': 'Contested',
        'year_taken': 1824,
        'description': 'Painted wooden coffin of the priest Hor from the Late Period. Notable for its vivid colors and detailed hieroglyphs.',
        'artifact_type': 'Wooden Coffin',
        'current_location': 'Louvre Museum, Paris',
        'image_url': '/static/images/hor_coffin.jpg',
        'images': ['/static/images/hor_1.jpg']
    },
    {
        'id': 32,
        'name': 'Statue of Niankhkhnum and Khnumhotep',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1964,
        'description': 'Unique double statue of two royal manicurists shown embracing. Their close relationship has been subject of much scholarly discussion.',
        'artifact_type': 'Limestone Statue',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/niankhkhnum.jpg',
        'images': ['/static/images/niankhkhnum_1.jpg']
    },
    {
        'id': 33,
        'name': 'Sphinx of Taharqa',
        'museum': 'British Museum',
        'city': 'London',
        'country': 'United Kingdom',
        'latitude': 51.5194,
        'longitude': -0.1270,
        'status': 'Contested',
        'year_taken': 1932,
        'description': 'Granite sphinx with the features of Pharaoh Taharqa, the Nubian ruler of the 25th Dynasty who controlled both Egypt and Kush.',
        'artifact_type': 'Granite Sphinx',
        'current_location': 'British Museum, London',
        'image_url': '/static/images/taharqa_sphinx.jpg',
        'images': ['/static/images/taharqa_1.jpg']
    },
    {
        'id': 34,
        'name': 'Statue of Khentkawes I',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1932,
        'description': 'Diorite statue of Queen Khentkawes I, who may have ruled Egypt at the end of the 4th Dynasty. From her tomb at Giza.',
        'artifact_type': 'Diorite Statue',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/khentkawes.jpg',
        'images': ['/static/images/khentkawes_1.jpg']
    },
    {
        'id': 35,
        'name': 'Bust of Ramesses II',
        'museum': 'Museo Egizio',
        'city': 'Turin',
        'country': 'Italy',
        'latitude': 45.0684,
        'longitude': 7.6843,
        'status': 'Contested',
        'year_taken': 1824,
        'description': 'Granite bust of the great pharaoh Ramesses II, part of the extensive Drovetti collection acquired in the early 19th century.',
        'artifact_type': 'Granite Bust',
        'current_location': 'Museo Egizio, Turin',
        'image_url': '/static/images/ramesses_turin.jpg',
        'images': ['/static/images/ramesses_2.jpg']
    },
    {
        'id': 36,
        'name': 'Mummy of Ramesses I',
        'museum': 'Luxor Museum',
        'city': 'Luxor',
        'country': 'Egypt',
        'latitude': 25.6872,
        'longitude': 32.6396,
        'status': 'Returned',
        'year_taken': 1861,
        'description': 'Mummy of the founder of the 19th Dynasty. Was in the Niagara Falls Museum until identified and returned to Egypt in 2003.',
        'artifact_type': 'Royal Mummy',
        'current_location': 'Luxor Museum, Egypt',
        'image_url': '/static/images/ramesses_i.jpg',
        'images': ['/static/images/ramesses_i_1.jpg']
    },
    {
        'id': 37,
        'name': 'Statue of Sobek',
        'museum': 'Louvre Museum',
        'city': 'Paris',
        'country': 'France',
        'latitude': 48.8606,
        'longitude': 2.3376,
        'status': 'Contested',
        'year_taken': 1823,
        'description': 'Granite statue of the crocodile god Sobek, worshipped particularly in the Faiyum region. From the temple at Kom Ombo.',
        'artifact_type': 'Granite Statue',
        'current_location': 'Louvre Museum, Paris',
        'image_url': '/static/images/sobek.jpg',
        'images': ['/static/images/sobek_1.jpg']
    },
    {
        'id': 38,
        'name': 'Golden Mask of Psusennes I',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1940,
        'description': 'Solid gold funeral mask of Pharaoh Psusennes I, discovered in his intact tomb at Tanis. Often compared to Tutankhamun\'s mask.',
        'artifact_type': 'Golden Mask',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/psusennes_mask.jpg',
        'images': ['/static/images/psusennes_1.jpg']
    },
    {
        'id': 39,
        'name': 'Statue of Djoser',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1924,
        'description': 'Life-sized seated statue of Pharaoh Djoser, builder of the Step Pyramid at Saqqara. Found in the serdab of his pyramid complex.',
        'artifact_type': 'Limestone Statue',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/djoser.jpg',
        'images': ['/static/images/djoser_1.jpg']
    },
    {
        'id': 40,
        'name': 'Sarcophagus of Alexander the Great',
        'museum': 'British Museum',
        'city': 'London',
        'country': 'United Kingdom',
        'latitude': 51.5194,
        'longitude': -0.1270,
        'status': 'Contested',
        'year_taken': 1801,
        'description': 'Elaborate sarcophagus believed made for Alexander the Great but used for Pharaoh Nectanebo II. From the cemetery at Sidon.',
        'artifact_type': 'Marble Sarcophagus',
        'current_location': 'British Museum, London',
        'image_url': '/static/images/alexander_sarcophagus.jpg',
        'images': ['/static/images/alexander_1.jpg']
    },
    {
        'id': 41,
        'name': 'Statue of Thutmose III',
        'museum': 'Kunsthistorisches Museum',
        'city': 'Vienna',
        'country': 'Austria',
        'latitude': 48.2039,
        'longitude': 16.3617,
        'status': 'Contested',
        'year_taken': 1912,
        'description': 'Granite statue of the "Napoleon of Egypt," Thutmose III, known for his military campaigns that expanded the Egyptian empire.',
        'artifact_type': 'Granite Statue',
        'current_location': 'Kunsthistorisches Museum, Vienna',
        'image_url': '/static/images/thutmose_iii.jpg',
        'images': ['/static/images/thutmose_1.jpg']
    },
    {
        'id': 42,
        'name': 'Mastaba of Ka-ni-Nisut',
        'museum': 'Kunsthistorisches Museum',
        'city': 'Vienna',
        'country': 'Austria',
        'latitude': 48.2039,
        'longitude': 16.3617,
        'status': 'Contested',
        'year_taken': 1912,
        'description': 'Complete tomb chapel from the Old Kingdom period with detailed reliefs showing daily life and offering scenes.',
        'artifact_type': 'Tomb Chapel',
        'current_location': 'Kunsthistorisches Museum, Vienna',
        'image_url': '/static/images/ka_ni_nisut.jpg',
        'images': ['/static/images/mastaba_1.jpg']
    },
    {
        'id': 43,
        'name': 'Statue of Meritamen',
        'museum': 'Museo Egizio',
        'city': 'Turin',
        'country': 'Italy',
        'latitude': 45.0684,
        'longitude': 7.6843,
        'status': 'Contested',
        'year_taken': 1824,
        'description': 'Granite statue of Princess Meritamen, daughter of Ramesses II and Nefertari. Shows her in the role of a chantress of Amun.',
        'artifact_type': 'Granite Statue',
        'current_location': 'Museo Egizio, Turin',
        'image_url': '/static/images/meritamen.jpg',
        'images': ['/static/images/meritamen_1.jpg']
    },
    {
        'id': 44,
        'name': 'Sphinx of Amenemhat III',
        'museum': 'Louvre Museum',
        'city': 'Paris',
        'country': 'France',
        'latitude': 48.8606,
        'longitude': 2.3376,
        'status': 'Contested',
        'year_taken': 1823,
        'description': 'Granite sphinx with the features of Pharaoh Amenemhat III, known for his extensive building projects including the Labyrinth.',
        'artifact_type': 'Granite Sphinx',
        'current_location': 'Louvre Museum, Paris',
        'image_url': '/static/images/amenemhat_sphinx.jpg',
        'images': ['/static/images/amenemhat_1.jpg']
    },
    {
        'id': 45,
        'name': 'Statue of Intef II',
        'museum': 'British Museum',
        'city': 'London',
        'country': 'United Kingdom',
        'latitude': 51.5194,
        'longitude': -0.1270,
        'status': 'Contested',
        'year_taken': 1835,
        'description': 'Sandstone statue of Pharaoh Intef II, a ruler of the 11th Dynasty who fought to reunify Egypt during the First Intermediate Period.',
        'artifact_type': 'Sandstone Statue',
        'current_location': 'British Museum, London',
        'image_url': '/static/images/intef_ii.jpg',
        'images': ['/static/images/intef_1.jpg']
    },
    {
        'id': 46,
        'name': 'Coffin of Ipi',
        'museum': 'Egyptian Museum of Cairo',
        'city': 'Cairo',
        'country': 'Egypt',
        'latitude': 30.0478,
        'longitude': 31.2333,
        'status': 'In Egypt',
        'year_taken': 1915,
        'description': 'Elaborate Middle Kingdom coffin of the steward Ipi, decorated with Coffin Texts and offering formulas to ensure his afterlife.',
        'artifact_type': 'Wooden Coffin',
        'current_location': 'Egyptian Museum, Cairo',
        'image_url': '/static/images/ipi_coffin.jpg',
        'images': ['/static/images/ipi_1.jpg']
    },
    {
        'id': 47,
        'name': 'Statue of Senenmut with Neferure',
        'museum': 'British Museum',
        'city': 'London',
        'country': 'United Kingdom',
        'latitude': 51.5194,
        'longitude': -0.1270,
        'status': 'Contested',
        'year_taken': 1837,
        'description': 'Statue showing Senenmut, architect and royal advisor to Hatshepsut, holding Princess Neferure in a protective embrace.',
        'artifact_type': 'Granite Statue',
        'current_location': 'British Museum, London',
        'image_url': '/static/images/senenmut.jpg',
        'images': ['/static/images/senenmut_1.jpg']
    }
]

OLLAMA_BASE_URL = "http://localhost:11434" 

requests_session = requests.Session()
requests_session.headers.update({"User-Agent": "EgyptArtifactsApp/1.0"})

OLLAMA_MODELS_CACHE = {"models": None, "ts": 0}
OLLAMA_CACHE_TTL = 20  # seconds

def get_ollama_models():
    """Return JSON from /api/tags (cached)."""
    now = time.time()
    if OLLAMA_MODELS_CACHE["models"] and (now - OLLAMA_MODELS_CACHE["ts"] < OLLAMA_CACHE_TTL):
        return OLLAMA_MODELS_CACHE["models"]

    try:
        resp = requests_session.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
        else:
            data = {"models": []}
    except Exception:
        data = {"models": []}

    OLLAMA_MODELS_CACHE["models"] = data
    OLLAMA_MODELS_CACHE["ts"] = now
    return data

def check_ollama_running():
    """Quick check if Ollama is running."""
    try:
        resp = requests_session.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False

def get_best_text_model():
    """Find a good text-only model (prefers llama3.2/llama3/llama in order)."""
    try:
        models_data = get_ollama_models()
        models = [m['name'] for m in models_data.get('models', []) if 'name' in m]
        if not models:
            return None

        for candidate in models:
            lower = candidate.lower()
            if 'llama3.2' in lower and 'vision' not in lower:
                return candidate
        for candidate in models:
            lower = candidate.lower()
            if 'llama3' in lower and 'vision' not in lower:
                return candidate
        for candidate in models:
            lower = candidate.lower()
            if 'llama' in lower and 'vision' not in lower:
                return candidate

        return models[0]
    except Exception:
        return None

def get_best_vision_model():
    """Find a model that supports vision (llava, vision, etc.)."""
    try:
        models_data = get_ollama_models()
        models = [m['name'] for m in models_data.get('models', []) if 'name' in m]
        if not models:
            return None

        for candidate in models:
            lower = candidate.lower()
            if 'llava' in lower or 'vision' in lower or 'bakllava' in lower:
                return candidate
        return None
    except Exception:
        return None

def try_match_artifact(description):
    """Try to match the AI description with artifacts in the dataset (basic scoring)."""
    if not description:
        return None
    description_lower = description.lower()
    matches = []

    for artifact in REAL_ARTIFACTS:
        score = 0
        name = artifact.get('name', '').lower()
        artifact_type = artifact.get('artifact_type', '').lower()

        if name and name in description_lower:
            score += 12
        if artifact_type and artifact_type in description_lower:
            score += 6

        materials = ['limestone', 'granite', 'sandstone', 'alabaster', 'gold', 'bronze', 'wood']
        for mat in materials:
            if mat in description_lower and mat in artifact_type:
                score += 3

        if score > 0:
            matches.append({'artifact': artifact, 'score': score})

    if matches:
        best = max(matches, key=lambda x: x['score'])
        a = best['artifact']
        return f"{a.get('name')} - {a.get('artifact_type')}\nLocation: {a.get('current_location')}\nStatus: {a.get('status')}"
    return None

def search_artifact_data(query):
    """Simple search for queries directly answerable from the artifact dataset."""
    if not query:
        return None
    q = query.lower()

    for artifact in REAL_ARTIFACTS:
        if artifact.get('name') and artifact['name'].lower() in q:
            return (
                f"🏺 **{artifact.get('name')}**\n"
                f"📋 Type: {artifact.get('artifact_type', 'Unknown')}\n"
                f"📍 Current Location: {artifact.get('current_location', 'Unknown')}\n"
                f"📊 Status: {artifact.get('status', 'Unknown')}\n"
                f"📅 Year Taken: {artifact.get('year_taken', 'Unknown')}\n"
                f"📖 Description: {artifact.get('description', '')}"
            )
        
    if "how many" in q and "artifact" in q:
        return f"📊 There are **{len(REAL_ARTIFACTS)}** artifacts in the dataset."

    if "countries" in q or ("where" in q and "artifacts" in q):
        countries = sorted(list(set(a.get('country', 'Unknown') for a in REAL_ARTIFACTS)))
        return "🌍 Artifacts are in: " + ", ".join(countries)

    if "contested" in q:
        c = len([a for a in REAL_ARTIFACTS if a.get('status') == 'Contested'])
        return f"⚖️ There are **{c}** contested artifacts."

    return None

def call_ollama_text(prompt, timeout=90, num_predict=350, temperature=0.7):
    """Call Ollama /api/generate (non-streaming) with session & tuned defaults."""
    model = get_best_text_model()
    if not model:
        return "No text model available. Please install a Llama family model (e.g., llama3.2)."

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict
        }
    }

    try:
        resp = requests_session.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=timeout)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if isinstance(data, dict):
                    if "response" in data:
                        return data.get("response") or ""
                    if "choices" in data and isinstance(data["choices"], list):
                        return data["choices"][0].get("text", "")
                return str(data)
            except ValueError:
                return "Invalid JSON received from Ollama."
        else:
            return f"Error from Ollama: {resp.status_code} - {resp.text}"
    except requests.exceptions.ReadTimeout:
        return "⚠️ Ollama read timeout — the model took too long. Try again or use a simpler prompt."
    except Exception as e:
        return f"Error calling Ollama: {str(e)}"

def call_ollama_vision(prompt, image_path, timeout=120, num_predict=500, temperature=0.3):
    """Call vision-capable Ollama model with image encoded as base64 in JSON."""
    model = get_best_vision_model()
    if not model:
        return "No vision model available. Please pull/install a vision-capable model (e.g., llava)."

    try:
        with open(image_path, "rb") as f:
            b = f.read()
            b64 = base64.b64encode(b).decode('utf-8')

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [b64]
                }
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict
            }
        }

        resp = requests_session.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=timeout)
        if resp.status_code == 200:
            try:
                data = resp.json()
                message = ""
                if isinstance(data, dict):
                    message = data.get("message", {}).get("content", "")
                if not message:
                    message = data.get("response", "") or str(data)
                m = try_match_artifact(message)
                if m:
                    message += f"\n\n🎯 POSSIBLE DATASET MATCH:\n{m}"
                return message
            except ValueError:
                return "Invalid JSON from Ollama vision."
        else:
            return f"Ollama vision error: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"Vision error: {str(e)}"

@app.route('/api/ai-stream', methods=['POST'])
def ai_stream():
    """
    SSE streaming endpoint.
    Expects JSON: { "message": "..." }
    Streams tokens as `data: <text>\n\n` events.
    """
    try:
        payload = request.json or {}
        user_message = payload.get("message", "").strip()
        if not user_message:
            return Response("data: Error: empty message\n\n", mimetype="text/event-stream")

        if not check_ollama_running():
            return Response("data: Error: Ollama not running. Start with 'ollama serve'.\n\n", mimetype="text/event-stream")

        model = get_best_text_model()
        if not model:
            return Response("data: Error: No model available.\n\n", mimetype="text/event-stream")

        prompt = f"""
You are an expert Egyptologist and general historian. Answer clearly and concisely.
If the user asks about a known artifact or person, provide historical context, key facts, and significance.

User question:
{user_message}

Answer:
"""

        def generate_stream():
            try:
                resp = requests_session.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {"temperature": 0.7}
                    },
                    stream=True,
                    timeout=120
                )

                if resp.status_code != 200:
                    yield f"data: Error from Ollama: {resp.status_code}\\n\\n"
                    return

                for raw in resp.iter_lines(decode_unicode=True):
                    if raw is None:
                        continue
                    line = raw.strip()
                    if not line:
                        continue
                    try:
                        parsed = json.loads(line)
                        token_text = ""
                        if isinstance(parsed, dict):
                            if "response" in parsed:
                                token_text = parsed.get("response", "")
                            elif "token" in parsed:
                                token_text = parsed.get("token", "")
                            elif "choices" in parsed and isinstance(parsed["choices"], list):
                                c = parsed["choices"][0]
                                token_text = c.get("text") or c.get("delta", {}).get("content", "") or ""
                            else:
                                token_text = parsed.get("text") or parsed.get("message", {}).get("content", "") or ""
                        else:
                            token_text = str(parsed)
                        if token_text:
                            for chunk in token_text.split("\n"):
                                yield f"data: {chunk}\n\n"
                        else:
                            yield f"data: {line}\n\n"
                    except Exception:
                        yield f"data: {line}\n\n"

                yield "data: [END]\n\n"

            except requests.exceptions.ReadTimeout:
                yield "data: Error: Ollama read timeout during streaming.\n\n"
            except Exception as e:
                yield f"data: Error: {str(e)}\n\n"

        return Response(generate_stream(), mimetype="text/event-stream")

    except Exception as e:
        return Response(f"data: Server error: {str(e)}\n\n", mimetype="text/event-stream")

@app.route('/api/ai-assistant', methods=['POST'])
def ai_assistant():
    """
    Non-streaming endpoint (used by your UI for single-response calls).
    Behavior:
      - Checks dataset first
      - If dataset can't answer, calls Ollama for a general expert answer
    """
    try:
        payload = request.json or {}
        user_message = payload.get('message', '').strip()
        if not user_message:
            return jsonify({'response': "Please send a question.", 'source': 'none'})

        dataset_ans = search_artifact_data(user_message)
        if dataset_ans:
            return jsonify({'response': dataset_ans, 'source': 'dataset'})

        if re.search(r'\b(hi|hello|hey|greetings)\b', user_message, re.I):
            reply = "Hello! I'm your Egyptian Artifacts AI assistant. Ask me about artifacts, pharaohs, or history."
            return jsonify({'response': reply, 'source': 'fallback'})

        if not check_ollama_running():
            return jsonify({'response': "⚠️ Ollama is not running. Start it with: ollama serve", 'source': 'error'})

        prompt = f"""
You are an expert Egyptologist and general historian AI.
Answer clearly and accurately. If the question is about a specific artifact, provide context and significance.
If the question is about a historical figure (e.g., Ramesses II), provide a concise biography and key facts.
If the question is general world knowledge, answer using authoritative tone.

User question:
{user_message}

Answer:
"""

        response_text = call_ollama_text(prompt)
        match = try_match_artifact(response_text)
        if match:
            response_text += f"\n\n🎯 POSSIBLE DATASET MATCH:\n{match}"

        return jsonify({'response': response_text, 'source': 'ollama'})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'response': f"Server error: {str(e)}", 'source': 'error'})

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/ai-vision', methods=['POST'])
def ai_vision():
    """
    Receives file upload (form-data 'file') and optional 'question' field.
    Returns JSON: { ok: bool, response: "..." }
    """
    try:
        if 'file' not in request.files:
            return jsonify({'ok': False, 'response': 'No file provided.'}), 400

        file = request.files['file']
        question = (request.form.get('question') or '').strip()

        if file.filename == '':
            return jsonify({'ok': False, 'response': 'No selected file.'}), 400

        if not allowed_file(file.filename):
            return jsonify({'ok': False, 'response': 'File type not allowed. Use PNG/JPG/GIF.'}), 400

        # Save file temporarily
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{int(time.time())}_{filename}")
        file.save(save_path)

        # Build enhanced prompt for vision
        user_q = question if question else "What is this artifact? Provide identification and context."
        enhanced_prompt = f"""
You are an Egyptologist specializing in artifact identification.

CONTEXT: dataset includes many Egyptian artifacts (Rosetta Stone, Nefertiti bust, statues, canopic jars, sarcophagi).

USER QUESTION: {user_q}

ANALYSIS REQUEST:
1. Identify artifact if possible (name/type/material).
2. Describe visible features.
3. Estimate historical period.
4. Comment on likely provenance.
"""

        response_text = call_ollama_vision(enhanced_prompt, save_path)

        try:
            os.remove(save_path)
        except Exception:
            pass

        return jsonify({'ok': True, 'response': response_text})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'ok': False, 'response': f"Server error: {str(e)}"}), 500

@app.route('/api/ollama-status')
def ollama_status():
    try:
        running = check_ollama_running()
        text_model = get_best_text_model() if running else None
        vision_model = get_best_vision_model() if running else None
        return jsonify({
            "running": running,
            "text_model": text_model,
            "vision_model": vision_model
        })
    except Exception as e:
        return jsonify({
            "running": False,
            "text_model": None,
            "vision_model": None,
            "error": str(e)
        })

@app.route('/')
def index():
    return render_template('index.html', artifacts=REAL_ARTIFACTS)

@app.route('/chat')
def chat_ui():
    return render_template('chat.html')

@app.route('/map')
def map_page():
    return render_template('map.html', artifacts=REAL_ARTIFACTS)

@app.route('/api/artifacts')
def get_artifacts():
    return jsonify(REAL_ARTIFACTS)

@app.route('/artifacts')
def artifacts_list():
    countries = sorted(list(set(artifact['country'] for artifact in REAL_ARTIFACTS)))
    return render_template('artifacts.html', artifacts=REAL_ARTIFACTS, countries=countries)

@app.route('/artifact/<int:artifact_id>')
def artifact_detail(artifact_id):
    artifact = next((a for a in REAL_ARTIFACTS if a['id'] == artifact_id), None)
    if artifact:
        return render_template('artifact_detail.html', artifact=artifact)
    else:
        return "Artifact not found", 404

@app.route('/statistics')
def statistics():
    total_artifacts = len(REAL_ARTIFACTS)
    contested_count = len([a for a in REAL_ARTIFACTS if a.get('status') == 'Contested'])
    returned_count = len([a for a in REAL_ARTIFACTS if a.get('status') == 'Returned'])
    in_egypt_count = len([a for a in REAL_ARTIFACTS if a.get('status') == 'In Egypt'])

    countries = {}
    for artifact in REAL_ARTIFACTS:
        c = artifact.get('country', 'Unknown')
        countries[c] = countries.get(c, 0) + 1

    country_names = list(countries.keys())
    country_counts = list(countries.values())

    return render_template('statistics.html',
                           total_artifacts=total_artifacts,
                           contested_count=contested_count,
                           returned_count=returned_count,
                           in_egypt_count=in_egypt_count,
                           countries=countries,
                           country_names=country_names,
                           country_counts=country_counts)

@app.errorhandler(413)
def request_entity_too_large(error):
    return "File too large. Max size is 8 MB.", 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
