
import typing
import webbrowser
from prettytable import PrettyTable
from pytube import YouTube
from pytube.cli import on_progress
import os
from youtubesearchpython import VideosSearch
import inquirer
import termcolor
from notification import Notification

class YoutubeVideoChannelThumbnail:
  def __init__(self,width : int,height: int,url: str) -> None:
    self.width = width
    self.heigth = height
    self.url = url


class YoutubeVideoChannel:
  def __init__(self,id: str,link: str,name: str,thumbnails: typing.List[YoutubeVideoChannelThumbnail]) -> None:
    self.id = id
    self.link = link
    self.name = name
    self.thumbnails : typing.List[YoutubeVideoChannelThumbnail] = thumbnails


class YoutubeVideo:
  def __init__(self) -> None:
    self.type = ""
    self.id = ""
    self.title = ""
    self.publishedTime = ""
    self.duration = ""
    self.link = ""
    self.thumbnails : typing.List[YoutubeVideoChannelThumbnail] = []
    self.channel : typing.List[YoutubeVideoChannel] = {}
  
  def link(self):
    return f"https://www.youtube.com/watch?v={self.id}"
  
  def show(self) -> None:
    table = PrettyTable()
    table.field_names = [ "Descripción", "Contenido" ]
    table.add_row(["Id",self.id])
    table.add_row(["Duración",self.duration])
    table.add_row(["Tipo de contenido",self.type])
    table.add_row(["Publicado hace",self.publishedTime])
    table.add_row(["Titúlo",self.title])
    table.add_row(["Link",self.link])
    print()
    print()
    print(termcolor.colored(table,"cyan"))
  
  def go(self, ready: bool = True) -> None:
    if ready:
      webbrowser.open(self.link)


class BuildListOfYoutubeData:
  def __init__(self) -> None:
    self.videos: typing.List[YoutubeVideo] = []

  def build(self,data) -> typing.List[YoutubeVideo]:
    for item in data:
      video = YoutubeVideo()
      video.type = item["type"]
      video.id = item["id"]
      video.title = item["title"]
      video.publishedTime = item["publishedTime"]
      video.duration = item["duration"]
      video.link = item["link"]
      video.thumbnails = [
        YoutubeVideoChannelThumbnail(
          height=thumbnailItem["height"],
          width=thumbnailItem["width"],
          url=thumbnailItem["url"],
        )  for thumbnailItem in item["thumbnails"]
      ]
      video.channel = YoutubeVideoChannel(
        id=item["channel"]["id"],
        link=item["channel"]["link"],
        name=item["channel"]["name"],
        thumbnails=item["channel"]["thumbnails"],
      )
      self.videos.append(video)

  def findVideo(self,pattern: typing.Callable[[YoutubeVideo], YoutubeVideo]) -> YoutubeVideo:
    video = YoutubeVideo()
    for currentVideo in self.videos:
      if pattern(currentVideo):
        video.title = currentVideo.title
        video.channel = currentVideo.channel
        video.duration = currentVideo.duration
        video.id = currentVideo.id
        video.link = currentVideo.link
        video.thumbnails = currentVideo.thumbnails
        video.type = currentVideo.type
        video.publishedTime = currentVideo.publishedTime
        break
    return video
  

class DownloadYoutubeVideo:
  def __init__(self, link) -> None:
    self.youtube = YouTube(link,on_progress_callback=on_progress)

  def audio(self) -> str:
    video = self.youtube.streams.filter(only_audio=True).first()
    downloaded = video.download()
    base,text = os.path.splitext(downloaded)
    audioFile = base + ".mp3"
    os.rename(downloaded,audioFile)
    return audioFile

  def video(self) -> str:
    downloaded = self.youtube.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
    return downloaded
  
  def downloadByFormat(self,format: str) -> None:
    if format == "mp3":
      self.audio()
    elif format == "mp4":
      self.video()
    else:
      print(termcolor.colored("No se encontró el formato de descarga","red"))


class Search:
  def __init__(self) -> None:
    print()
    self.term = input(termcolor.colored("Ingresar video a buscar, puedes escribir cualquier contenido... ","magenta"))
    print()
    print()

  def getTerm(self):
    return self.term


class Application:

  def build(self):
    search = Search()
    videosSearch = VideosSearch(search.getTerm(), limit = 20)
    buildYoutubeVideosList = BuildListOfYoutubeData()
    buildYoutubeVideosList.build(videosSearch.result()["result"])

    questions = inquirer.prompt([
      inquirer.List(
        'video',
        message="Encontramos los siguientes resultados para tu busqueda",
        choices=[
          currentSearchedVideo.title
          for currentSearchedVideo in buildYoutubeVideosList.videos
        ],
      ),
      inquirer.List(
        "format",
        message="En que formato deseas descargar el video(mp4, mp3)",
        choices=[currentFormat for currentFormat in ["mp4","mp3"]]
      ),
      inquirer.Confirm(
        "openLink",
        message= "Abrir link del video una vez descargado?"
      )
    ])

    selectedVideo = buildYoutubeVideosList.findVideo(pattern = lambda video: video.title == questions["video"])
    donwloader = DownloadYoutubeVideo(link = selectedVideo.link)
    donwloader.downloadByFormat(format=questions["format"])
    selectedVideo.show()
    Notification.notify(
      title="Contenido de youtube descargado",
      message=f"Se ha descargado el video {selectedVideo.title} en el formato elegido"
    )
    selectedVideo.go(questions["openLink"])

if __name__ == "__main__":
  Application().build()