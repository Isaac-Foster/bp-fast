class UserBusinessRules:
    """Regras de negócio do usuário"""

    @staticmethod
    def should_block_user(attempts: int, threshold: int = 3) -> bool:
        """Determina se usuário deve ser bloqueado"""
        return attempts >= threshold

    @staticmethod
    def can_attempt_login(blocked: bool, allowed: bool) -> bool:
        """Verifica se usuário pode tentar login"""
        return not blocked and allowed

    @staticmethod
    def needs_otp_setup(user) -> bool:
        """Verifica se usuário precisa configurar OTP"""
        return user.secret_otp and not user.otp
