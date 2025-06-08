from rest_framework import serializers
from .models import Leak


class LeakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leak
        fields = [
            "id",
            "site",
            "company",
            "country",
            "found_at",
            "source_url",
            "views",
            "publication_date",
            "amount_of_data",
            "information",
            "comment",
            "download_links",
            "rar_password",
        ]
