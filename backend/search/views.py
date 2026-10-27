import hmac
import logging
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .cache import clear_app_cache, get_cached_search, set_cached_search,save_search_query,get_search_history
from .normalizers import normalize_search_response
from rest_framework.authentication import TokenAuthentication
from .serializers import SearchRequestSerializer
from .services import (
    RESULTS_PER_PAGE,
    GitHubAPIError,
    GitHubRateLimitError,
    GitHubTimeoutError,
    search_github,
)

logger = logging.getLogger(__name__)


class SearchView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        search_type = serializer.validated_data["type"]
        query = serializer.validated_data["query"]
        page = serializer.validated_data["page"]

        cached_result = get_cached_search(search_type, query, page)
        if cached_result is not None:
            if page == 1:
                save_search_query(search_type, query, request.user.id)
            return Response({**cached_result, "cached": True})

        try:
            raw_response = search_github(search_type, query, page)
        except GitHubRateLimitError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except GitHubTimeoutError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except GitHubAPIError as exc:
            logger.warning("Помилка GitHub API: %s", exc)
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        result = normalize_search_response(search_type, raw_response, page, RESULTS_PER_PAGE)
        if page == 1:
            save_search_query(search_type, query, request.user.id)
        set_cached_search(search_type, query, result, page)

        return Response({**result, "cached": False})
class ClearCacheView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        deleted_count = clear_app_cache()
        return Response({"deleted_keys": deleted_count})

class HistoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = get_search_history(request.user.id)

        return Response({"history": history})
