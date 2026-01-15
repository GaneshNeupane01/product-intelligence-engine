"""
API views for the search app.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import SearchQuery
from .serializers import (
    SearchQuerySerializer,
    SearchRequestSerializer,
)
from .services import execute_search


@api_view(["POST"])
def search_products(request):
    """
    POST /api/search/
    Body: { "query": "RTX 5070", "num_sites": 5 }

    Runs the full search pipeline and returns structured results.
    """
    serializer = SearchRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data["query"]
    num_sites = serializer.validated_data["num_sites"]

    search_query = execute_search(query=query, num_sites=num_sites)

    result_serializer = SearchQuerySerializer(search_query)
    http_status = (
        status.HTTP_200_OK
        if search_query.status == "completed"
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result_serializer.data, status=http_status)


@api_view(["GET"])
def search_detail(request, search_id):
    """
    GET /api/search/<uuid>/
    Returns a previously stored search with all its results.
    """
    try:
        search_query = SearchQuery.objects.get(id=search_id)
    except SearchQuery.DoesNotExist:
        return Response(
            {"error": "Search not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = SearchQuerySerializer(search_query)
    return Response(serializer.data)


@api_view(["GET"])
def search_history(request):
    """
    GET /api/search/history/
    Returns the last 20 searches.
    """
    queries = SearchQuery.objects.all()[:20]
    serializer = SearchQuerySerializer(queries, many=True)
    return Response(serializer.data)
