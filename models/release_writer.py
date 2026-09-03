from datetime import datetime

from . import db


class ReleaseWriter(db.Model):
    __tablename__ = "release_writers"

    # =====================================================
    # PRIMARY KEY / RELATIONSHIP
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    release_id = db.Column(
        db.Integer,
        db.ForeignKey("releases.id"),
        nullable=False,
        index=True,
    )


    # =====================================================
    # WRITER INFORMATION
    # =====================================================

    writer_name = db.Column(
        db.String(200),
        nullable=False,
    )

    pro_publisher = db.Column(
        db.Text,
        nullable=True,
    )

    split_percent = db.Column(
        db.Float,
        nullable=True,
    )

    ipi_number = db.Column(
        db.String(100),
        nullable=True,
    )


    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"<ReleaseWriter {self.writer_name}>"
        )