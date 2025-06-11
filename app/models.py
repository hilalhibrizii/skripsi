# app/models.py

import json
import logging
from .utils import get_db_connection

# Kelas ini adalah contoh. Anda bisa membuatnya lebih canggih dengan ORM seperti SQLAlchemy.

class Intent:
    @staticmethod
    def get_all():
        # Logika query untuk SELECT * FROM intents
        pass

    @staticmethod
    def create(tag, patterns, responses):
        # Logika query untuk INSERT INTO intents
        pass

    @staticmethod
    def update(tag, patterns, responses):
        # Logika query untuk UPDATE intents
        pass

class JadwalKuliah:
    @staticmethod
    def get_all(search_query, semester_filter, semester_aktif):
        # Logika query untuk SELECT * FROM jadwal_kuliah dengan filter
        pass

    @staticmethod
    def get_by_id(id_jadwal):
        # Logika query untuk SELECT FROM jadwal_kuliah WHERE id
        pass

    @staticmethod
    def create(data):
        # Logika query untuk INSERT INTO jadwal_kuliah
        pass
    
    @staticmethod
    def update(id_jadwal, data):
        # Logika query untuk UPDATE jadwal_kuliah
        pass

    @staticmethod
    def delete(id_jadwal):
        # Logika query untuk DELETE FROM jadwal_kuliah
        pass