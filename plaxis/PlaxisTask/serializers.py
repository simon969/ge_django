from datetime import datetime
import pytz
import json

# # https://www.django-rest-framework.org/tutorial/1-serialization

from rest_framework import serializers

from plaxis.PlaxisTask.models import PlaxisTask, LANGUAGE_CHOICES, STYLE_CHOICES, any_task_connected

# Manually assign serializer fields
class PlaxisTaskSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    conn = serializers.JSONField(required=True)
    owner = serializers.CharField(max_length=100, required=True)
    query =  serializers.JSONField(required=True)
    createdDT = serializers.DateTimeField()
    completedDT = serializers.DateTimeField()
    is_connected = serializers.BooleanField(required=True)
    progress = serializers.CharField(style={'base_template': 'textarea.html'})
    result = serializers.CharField(style={'base_template': 'textarea.html'})
    files = serializers.CharField(style={'base_template': 'textarea.html'})
    status =  serializers.IntegerField(required=True)
    
    def create(self, validated_data):
        """
        Create and return a new `Plaxis` instance, given the validated data.
        """
        return PlaxisTask.objects.create(**validated_data)
        

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.conn = validated_data.get('conn', instance.conn)
        instance.owner = validated_data.get('owner', instance.owner)
        instance.query = validated_data.get('query', instance.query)
        instance.completedDT = validated_data.get('completedDT', instance.completedDT)
        instance.createdDT = validated_data.get('createdDT', instance.createdDT)
        instance.is_connected = validated_data.get('is_connected', instance.is_connected)
        instance.progress = validated_data.get('progresss', instance.progress)
        instance.result = validated_data.get('result', instance.result)
        instance.files = validated_data.get('files', instance.files)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
    
# Alternatively get serializer fields directly from model 
class PlaxisTaskSerializerForList(serializers.ModelSerializer):
    class Meta:
        model = PlaxisTask
       
class PlaxisTaskSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = PlaxisTask
        fields = ['id', 'conn', 'query', 'owner','createdDT']
       
    def create(self, validated_data):
        """
        Create and return a new `Plaxis` instance, given the validated data.
        """
        print (validated_data)
        task = PlaxisTask(
            conn = validated_data['conn'],
            query = validated_data['query'],
            owner = validated_data['owner'],
            createdDT = datetime.now(pytz.UTC)
        )
        task.save()
        return task
    def is_available(self, validated_data):
                conn = json.loads(validated_data['conn'].replace("'","\""))
                host = conn["host"]
                port = conn["port"]
                return not any_task_connected(host, port)
    
                #     msg  = "Unable to create new ge_task, host({0}) on port({1}) is currently in use by another task".format(host, port)
                #     return JsonResponse({'message': msg}, status=409)
                # else:
    
     