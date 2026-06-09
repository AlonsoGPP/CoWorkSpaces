from uuid import UUID

from application.dto.auth_dto import AuthenticatedUserDTO
from application.interfaces.token_service import TokenService
from application.interfaces.unit_of_work import UnitOfWork
from domain.exceptions import AuthenticationError, AuthorizationError


class ResolveAuthenticatedUserUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        token_service: TokenService,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._token_service = token_service

    def execute(self, access_token: str) -> AuthenticatedUserDTO:
        payload = self._token_service.decode_access_token(access_token)

        try:
            user_id = UUID(payload.subject)
        except ValueError as error:
            raise AuthenticationError("Token invalido o expirado") from error

        with self._unit_of_work as uow:
            user = uow.user_repository.get_by_id(user_id)

        if user is None:
            raise AuthenticationError("Token invalido o expirado")

        if not user.is_active:
            raise AuthorizationError("El usuario se encuentra inactivo")

        return AuthenticatedUserDTO(user_id=user.id, email=user.email)
