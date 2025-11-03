import os
import platform
import shutil
import zipfile
import tarfile
import urllib.request
import subprocess

class FFMPEG:
    __ffmpeg_binary: str | None = None

    @staticmethod
    def init(ffmpeg_binary: str | None = None) -> str:
        if ffmpeg_binary is not None and os.path.isfile(ffmpeg_binary):
            FFMPEG.__ffmpeg_binary = ffmpeg_binary
            return ffmpeg_binary
        
        # Detect OS and architecture
        system = platform.system().lower()
        arch = platform.machine().lower()
        install_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg')
        
        # URLs for latest static builds from https://www.gyan.dev/ffmpeg/builds/ (Windows) or https://johnvansickle.com/ffmpeg/ (Linux)
        ffmpeg_url = None
        zip_name = None

        if system == 'windows':
            # Windows 64-bit static build (official builds)
            ffmpeg_url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
            zip_name = 'ffmpeg-release-essentials.zip'
        elif system == 'linux':
            if 'x86_64' in arch or 'amd64' in arch:
                ffmpeg_url = 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'
                zip_name = 'ffmpeg-release-amd64-static.tar.xz'
            else:
                raise RuntimeError(f"Unsupported arch {arch} for Linux in this script")
        elif system == 'darwin':
            # macOS - static build from evermeet.cx
            ffmpeg_url = 'https://evermeet.cx/ffmpeg/get/zip'
            zip_name = 'ffmpeg.zip'
        else:
            raise RuntimeError(f"Unsupported OS {system}")

        urllib.request.urlretrieve(ffmpeg_url, zip_name)

        # Extract files
        if zip_name.endswith('.zip'):
            with zipfile.ZipFile(zip_name, 'r') as zip_ref:
                zip_ref.extractall(install_path)
        elif zip_name.endswith('.tar.xz'):
            with tarfile.open(zip_name, 'r:xz') as tar_ref:
                tar_ref.extractall(install_path)
        else:
            raise RuntimeError("Unsupported archive format")
        
        os.remove(zip_name)
        filename = "ffmpeg.exe" if system == 'windows' else "ffmpeg"
        #search for ffmpeg binary in extracted folder, move to the root of install_path
        for root, _, files in os.walk(install_path):
            if filename in files:
                shutil.move(os.path.join(root, filename), os.path.join(install_path, filename))
                break
        
        #delete all other extracted files/folders
        for item in os.listdir(install_path):
            item_path = os.path.join(install_path, item)
            if item != filename:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
        
        FFMPEG.__ffmpeg_binary = os.path.join(install_path, filename)
        return FFMPEG.__ffmpeg_binary
    
    @staticmethod
    def is_initialized() -> bool:
        return FFMPEG.__ffmpeg_binary is not None

    @staticmethod
    def execute_command(args: list[str]) -> None:
        if FFMPEG.__ffmpeg_binary is None:
            raise RuntimeError("FFMPEG not initialized. Call FFMPEG.init() first.")
        
        command = [FFMPEG.__ffmpeg_binary] + args

        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,  # suppress normal output
                stderr=subprocess.PIPE,      # capture errors
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg execution failed:\n{e.stderr.strip()}") from e
