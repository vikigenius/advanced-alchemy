"""Example domain objects for testing."""

from __future__ import annotations

from datetime import date, datetime
from typing import List
from uuid import UUID

from sqlalchemy import Column, FetchedValue, ForeignKey, String, Table, func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from advanced_alchemy.base import (
    TableArgsType,  # pyright: ignore[reportPrivateUsage]
    UUIDAuditBase,
    UUIDBase,
    UUIDv6Base,
    UUIDv7Base,
    merge_table_arguments,
)
from advanced_alchemy.mixins import SlugKey
from advanced_alchemy.types.encrypted_string import EncryptedString, EncryptedText


class UUIDAuthor(UUIDAuditBase):
    """The UUIDAuthor domain object."""

    name: Mapped[str] = mapped_column(String(length=100))
    string_field: Mapped[str] = mapped_column(String(20), default="static value", nullable=True)
    dob: Mapped[date] = mapped_column(nullable=True)
    books: Mapped[List[UUIDBook]] = relationship(
        lazy="selectin",
        back_populates="author",
        cascade="all, delete",
    )


class UUIDBook(UUIDBase):
    """The Book domain object."""

    title: Mapped[str] = mapped_column(String(length=250))
    author_id: Mapped[UUID] = mapped_column(ForeignKey("uuid_author.id"))
    author: Mapped[UUIDAuthor] = relationship(lazy="joined", innerjoin=True, back_populates="books")


class UUIDSlugBook(UUIDBase, SlugKey):
    """The Book domain object with a slug key."""

    title: Mapped[str] = mapped_column(String(length=250))
    author_id: Mapped[str] = mapped_column(String(length=250))

    @declared_attr.directive
    @classmethod
    def __table_args__(cls) -> TableArgsType:
        return merge_table_arguments(
            cls,
            table_args={"comment": "Slugbook"},
        )


class UUIDEventLog(UUIDAuditBase):
    """The event log domain object."""

    logged_at: Mapped[datetime] = mapped_column(default=datetime.now())
    payload: Mapped[dict] = mapped_column(default={})


class UUIDSecret(UUIDv7Base):
    """The secret domain model."""

    secret: Mapped[str] = mapped_column(
        EncryptedString(key="super_secret"),
    )
    long_secret: Mapped[str] = mapped_column(
        EncryptedText(key="super_secret"),
    )
    length_validated_secret: Mapped[str] = mapped_column(
        EncryptedString(key="super_secret", length=10),
        nullable=True,
    )


class UUIDModelWithFetchedValue(UUIDv6Base):
    """The ModelWithFetchedValue UUIDBase."""

    val: Mapped[int]
    updated: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        server_onupdate=FetchedValue(),
    )


uuid_item_tag = Table(
    "uuid_item_tag",
    UUIDBase.metadata,
    Column("item_id", ForeignKey("uuid_item.id"), primary_key=True),
    Column("tag_id", ForeignKey("uuid_tag.id"), primary_key=True),
)


class UUIDItem(UUIDBase):
    name: Mapped[str] = mapped_column(String(length=50))
    description: Mapped[str] = mapped_column(String(length=100), nullable=True)
    tags: Mapped[List[UUIDTag]] = relationship(secondary=lambda: uuid_item_tag, back_populates="items")


class UUIDTag(UUIDAuditBase):
    """The event log domain object."""

    name: Mapped[str] = mapped_column(String(length=50))
    items: Mapped[List[UUIDItem]] = relationship(secondary=lambda: uuid_item_tag, back_populates="tags")


class UUIDRule(UUIDAuditBase):
    """The rule domain object."""

    name: Mapped[str] = mapped_column(String(length=250))
    config: Mapped[dict] = mapped_column(default=lambda: {})
