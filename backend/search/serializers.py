from rest_framework import serializers


class SearchRequestSerializer(serializers.Serializer):
    # Тип пошуку: тільки одне з трьох значень, інакше помилка 400
    type = serializers.ChoiceField(choices=["users", "repositories", "issues"])
    query = serializers.CharField(min_length=3, max_length=256, trim_whitespace=True)
    page = serializers.IntegerField(min_value=1,default=1,required=False)

class UserItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    login = serializers.CharField()
    avatar_url = serializers.URLField()
    html_url = serializers.URLField()


class RepositoryItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    full_name = serializers.CharField()
    owner_login = serializers.CharField()
    html_url = serializers.URLField()
    description = serializers.CharField(allow_null=True, allow_blank=True)
    stars = serializers.IntegerField()
    forks = serializers.IntegerField()
    language = serializers.CharField(allow_null=True, allow_blank=True)


class IssueItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    html_url = serializers.URLField()
    state = serializers.CharField()
    author_login = serializers.CharField(allow_null=True)
    comments = serializers.IntegerField()
    created_at = serializers.DateTimeField()
