from rest_framework import serializers


class NameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        language = self.context.get('request').headers.get('language', 'kz')
        if language == 'kz':
            return obj.name_kz
        elif language == 'en':
            return obj.name_ru
        return obj.name_ru
