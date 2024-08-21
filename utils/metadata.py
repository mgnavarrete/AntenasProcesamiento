import os
import json
import subprocess
import io
from tqdm import tqdm


def get_string_meta_data(path):

    # call exiftool with 'JSON'-output flag
    EXIFTOOL = "exiftool"

    cmd = [EXIFTOOL, path, "-a", "-j", "-z"]
    dta = subprocess.check_output(cmd, universal_newlines=True)
    # convert to stream and load using 'json' library
    data = json.load(io.StringIO(dta))
    # reduce dimension if singleton
    if isinstance(data, list) and len(data) == 1:
        data = data[0]
    return data


def get_metadata(root):
    for folderRoot in root:
        imagesRoot = os.path.join(folderRoot, "images")
        print(imagesRoot)
        images = os.listdir(imagesRoot)

        for image in tqdm(images):

            image_path = os.path.join(imagesRoot, image)
            try:
                with open(image_path, "r") as file:
                    metadata = json.load(file)
            except:
                metadata = get_string_meta_data(image_path)

            filename = image.split(".")[0]
            matadata_file = os.path.join(folderRoot, "metadata", f"{filename}.txt")
            if not os.path.exists(os.path.join(folderRoot, "metadata")):
                os.makedirs(os.path.join(folderRoot, "metadata"), exist_ok=True)
            with open(matadata_file, "w") as file:
                file.write(json.dumps(metadata, indent=4, sort_keys=True, default=str))
