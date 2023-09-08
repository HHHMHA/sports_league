from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework.relations import RelatedField


class CustomOutputFieldMixin:
    def __init__(self, **kwargs):
        self.instance_serializer_class = kwargs.pop("instance_serializer", None)
        super().__init__(**kwargs)

    def to_representation(self, value):
        if self.instance_serializer is not None:
            return self.instance_serializer(value, context=self.context).data
        return super().to_representation(value)

    def bind(self, field_name, parent):
        if self.instance_serializer_class is None:
            method_name = f"get_{field_name}_serializer_class"
            func = getattr(parent, method_name, None)
            if callable(func):
                self.instance_serializer_class = func()

        super().bind(field_name, parent)


class UniqueRelatedField(CustomOutputFieldMixin, RelatedField):
    default_error_messages = {
        "required": _("This field is required."),
        "does_not_exist": _("Invalid unique value '{unique_value}' - object does not exist."),
        "fail_create": _("Failed to create model based on '{unique_value}'"),
        "incorrect_type": _("Incorrect type. Expected unique value, received {data_type}."),
    }

    def __init__(self, unique_field, create=False, **kwargs):
        super().__init__(**kwargs)
        self.unique_field = unique_field
        self.create = create
        assert hasattr(self.queryset.model, self.unique_field), _("Field doesn't exist")

    def use_pk_only_optimization(self):
        return False

    def to_internal_value(self, data):
        queryset = self.get_queryset()
        look_up = {self.unique_field: data}
        try:
            if isinstance(data, bool):
                raise TypeError
            return queryset.get(**look_up)
        except ObjectDoesNotExist:
            if self.create:
                try:
                    return queryset.model.objects.create(**look_up)
                except ObjectDoesNotExist:
                    self.fail("fail_create", unique_value=data)
            else:
                self.fail("does_not_exist", unique_value=data)
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data).__name__)

    def to_representation(self, value):
        return getattr(value, self.unique_field)
