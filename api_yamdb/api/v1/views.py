from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import TitleFilter
from .permissions import (IsAdmin, IsAdminmOrReadOnly, IsAdminOrReadOnly,
                          IsAuthorOrModeRatOrOrAdminOrReadOnly)
from .serializers import (CategoriesSerializer, CommentSerializer,
                          GenresSerializer, ReviewSerializer, SignUpSerializer,
                          TitleSerializer, TokenRegSerializer,
                          UserEditSerializer, UserSerializer)


class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (IsAdminmOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


@api_view(['DELETE'])
@permission_classes([IsAdminmOrReadOnly])
def categorie_delete(request, slug):
    categorie = Category.objects.get(slug=slug)
    if request.method == 'DELETE':
        categorie.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViwSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (IsAdminmOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


@api_view(['DELETE'])
@permission_classes([IsAdminmOrReadOnly])
def genres_delete(request, slug):
    genres = Genre.objects.get(slug=slug)
    if request.method == 'DELETE':
        genres.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg("reviews__score"))
    serializer_class = TitleSerializer
    permission_classes = (IsAdminmOrReadOnly, )
    filterset_class = TitleFilter
    filterset_fields = ('name',)
    ordering = ('name',)


class AdminViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class SignUpApiView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            username = serializer.validated_data.get("username")
            email = serializer.validated_data.get("email")
            user, _ = User.objects.get_or_create(
                username=username,
                email=email
            )
        except IntegrityError:
            return Response("Это имя или email уже существует",
                            status.HTTP_400_BAD_REQUEST)
        code = default_token_generator.make_token(user)
        send_mail(
            "Код токена",
            f"Код для получения токена {code}",
            settings.DEFAULT_FROM_EMAIL,
            [serializer.validated_data.get("email")]
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenRegApiView(APIView):
    def post(self, request):
        serializer = TokenRegSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        confirmation_code = serializer.validated_data.get(
            "confirmation_code")
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            message = (
                "Вы использовали неверный код подтверждения.")
            return Response({message}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(user)
        return Response({"token": str(token.access_token)},
                        status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        methods=['patch', 'get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        serializer = UserEditSerializer(user)
        if request.method == 'PATCH':
            serializer = UserEditSerializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeRatOrOrAdminOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeRatOrOrAdminOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get("review_id"))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
