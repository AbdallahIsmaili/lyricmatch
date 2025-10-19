import yt_dlp
import os

# Create audio directory if it doesn't exist
os.makedirs("data/audio_samples", exist_ok=True)

urls = [
    # Cardi B
    "https://www.youtube.com/watch?v=PEGccV-NOm8",
    "https://youtu.be/hXnMSaK6C2w",
    "https://youtu.be/8zSRkr1nQNw",
    
    # Charlie Puth
    "https://www.youtube.com/watch?v=nfs8NYg7yQM",
    "https://www.youtube.com/watch?v=3AtDnEC4zak",
    "https://www.youtube.com/watch?v=CwfoyVa980U",
    
    # Coldplay
    "https://www.youtube.com/watch?v=RB-RcX5DS5A",
    "https://www.youtube.com/watch?v=dvgZkm1xWPE",
    "https://www.youtube.com/watch?v=k4V3Mo61fJM",
    
    # Drake
    "https://www.youtube.com/watch?v=xpVfcZ0ZcFM",
    "https://www.youtube.com/watch?v=DRS_PpOrUZ4",
    "https://www.youtube.com/watch?v=uxpDa-c-4Mc",
    
    # Ed Sheeran
    "https://www.youtube.com/watch?v=JGwWNGJdvx8",
    "https://www.youtube.com/watch?v=2Vv-BfVoq4g",
    "https://www.youtube.com/watch?v=K0ibBPhiaG0",
    
    # Eminem
    "https://www.youtube.com/watch?v=XbGs_qK2PQA",
    "https://youtu.be/FxQTY-W6GIo",
    "https://youtu.be/r_0JjYUe5jo",
    
    # Justin Bieber
    "https://www.youtube.com/watch?v=oyEuk8j8imI",
    "https://www.youtube.com/watch?v=fRh_vgS2dFE",
    "https://youtu.be/8EJ3zbKTWQ8",
    
    # Katy Perry
    "https://youtu.be/iGk5fR-t5AU",
    "https://www.youtube.com/watch?v=Um7pMggPnug",
    "https://www.youtube.com/watch?v=0KSOMA3QBU0",
    
    # Khalid
    "https://www.youtube.com/watch?v=IPfJnp1guPc",
    "https://youtu.be/by3yRdlQvzs",
    "https://youtu.be/x3bfa3DZ8JM",
    
    # Lady Gaga
    "https://youtu.be/wAeV90a5l-E",
    "https://youtu.be/5vheNbQlsyU",
    "https://www.youtube.com/watch?v=qrO4YZeyl0I",
    
    # Maroon 5
    "https://www.youtube.com/watch?v=aJOTlE1K90k",
    "https://youtu.be/5Wiio4KoGe8",
    "https://www.youtube.com/watch?v=SlPhMPnQ58k",
    
    # Nicki Minaj
    "https://youtu.be/zXtsGAkyeIo",
    "https://youtu.be/0Kg9xRooTVk",
    "https://youtu.be/_bvLphVWHpo",
    
    # Post Malone
    "https://youtu.be/SLsTskih7_I",
    "https://www.youtube.com/watch?v=SC4xMk98Pdc",
    "https://www.youtube.com/watch?v=au2n7VVGv_c",
    
    # Rihanna
    "https://www.youtube.com/watch?v=HL1UzIK-flA",
    "https://youtu.be/QMP-o8WXSPM",
    "https://youtu.be/wfN4PVaOU5Q",
    
    # Selena Gomez
    "https://youtu.be/zlJDTxahav0",
    "https://www.youtube.com/watch?v=VY1eFxgRR-k",
    "https://youtu.be/STO4-8vkG0U",
    
    # Taylor Swift
    "https://www.youtube.com/watch?v=-BjZmE2gtdo",
    "https://www.youtube.com/watch?v=3tmd-ClpJxA",
    "https://youtu.be/dfnCAmr569k"
]

ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "data/audio_samples/%(title)s.%(ext)s",
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "wav",
        "preferredquality": "192",
    }],
    # Improved options
    "restrictfilenames": True,  # Remove special characters from filenames
    "noplaylist": True,  # Download only single video, not playlist
    "continue_dl": True,  # Continue interrupted downloads
    "ignoreerrors": True,  # Continue on download errors
    "no_warnings": False,  # Show warnings
    "quiet": False,  # Don't be too quiet
    "verbose": False,
}

def download_songs():
    print(f"Starting download of {len(urls)} songs...")
    successful_downloads = 0
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for i, url in enumerate(urls, 1):
            try:
                print(f"Downloading {i}/{len(urls)}: {url}")
                ydl.download([url])
                successful_downloads += 1
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")
                continue
    
    print(f"Download completed! {successful_downloads}/{len(urls)} songs downloaded successfully.")

if __name__ == "__main__":
    download_songs()