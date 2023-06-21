from typing import List, Union, Tuple
from pathlib import Path
import concurrent.futures
from functools import partial

from tqdm import tqdm
from matplotlib import image
import numpy as np

from .vob_sub_parser import VobSubParser
from .vob_sub_merge_pack import VobSubMergedPack


def extract_vob_sub_img(vob_sub_file_name: Path, folder_path: Union[str, Path], n_jobs: int = 1) -> List[Path]:
    if isinstance(folder_path, str):
        folder_path = Path(folder_path)
    vob_sub_parser = VobSubParser(True)
    idx_file_name = vob_sub_file_name.with_suffix('.idx')

    if not idx_file_name.exists() or not vob_sub_file_name.exists():
        raise FileNotFoundError(f"One of those 2 files don't exist '{idx_file_name}', '{vob_sub_file_name}'")

    vob_sub_parser.open_sub_idx(str(vob_sub_file_name), str(idx_file_name))
    _vob_sub_merged_pack_list = vob_sub_parser.merge_vob_sub_packs()
    _palette = vob_sub_parser.idx_palette

    if not folder_path.exists():
        folder_path.mkdir(parents=True)

    if n_jobs > 1:
        return multiprocess(_vob_sub_merged_pack_list, folder_path, _palette, n_jobs)
    else:
        return process_list_pack(_vob_sub_merged_pack_list, folder_path, _palette)

def process_list_pack(_vob_sub_merged_pack_list: List[VobSubMergedPack], folder_path: Path, _palette: List[str]) -> Tuple[str, List[Path]]:
    image_paths = []
    subfile = ""
    for id_pack, pack in enumerate(tqdm(_vob_sub_merged_pack_list)):
        subfile_text, img_path = process_pack(id_pack, pack, folder_path, _palette)
        image_paths.append(img_path)
        subfile += subfile_text
    return subfile, image_paths

def process_pack(id_pack: int, pack: VobSubMergedPack, folder_path: Path, palette: List[str]) -> Tuple[Path, str]:
    image_path = folder_path / f'{id_pack + 1}.png'
    img = extract_subtitle_image_from_pack(pack, palette)
    image.imsave(image_path, (img * 255).astype('uint8'))
    subfile_text = create_subfile_text(id_pack, pack, image_path)
    return subfile_text, image_path

def create_subfile_text(pack_id, pack: VobSubMergedPack, image_path: Path):
    return f"{pack_id + 1}\n" + \
        f"{pack.start_time.get_str_format()} --> {pack.end_time.get_str_format()}\n" + \
        f"{image_path}\n\n"


def extract_subtitle_image_from_pack(pack: VobSubMergedPack, palette: List[str]) -> np.ndarray :
    pack.palette = palette
    img = pack.get_bitmap()
    # img = (bitmap * 255).astype('uint8')
    # Resize image to make sure we don't keep large empty space
    x, y, _ = np.where(img > 0)
    img = img[max(np.min(x) - 5, 0):np.max(x) + 5, max(np.min(y) - 5, 0): np.max(y) + 5]
    return img


def multiprocess(_vob_sub_merged_pack_list, folder_path, _palette, n_jobs):
    image_paths = []
    subfile_texts = []
    multi_process_pack = partial(process_pack, folder_path=folder_path, palette=_palette)
    num_packs = len(_vob_sub_merged_pack_list)
    with concurrent.futures.ProcessPoolExecutor(n_jobs) as executor:
        for result in tqdm(executor.map(
                multi_process_pack, range(num_packs), _vob_sub_merged_pack_list
            ), total=num_packs):
            subfile_text, image_path = result
            subfile_texts.append(subfile_text)
            image_paths.append(image_path)
    id_image = [int(p.stem) for p in image_paths]
    image_paths = sum(np.array(image_paths)[id_image].tolist(), [])
    subfile = sum(np.array(subfile_texts)[id_image].tolist(), "")
    return subfile, image_paths



# h, w, c = img.shape
# # img = resize(img, (h*2, w*2))
# img = np.pad(img, ((int(h/2), int(h/2)), (int(w/10), int(w/10)), (0,0)))
# # image.imsave(image_path, img, cmap="Greys")
# # image.imsave(image_path, np.dot((img * 255).astype('uint8')[..., :3], [0.2989, 0.5870, 0.1140]), cmap="Greys")
