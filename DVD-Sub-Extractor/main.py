from pathlib import Path
from matplotlib import image
import numpy as np
import easyocr
from tqdm import tqdm
from skimage.transform import resize
from skimage.color import rgb2gray

from vob_sub_parser import VobSubParser


def initialize_sub_idx(vob_sub_file_name: Path):
    name = "hanabi"
    vob_sub_parser = VobSubParser(True)
    idx_file_name = vob_sub_file_name.with_suffix('.idx')

    vob_sub_parser.open_sub_idx(str(vob_sub_file_name), str(idx_file_name))
    _vob_sub_merged_pack_list = vob_sub_parser.merge_vob_sub_packs()
    _palette = vob_sub_parser.idx_palette
    folder_path = Path(f'{name}_img')
    if not folder_path.exists():
        folder_path.mkdir(parents=True)
    with open(f'{name}.srt', 'w') as file:
        file.write('')
        for i, pack in enumerate(_vob_sub_merged_pack_list):
            image_path = folder_path / f'{i + 1}.png'
            pack.palette = _palette
            img = pack.get_bitmap()
            img = (img * 255).astype('uint8')
            # img = rgb2gray(img)
            h, w, c = img.shape
            # img = resize(img, (h*2, w*2))
            img = np.pad(img, ((int(h/2), int(h/2)), (int(w/10), int(w/10)), (0,0)))
            # image.imsave(image_path, img, cmap="Greys")
            # image.imsave(image_path, np.dot((img * 255).astype('uint8')[..., :3], [0.2989, 0.5870, 0.1140]), cmap="Greys")
            image.imsave(image_path, img)
            with open(f'{name}.srt', 'a') as file:
                file.write(f'{i + 1}\n')
                file.write(f'{pack.start_time.get_str_format()} --> {pack.end_time.get_str_format()}\n')
                file.write(f'{image_path}\n')
                file.write(f'\n')

    with open(f'{name}.srt', 'r') as file:
        srt_file = file.read()

    reader = easyocr.Reader(['ja', 'en'])
    for path in tqdm(list(folder_path.iterdir())):
        result = reader.readtext(str(path), paragraph=True)
        result = ' '.join([r[-1] for r in result])

        srt_file = srt_file.replace(str(path), result)
    with open(f'{name}.srt', 'w') as file:
        file.write(srt_file)


if __name__ == "__main__":
    initialize_sub_idx(Path("/media/vincent/C0FC3B20FC3B0FE0/Film/Hanabi/hanabi.sub"))
    # initialize_sub_idx(Path("/media/vincent/C0FC3B20FC3B0FE0/Film/Godzilla/test_2_godz.sub"))