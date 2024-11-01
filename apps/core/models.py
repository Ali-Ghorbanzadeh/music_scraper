from django.db import models
from django.core.cache import cache
from apps.core.managers import LogicalManager
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LogicalDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False)

    objects = LogicalManager()

    def delete(self, using=None, keep_parents=False):
        if not self.is_deleted:
            self.is_deleted = True
            self.save(update_fields=["is_deleted"])

    class Meta:
        abstract = True


# class CacheMetaClass:
#     def __new__(cls, name, bases, attrs, **kwargs):
#         if not attrs.get('Meta', None) or not getattr(attrs['Meta'], 'abstract', False):
#             if 'lookup_field' not in attrs:
#                 raise TypeError(f"Model {name} must define a 'lookup_field' field")
#
#             elif 'cache_time' not in attrs:
#                 raise TypeError(f"Model {name} must define a 'lookup_field' field")
#
#         return super().__new__(cls)


class CacheRetrieveMixin:
    """ CACHING """
    def retrieve(self, request, *args, **kwargs):
        field = kwargs.get(self.lookup_field)
        obj = cache.get(f'{self.__class__.__name__}_{field}')
        if obj is None:
            if self.lookup_field == 'pk' or self.lookup_field == 'id':
                assert field.isdigit(), 'field must be integer !'
                instance = self.queryset.filter(id=field)
            else:
                instance = self.queryset.filter(**{f'{self.lookup_field}__icontains':field})

            cache.set(
                key=f'{self.__class__.__name__}_{field}',
                value=instance,
                timeout=self.cache_time,
            )
            print('cashed')
            obj = cache.get(f'{self.__class__.__name__}_{field}')

        if not obj:
            return super().retrieve(self, request, *args, **kwargs)

        elif len(obj) == 1:
            serializer = self.get_serializer(obj.first())

        else:
            serializer = self.get_serializer(obj, many=True)

        return Response(serializer.data)

    class Meta:
        abstract = True
        