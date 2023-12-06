from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework import generics, permissions
from .models import Habit
from .pagination import StandardResultsSetPagination
from .serializers import HabitSerializer


class HabitListCreateView(generics.ListCreateAPIView):
    """
        Представление для списка и создания привычек.

        Это представление предоставляет API для получения списка привычек конкретного пользователя
        и создания новой привычки. Только аутентифицированные пользователи имеют доступ
        к этому представлению. Используется пагинация для управления объемом данных.

        Атрибуты:
            serializer_class (HabitSerializer): Сериализатор для привычек.
            permission_classes (list): Список классов разрешений.
            pagination_class (StandardResultsSetPagination): Класс пагинации.

        Методы:
            get_queryset: Возвращает queryset, фильтруемый по текущему пользователю.
            perform_create: Сохраняет созданную привычку с привязкой к текущему пользователю.
    """
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['location', 'is_public', 'is_pleasant', 'action']
    ordering_fields = ['time', 'action', 'frequency']

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
        Представление для получения, обновления и удаления привычки.

        Это представление позволяет пользователям получать детальную информацию о привычке,
        а также обновлять или удалять ее. Доступно только аутентифицированным пользователям,
        которые являются владельцами привычки.

        Атрибуты:
            serializer_class (HabitSerializer): Сериализатор для привычек.
            permission_classes (list): Список классов разрешений.

        Методы:
            get_queryset: Возвращает queryset, фильтруемый по текущему пользователю.
    """
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class PublicHabitListView(generics.ListAPIView):
    """
        Представление для списка публичных привычек.

        Это представление предоставляет API для получения списка привычек,
        отмеченных как публичные.
        Доступно для всех аутентифицированных пользователей.
        Используется пагинация для управления объемом данных.

        Атрибуты:
            serializer_class (HabitSerializer): Сериализатор для привычек.
            permission_classes (list): Список классов разрешений.
            pagination_class (StandardResultsSetPagination): Класс пагинации.

        Методы:
            get_queryset: Возвращает queryset, содержащий только публичные привычки.
    """
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)
