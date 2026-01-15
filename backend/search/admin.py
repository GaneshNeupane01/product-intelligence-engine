from django.contrib import admin
from .models import SearchQuery, SearchResult, RawMarkdown


class SearchResultInline(admin.TabularInline):
    model = SearchResult
    extra = 0
    readonly_fields = ["id", "url", "title", "position", "created_at"]


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ["query", "num_sites", "provider", "status", "created_at"]
    list_filter = ["status", "provider"]
    search_fields = ["query"]
    inlines = [SearchResultInline]


@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ["title", "url", "position", "search_query", "created_at"]
    list_filter = ["search_query__status"]


@admin.register(RawMarkdown)
class RawMarkdownAdmin(admin.ModelAdmin):
    list_display = ["search_result", "content_length", "extracted_at"]
