# otp_manager.py
import io
import base64

import pyotp
import qrcode


class OTPManager:
    @staticmethod
    def generate_secret() -> str:
        """Gera um secret base32 (guarde no seu banco, ligado ao usuário)."""
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(secret: str, name: str, app_name: str) -> str:
        """
        Gera a URI padrão (otpauth://...) para ser convertida em QR Code
        e vinculada no Google Authenticator / Authy.
        """

        ## default: 30s, 6 dígitos, SHA1
        uri = pyotp.TOTP(secret, interval=30, digits=6).provisioning_uri(
            name=name, issuer_name=app_name
        )
        image = qrcode.make(uri)
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        image_base64 = base64.b64encode(bio.getvalue()).decode('utf-8')
        return image_base64

    @staticmethod
    def verify_code(secret: str, otp_code: str) -> bool:
        """
        Valida o código TOTP informado pelo usuário.
        valid_window aceita ±1 janela de 30s (ajuda com atraso de relógio).
        """
        totp = pyotp.TOTP(
            secret, interval=30, digits=6
        )  # default: 30s, 6 dígitos, SHA1
        return totp.verify(otp_code)

    @staticmethod
    def generate_current_otp(secret: str) -> str:
        """Opcional: gera o OTP atual (útil para teste)."""
        return pyotp.TOTP(secret, interval=30, digits=6).now()
