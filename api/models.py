from django.db import models
import uuid

class Location(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(default="都道府県", max_length=255)
    class Meta:
        ordering = ('name',)  
    def __str__(self):
        return self.name

class TVStation(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(default="放送局", max_length=255)
    class Meta:
        ordering = ('name',)  
    def __str__(self):
        return self.name

class Broadcast(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    tv_station = models.ForeignKey(TVStation, on_delete=models.CASCADE, related_name='broadcasts')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='broadcasts')
    channel = models.IntegerField(default=1)

    class Meta:
        ordering = ('location__name',) 
    def __str__(self):
        return f"{self.location.name}({self.channel}) {self.tv_station.name}"


# ルームをどの段階で作成するのか問題
# 1. 番組を取得したタイミングで作成しておく
# 2. 初めてコメントしたタイミングで作成
class Room(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(default="No Title", max_length=255)
    def __str__(self):
        return  self.name
    
from django.utils import timezone

class Program(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    title = models.CharField(default="No Title", max_length=255)
    detail = models.TextField()
    tv_station = models.ForeignKey(TVStation, on_delete=models.CASCADE, related_name='programs')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    room = models.ForeignKey(Room,on_delete=models.CASCADE,related_name='programs')
    class Meta:
        ordering = ('title',) 
    def __str__(self):
        return  "[ " + self.tv_station.name+ " ]" + self.title



# 番組のタイトルに対してchatを作成する.
# 金曜ロードショー「ＳＩＮＧ／シング」のチャットを作成する。
# get(title="金曜ロードショー「ＳＩＮＧ／シング」") chatを取得する
    
