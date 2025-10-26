from fastapi import APIRouter, Depends, Request, Response, Query

from src.infra.security.auth import get_current_user

router = APIRouter(prefix='/otp')


def _ensure_png_bytes(image_any) -> bytes:
    if isinstance(image_any, bytes):
        return image_any
    if isinstance(image_any, str):
        # assume base64 sem prefixo data:; se tiver, remova o cabeçalho antes
        return base64.b64decode(image_any)
    try:
        # Tentativa: objeto PIL.Image
        from PIL import Image

        if isinstance(image_any, Image.Image):
            buf = io.BytesIO()
            image_any.save(buf, format='PNG')
            return buf.getvalue()
    except Exception:
        pass
    raise TypeError('Formato de imagem não suportado')


@router.get('/create')
async def create(
    request: Request,
    response: Response,
    auth_response=Depends(get_current_user()),
):
    return auth_response


@router.get('/create/qrcode')
async def create_qrcode(
    request: Request,
    response: Response,
    auth_response=Depends(get_current_user()),
):
    auth_response = auth_response
    print(auth_response)
    pass


@router.get('/verify')
async def verify(
    request: Request,
    response: Response,
    # feature_flag: str = Query(None),
    # operation_id: str = Query(None),
    opt_code: str = Query(None, pattern=r'^\d{6}$'),
    auth_response=Depends(get_current_user),
):
    """
    Verifica o código OTP
    Extra:
    recurso futuro/citaçao de uso
        feature_flag:
            ditara em na tabela a qual recurso pertence a solicitaçao DE 2fa
            ex: 'login', 'register', 'change_password', 'change_email', 'transfer'
        operation_id:
            ditara o id da operação que está sendo realizada
            ex: 1
        conjunto de fields buscados em conjunto
        para aprovar ou rejeitar a solicitação
    """
    user, payload = auth_response
    pass
