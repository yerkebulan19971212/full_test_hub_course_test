from rest_framework import serializers


class NameSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    # @staticmethod
    def get_name(self, obj):
        return obj.name_kz
        language = self.context.get('request').headers.get('language', 'kz')
        if language == 'kz':
            return obj.name_kz
        return obj.name_ru
