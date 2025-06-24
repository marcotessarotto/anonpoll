from .models import EventLog, Subscriber
from django.utils import timezone


def create_event_log(event_type, event_title, event_data, event_target=None):
    """
    Creates an instance of EventLog with the provided details.

    Args:
    event_type (str): The type of the event (e.g., EMAIL_SENT, NEWSLETTER_SUBSCRIPTION_CONFIRMED).
    event_title (str): A short title or description of the event.
    event_data (str): Additional data or details about the event.
    event_target (str, optional): The target or subject of the event. Defaults to None.

    Returns:
    EventLog: The created EventLog instance.
    """
    try:
        event_log = EventLog(
            event_type=event_type,
            event_title=event_title,
            event_data=event_data,
            event_target=event_target,
            created_at=timezone.now()
        )
        event_log.save()
        return event_log
    except Exception as e:
        print(e)
        return None


def create_subscriber(email, name, surname, matricola):
    """
    Creates a new Subscriber instance and saves it to the database.

    Parameters:
    - email (str): The email of the subscriber.
    - name (str): The first name of the subscriber.
    - surname (str): The last name of the subscriber.
    - matricola (str): The matricola (unique identifier) of the subscriber.

    Returns:
    - subscriber (Subscriber): The newly created Subscriber instance.
    """
    subscriber = Subscriber(email=email, name=name, surname=surname, matricola=matricola)
    subscriber.save()
    return subscriber


def create_subscriber_if_not_exits(email, name, surname, matricola, uaf, structure):
    """
    Creates a new Subscriber instance and saves it to the database if it does not already exist.

    Parameters:
    - email (str): The email of the subscriber.
    - name (str): The first name of the subscriber.
    - surname (str): The last name of the subscriber.
    - matricola (str): The matricola (unique identifier) of the subscriber.

    Returns:
    - subscriber (Subscriber): The newly created or existing Subscriber instance.
    """
    subscriber, created = Subscriber.objects.get_or_create(email=email, name=name, surname=surname, matricola=matricola, uaf=uaf, structure=structure)
    return subscriber


def create_or_update_subscriber(email, name, surname, matricola, uaf, structure):
    """
    Creates a new Subscriber instance or updates an existing one based on email and matricola lookup.
    If multiple subscribers exist with the same email and matricola, updates the first one found.

    Parameters:
    - email (str): The email of the subscriber.
    - name (str): The first name of the subscriber.
    - surname (str): The last name of the subscriber.
    - matricola (str): The matricola (unique identifier) of the subscriber.
    - uaf (str): The UAF of the subscriber.
    - structure (str): The structure of the subscriber.

    Returns:
    - tuple: (subscriber, created) where subscriber is the Subscriber instance
             and created is a boolean indicating if it was newly created.
    """
    try:
        # Try to find the existing subscriber by email and matricola
        # Use filter().first() to handle multiple matches gracefully
        subscriber = Subscriber.objects.filter(email=email, matricola=matricola).first()

        if subscriber:
            # Update the existing subscriber with new data
            subscriber.name = name
            subscriber.surname = surname
            subscriber.uaf = uaf
            subscriber.structure = structure
            subscriber.save()

            return subscriber, False  # False indicates it was updated, not created
        else:
            # No subscriber found, create new one
            subscriber = Subscriber.objects.create(
                email=email,
                name=name,
                surname=surname,
                matricola=matricola,
                uaf=uaf,
                structure=structure
            )

            return subscriber, True  # True indicates it was newly created

    except Exception as e:
        # Handle any unexpected errors by creating a new subscriber
        print(f"Error in create_or_update_subscriber: {e}")
        subscriber = Subscriber.objects.create(
            email=email,
            name=name,
            surname=surname,
            matricola=matricola,
            uaf=uaf,
            structure=structure
        )

        return subscriber, True  # True indicates it was newly created