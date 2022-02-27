from rest_framework.serializers import ModelSerializer
from rest_framework import exceptions
from ags.AGSTask.models import AGSDocuments, AGSTask
from ge_py.quickstart.models import is_null_or_empty


class AGSTaskViewSetSerializer(ModelSerializer):
    
    def create (self, validated_data):
        documents = self.context['documents']
        doc_names = []
        for document in documents:
            doc_names.append(document.name)
        validated_data["files"] = ",".join(doc_names)
        task = AGSTask.objects.create(**validated_data)
        for document in documents:
            doc = AGSDocuments.objects.create(task=task, document=document)
        return task
    class Meta:
        model = AGSTask
        fields = '__all__'