from time import sleep
from notifypy import Notify

class Notification:
  @staticmethod
  def notify(title: str, message: str) -> None:
    notification = Notify()
    notification.title = title
    notification.message = message
    notification.application_name = "Conversor de videos"
    notification.icon = "./youtube.png"
    notification.send() 
    sleep(3)
