"""Resolution d'identite inter-fournisseurs (aujourd'hui: equipes uniquement).

Le meme principe (table de correspondance + resolver) pourra etre reproduit pour
les ligues ou les joueurs le jour ou une 2e source les concerne aussi -- pas
construit par anticipation tant qu'un seul fournisseur (api_sports) existe.
"""

from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .models.team import Team
from .models.team_identity_map import TeamIdentityMap


class TeamResolver:
    """Trouve ou cree le master_team_id d'une equipe pour (provider, sport, team_id)."""

    @staticmethod
    def resolve(session: Session, provider: str, sport: str, team_id: int) -> int:
        existing = session.execute(
            select(TeamIdentityMap.master_team_id).where(
                TeamIdentityMap.provider == provider,
                TeamIdentityMap.sport == sport,
                TeamIdentityMap.team_id == team_id,
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing

        # Nouvelle entite: son propre id de ligne sert de master_team_id initial.
        row = TeamIdentityMap(provider=provider, sport=sport, team_id=team_id, master_team_id=0)
        session.add(row)
        session.flush()  # genere row.id
        row.master_team_id = row.id
        session.flush()
        return row.master_team_id

    @staticmethod
    def link(session: Session, provider: str, sport: str, team_id: int, master_team_id: int) -> None:
        """Rattache explicitement (provider, sport, team_id) a un master_team_id deja
        connu -- utilise une fois qu'on a identifie que 2 sources decrivent la meme
        equipe reelle (rapprochement manuel ou automatique, hors scope de ce module).

        Met aussi a jour `teams.master_team_id` immediatement si la ligne existe deja:
        sans ca, l'effet n'apparaitrait qu'a la prochaine ingestion de ce provider."""
        existing = session.execute(
            select(TeamIdentityMap).where(
                TeamIdentityMap.provider == provider,
                TeamIdentityMap.sport == sport,
                TeamIdentityMap.team_id == team_id,
            )
        ).scalar_one_or_none()
        if existing is not None:
            existing.master_team_id = master_team_id
        else:
            session.add(
                TeamIdentityMap(provider=provider, sport=sport, team_id=team_id, master_team_id=master_team_id)
            )

        session.execute(
            update(Team)
            .where(Team.provider == provider, Team.sport == sport, Team.team_id == team_id)
            .values(master_team_id=master_team_id)
        )
        session.flush()
