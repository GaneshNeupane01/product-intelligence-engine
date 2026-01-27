"""
Database models for the search app.

Phase 1 stores:
- SearchQuery: the user's original search
- SearchResult: each URL returned by the search provider
- RawMarkdown: the extracted markdown content per result

Phase 3: NormalizedProduct
Phase 4: ComparisonResult
"""

from django.db import models
import uuid


class SearchQuery(models.Model):
    """Represents a single user search."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.CharField(max_length=500)
    num_sites = models.IntegerField(default=5)
    provider = models.CharField(max_length=50, default="firecrawl")
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("searching", "Searching"),
            ("crawling", "Crawling"),
            ("parsing", "Parsing"),
            ("normalizing", "Normalizing"),
            ("comparing", "Comparing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Search queries"

    def __str__(self):
        return f"[{self.status}] {self.query}"


class SearchResult(models.Model):
    """A single URL result from a search."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_query = models.ForeignKey(
        SearchQuery,
        on_delete=models.CASCADE,
        related_name="results",
    )
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=500, blank=True, default="")
    description = models.TextField(blank=True, default="")
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"#{self.position} — {self.title or self.url}"


class RawMarkdown(models.Model):
    """Raw markdown content extracted from a search result page."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_result = models.OneToOneField(
        SearchResult,
        on_delete=models.CASCADE,
        related_name="raw_markdown",
    )
    content = models.TextField(blank=True, default="")
    content_length = models.IntegerField(default=0)
    extracted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Raw markdown"

    def save(self, *args, **kwargs):
        self.content_length = len(self.content) if self.content else 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Markdown for {self.search_result.url} ({self.content_length} chars)"


class ParsedProduct(models.Model):
    """Structured JSON output extracted by the Parser Agent from RawMarkdown."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_result = models.OneToOneField(
        SearchResult,
        on_delete=models.CASCADE,
        related_name="parsed_product",
    )
    raw_markdown = models.OneToOneField(
        RawMarkdown,
        on_delete=models.CASCADE,
        related_name="parsed_product",
    )

    # Store the completely structured JSON dict
    data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True, null=True)

    parsed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Parsed products"

    def __str__(self):
        return f"Structured JSON for {self.search_result.url}"


class NormalizedProduct(models.Model):
    """Phase 3: Normalized specifications and price from ParsedProduct."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parsed_product = models.OneToOneField(
        ParsedProduct,
        on_delete=models.CASCADE,
        related_name="normalized",
    )
    normalized_specs = models.JSONField(default=dict)
    normalized_price = models.JSONField(default=dict)
    normalized_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Normalized products"

    def __str__(self):
        return f"Normalized specs for {self.parsed_product.search_result.url}"


class ComparisonResult(models.Model):
    """Phase 4: Comparison matrix for all products in a SearchQuery."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_query = models.OneToOneField(
        SearchQuery,
        on_delete=models.CASCADE,
        related_name="comparison",
    )
    data = models.JSONField(default=dict)
    compared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Comparison results"

    def __str__(self):
        return f"Comparison for '{self.search_query.query}'"
