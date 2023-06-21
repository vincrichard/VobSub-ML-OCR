
# VobSub Image Extractor and OCR

This is a Python program designed to extract images from VobSub (`.sub/.idx`) files and convert them to text using OCR (Optical Character Recognition).

The extraction of the VobSub as been taken from [SubtitleEdit](https://github.com/SubtitleEdit/subtitleedit) and ported to python.

## Features

1. **Image Extraction**: The program can extract images from provided VobSub files. The user can specify the file and destination folder for the extracted images.

2. **OCR Processing**: The program can use OCR to convert pre-extracted images to text. It supports multiple languages and uses different models for different languages. Specifically, it uses the `MangaOcr` model for Japanese (`ja`) and `easyocr.Reader` for other languages.

3. **Flexible Modes**: The program offers flexibility in its operation. Users can choose to only extract images from VobSub files, only perform OCR on existing images, or both.

4. [Not fully tested] **Parallel Processing**: The program allows the user to specify the number of jobs to run in parallel for image extraction, speeding up the process for large files.


## Installation and Setup

Before running this program, it's recommended to create a virtual environment. This helps to isolate the project and avoid conflicts with dependencies of other projects. Here's how you can do it:

### Creating a virtual environment

**Using venv:**

```bash
# Create a virtual environment
python3 -m venv env

# Activate the virtual environment
source env/bin/activate  # On Windows, use `.\env\Scripts\activate`
```

**Using conda:**

```bash
# Create a virtual environment
conda create --name myenv

# Activate the virtual environment
conda activate myenv
```

Replace `myenv` with any name you like for your environment.

### Installing Dependencies

The next step is to install the necessary dependencies. These dependencies are listed in a file named `requirements.txt`.

```bash
pip install -r requirements.txt
```

Ensure you're still within your virtual environment when you run this command.


## Usage

The program can be used from the command line as follows:

```bash
python script.py -m <mode> -s <sub_file> -d <destination_folder> -l <language> -j <jobs>
```

The arguments are:

* `-m` or `--mode`: Mode of operation. 'extract' to only extract images, 'predict' to only perform OCR on existing images, 'both' to extract and then perform OCR. Default is 'both'.
* `-s` or `--sub-file`: Path to the VobSub (`.sub`) file to process. This argument is required.
* `-d` or `--destination-folder`: Directory where the extracted images should be stored or where to find images for OCR, depending on the mode. This argument is required.
* `-l` or `--language`: The language(s) of the subtitles. If 'ja', MangaOcr model will be used. If 'other', easyocr.Reader will be used. Can be a list of languages. Default is 'ja'.
* `-j` or `--jobs`: Number of jobs to run in parallel for image extraction. Only applies in 'extract' and 'both' modes. Default is 1.

Remember to replace `script.py` with the actual name of your Python script.


### Extract .sub/.idx Files using `mkvmerge` and `mkvextract`

1. **Download and install `MKVToolNix`**

    You can find it here: [MKVToolNix download page](https://mkvtoolnix.download/downloads.html)


2. **Rip DVD to MKV**

    You can use a tool like `MakeMKV` to rip your DVD into an MKV file. The process is usually straightforward: insert your DVD, open `MakeMKV`, and follow the on-screen instructions.

3. **Identify the subtitle track**

    Use the `mkvmerge` tool to identify the subtitle track in the MKV file. Open a terminal window and type the following command:

    ```bash
    mkvmerge -I yourfile.mkv
    ```

    This will list all tracks in the file. Look for lines that begin with `Track ID`. Note down the track ID of the subtitle track you're interested in.

4. **Extract the subtitle track**

    To extract the subtitle track, use `mkvextract`. Replace `#` with the track ID from the previous step. The command looks like this:

    ```bash
    mkvextract yourfile.mkv tracks track_id:outputfile.sub
    ```

    This will extract the subtitle track into `outputfile.sub`. If the subtitle track is in VobSub format, an additional `outputfile.idx` file will also be created.

Remember, the paths `yourfile.mkv` and `outputfile.sub` should be replaced with the appropriate paths and filenames on your system.
