from django.db import models


class EventManager(models.Manager):
    """
    Custom manager for Cycle model

    This custom manager allow us to use property
    directly in the filter request
    """
    def filter(self, is_active=None, *args, **kwargs):
        filtered_event = super(
            EventManager,
            self
        ).filter(*args, **kwargs)

        if is_active is not None:
            list_exclude = list()

            for event in filtered_event:
                if event.is_active != is_active:
                    list_exclude.append(event)

            filtered_event = filtered_event.exclude(
                pk__in=[event.pk for event in list_exclude]
            )

        return filtered_event
