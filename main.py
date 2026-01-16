import yt_dlp
from yt_dlp import DownloadError
import asyncio
import time
import tkinter

class API:
    def __init__(self, urls):
        self.urls = urls if isinstance(urls, list) else [urls]
        self.download_params = {
            "noplaylist": True,
            "format": "mp3/bestaudio/best",
            "outtmpl": "downloads/",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",}]}
        self.list_params = {
            "extract_flat": True,
            "quiet": True,
            "skip_download": True}

    async def get_info(self):
        results = await asyncio.gather(*[self.fetch_info(url) for url in self.urls], return_exceptions=True)
        flattened = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Error fetching info for URL: {result}")
            else:
                flattened.extend(result)
        self.urls = flattened

    async def fetch_info(self, url):
        try:
            with yt_dlp.YoutubeDL(self.list_params) as downloading_session:
                info = await asyncio.to_thread(downloading_session.extract_info, url, download=False)
                if "entries" in info:
                    extracted_urls = []
                    for entry in info["entries"]:
                        extracted_urls.append(entry["url"])
                        print(f"Extracted URL: {entry["url"]}")
                        print(f"Title: {entry["title"]}")
                        print(f"Runtime: {entry["duration"]} seconds")
                    return extracted_urls
                else:
                    print("Single video URL.")
                    return [url]
                
        except DownloadError as e:
            print(f"Download error for {url}: {e}")
        except Exception as e:
            print(f"Unexpected error fetching info for {url}: {e}")

        return            
    
    async def download_single(self,url):
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


async def main():
    url_input = input("Enter URLs: ")
    urls = [url.strip() for url in url_input.split(",")]
    api = API(urls)
    await api.get_info()
    await api.download()

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Runtime: {end_time - start_time} seconds")