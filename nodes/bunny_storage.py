import io
import json
import os.path
import tempfile

import numpy as np
from BunnyCDN.Storage import Storage
from PIL import Image


def save_file(client: Storage, pathname: str, local_filepath: str):
    filename = os.path.basename(local_filepath)
    filepath = os.path.dirname(local_filepath)
    client.PutFile(filename, pathname, filepath)


def init_client(api_key: str, storage_zone: str, storage_zone_region: str = 'la'):
    return Storage(api_key, storage_zone, storage_zone_region)


class SaveImageToBunnyStorage:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"images": ("IMAGE",),
                             "api_key": ("STRING", {"multiline": False, "default": ""}),
                             "storage_zone": ("STRING", {"multiline": False, "default": ""}),
                             "storage_zone_region": ("STRING", {"multiline": False, "default": "la"}),
                             "pathname": ("STRING", {"multiline": False, "default": "pathname for file"})
                             },
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
                }

    RETURN_TYPES = ()
    FUNCTION = "save_image_to_bunny_storage"
    CATEGORY = "image"
    OUTPUT_NODE = True

    def save_image_to_bunny_storage(self, images, api_key, storage_zone, storage_zone_region, pathname, prompt=None,
                                    extra_pnginfo=None):
        client = init_client(api_key, storage_zone, storage_zone_region)
        results = list()
        print(f"Saving to BunnyStorage...")

        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            with tempfile.NamedTemporaryFile(suffix='.png', dir='/tmp') as tmp:
                img.save(tmp, format='PNG')
                save_file(client, "%s/%i.png" % (pathname, batch_number), tmp.name)

            results.append({
                "filename": "%s_%i.png" % (pathname, batch_number),
                "subfolder": "",
                "type": "output"
            })
        print(results)
        return {"ui": {"images": results}}
