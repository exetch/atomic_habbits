
from rest_framework import viewsets
from .models import CustomUser
from .permissions import IsOwnerOrReadOnly
from .serializers import UserSerializer



class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrReadOnly]

