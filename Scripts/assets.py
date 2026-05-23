import pygame
from  Scripts.utils import load_image, load_images, load_sound, load_sounds, Animation

class Assets:

    def __init__(self):
        self.assets = {
           'img' : {},
           'sfx' : {}
        }

    def insert(self, assets, key=''):
       if key in self.assets:
          self.assets[key].update(assets)
          return True
       else:
          return False
       
    def fetch(self, payload={}, fetch_all=False):
        assets = {}
        if fetch_all:
          file_types = list(self.assets)
          for file_type in file_types:
              for obj_type in self.assets[file_type]:
                assets.update(self.assets[file_type][obj_type])
          return assets
        else:
          for file_type in payload:
            if 'all' in payload[file_type]:
               for obj_type in self.assets[file_type]:
                  assets.update(self.assets[file_type][obj_type])
            else:
              for obj_type in payload[file_type]:
                assets.update(self.assets[file_type][obj_type])
          return assets 