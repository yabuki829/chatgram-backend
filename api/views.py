from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Program,Location,TVStation,Broadcast
from .serializers import ProgramSerializer
from django.utils import timezone

from utils.broadcaster import Broadcaster
class ProgramList(APIView):
    def get(self, request, format=None):
        # 都道府県とchannelで分ける
        # 取得例) 大阪の10channelを取得する
        # データの中を確認して location, channel を取得する
        

        location = Location.objects.get(name="大阪")
        today = timezone.now().date()
        broadcast = Broadcast.objects.filter(channel=10, location=location).first()

        if broadcast:
            programs_today = Program.objects.filter(tv_station=broadcast.tv_station, date=today).order_by('time')
            serializer = ProgramSerializer(programs_today, many=True)

        else:
            print("指定された条件に一致するBroadcastが見つかりません。")
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProgramSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
@api_view(['GET'])
def test(request):
    print("test")
    broadcaster = Broadcaster()
    broadcaster.get_nihonTV_program()
    broadcaster.get_yomiuriTV_2()
    return Response({"message": "取得完了"})