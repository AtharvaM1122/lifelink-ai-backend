from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification

from app.repositories.notification_repository import (
    NotificationRepository
)

from app.repositories.emergency_response_repository import (
    EmergencyResponseRepository
)

from app.schemas.notification import (
    NotificationCreate
)

from app.repositories.emergency_contact_repository import (
    EmergencyContactRepository
)

from app.repositories.hospital_repository import (
    HospitalRepository
)


class NotificationService:

    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        response_id: int,
        notification_data: NotificationCreate,
        commit: bool = True
    ):

        # Find emergency response
        response = EmergencyResponseRepository.get_by_id(
            db,
            response_id
        )

        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency response not found."
            )

        # Make sure response belongs to current user
        if response.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to access this response."
            )

        # Validate recipient type
        allowed_recipient_types = [
            "EMERGENCY_CONTACT",
            "HOSPITAL"
        ]

        if notification_data.recipient_type not in allowed_recipient_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid recipient type."
            )

        # Validate recipient

        if notification_data.recipient_type == "EMERGENCY_CONTACT":

            if notification_data.recipient_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Emergency contact recipient ID is required."
                )

            contact = EmergencyContactRepository.get_by_id(
                db,
                notification_data.recipient_id
            )

            if not contact:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Emergency contact not found."
                )

            # Ensure contact belongs to the emergency user
            if contact.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "You are not allowed to send a notification "
                        "to this emergency contact."
                    )
                )


        elif notification_data.recipient_type == "HOSPITAL":

            if notification_data.recipient_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Hospital recipient ID is required."
                )

            hospital = HospitalRepository.get_by_id(
                db,
                notification_data.recipient_id
            )

            if not hospital:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Hospital not found."
                )

            if hospital.status != "ACTIVE":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Hospital is not active."
                )

        # Validate channel
        allowed_channels = [
            "SMS",
            "PUSH"
        ]

        if notification_data.channel not in allowed_channels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid notification channel."
            )

        # Create notification
        new_notification = Notification(
            response_id=response_id,
            user_id=user_id,
            recipient_type=notification_data.recipient_type,
            recipient_id=notification_data.recipient_id,
            channel=notification_data.channel,
            status="PENDING",
            message=notification_data.message
        )

        return NotificationRepository.create(
            db,
            new_notification,
            commit=commit
        )

    @staticmethod
    def get_notification(
        db: Session,
        user_id: int,
        notification_id: int
    ):

        notification = NotificationRepository.get_by_id(
            db,
            notification_id
        )

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found."
            )

        # Ownership check
        if notification.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to access this notification."
            )

        return notification

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int
    ):

        return NotificationRepository.get_by_user(
            db,
            user_id
        )

    @staticmethod
    def get_response_notifications(
        db: Session,
        user_id: int,
        response_id: int
    ):

        # Verify response exists
        response = EmergencyResponseRepository.get_by_id(
            db,
            response_id
        )

        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency response not found."
            )

        # Verify ownership
        if response.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to access this response."
            )

        return NotificationRepository.get_by_response(
            db,
            response_id
        )

    