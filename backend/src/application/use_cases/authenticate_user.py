from application.dto.auth_dto import AuthTokenOutputDTO, LoginInputDTO
from application.interfaces.password_hasher import PasswordHasher
from application.interfaces.token_service import TokenService
from application.interfaces.unit_of_work import UnitOfWork
from domain.exceptions import AuthorizationError, InvalidCredentialsError


class AuthenticateUserUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        *,
        access_token_ttl_seconds: int,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._access_token_ttl_seconds = access_token_ttl_seconds

    def execute(self, input_dto: LoginInputDTO) -> AuthTokenOutputDTO:
        normalized_email = input_dto.email.strip().lower()

        with self._unit_of_work as uow:
            user = uow.user_repository.get_by_email(normalized_email)

        if user is None:
            raise InvalidCredentialsError("Credenciales invalidas")

        if not self._password_hasher.verify_password(
            input_dto.password,
            user.password_hash,
        ):
            raise InvalidCredentialsError("Credenciales invalidas")

        if not user.is_active:
            raise AuthorizationError("El usuario se encuentra inactivo")

        token = self._token_service.create_access_token(
            subject=str(user.id),
            additional_claims={"email": user.email},
        )
        return AuthTokenOutputDTO(
            access_token=token,
            token_type="bearer",
            expires_in_seconds=self._access_token_ttl_seconds,
        )
