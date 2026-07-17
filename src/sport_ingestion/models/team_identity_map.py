from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..db.base import Base


class TeamIdentityMap(Base):
    """Correspondance entre l'id d'une equipe cote fournisseur et un id "maitre"
    stable, commun a toutes les sources qui decrivent la meme equipe reelle.

    `id` est la cle propre de CETTE ligne de correspondance (une par source).
    `master_team_id` est la valeur partagee entre plusieurs lignes qui decrivent
    la meme equipe reelle -- ce n'est PAS une cle unique: plusieurs sources
    (une ligne chacune) peuvent legitimement pointer vers le meme master_team_id.
    """

    __tablename__ = "team_identity_map"
    __table_args__ = (UniqueConstraint("provider", "sport", "team_id", name="uq_team_identity_map_source"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(32))
    sport: Mapped[str] = mapped_column(String(32))
    team_id: Mapped[int] = mapped_column(Integer)
    master_team_id: Mapped[int] = mapped_column(Integer, index=True)
