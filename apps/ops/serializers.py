# -*- coding: utf-8 -*-
from ops import models
from rest_framework import serializers

__all__ = [
    "MetaSerializer", "MetaContentSerializer",

]


class MetaContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.META_CONTENT
        fields = (
            'id', 'name', 'module', 'args', 'sort', 'need_file'
        )
        read_only_fields = (
            'id',
        )


class MetaSerializer(serializers.ModelSerializer):
    hosts = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Host.objects.all())
    contents = MetaContentSerializer(required=True, many=True, allow_null=True)
    group = serializers.PrimaryKeyRelatedField(queryset=models.Group.objects.all())
    group_name = serializers.CharField(source="group.name",read_only=True)
    qrcode = serializers.CharField(required=True, write_only=True,)

    class Meta:
        model = models.META
        fields = (
            'id', 'uuid', 'hosts', 'contents', 'group', 'group_name', 'info', 'qrcode'
        )
        read_only_fields = (
            'id', 'uuid','group_name'
        )

    def create(self, validated_data):
        contents = validated_data.pop('contents')
        id_list = []
        for content in contents:
            content_instance = models.META_CONTENT.objects.create(**content)
            id_list.append(content_instance.id)
        hosts = validated_data.pop('hosts')

        contests_list = models.META_CONTENT.objects.filter(id__in=id_list)

        obj = models.META.objects.create(**validated_data)
        obj.contents.add(*contests_list)
        obj.hosts.set(hosts)
        obj.save()

        return obj

    def update(self, instance, validated_data):
        contents = validated_data.pop('contents')
        obj = super(MetaSerializer,self).update(instance,validated_data)
        for content in obj.contents.all():
            content.delete()
        obj.contents.clear()

        id_list = []
        for content in contents:
            content_instance = models.META_CONTENT.objects.create(**content)
            id_list.append(content_instance.id)

        contests_list = models.META_CONTENT.objects.filter(id__in=id_list)
        obj.contents.add(*contests_list)
        obj.save()
        return obj


class MissionNeedFileSerializer(serializers.ModelSerializer):
    filelist = serializers.ListField(source='file_list',read_only=True)

    class Meta:
        model = models.Mission
        fields = (
            'filelist',
        )


class MissionSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=models.Group.objects.all())
    metas = serializers.PrimaryKeyRelatedField(many=True, queryset=models.META.objects.all())
    group_name = serializers.CharField(source="group.name",read_only=True)
    counts = serializers.IntegerField(source="count",read_only=True)

    class Meta:
        model = models.Mission
        fields = (
            'id', 'uuid', 'group', 'metas', 'info', 'need_validate', 'group_name', 'counts'
        )
        read_only_fields = (
            'id', 'uuid', 'group_name', 'counts'
        )


class PushMissionSerializer(serializers.ModelSerializer):
    mission = serializers.PrimaryKeyRelatedField(queryset=models.Mission.objects.all())

    class Meta:
        model = models.Push_Mission
        fields = (
            'mission',
        )

    def create(self, validated_data):
        mission = validated_data.pop('mission')
        obj = models.Push_Mission(mission=mission)
        obj.save()
        return obj
