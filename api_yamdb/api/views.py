from sqlite3 import IntegrityError

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import (Category, Genre, Review,
                            Title, User, UserRole)

from .filters import TitleFilter
from .mixins import CreateListDestroyMixinSet
from .permissions import IsAdminOnly, IsAdminModerator, IsAnonymous
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetCodeSerializer,
                          GetTokenSerializer, ReviewSerializer,
                          TitleCUDSerializer, TitleSerializer,
                          UserSerializer)


class CategoryViewSet(CreateListDestroyMixinSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyMixinSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAnonymous | IsAdminOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).all().order_by('-id')

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitleCUDSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminModerator]
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminModerator]
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        return review.comments.all()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAdminOnly]
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path="me",
        permission_classes=[IsAuthenticated],
        serializer_class=UserSerializer,
    )
    def me(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status.HTTP_200_OK)

        if request.method == 'PATCH':
            user = get_object_or_404(User, id=user.id)
            fixed_data = self.request.data.copy()
            if ('role' in self.request.data
                    and user.role == UserRole.USER.value):
                fixed_data['role'] = UserRole.USER.value
            serializer = self.get_serializer(
                user,
                data=fixed_data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    """Получить код подтверждения на указанный email"""
    serializer = GetCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, created = User.objects.get_or_create(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email']
        )
    except IntegrityError:
        return Response(
            'Username or Email already taken',
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception:
        return Response(
            'Username or Email already taken',
            status=status.HTTP_400_BAD_REQUEST
        )
    user.confirmation_code = default_token_generator.make_token(user)
    user.save()
    subject = 'Регистрация на YAMDB'
    message = f'Код подтверждения: {user.confirmation_code}'
    send_mail(subject, message, 'YAMDB', [user.email])
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """Получить токен для работы с API по коду подтверждения"""
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    if confirmation_code == user.confirmation_code:
        token = AccessToken.for_user(user)
        return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
    return Response({'confirmation_code': 'Неверный код подтверждения'},
                    status=status.HTTP_400_BAD_REQUEST)
