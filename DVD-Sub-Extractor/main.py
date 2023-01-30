from pathlib import Path
from matplotlib import image

from vob_sub_parser import VobSubParser
import easyocr
from tqdm import tqdm


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
            image.imsave(image_path, (img * 255).astype('uint8'))
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
        a = 0

        srt_file = srt_file.replace(str(path), result)
    a = 0
    with open(f'{name}.srt', 'w') as file:
        file.write(srt_file)


if __name__ == "__main__":
    initialize_sub_idx(Path("/media/vincent/C0FC3B20FC3B0FE0/Film/Hanabi/sub_hanabi.sub"))
    # initialize_sub_idx(Path("/media/vincent/C0FC3B20FC3B0FE0/Film/Godzilla/sub_godzila.sub"))