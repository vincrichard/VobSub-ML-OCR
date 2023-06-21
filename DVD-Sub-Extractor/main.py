from typing import List
from pathlib import Path
import argparse


from tqdm import tqdm
from vob_sub.main import extract_vob_sub_img

def create_generate_sub_images(vob_sub_file_name: Path, folder_imgs: Path, n_jobs: int = 1):
    subfile, image_paths = extract_vob_sub_img(vob_sub_file_name, folder_imgs, n_jobs)
    srt_filepath = vob_sub_file_name.with_suffix('.srt')

    with open(srt_filepath, 'w') as file:
        file.write(subfile)

    return image_paths

def predict_text_on_sub_images(vob_sub_file_name: Path, image_paths:List[Path], lang: List[str]):
    srt_filepath = vob_sub_file_name.with_suffix('.srt')
    with open(srt_filepath, 'r') as file:
        subfile = file.read()

    # Create Model
    if lang == ["ja"]:
        from manga_ocr import MangaOcr
        model = MangaOcr()
    else:
        import easyocr
        model = easyocr.Reader(lang)

    # Predict and replace text
    for path in tqdm(image_paths):
        if lang == ["ja"]:
            predicted_text = model(path)
        else:
            result = model.readtext(str(path), paragraph=True)
            predicted_text = ' '.join([r[-1] for r in result])

        subfile = subfile.replace(str(path), predicted_text)

    with open(srt_filepath, 'w') as file:
        file.write(subfile)


def launch(mode, vob_sub_file_name: Path, folder_imgs: Path, lang: List[str]=["ja"], n_jobs=1):
    if mode in ['extract', 'both']:
        image_paths = create_generate_sub_images(vob_sub_file_name, folder_imgs, n_jobs)
    else:
        image_paths = list(folder_imgs.iterdir())
        if len(image_paths) == 0:
            raise FileNotFoundError("No image found, in the folder directory")

    if mode in ['predict', 'both']:
        predict_text_on_sub_images(vob_sub_file_name, image_paths, lang)


def parse_args():
    parser = argparse.ArgumentParser(description="Extract images from VobSub (.sub/.idx) files and convert them to text using OCR.")

    parser.add_argument("-m", "--mode", choices=['extract', 'predict', 'both'], default='both', help="Mode of operation. 'extract' to only extract images, 'predict' to only perform OCR on existing images, 'both' to extract and then perform OCR.")
    parser.add_argument("-s", "--sub-file", type=Path, required=True, help="The path to the VobSub (.sub) file to process.")
    parser.add_argument("-d", "--destination-folder", type=Path, help="The directory where the extracted images should be stored. default: sub-file folder")
    parser.add_argument("-l", "--language", nargs="*", default=["ja"], help="The language of the subtitles. If 'ja', MangaOcr model will be used. If 'other', easyocr.Reader will be used.")
    parser.add_argument("-j", "--jobs", type=int, default=1, help="Number of jobs to run in parallel for image extraction.")

    return parser.parse_args()


def main():
    args = parse_args()
    sub_file = Path(args.sub_file)
    dest_folder = Path(args.destination_folder) if args.destination_folder is not None else sub_file.parent / f"{sub_file.stem}_img"
    launch(args.mode, sub_file, dest_folder, args.language, args.jobs)


if __name__ == "__main__":
    main()


# if __name__ == "__main__":
#     vob_sub_file_name = Path("example/godzilla.sub")
#     folder_imgs = vob_sub_file_name.parent / f'{vob_sub_file_name.stem}_img'
#     main(vob_sub_file_name, folder_imgs)


    # python script.py -s example/godzilla.sub
