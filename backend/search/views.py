import hmac
import logging
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .cache import clear_app_cache, get_cached_search, set_cached_search
from .normalizers import normalize_search_response
from .serializers import SearchRequestSerializer
from .services import (
    GitHubAPIError,
    GitHubRateLimitError,
    GitHubTimeoutError,
    search_github,
)

logger = logging.getLogger(__name__)


class SearchView(APIView):
    # Пошук публічний. Вимикаємо автентифікацію, щоб не було вимог CSRF
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        search_type = serializer.validated_data["type"]
        query = serializer.validated_data["query"]

        cached_result = get_cached_search(search_type, query)
        if cached_result is not None:
            return Response({**cached_result, "cached": True})

        try:
            raw_response = search_github(search_type, query)
        except GitHubRateLimitError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except GitHubTimeoutError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except GitHubAPIError as exc:
            logger.warning("Помилка GitHub API: %s", exc)
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        result = normalize_search_response(search_type, raw_response)
        # Кешуємо лише успішну відповідь
        set_cached_search(search_type, query, result)

        return Response({**result, "cached": False})


class ClearCacheView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        expected_token = settings.CLEAR_CACHE_TOKEN
        provided_token = request.headers.get("X-Admin-Token", "")

        # Порожній токен у налаштуваннях означає, що очищення вимкнене
        is_authorized = bool(expected_token) and hmac.compare_digest(
            provided_token.encode(), expected_token.encode()
        )
        if not is_authorized:
            return Response(
                {"detail": "Доступ заборонено"},
                status=status.HTTP_403_FORBIDDEN,
            )

        deleted_count = clear_app_cache()
        return Response({"deleted_keys": deleted_count})