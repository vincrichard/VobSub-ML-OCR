from dataclasses import dataclass
from pathlib import Path

@dataclass
class SettingsArgs:

    task: str
    path_file_idx: Path
    name_dir_img: Path = "tmp_subtitle_img"
    keep_img: bool = False
