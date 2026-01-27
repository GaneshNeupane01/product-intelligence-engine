"""
DRF Serializers for the search app.
"""

from rest_framework import serializers
from .models import SearchQuery, SearchResult, RawMarkdown, ParsedProduct, NormalizedProduct


class RawMarkdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMarkdown
        fields = ["id", "content", "content_length", "extracted_at"]


class NormalizedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalizedProduct
        fields = ["id", "normalized_specs", "normalized_price", "normalized_at"]


class ParsedProductSerializer(serializers.ModelSerializer):
    normalized = NormalizedProductSerializer(read_only=True)

    class Meta:
        model = ParsedProduct
        fields = ["id", "data", "error_message", "parsed_at", "normalized"]


class SearchResultSerializer(serializers.ModelSerializer):
    raw_markdown = RawMarkdownSerializer(read_only=True)
    parsed_product = ParsedProductSerializer(read_only=True)

    class Meta:
        model = SearchResult
        fields = [
            "id",
            "url",
            "title",
            "description",
            "position",
            "raw_markdown",
            "parsed_product",
            "created_at",
        ]


class SearchQuerySerializer(serializers.ModelSerializer):
    results = SearchResultSerializer(many=True, read_only=True)

    class Meta:
        model = SearchQuery
        fields = [
            "id",
            "query",
            "num_sites",
            "provider",
            "status",
            "error_message",
            "results",
            "created_at",
            "completed_at",
        ]


class SearchRequestSerializer(serializers.Serializer):
    """Validates incoming search requests."""
    query = serializers.CharField(max_length=500, required=True)
    num_sites = serializers.IntegerField(min_value=1, max_value=10, default=5)
