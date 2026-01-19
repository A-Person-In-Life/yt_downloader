from yt_dlp import DownloadError
import yt_dlp
import asyncio
import time
import tkinter
from tkinter import ttk
import os

class API:
    def __init__(self, urls):
        self.urls = urls if isinstance(urls, list) else [urls]

        self.list_params = {
            "extract_flat": True,
            "quiet": True,
            "skip_download": True}
        
        self.location = "/home/gavin/downloads/yt_downloads"
        self.download_params = {
            "noplaylist": True,
            "format": "mp3/bestaudio/best",
            "outtmpl": f"{self.location}/%(title)s.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",}],
            "quiet": True}

    async def get_info(self):
        results = await asyncio.gather(*[self.fetch_url(url) for url in self.urls], return_exceptions=True)
        flattened = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Error fetching info for URL: {result}")
            else:
                flattened.extend(result)
        self.urls = flattened

    async def fetch_name(self, url):
        try:
            with yt_dlp.YoutubeDL(self.list_params) as downloading_session:
                info = await asyncio.to_thread(downloading_session.extract_info, url, download=False)
                if "entries" in info:
                    for entry in info["entries"]:
                        return entry.get("title", "Unknown")
                else:
                    return info.get("title", "Unknown")
                
        except DownloadError as e:
            print(f"Download error for {url}: {e}")
        except Exception as e:
            print(f"Unexpected error fetching title for {url}: {e}")

        return None


    async def fetch_url(self, url):
        try:
            with yt_dlp.YoutubeDL(self.list_params) as downloading_session:
                info = await asyncio.to_thread(downloading_session.extract_info, url, download=False)
                if "entries" in info:
                    extracted_urls = []
                    for entry in info["entries"]:
                        extracted_urls.append(entry["url"])
                        print(f"Extracted URL: {entry['url']}")
                        print(f"Title: {entry['title']}")
                        print(f"Runtime: {entry['duration']} seconds")
                    return extracted_urls
                else:
                    print("Single video URL.")
                    return [url]
                
        except DownloadError as e:
            print(f"Download error for {url}: {e}")
        except Exception as e:
            print(f"Unexpected error fetching info for {url}: {e}")

        return []            
    
    async def download_single(self, url):
        try:
            with yt_dlp.YoutubeDL(self.download_params) as downloading_session:
                await asyncio.to_thread(downloading_session.download, [url])
            print(f"Successfully downloaded: {url}")

        except DownloadError as e:
            print(f"Download error for {url}: {e}")
        except Exception as e:
            print(f"Unexpected error downloading {url}: {e}")
                            
    async def download(self):
        await asyncio.gather(*[self.download_single(url) for url in self.urls])


class Executer:
    def __init__(self, extracted_urls): 
        self.location = "/home/gavin/downloads/yt_downloads"
        self.extracted_urls = extracted_urls
        self.api = API(extracted_urls)

    async def predownload_processing(self):
        try:
            await self.api.get_info()
            print(f"Extracted {len(self.api.urls)} URLs.")
            
            existing_files = set(os.listdir(self.location))
            
            titles = await asyncio.gather(*[self.api.fetch_name(url) for url in self.api.urls])
            
            filtered_urls = []
            for url, title in zip(self.api.urls, titles):
                if title:
                    sanitized_title = title.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
                    filename = f"{sanitized_title}.mp3"
                    if filename in existing_files:
                        print(f"File already exists: {filename}, skipping URL: {url}")
                    else:
                        filtered_urls.append(url)
                else:
                    print(f"Could not fetch title for {url}, skipping.")
            self.api.urls = filtered_urls
            print(f"Filtered to {len(self.api.urls)} URLs to download.")

        except Exception as e:
            print(f"Error in predownload_processing: {e}")
    
    async def start_download(self):
        try:
            await self.api.download()

        except Exception as e:
            print(f"Error in start_download: {e}")


            
class GUI:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("YouTube Downloader")

        self.label = tkinter.Label(self.root, text="Enter YouTube URLs (comma separated):")
        self.label.pack()

        self.url_entry = tkinter.Entry(self.root, width=50)
        self.url_entry.pack()

        self.download_button = tkinter.Button(self.root, text="Download", command=self.start_download)
        self.download_button.pack()

        self.root.mainloop()

    def start_download(self):
        try:
            url_input = self.url_entry.get().strip()
            if not url_input:
                print("No URL entered.")
                return
            
            urls = [url.strip() for url in url_input.split(",") if url.strip()]
            
            loc = url_input.find("list=")
            if loc != -1:
                print("Playlist detected")
                playlist_id = url_input[loc + 5:].split('&')[0] 
                urls = [f"https://www.youtube.com/playlist?list={playlist_id}"]
            
            self.executer = Executer(urls)
            
            async def run_async():
                await self.executer.predownload_processing()
                download_start = time.time()
                await self.executer.start_download()
                download_end = time.time()
                print(f"Download Runtime: {download_end - download_start} seconds")
            
            asyncio.run(run_async())
        except Exception as e:
            print(f"Error starting download: {e}")

if __name__ == "__main__":
    gui = GUI()
